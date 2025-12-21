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

# set a fancy prompt (non-color, unless we know we "want" color)
case "$TERM" in
xterm-color | *-256color) color_prompt=yes ;;
esac

# uncomment for a colored prompt, if the terminal has the capability; turned
# off by default to not distract the user: the focus in a terminal window
# should be on the output of commands, not on the prompt
force_color_prompt=yes

if [ -n "$force_color_prompt" ]; then
    if [ -x /usr/bin/tput ] && tput setaf 1 >&/dev/null; then
        # We have color support; assume it's compliant with Ecma-48
        # (ISO/IEC-6429). (Lack of such support is extremely rare, and such
        # a case would tend to support setf rather than setaf.)
        color_prompt=yes
    else
        color_prompt=
    fi
fi

if [ "$color_prompt" = yes ]; then
    PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '
else
    PS1='${debian_chroot:+($debian_chroot)}\u@\h:\w\$ '
fi
unset color_prompt force_color_prompt

# If this is an xterm set the title to user@host:dir
case "$TERM" in
xterm* | rxvt*)
    PS1="\[\e]0;${debian_chroot:+($debian_chroot)}\u@\h: \w\a\]$PS1"
    ;;
*) ;;
esac

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

# Alias definitions

if [ -f "${HOME}/.bash_aliases" ]; then
    . "${HOME}/.bash_aliases"
fi

if [ -f "${HOME}/.bash_functions" ]; then
    . "${HOME}/.bash_functions"
fi

# Secrets

if [ -f "${HOME}/.secrets" ]; then
    . "${HOME}/.secrets"
fi
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

# OS / server / environment-specific Settings. Cases:
#   Linux:
#       Sardine Servers: Artemis, Poseidon, Dionysus, Hades
#       Linux (any other e.g. Vast, AWS, GCP)
#   macOS ("Darwin"; local)

# Linux
if [ "$(uname -s)" == "Linux" ]; then
    # Linux: Sardine
    if [[ "$(uname -n)" =~ ^(artemis|poseidon|dionysus|hades)$ ]]; then # TODO Add new server(s) when added
        export HAFH='/mnt/scratch-artemis/anilkeshwani'           # Set "Home Away From Home" path environment variable
        CONDA_INSTALL_PREFIX="${HAFH}/miniconda3"                 # Set default CONDA_INSTALL_PREFIX
        module load jq                                            # Load jq module for JSON processing
    # Linux: Any other
    else
        CONDA_INSTALL_PREFIX="${HOME}/miniconda3" # Set default CONDA_INSTALL_PREFIX
    fi
# macOS ("Darwin"; local)
elif [ "$(uname -s)" == "Darwin" ]; then
    CONDA_INSTALL_PREFIX="${HOME}/miniconda3" # Set default CONDA_INSTALL_PREFIX

    # >>> juliaup initialize >>>
    # !! Contents within this block are managed by juliaup !!
    case ":$PATH:" in
    *:/Users/anilkeshwani/.juliaup/bin:*) ;;
    *)
        export PATH=/Users/anilkeshwani/.juliaup/bin${PATH:+:${PATH}}
        ;;
    esac
    # <<< juliaup initialize <<<

    # NVM
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"                   # This loads nvm
    [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion" # This loads nvm bash_completion

    # Use Node version lts/iron -> v20.18.0 (used for quartz)
    nvm use lts/iron

    # Added by Antigravity
    export PATH="${HOME}/.antigravity/antigravity/bin:$PATH"
fi
####################################################################################################

# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$("${CONDA_INSTALL_PREFIX}/bin/conda" 'shell.bash' 'hook' 2>/dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "${CONDA_INSTALL_PREFIX}/etc/profile.d/conda.sh" ]; then
        . "${CONDA_INSTALL_PREFIX}/etc/profile.d/conda.sh"
    else
        export PATH="${CONDA_INSTALL_PREFIX}/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<
####################################################################################################

# Modifications to PATH environment variable
export PATH="$PATH:${HOME}/bin" # contains delta - https://github.com/dandavison/delta/releases
export PATH="$PATH:${HOME}/.local/bin"

# Utils
# TODO Add source of ../modules/fzf/shell/completion.bash
# ...

conda activate main
conda env list
