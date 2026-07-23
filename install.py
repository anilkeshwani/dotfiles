#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import logging
import os
import shutil
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
BACKUP_ROOT = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state")) / "dotfiles-backups"

CODEX_SKILLS_DIR = REPO_ROOT / "agents" / "codex" / "skills"

# Install only maintained personal skills. Other directories in CODEX_SKILLS_DIR
# may be vendored system skills or unfinished drafts.
INSTALLED_CODEX_SKILLS = ("deslop-code", "deslop-prose")


def discover_dotfiles(source: Path) -> list[str]:
    """Walk source and return all file paths relative to it."""
    return sorted(str(p.relative_to(source)) for p in source.rglob("*") if p.is_file())


def build_install_plan(source: Path, home: Path) -> list[tuple[Path, Path]]:
    """Return the source and destination paths managed by the installer."""
    installs = [(source / rel, home / rel) for rel in discover_dotfiles(source)]

    codex_skills = home / ".agents" / "skills"
    for skill_name in INSTALLED_CODEX_SKILLS:
        skill_source = CODEX_SKILLS_DIR / skill_name
        if not skill_source.is_dir():
            LOGGER.warning("Codex skill not found, skipping: %s", skill_source)
            continue
        installs.append((skill_source, codex_skills / skill_name))

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


def install(source: Path, dry_run: bool) -> None:
    source = source.resolve()
    installs = build_install_plan(source, Path.home())

    if not installs:
        LOGGER.warning("No dotfiles found in %s. Nothing to install.", source)
        return

    if dry_run:
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
    if existing_targets:
        LOGGER.info("Existing dotfiles found:\n%s", "\n".join(str(p) for p in existing_targets))
        BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
        backup_dir = unique_path(BACKUP_ROOT / datetime.now().strftime("%Y%m%d-%H%M%S"))
        backup_dir.mkdir(parents=True, exist_ok=False)
        LOGGER.info("Created backup directory at %s", backup_dir)

    for src, dst in installs:
        dst.parent.mkdir(parents=True, exist_ok=True)

        if is_same_symlink_target(dst, src):
            LOGGER.info("Already linked: %s -> %s", dst, src)
            continue

        if dst.exists() or dst.is_symlink():
            if backup_dir is None:
                BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
                backup_dir = unique_path(BACKUP_ROOT / datetime.now().strftime("%Y%m%d-%H%M%S"))
                backup_dir.mkdir(parents=True, exist_ok=False)
            bk = unique_path(backup_dir / dst.relative_to(Path.home()))
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
    install(source=args.source, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
