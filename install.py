#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = ["tomlkit>=0.13,<1"]
# ///

from __future__ import annotations

import argparse
import logging
import os
import shutil
import stat
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import tomlkit

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
LOGGER = logging.getLogger(__file__)

REPO_ROOT = Path(__file__).resolve().parent
SOURCE_DIR = REPO_ROOT / "home"
BACKUP_ROOT = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state")) / "dotfiles-backups"
VSCODE_SETTINGS_SOURCE = REPO_ROOT / "apps" / "vscode" / "settings.json"
MACOS_VSCODE_SETTINGS_DESTINATION = Path(
    "Library/Application Support/Code/User/settings.json"
)

CODEX_SKILLS_DIR = REPO_ROOT / "agents" / "codex" / "skills"

# Install only maintained personal skills. Other directories in CODEX_SKILLS_DIR
# may be vendored system skills or unfinished drafts.
INSTALLED_CODEX_SKILLS = ("deslop-code", "deslop-prose")

CODEX_CONFIG_RELATIVE_PATH = Path(".codex/config.toml")
CODEX_EXTERNAL_IMPORT_SETTING = "external-agent-import-sync-enabled"
IMPORTED_PLUGIN_MARKETPLACES = ("claude-plugins-official", "skypilot")
DENIED_CODEX_PLUGINS = (
    "explanatory-output-style@claude-plugins-official",
    "security-guidance@claude-plugins-official",
    "posthog@claude-plugins-official",
)

# Claude Code reads its whole config tree from $CLAUDE_CONFIG_DIR, defaulting to
# ~/.claude. That tree includes .claude.json, which carries oauthAccount — so a second
# config dir is a second login, and several subscriptions can run concurrently. These env
# vars name the extra dirs; set them per host in .env / .env_linux / .env_macos.
CLAUDE_CONFIG_SUBDIR = ".claude"
EXTRA_CLAUDE_CONFIG_DIR_VARS = ("CLAUDE_CONFIG_DIR_PERSONAL", "CLAUDE_CONFIG_DIR_WORK_EXTRA")

# Shared across accounts but not tracked in the repo: marketplace clones are bulky and the
# enabled plugin set is already pinned by the shared settings.json, so one copy serves all.
# Anything account-specific (.claude.json, .credentials.json, projects/, history.jsonl,
# sessions/) is deliberately absent — Claude Code creates it per config dir.
SHARED_CLAUDE_LOCAL_STATE = ("plugins",)


def discover_dotfiles(source: Path) -> list[str]:
    """Walk source and return all file paths relative to it."""
    return sorted(str(p.relative_to(source)) for p in source.rglob("*") if p.is_file())


def extra_claude_config_dirs(home: Path) -> list[Path]:
    """Return the additional Claude Code config dirs named by the environment."""
    default_dir = (home / CLAUDE_CONFIG_SUBDIR).resolve()
    config_dirs = []

    for var in EXTRA_CLAUDE_CONFIG_DIR_VARS:
        value = os.environ.get(var)
        if not value:
            LOGGER.debug("%s unset, skipping", var)
            continue
        config_dir = Path(value).expanduser()
        if config_dir.resolve() == default_dir:
            LOGGER.warning("%s points at the default config dir %s, skipping", var, default_dir)
            continue
        config_dirs.append(config_dir)

    return config_dirs


def build_install_plan(
    source: Path,
    home: Path,
    codex_only: bool = False,
) -> list[tuple[Path, Path]]:
    """Return the source and destination paths managed by the installer."""
    dotfiles = discover_dotfiles(source)
    if codex_only:
        dotfiles = [rel for rel in dotfiles if Path(rel).parts[0] == ".codex"]
    installs = [(source / rel, home / rel) for rel in dotfiles]

    if sys.platform == "darwin" and not codex_only:
        installs.append(
            (VSCODE_SETTINGS_SOURCE, home / MACOS_VSCODE_SETTINGS_DESTINATION)
        )

    codex_skills = home / ".agents" / "skills"
    for skill_name in INSTALLED_CODEX_SKILLS:
        skill_source = CODEX_SKILLS_DIR / skill_name
        if not skill_source.is_dir():
            LOGGER.warning("Codex skill not found, skipping: %s", skill_source)
            continue
        installs.append((skill_source, codex_skills / skill_name))

    if not codex_only:
        claude_rels = [
            Path(rel) for rel in dotfiles if Path(rel).parts[0] == CLAUDE_CONFIG_SUBDIR
        ]
        for config_dir in extra_claude_config_dirs(home):
            for rel in claude_rels:
                installs.append(
                    (source / rel, config_dir / rel.relative_to(CLAUDE_CONFIG_SUBDIR))
                )
            for name in SHARED_CLAUDE_LOCAL_STATE:
                shared = home / CLAUDE_CONFIG_SUBDIR / name
                if not shared.exists():
                    LOGGER.warning("Shared Claude state not found, skipping: %s", shared)
                    continue
                installs.append((shared, config_dir / name))

    return sorted(installs, key=lambda install: str(install[1]))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install dotfiles via symlinks.")
    parser.add_argument(
        "--source",
        type=Path,
        default=SOURCE_DIR,
        help=f"Source directory containing dotfiles (default: {SOURCE_DIR})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change without updating destination files.",
    )
    parser.add_argument(
        "--codex-only",
        action="store_true",
        help="Apply only Codex config, instructions, agent profiles and skills.",
    )
    return parser.parse_args()


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    counter = 1
    while True:
        candidate = path.with_name(f"{path.name}.{counter}")
        if not candidate.exists():
            return candidate
        counter += 1


def is_same_symlink_target(link: Path, target: Path) -> bool:
    if not link.is_symlink():
        return False
    raw = link.readlink()
    resolved = (link.parent / raw).resolve()
    return resolved == target.resolve()


def reconcile_codex_config(raw_config: str | None) -> tuple[str, tuple[str, ...]]:
    """Return Codex config with the persistent plugin policy applied."""
    document = tomlkit.parse(raw_config) if raw_config is not None else tomlkit.document()
    changes = []

    desktop = document.get("desktop")
    if desktop is None:
        desktop = tomlkit.table()
        document["desktop"] = desktop
    elif not hasattr(desktop, "get"):
        raise ValueError("Codex config [desktop] must be a table")

    import_sync_was_enabled = desktop.get(CODEX_EXTERNAL_IMPORT_SETTING) is True

    plugins = document.get("plugins")
    if plugins is not None and not hasattr(plugins, "keys"):
        raise ValueError("Codex config [plugins] must be a table")
    if plugins is not None:
        for plugin_id in list(plugins.keys()):
            imported_plugin = import_sync_was_enabled and any(
                plugin_id.endswith(f"@{marketplace}")
                for marketplace in IMPORTED_PLUGIN_MARKETPLACES
            )
            if plugin_id in DENIED_CODEX_PLUGINS or imported_plugin:
                del plugins[plugin_id]
                changes.append(f"remove plugin {plugin_id}")

    marketplaces = document.get("marketplaces")
    if marketplaces is not None and not hasattr(marketplaces, "keys"):
        raise ValueError("Codex config [marketplaces] must be a table")
    if import_sync_was_enabled and marketplaces is not None:
        for marketplace in IMPORTED_PLUGIN_MARKETPLACES:
            if marketplace in marketplaces:
                del marketplaces[marketplace]
                changes.append(f"remove marketplace {marketplace}")

    if desktop.get(CODEX_EXTERNAL_IMPORT_SETTING) is not False:
        desktop[CODEX_EXTERNAL_IMPORT_SETTING] = False
        changes.append("disable external agent import sync")

    return tomlkit.dumps(document), tuple(changes)


def write_text_atomic(path: Path, content: str) -> None:
    """Atomically replace a text file while retaining restrictive permissions."""
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o600
    fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary_name)
    try:
        os.fchmod(fd, mode)
        with os.fdopen(fd, "w", encoding="utf-8") as temporary_file:
            temporary_file.write(content)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def install(
    source: Path,
    dry_run: bool,
    home: Path | None = None,
    backup_root: Path | None = None,
    codex_only: bool = False,
) -> None:
    source = source.resolve()
    home = Path.home() if home is None else home
    backup_root = BACKUP_ROOT if backup_root is None else backup_root
    installs = build_install_plan(source, home, codex_only=codex_only)

    codex_config = home / CODEX_CONFIG_RELATIVE_PATH
    raw_codex_config = (
        codex_config.read_text(encoding="utf-8") if codex_config.exists() else None
    )
    updated_codex_config, codex_changes = reconcile_codex_config(raw_codex_config)
    codex_config_changed = raw_codex_config != updated_codex_config

    if not installs:
        LOGGER.warning("No dotfiles found in %s.", source)

    if dry_run:
        if codex_config_changed:
            LOGGER.info("WOULD UPDATE CODEX CONFIG: %s", codex_config)
            for change in codex_changes:
                LOGGER.info("  %s", change)
        else:
            LOGGER.info("OK (Codex policy already applied): %s", codex_config)
        for src, dst in installs:
            if is_same_symlink_target(dst, src):
                LOGGER.info("OK (already linked): %s -> %s", dst, src)
            elif dst.exists(follow_symlinks=False) or dst.is_symlink():
                LOGGER.info("WOULD UPDATE: %s -> %s", dst, src)
            else:
                LOGGER.info("WOULD LINK:   %s -> %s", dst, src)
        return

    # Collect targets that will actually be replaced (exist and are not already the
    # correct symlink) so we can create one backup dir up front. Reruns where everything
    # is already linked must not create empty backup dirs.
    existing_targets = [
        dst
        for src, dst in installs
        if (dst.exists() or dst.is_symlink()) and not is_same_symlink_target(dst, src)
    ]

    backup_dir: Path | None = None
    config_needs_backup = codex_config_changed and codex_config.exists()
    if existing_targets or config_needs_backup:
        paths_to_back_up = [*existing_targets]
        if config_needs_backup:
            paths_to_back_up.append(codex_config)
        LOGGER.info(
            "Existing files found:\n%s",
            "\n".join(str(p) for p in paths_to_back_up),
        )
        backup_root.mkdir(parents=True, exist_ok=True)
        backup_dir = unique_path(backup_root / datetime.now().strftime("%Y%m%d-%H%M%S"))
        backup_dir.mkdir(parents=True, exist_ok=False)
        LOGGER.info("Created backup directory at %s", backup_dir)

    if codex_config_changed:
        if config_needs_backup:
            assert backup_dir is not None
            config_backup = backup_dir / CODEX_CONFIG_RELATIVE_PATH
            config_backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(codex_config, config_backup)
            LOGGER.info("Backed up %s -> %s", codex_config, config_backup)
        write_text_atomic(codex_config, updated_codex_config)
        LOGGER.info("Updated Codex config: %s", codex_config)
        for change in codex_changes:
            LOGGER.info("  %s", change)
    else:
        LOGGER.info("Codex policy already applied: %s", codex_config)

    for src, dst in installs:
        dst.parent.mkdir(parents=True, exist_ok=True)

        if is_same_symlink_target(dst, src):
            LOGGER.info("Already linked: %s -> %s", dst, src)
            continue

        if dst.exists() or dst.is_symlink():
            if backup_dir is None:
                backup_root.mkdir(parents=True, exist_ok=True)
                backup_dir = unique_path(backup_root / datetime.now().strftime("%Y%m%d-%H%M%S"))
                backup_dir.mkdir(parents=True, exist_ok=False)
            bk = unique_path(backup_dir / dst.relative_to(home))
            bk.parent.mkdir(parents=True, exist_ok=True)
            # shutil.move (unlike Path.rename) survives XDG_STATE_HOME on another
            # filesystem, and recreates symlinks rather than following them
            shutil.move(dst, bk)
            LOGGER.info("Backed up %s -> %s", dst, bk)

        dst.symlink_to(src)
        LOGGER.info("Linked %s -> %s", dst, src)

    LOGGER.info("Done.")


def main() -> None:
    args = parse_args()
    install(source=args.source, dry_run=args.dry_run, codex_only=args.codex_only)


if __name__ == "__main__":
    main()
