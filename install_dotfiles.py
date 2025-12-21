#!/usr/bin/env python

import logging
from pathlib import Path


logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
LOGGER = logging.getLogger(__file__)

# Constants
DOTFILES_DIR = Path(__file__).parent / "dotfiles"
DOTFILES_BACKUP_DIR = Path.home() / "dotfiles_backup"


def main():
    dotfiles: list[Path] = [p for p in DOTFILES_DIR.iterdir() if p.name != ".config"]
    installs: list[tuple[Path, Path]] = [(dotfile, Path.home() / dotfile.name) for dotfile in dotfiles]

    extra_installs: list[tuple[Path, Path]] = [
        (
            DOTFILES_DIR / ".config/nvim/init.lua",
            Path.home() / ".config/nvim/init.lua",
        ),
    ]
    installs.extend([(src, dst) for src, dst in extra_installs if src.exists()])

    symlink_tgts_exist: list[Path] = [dst for _, dst in installs if dst.exists(follow_symlinks=False)]

    # Create the backup directory if we have any existing dotfiles (inc. as symbolic links) to move
    if symlink_tgts_exist:
        LOGGER.info(f"Existing dotfiles found in {Path.home()}:\n" + "\n".join([str(p) for p in symlink_tgts_exist]))
        try:
            DOTFILES_BACKUP_DIR.mkdir(exist_ok=False)
            LOGGER.info(f"Created directory to store existing dotfiles at {DOTFILES_BACKUP_DIR!s}")
        except FileExistsError as e:
            raise FileExistsError(f"Default backup directory for dotfiles exists at {DOTFILES_BACKUP_DIR}") from e

    # Symlink the dotfiles in the home directory
    for dotfile, symlink_tgt in installs:
        symlink_tgt.parent.mkdir(parents=True, exist_ok=True)
        if symlink_tgt.exists(follow_symlinks=False):
            rel = symlink_tgt.relative_to(Path.home())
            dst = DOTFILES_BACKUP_DIR / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            symlink_tgt.rename(dst)
            LOGGER.info(f"Moved existing {symlink_tgt} to {dst}")
        symlink_tgt.symlink_to(dotfile)
        LOGGER.info(f"Symlinked {symlink_tgt} to {dotfile}")

    LOGGER.info("Installed dotfiles")


if __name__ == "__main__":
    main()
