#!/usr/bin/env python3

from __future__ import annotations

import argparse
import logging
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
LOGGER = logging.getLogger(__file__)

REPO_ROOT = Path(__file__).resolve().parent
SOURCE_DIR = REPO_ROOT
BACKUP_ROOT = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state")) / "dotfiles-backups"
LEGACY_SOURCE_TARGETS: list[tuple[str, str]] = [
    ("dot_bash_aliases", ".bash_aliases"),
    ("dot_bash_functions", ".bash_functions"),
    ("dot_bashrc", ".bashrc"),
    ("dot_gitattributes", ".gitattributes"),
    ("dot_gitconfig", ".gitconfig"),
    ("dot_gitignore_global", ".config/git/ignore"),
    ("dot_profile", ".profile"),
    ("dot_tmux.conf", ".tmux.conf"),
    ("dot_vimrc", ".vimrc"),
    ("dot_zshrc", ".zshrc"),
    ("dot_config/nvim/init.lua", ".config/nvim/init.lua"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install dotfiles via chezmoi.")
    parser.add_argument(
        "--source",
        type=Path,
        default=SOURCE_DIR,
        help=f"chezmoi source directory (default: {SOURCE_DIR})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change without updating destination files.",
    )
    parser.add_argument(
        "--legacy-fallback",
        action="store_true",
        help="Use fallback symlink installer from repo-root source-state files (deprecated).",
    )
    return parser.parse_args()


def run_checked(cmd: list[str]) -> None:
    LOGGER.info("Running: %s", " ".join(cmd))
    subprocess.run(cmd, check=True)


def resolve_chezmoi() -> str:
    chezmoi = shutil.which("chezmoi")
    if chezmoi is None:
        raise RuntimeError("chezmoi is not installed or not on PATH.")
    run_checked([chezmoi, "--version"])
    return chezmoi


def run_chezmoi_install(source: Path, dry_run: bool) -> None:
    source = source.resolve()
    chezmoi = resolve_chezmoi()

    # Initialize against this repository; this keeps source state in-repo.
    run_checked([chezmoi, "init", "--source", str(source)])

    if dry_run:
        run_checked([chezmoi, "-S", str(source), "diff"])
        run_checked([chezmoi, "-n", "-v", "-S", str(source), "apply"])
        return

    run_checked([chezmoi, "-v", "-S", str(source), "apply"])


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


def run_legacy_install() -> None:
    installs: list[tuple[Path, Path]] = []
    missing_sources: list[str] = []
    for source_rel, target_rel in LEGACY_SOURCE_TARGETS:
        source = REPO_ROOT / source_rel
        if not source.exists():
            missing_sources.append(source_rel)
            continue
        installs.append((source, Path.home() / target_rel))

    if missing_sources:
        LOGGER.warning(
            "Skipping missing source-state files for fallback symlink install:\n%s",
            "\n".join(missing_sources),
        )

    if not installs:
        LOGGER.warning("No fallback source-state files found in repo root. Nothing to install.")
        return

    # follow_symlinks=False with dst.is_symlink() -> safe in case of *broken* symlinks
    existing_targets: list[Path] = [
        dst for _, dst in installs if dst.exists(follow_symlinks=False) or dst.is_symlink()
    ]

    backup_dir: Path | None = None
    if existing_targets:
        LOGGER.info("Existing dotfiles found in %s:\n%s", Path.home(), "\n".join([str(p) for p in existing_targets]))
        BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
        backup_dir = BACKUP_ROOT / datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_dir = unique_path(backup_dir)
        backup_dir.mkdir(parents=True, exist_ok=False)
        LOGGER.info("Created backup directory at %s", backup_dir)

    for dotfile, symlink_tgt in installs:
        symlink_tgt.parent.mkdir(parents=True, exist_ok=True)
        if is_same_symlink_target(symlink_tgt, dotfile):
            LOGGER.info("Symlink already in place: %s -> %s", symlink_tgt, dotfile)
            continue
        if symlink_tgt.exists(follow_symlinks=False) or symlink_tgt.is_symlink():
            if backup_dir is None:
                BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
                backup_dir = BACKUP_ROOT / datetime.now().strftime("%Y%m%d-%H%M%S")
                backup_dir = unique_path(backup_dir)
                backup_dir.mkdir(parents=True, exist_ok=False)
            rel = symlink_tgt.relative_to(Path.home())
            dst = backup_dir / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst = unique_path(dst)
            symlink_tgt.rename(dst)
            LOGGER.info("Moved existing %s to %s", symlink_tgt, dst)
        symlink_tgt.symlink_to(dotfile)
        LOGGER.info("Symlinked %s to %s", symlink_tgt, dotfile)

    LOGGER.info("Installed dotfiles using legacy symlink mode.")


def main() -> None:
    args = parse_args()

    if args.legacy_fallback:
        LOGGER.warning("Running deprecated fallback symlink installer mode from repo-root source-state files.")
        run_legacy_install()
        return

    try:
        run_chezmoi_install(source=args.source, dry_run=args.dry_run)
        LOGGER.info("Installed dotfiles via chezmoi.")
    except Exception as exc:
        LOGGER.error("chezmoi install failed: %s", exc)
        LOGGER.info("Use --legacy-fallback to run the direct symlink fallback behavior.")
        raise


if __name__ == "__main__":
    main()
