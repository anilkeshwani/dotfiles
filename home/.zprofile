# ~/.zprofile — zsh login shell setup.
# Sourced once per login session, before .zshrc.
# Analogous to ~/.profile for bash.

# Shell-agnostic env: PATH additions, NVM, Volta, Go
[ -f "${HOME}/.env" ] && . "${HOME}/.env"

# Aliases for non-interactive login shells, including Codex shell mode
[ -f "${HOME}/.aliases" ] && . "${HOME}/.aliases"

# Machine-specific login-shell extras
case "$(uname -s)" in
    Darwin)
        [ -f "${HOME}/.profile_macos" ] && . "${HOME}/.profile_macos"
        ;;
    Linux)
        [ -f "${HOME}/.profile_linux" ] && . "${HOME}/.profile_linux"
        ;;
esac
