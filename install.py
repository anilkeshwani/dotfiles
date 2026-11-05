#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# ///

from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
LOGGER = logging.getLogger(__file__)

REPO_ROOT = Path(__file__).resolve().parent
SOURCE_DIR = REPO_ROOT / "home"
STATE_ROOT = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state"))
BACKUP_ROOT = STATE_ROOT / "dotfiles-backups"
MERGE_BASE_ROOT = STATE_ROOT / "dotfiles-merge-base"
VSCODE_SETTINGS_SOURCE = REPO_ROOT / "apps" / "vscode" / "settings.json"
MACOS_VSCODE_SETTINGS_DESTINATION = Path(
    "Library/Application Support/Code/User/settings.json"
)

CODEX_SKILLS_DIR = REPO_ROOT / "agents" / "codex" / "skills"

# JSON settings files that their app rewrites on every start (agy re-sorts its keys and
# replaces the file, which turns a symlink into a detached copy). These are merged instead of
# linked, as a three-way merge against the tracked file applied last time (kept under
# MERGE_BASE_ROOT). Tracked values win, entries the app added (such as agy's
# trustedWorkspaces) are kept, and entries removed from the tracked file are removed.
MERGED_JSON_SETTINGS = (".gemini/antigravity-cli/settings.json",)

# Install only maintained personal skills. Other directories in CODEX_SKILLS_DIR
# may be vendored system skills or unfinished drafts.
INSTALLED_CODEX_SKILLS = ("deslop-code", "deslop-prose")

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
        help="Apply only Codex instructions, agent profiles and skills.",
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


def three_way_merge(installed: object, tracked: object, base: object) -> object:
    """Merge tracked settings into installed ones, using base (the tracked settings applied
    last time) to tell the app's own additions from entries since dropped from the repo."""
    if isinstance(tracked, dict) and isinstance(installed, dict):
        base = base if isinstance(base, dict) else {}
        merged = {
            key: value
            for key, value in installed.items()
            if key not in tracked and key not in base
        }
        for key, value in tracked.items():
            merged[key] = (
                three_way_merge(installed[key], value, base.get(key))
                if key in installed
                else value
            )
        return merged
    if isinstance(tracked, list) and isinstance(installed, list):
        base = base if isinstance(base, list) else []
        added_by_app = [x for x in installed if x not in tracked and x not in base]
        return tracked + added_by_app
    return tracked


class LazyBackupDir:
    """One timestamped backup directory per installer run, created on first use."""

    def __init__(self, backup_root: Path, home: Path) -> None:
        self.backup_root = backup_root
        self.home = home
        self.path: Path | None = None

    def destination_for(self, dst: Path) -> Path:
        if self.path is None:
            self.backup_root.mkdir(parents=True, exist_ok=True)
            self.path = unique_path(
                self.backup_root / datetime.now().strftime("%Y%m%d-%H%M%S")
            )
            self.path.mkdir(parents=True, exist_ok=False)
            LOGGER.info("Created backup directory at %s", self.path)
        bk = unique_path(self.path / dst.relative_to(self.home))
        bk.parent.mkdir(parents=True, exist_ok=True)
        return bk


def install_merged_json(
    src: Path,
    dst: Path,
    dry_run: bool,
    backups: LazyBackupDir,
    base_file: Path,
) -> None:
    tracked = json.loads(src.read_text())
    # A dangling symlink (say, into a moved repo) counts as no installed settings.
    current = json.loads(dst.read_text()) if dst.is_file() else None
    base = json.loads(base_file.read_text()) if base_file.is_file() else tracked
    merged = tracked if current is None else three_way_merge(current, tracked, base)

    if current == merged and not dst.is_symlink():
        LOGGER.info("OK (settings match): %s", dst)
    elif dry_run:
        LOGGER.info("WOULD MERGE:  %s <- %s", dst, src)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists() or dst.is_symlink():
            bk = backups.destination_for(dst)
            # Copy rather than move so that writing in place keeps the file's mode; a
            # symlink is copied as a link, which also works when it dangles.
            shutil.copy2(dst, bk, follow_symlinks=False)
            LOGGER.info("Backed up %s -> %s", dst, bk)
            if dst.is_symlink():
                dst.unlink()
        dst.write_text(json.dumps(merged, indent=2) + "\n")
        LOGGER.info("Merged %s <- %s", dst, src)

    if not dry_run:
        base_file.parent.mkdir(parents=True, exist_ok=True)
        base_file.write_text(json.dumps(tracked, indent=2) + "\n")


def install(
    source: Path,
    dry_run: bool,
    home: Path | None = None,
    backup_root: Path | None = None,
    codex_only: bool = False,
    merge_base_root: Path | None = None,
) -> None:
    source = source.resolve()
    home = Path.home() if home is None else home
    backup_root = BACKUP_ROOT if backup_root is None else backup_root
    merge_base_root = MERGE_BASE_ROOT if merge_base_root is None else merge_base_root
    backups = LazyBackupDir(backup_root, home)
    installs = build_install_plan(source, home, codex_only=codex_only)

    merged_targets = {home / rel for rel in MERGED_JSON_SETTINGS}
    for src, dst in installs:
        if dst in merged_targets:
            base_file = merge_base_root / dst.relative_to(home)
            install_merged_json(src, dst, dry_run, backups, base_file)
    installs = [(src, dst) for src, dst in installs if dst not in merged_targets]

    if not installs:
        LOGGER.warning("No dotfiles found in %s.", source)

    if dry_run:
        for src, dst in installs:
            if is_same_symlink_target(dst, src):
                LOGGER.info("OK (already linked): %s -> %s", dst, src)
            elif dst.exists(follow_symlinks=False) or dst.is_symlink():
                LOGGER.info("WOULD UPDATE: %s -> %s", dst, src)
            else:
                LOGGER.info("WOULD LINK:   %s -> %s", dst, src)
        return

    existing_targets = [
        dst
        for src, dst in installs
        if (dst.exists() or dst.is_symlink()) and not is_same_symlink_target(dst, src)
    ]
    if existing_targets:
        LOGGER.info(
            "Existing files found:\n%s",
            "\n".join(str(p) for p in existing_targets),
        )

    for src, dst in installs:
        dst.parent.mkdir(parents=True, exist_ok=True)

        if is_same_symlink_target(dst, src):
            LOGGER.info("Already linked: %s -> %s", dst, src)
            continue

        if dst.exists() or dst.is_symlink():
            bk = backups.destination_for(dst)
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
