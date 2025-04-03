#!/usr/bin/env python

import argparse
import csv
import logging
from pathlib import Path


logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
LOGGER = logging.getLogger("dotfiles_installer")

# Constants
DOTFILES_DIR = Path(__file__).parent / "dotfiles"
DOTFILES_BACKUP_DIR = Path.home() / "dotfiles_backup"
LINK_MAP_TSV = Path(__file__).parent / "link_map.tsv"


def expand_path(path: str) -> Path:
    return Path(path).expanduser().resolve()


def parse_link_map_tsv(tsv_path: Path) -> list[tuple[Path, Path]]:
    mappings = []
    if tsv_path.exists():
        with open(tsv_path, newline="") as file:
            reader = csv.reader(file, delimiter="\t")
            for source, target in reader:
                mappings.append((expand_path(source), expand_path(target)))  # TODO
    return mappings


def backup_and_symlink(source: Path, target: Path, dry_run: bool = False):
    if target.exists() or target.is_symlink():
        if target.is_symlink() and target.resolve() != source:  # TODO
            LOGGER.warning(f"Removing incorrect symlink: {target} -> {target.resolve()}")
            if not dry_run:
                target.unlink()
        elif target.is_file() or target.is_dir():
            backup_path = DOTFILES_BACKUP_DIR / target.name
            LOGGER.info(f"Backing up existing file {target} -> {backup_path}")
            if not dry_run:
                DOTFILES_BACKUP_DIR.mkdir(exist_ok=True)
                target.rename(backup_path)

    LOGGER.info(f"Symlinking {source} -> {target}")
    if not dry_run:
        target.symlink_to(source)


def main(tsv_path: Path, dry_run: bool = False):
    mappings = dict(parse_link_map_tsv(tsv_path))

    # Ensure all files in dotfiles/ are covered, defaulting to home directory
    for dotfile in DOTFILES_DIR.iterdir():
        if dotfile not in mappings:
            mappings[dotfile] = Path.home() / dotfile.name

    for source, target in mappings.items():
        if not source.exists():
            LOGGER.error(f"Source file does not exist: {source}")
            continue
        backup_and_symlink(source, target, dry_run=dry_run)
    LOGGER.info("Dotfiles installation complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Install dotfiles via symlinks.")
    parser.add_argument("-t", "--tsv", type=Path, default=LINK_MAP_TSV, help="Path to the TSV file.")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without modifying files.")
    args = parser.parse_args()
    main(args.tsv, dry_run=args.dry_run)
