#!/usr/bin/env bash

# Bootstrap a fresh Ubuntu/Linux instance for development.
# Works with or without root — falls back to Homebrew when sudo is unavailable.
# Run: bash scripts/bootstrap_ubuntu.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
export DEBIAN_FRONTEND=noninteractive

# ---------------------------------------------------------------------------
# Privilege detection
#   can_sudo: returns 0 if we are root or have passwordless sudo.
#   SUDO: prefix for commands that need root. Empty when already root,
#         "sudo" otherwise. Only meaningful when can_sudo returns 0.
# ---------------------------------------------------------------------------

SUDO=""
if [ "$(id -u)" -ne 0 ]; then
    SUDO="sudo"
fi

can_sudo() {
    [ "$(id -u)" -eq 0 ] || sudo -n true 2>/dev/null
}

# ---------------------------------------------------------------------------
# Fix ~/.config ownership
#   On some Ubuntu images, ~/.config is created by root (e.g. for system pip
#   config). Many user-level tools (uv, etc.) need to write here, so ensure
#   the current user owns it.
# ---------------------------------------------------------------------------

if [ -d "${HOME}/.config" ] && [ "$(stat -c '%u' "${HOME}/.config")" != "$(id -u)" ]; then
    if can_sudo; then
        $SUDO chown -R "$(id -u):$(id -g)" "${HOME}/.config"
        echo "Fixed ownership of ~/.config"
    else
        echo "ERROR: ~/.config is not owned by you and no sudo available." >&2
        exit 1
    fi
fi

# ---------------------------------------------------------------------------
# APT packages (requires root or passwordless sudo)
# ---------------------------------------------------------------------------

install_apt_packages() {
    echo "--- Installing apt packages via apt ---"
    $SUDO apt-get update -qq
    $SUDO apt-get install -y -qq \
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
        zsh \
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
        htop \
        zsh
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
# Set zsh as default shell
#   Uses chsh when we have root/sudo. On HPC clusters without sudo, chsh
#   won't work — the bootstrap prints a hint to add 'exec zsh' to .bashrc
#   as a workaround (the dotfiles installer will overwrite .bashrc anyway,
#   so this is safe to do before running install.py).
# ---------------------------------------------------------------------------

set_default_shell_zsh() {
    local zsh_path
    zsh_path="$(command -v zsh)"
    if [ -z "${zsh_path}" ]; then
        echo "--- zsh not found, skipping default shell change ---"
        return
    fi
    if [ "$(basename "${SHELL}")" = "zsh" ]; then
        echo "--- zsh is already the default shell, skipping ---"
        return
    fi
    if can_sudo; then
        echo "--- Setting zsh as default shell ---"
        # Ensure zsh is listed in /etc/shells — chsh rejects unlisted shells
        if ! grep -qx "${zsh_path}" /etc/shells 2>/dev/null; then
            echo "${zsh_path}" | $SUDO tee -a /etc/shells >/dev/null
        fi
        $SUDO chsh -s "${zsh_path}" "$(whoami)"
        echo "Default shell set to ${zsh_path}."
    else
        echo "--- Cannot change default shell without sudo ---"
        echo "    Workaround: add 'exec zsh' to the end of ~/.bashrc"
    fi
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
    tic -x "${REPO_DIR}/data/xterm-ghostty.terminfo"
    echo "xterm-ghostty terminfo installed."
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
    if command -v uv >/dev/null 2>&1; then
        echo "--- uv already installed, skipping ---"
        return
    fi
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
# Claude Code
# ---------------------------------------------------------------------------

install_claude() {
    if command -v claude >/dev/null 2>&1; then
        echo "--- Claude Code already installed, skipping ---"
        return
    fi
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
    set_default_shell_zsh
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
    echo "  3. Open a new shell session"
}

main "$@"
