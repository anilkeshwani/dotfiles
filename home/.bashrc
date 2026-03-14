# ~/.bashrc: executed by bash(1) for non-login shells.
# see /usr/share/doc/bash/examples/startup-files (in the package bash-doc)
# for examples

# If not running interactively, don't do anything
case $- in
*i*) ;;
*) return ;;
esac

# don't put duplicate lines or lines starting with space in the history.
# See bash(1) for more options
HISTCONTROL=ignoreboth

# append to the history file, don't overwrite it
shopt -s histappend

# for setting history length see HISTSIZE and HISTFILESIZE in bash(1)
HISTSIZE=1000
HISTFILESIZE=2000

# check the window size after each command and, if necessary,
# update the values of LINES and COLUMNS.
shopt -s checkwinsize

# If set, the pattern "**" used in a pathname expansion context will
# match all files and zero or more directories and subdirectories.
#shopt -s globstar

# make less more friendly for non-text input files, see lesspipe(1)
[ -x /usr/bin/lesspipe ] && eval "$(SHELL=/bin/sh lesspipe)"

# set variable identifying the chroot you work in (used in the prompt below)
if [ -z "${debian_chroot:-}" ] && [ -r /etc/debian_chroot ]; then
    debian_chroot=$(cat /etc/debian_chroot)
fi

# enable color support of ls and also add handy aliases
if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    alias ls='ls --color=auto'
    #alias dir='dir --color=auto'
    #alias vdir='vdir --color=auto'

    alias grep='grep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'
fi

# colored GCC warnings and errors
#export GCC_COLORS='error=01;31:warning=01;35:note=01;36:caret=01;32:locus=01:quote=01'

####################################################################################################
# Shell-agnostic configuration

[ -f "${HOME}/.aliases" ]   && . "${HOME}/.aliases"
[ -f "${HOME}/.functions" ] && . "${HOME}/.functions"
[ -f "${HOME}/.env" ]       && . "${HOME}/.env"
[ -f "${HOME}/.secrets" ]   && . "${HOME}/.secrets"

# Machine-specific aliases and env
case "$(uname -s)" in
    Darwin)
        [ -f "${HOME}/.aliases_macos" ] && . "${HOME}/.aliases_macos"
        [ -f "${HOME}/.env_macos" ]     && . "${HOME}/.env_macos"
        ;;
    Linux)
        [ -f "${HOME}/.aliases_linux" ] && . "${HOME}/.aliases_linux"
        if [[ "$(uname -n)" =~ ^(artemis|poseidon|dionysus|hades)$ ]]; then
            [ -f "${HOME}/.aliases_sardine" ] && . "${HOME}/.aliases_sardine"
            [ -f "${HOME}/.env_sardine" ]     && . "${HOME}/.env_sardine"
        fi
        ;;
esac

####################################################################################################

# enable programmable completion features (you don't need to enable
# this, if it's already enabled in /etc/bash.bashrc and /etc/profile
# sources /etc/bash.bashrc).
if ! shopt -oq posix; then
    if [ -f /usr/share/bash-completion/bash_completion ]; then
        . /usr/share/bash-completion/bash_completion
    elif [ -f /etc/bash_completion ]; then
        . /etc/bash_completion
    fi
fi

####################################################################################################
# Prompt

[ -f "${HOME}/.prompt" ] && . "${HOME}/.prompt"

_bashrc_prompt_cmd() {
    local exit_code=$?
    local rst='\[\033[0m\]'
    local grn='\[\033[01;32m\]'
    local red='\[\033[01;31m\]'
    local blu='\[\033[01;34m\]'
    local mag='\[\033[0;35m\]'
    local yel='\[\033[0;33m\]'
    local arrow_color; [ $exit_code -eq 0 ] && arrow_color=$grn || arrow_color=$red
    PS1="${grn}\u@\h${rst} ${blu}\w${rst}${mag}$(_prompt_git_branch)${rst}${yel}$(_prompt_venv)${rst}\n${arrow_color}❯${rst} "
}
PROMPT_COMMAND=_bashrc_prompt_cmd
