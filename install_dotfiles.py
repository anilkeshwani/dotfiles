#!/usr/bin/env python3

from __future__ import annotations

import argparse
import logging
import os
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

# Paths relative to SOURCE_DIR — identical to paths relative to $HOME.
DOTFILES: list[str] = [
    # Shell-agnostic
    ".aliases",
    ".aliases_macos",
    ".aliases_linux",
    ".aliases_sardine",
    ".functions",
    ".env",
    ".env_macos",
    ".env_sardine",
    ".prompt",
    # Shell-specific
    ".bashrc",
    ".zshrc",
    ".profile",
    ".profile_macos",
    # Git
    ".gitattributes",
    ".gitconfig",
    ".config/git/ignore",
    # Editor
    ".tmux.conf",
    ".vimrc",
    ".config/nvim/init.lua",
    # Terminal
    ".config/ghostty/config",
]


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
    installs: list[tuple[Path, Path]] = []
    missing_sources: list[str] = []

    for dotfile_rel in DOTFILES:
        src = source / dotfile_rel
        if not src.exists():
            missing_sources.append(dotfile_rel)
            continue
        installs.append((src, Path.home() / dotfile_rel))

    if missing_sources:
        LOGGER.warning(
            "Skipping missing source files:\n%s",
            "\n".join(missing_sources),
        )

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

    # Collect targets that already exist so we can create one backup dir up front.
    existing_targets = [
        dst for _, dst in installs if dst.exists(follow_symlinks=False) or dst.is_symlink()
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

        if dst.exists(follow_symlinks=False) or dst.is_symlink():
            if backup_dir is None:
                BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
                backup_dir = unique_path(BACKUP_ROOT / datetime.now().strftime("%Y%m%d-%H%M%S"))
                backup_dir.mkdir(parents=True, exist_ok=False)
            bk = unique_path(backup_dir / dst.relative_to(Path.home()))
            bk.parent.mkdir(parents=True, exist_ok=True)
            dst.rename(bk)
            LOGGER.info("Backed up %s -> %s", dst, bk)

        dst.symlink_to(src)
        LOGGER.info("Linked %s -> %s", dst, src)

    LOGGER.info("Done.")


def main() -> None:
    args = parse_args()
    install(source=args.source, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
