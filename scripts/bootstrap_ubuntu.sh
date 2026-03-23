#!/usr/bin/env bash

# Bootstrap a fresh Ubuntu instance for development.
# Designed for cloud GPU providers: Vast, Lambda Labs, Prime Intellect, AWS, etc.
# Run: bash scripts/bootstrap_ubuntu.sh

set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

# ---------------------------------------------------------------------------
# APT packages
# ---------------------------------------------------------------------------

install_apt_packages() {
    echo "--- Installing apt packages ---"
    apt-get update -qq
    apt-get install -y -qq \
        build-essential \
        curl \
        wget \
        unzip \
        git \
        git-lfs \
        vim \
        tmux \
        tree \
        bat \
        ripgrep \
        fd-find \
        fzf \
        jq \
        ncdu \
        htop \
        >/dev/null
    git lfs install
    echo "apt packages installed."
}

# ---------------------------------------------------------------------------
# Symlinks for Ubuntu-renamed binaries
#   Ubuntu installs bat as "batcat" and fd as "fdfind" due to name conflicts.
#   Create symlinks in ~/.local/bin so the standard names work everywhere.
# ---------------------------------------------------------------------------

setup_symlinks() {
    echo "--- Setting up binary symlinks ---"
    mkdir -p "${HOME}/.local/bin"
    [ ! -e "${HOME}/.local/bin/bat" ] && ln -s "$(command -v batcat)" "${HOME}/.local/bin/bat" || true
    [ ! -e "${HOME}/.local/bin/fd" ]  && ln -s "$(command -v fdfind)" "${HOME}/.local/bin/fd"  || true
    echo "Symlinks created in ~/.local/bin."
}

# ---------------------------------------------------------------------------
# Rust (via rustup)
# ---------------------------------------------------------------------------

install_rust() {
    if command -v rustup >/dev/null 2>&1; then
        echo "--- Rust already installed, updating ---"
        rustup update
    else
        echo "--- Installing Rust via rustup ---"
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
        # Make cargo available for the rest of this script
        . "${HOME}/.cargo/env"
    fi
    echo "Rust $(rustc --version) installed."
}

# ---------------------------------------------------------------------------
# UV (Python package manager)
# ---------------------------------------------------------------------------

install_uv() {
    echo "--- Installing uv ---"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "uv installed."
}

# ---------------------------------------------------------------------------
# Delta (git pager with syntax highlighting)
# ---------------------------------------------------------------------------

install_delta() {
    local version="0.19.1"
    local archive="delta-${version}-x86_64-unknown-linux-gnu"
    local url="https://github.com/dandavison/delta/releases/download/${version}/${archive}.tar.gz"
    local install_dir="${HOME}/.local/bin"

    echo "--- Installing delta ${version} ---"

    local tmpdir
    tmpdir="$(mktemp -d)"
    trap 'rm -rf "${tmpdir}"' RETURN  # clean up temp dir when this function returns

    wget -q "${url}" -O "${tmpdir}/delta.tar.gz"
    tar -xzf "${tmpdir}/delta.tar.gz" -C "${tmpdir}"
    mkdir -p "${install_dir}"
    mv "${tmpdir}/${archive}/delta" "${install_dir}/delta"
    echo "delta installed to ${install_dir}/delta."
}

# ---------------------------------------------------------------------------
# NVM (Node Version Manager)
# ---------------------------------------------------------------------------

install_nvm() {
    if [ -d "${HOME}/.nvm" ]; then
        echo "--- NVM already installed, skipping ---"
        return
    fi
    echo "--- Installing NVM ---"
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
    echo "NVM installed. Run 'nvm install --lts' to install Node."
}

# ---------------------------------------------------------------------------
# Claude Code
# ---------------------------------------------------------------------------

install_claude() {
    echo "--- Installing Claude Code ---"
    curl -fsSL https://claude.ai/install.sh | bash
    echo "Claude Code installed."
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

main() {
    echo "=== Ubuntu bootstrap starting ==="

    install_apt_packages
    setup_symlinks
    install_rust
    install_uv
    install_delta
    install_nvm
    install_claude

    echo ""
    echo "=== Bootstrap complete ==="
    echo "Next steps:"
    echo "  1. Set up SSH keys and clone dotfiles"
    echo "  2. Run: uv run --script install_dotfiles.py"
    echo "  3. Run: exec bash"
}

main "$@"
