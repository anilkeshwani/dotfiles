#!/usr/bin/env bash

# Bootstrap a fresh Ubuntu/Linux instance for development.
# Works with or without root — falls back to Homebrew when sudo is unavailable.
# Run: bash scripts/bootstrap_ubuntu.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export DEBIAN_FRONTEND=noninteractive

# ---------------------------------------------------------------------------
# Privilege detection
# ---------------------------------------------------------------------------

can_sudo() {
    [ "$(id -u)" -eq 0 ] || sudo -n true 2>/dev/null
}

# ---------------------------------------------------------------------------
# APT packages (requires root or passwordless sudo)
# ---------------------------------------------------------------------------

install_apt_packages() {
    echo "--- Installing apt packages via apt ---"
    local sudo=""
    if [ "$(id -u)" -ne 0 ]; then
        sudo="sudo"
    fi
    $sudo apt-get update -qq
    $sudo apt-get install -y -qq \
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
#   Only needed for the apt path — Homebrew uses the standard names.
# ---------------------------------------------------------------------------

setup_apt_symlinks() {
    echo "--- Setting up binary symlinks ---"
    mkdir -p "${HOME}/.local/bin"
    [ ! -e "${HOME}/.local/bin/bat" ] && ln -s "$(command -v batcat)" "${HOME}/.local/bin/bat" || true
    [ ! -e "${HOME}/.local/bin/fd" ]  && ln -s "$(command -v fdfind)" "${HOME}/.local/bin/fd"  || true
    echo "Symlinks created in ~/.local/bin."
}

# ---------------------------------------------------------------------------
# Homebrew on Linux (rootless fallback)
# ---------------------------------------------------------------------------

install_homebrew() {
    if command -v brew >/dev/null 2>&1; then
        echo "--- Homebrew already installed ---"
        return
    fi
    echo "--- Installing Homebrew (no root required) ---"
    NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    # Add brew to PATH for the rest of this script
    eval "$("${HOME}/.linuxbrew/bin/brew" shellenv 2>/dev/null || "/home/linuxbrew/.linuxbrew/bin/brew" shellenv)"
    echo "Homebrew installed."
}

install_brew_packages() {
    echo "--- Installing packages via Homebrew ---"
    brew install \
        gcc \
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
        fd \
        fzf \
        jq \
        ncdu \
        htop
    git lfs install
    echo "Homebrew packages installed."
}

# ---------------------------------------------------------------------------
# System packages — dispatches to apt or Homebrew based on privileges
# ---------------------------------------------------------------------------

install_system_packages() {
    if can_sudo; then
        install_apt_packages
        setup_apt_symlinks
    else
        echo "--- No root/sudo access detected, using Homebrew ---"
        install_homebrew
        install_brew_packages
    fi
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
#   Delegates to the standalone install_delta.sh script.
# ---------------------------------------------------------------------------

install_delta() {
    bash "${SCRIPT_DIR}/install_delta.sh"
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
# Ghostty terminfo
#   Compiles the xterm-ghostty terminfo entry so that SSH sessions from
#   Ghostty on macOS work correctly (clear, Ctrl+L, tmux, etc.).
#   tic installs to ~/.terminfo/ as a regular user, or /usr/share/terminfo/
#   as root — no special handling needed.
# ---------------------------------------------------------------------------

install_ghostty_terminfo() {
    if infocmp xterm-ghostty >/dev/null 2>&1; then
        echo "--- xterm-ghostty terminfo already installed, skipping ---"
        return
    fi
    echo "--- Installing xterm-ghostty terminfo ---"
    tic -x "${SCRIPT_DIR}/xterm-ghostty.terminfo"
    echo "xterm-ghostty terminfo installed."
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
    echo "=== Bootstrap starting ==="

    install_system_packages
    install_ghostty_terminfo
    install_rust
    install_uv
    install_delta
    install_nvm
    install_claude

    echo ""
    echo "=== Bootstrap complete ==="
    echo "Next steps:"
    echo "  1. Set up SSH keys and clone dotfiles"
    echo "  2. Run: uv run --script install.py"
    echo "  3. Run: exec bash"
}

main "$@"
