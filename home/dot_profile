# ~/.profile: executed by the command interpreter for login shells.
# This file is not read by bash(1), if ~/.bash_profile or ~/.bash_login
# exists.
# see /usr/share/doc/bash/examples/startup-files for examples.
# the files are located in the bash-doc package.

# the default umask is set in /etc/profile; for setting the umask
# for ssh logins, install and configure the libpam-umask package.
#umask 022

# if running bash
if [ -n "$BASH_VERSION" ]; then
    # include .bashrc if it exists
    if [ -f "$HOME/.bashrc" ]; then
        . "$HOME/.bashrc"
    fi
fi

# set PATH so it includes user's private bin if it exists
if [ -d "$HOME/bin" ]; then
    PATH="$HOME/bin:$PATH"
fi

# set PATH so it includes user's private bin if it exists
if [ -d "$HOME/.local/bin" ]; then
    PATH="$HOME/.local/bin:$PATH"
fi

# Only run this block if we are on macOS

if [ "$(uname)" == "Darwin" ]; then
    # Homebrew
    eval "$(/opt/homebrew/bin/brew shellenv)"

    export BASH_SILENCE_DEPRECATION_WARNING=1 # Silence deprecation warnings

    # GLOBALS
    export GARDEN="${HOME}/Desktop/garden-builder"
    export JOURNAL="${HOME}/Desktop/journal"

    # Cargo (Rust)
    . "${HOME}/.cargo/env"

    # Ruby
    source /opt/homebrew/opt/chruby/share/chruby/chruby.sh
    source /opt/homebrew/opt/chruby/share/chruby/auto.sh
    chruby ruby-3.1.3 # Set the default Ruby version

    # >>> juliaup initialize >>>
    # !! Contents within this block are managed by juliaup !!
    case ":$PATH:" in
    *:/Users/anilkeshwani/.juliaup/bin:*) ;;
    *)
        export PATH=/Users/anilkeshwani/.juliaup/bin${PATH:+:${PATH}}
        ;;
    esac
    # <<< juliaup initialize <<<
fi
