#!/usr/bin/env python

import logging
from pathlib import Path


logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
LOGGER = logging.getLogger(__file__)

DOTFILES_DIR = Path(__file__).parent / "dotfiles"
DOTFILES_BACKUP_DIR = Path.home() / "dotfiles_backup"

dotfiles: list[Path] = list(DOTFILES_DIR.iterdir())
symlink_srcs: list[Path] = [Path.home() / dotfile.name for dotfile in dotfiles]
existing_symlink_srcs: list[Path] = [p for p in symlink_srcs if p.exists(follow_symlinks=False)]

if existing_symlink_srcs:
    LOGGER.info(f"Existing dotfiles found in {Path.home()}:\n" + "\n".join([str(p) for p in existing_symlink_srcs]))
    try:
        DOTFILES_BACKUP_DIR.mkdir(exist_ok=False)
        LOGGER.info(f"Created directory to store existing dotfiles at {DOTFILES_BACKUP_DIR!s}")
    except FileExistsError as e:
        raise FileExistsError(f"Default backup directory for dotfiles exists at {DOTFILES_BACKUP_DIR}") from e

for dotfile, symlink_src in zip(dotfiles, symlink_srcs):
    if symlink_src.exists():
        dst = DOTFILES_BACKUP_DIR / symlink_src.name
        symlink_src.rename(dst)
        LOGGER.info(f"Moved existing {symlink_src} to {dst}")
    symlink_src.symlink_to(dotfile)
    LOGGER.info(f"Symlinked {symlink_src} to {dotfile}")

LOGGER.info("Installed dotfiles")
