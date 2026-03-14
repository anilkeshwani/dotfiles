# ~/.zprofile — zsh login shell setup.
# Sourced once per login session, before .zshrc.
# Analogous to ~/.profile for bash.

# Shell-agnostic env: PATH additions, NVM, Volta, Go
[ -f "${HOME}/.env" ] && . "${HOME}/.env"

# Machine-specific login-shell extras
case "$(uname -s)" in
    Darwin)
        [ -f "${HOME}/.profile_macos" ] && . "${HOME}/.profile_macos"
        ;;
esac
