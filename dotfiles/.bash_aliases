#!/usr/bin/env bash

# Alias definitions.
# See /usr/share/doc/bash-doc/examples in the bash-doc package.

# some more ls aliases
if [[ "$(uname)" == "Darwin" ]]; then
    # macOS
    alias ll='ls -vAFlh'
    alias gdn='(cd $GARDEN && git pull && ./populatecontent.sh && npx quartz build && (cd public && git add -A && git commit --amend -am "$(date)" -m "$(git status --porcelain | tr -d \"\"\" | sort)" && git push --force-with-lease))'
else
    # Linux
    alias ll='ls -vAFlh --group-directories-first'
    # Add an "alert" alias for long running commands. Usage: `sleep 10; alert`
    alias alert='notify-send --urgency=low -i "$([ $? = 0 ] && echo terminal || echo error)" "$(history|tail -n1|sed -e '\''s/^\s*[0-9]\+\s*//;s/[;&|]\s*alert$//'\'')"'
fi

alias la='ls -A'
alias l='ls -lF'
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias .....='cd ../../../..'

# Git Aliases
alias gs='git status'
alias gsu='git status -u'
alias ga='git add'
alias gc='git commit'
alias gco='git checkout'
alias gb='git branch'
alias gr='git remote'
alias gt='git tag'
alias gdsc='git describe'
alias gdscta='git describe --tags --always'
alias gdsctad='git describe --tags --always --dirty'
alias gd='git diff'
alias gdd='git diff | delta --side-by-side --line-numbers'
alias gddl='git diff | delta --side-by-side --line-numbers --light'
alias gds='git diff --staged'
alias gdsd='git diff --staged | delta --side-by-side --line-numbers'
alias gdsdl='git diff --staged | delta --side-by-side --line-numbers --light'
alias gdh1='git diff HEAD~1..HEAD'
alias gddh1='git diff HEAD~1..HEAD | delta'
alias gl='git log'
alias gla='git log --all' # useful for when you're in a detached HEAD state e.g. checked out earlier commit
alias glo='git log --oneline'
alias gldog='git log --decorate --oneline --graph' # remember that tig is also an option
alias gldtsbd='git log --decorate --tags --simplify-by-decoration' # only tagged commits
alias gldtsbdo='git log --decorate --tags --simplify-by-decoration --oneline' # only tagged commits; compact
alias gsh='git show'                               # useful to diff a commit with its parent
alias gst='git stash'
alias gstl='git stash list'
alias gstls='git stash list' # doesn't adhere to the first letter-only rule but I always think it's this
alias gcp='git cherry-pick' # Google Cloud Platform's CLI is gcloud so all good
alias gf='git fetch'
alias gpl='git pull'
alias gplr='git pull --rebase'
alias gplap='git pull --all --prune '
alias gp='git push'
alias gpp='git pull && git push'
alias gpf='git push --force-with-lease'

# Conda
alias ca='conda activate'
alias cel='conda env list'

# Docker
alias d='docker'
alias dc='docker container'
alias di='docker image'
alias ds='docker system'
alias dps='docker ps'
alias drit='docker run -it'

# Python - Tools
alias isort='isort --profile=black --line-length=120 --lines-after-imports=2 --force-alphabetical-sort-within-sections'
alias black='black --line-length=120'

# Executables
alias chmox='chmod +x'

# tmux
alias tm='tmux'
alias tmns='tmux new-session'     # new session
alias tmnss='tmux new-session -s' # new named session
alias tmnsa='tmux new-session -A' # new named session attaching if exists
alias tma='tmux attach'
alias tmls='tmux ls'              # NOTE tmux ls defaults to listing *sessions* / is a shortcut for tmux list-sessions
alias tmlsw='tmux list-windows'   # NOTE this is already aliased _by tmux_ as tmux lsw
alias tmlsp='tmux list-panes'     # NOTE this is already aliased _by tmux_ as tmux lsp
alias tmlspa='tmux list-panes -a' # NOTE like tmux list-panes but includes all sessions/windows
alias tmcp='tmux capture-pane'
# watch -n .1 'tmux capture-pane -p -t 0 | tail -n 25' # TODO add this (here or in .bash_functions)

# Code
# alias code='code-insiders' # remember that you're using Insiders ;)
alias curs='cursor'

# Jekyll
alias jkl='bundle exec jekyll'
alias jklsw='bundle exec jekyll serve --watch --incremental'

# VPN
alias vpn='sudo openvpn --config \"${HOME}/.ssh/VPN/masterpf-UDP4-1194-config.ovpn\"'

# Journal
alias jc='git add -A && git commit -am "$(date)" -m "$(git status --porcelain | tr -d \"\"\" | sort)"'
alias jp='git pull && git add -A && git commit -am "$(date)" -m "$(git status --porcelain | tr -d \"\"\" | sort)" && git push'

# SSH
alias ska='sshkeyadd'
alias skagh='sshkeyaddgh'

# Sardine - SSH
# alias artemis='ssh artemis'
# alias poseidon='ssh poseidon'
# alias dionysus='ssh dionysus'
# alias hades='ssh hades'
alias hafh='cd "$HAFH"'

# Sardine - Monitoring
if [[ "$(uname -n)" =~ ^(artemis|poseidon|dionysus|hades)$ ]]; then
    alias wpsq='watch "FORCE_COLOR=1 psqueue"'
fi

# Sardine - Slurm
alias slurm-debug='echo "Queueing debug job..." && srun --partition a6000 --time=01:00:00 --gres=gpu:1 --qos=gpu-debug --pty bash'
alias slurm-debug-w='srun --partition a6000 --time=01:00:00 --gres=gpu:1 --qos=gpu-debug --pty bash -w' # allow node specification
alias slurm-debug-pos='echo "Queueing debug job on Poseidon..." && srun --partition a6000 --time=01:00:00 --gres=gpu:1 --qos=gpu-debug -w poseidon --pty bash'
alias slurm-debug-art='echo "Queueing debug job on Artemis..." && srun --partition a6000 --time=01:00:00 --gres=gpu:1 --qos=gpu-debug -w artemis --pty bash'

# Slurm
alias isslurm='export -p | grep SLURM'

# Utils
alias watch='watch --color --interval 0.1' # NOTE appending subsequent intervals with -n is valid; overrides -n 0.1 here
alias fzfp='fzf --preview "cat {}"'
alias fzfpo='open "$(fzf --preview "cat {}")"'
alias tvt='tv text'       # https://github.com/alexpasmantier/television; `text` should be the default but it's `files`
alias dog='pygmentize -g' # requires pygmentize from the python package python-pygments: `pip install Pygments`
alias grepxg='grep --exclude-dir=.git'
alias get-gpu='export -p | grep CUDA_VISIBLE_DEVICES' # NOTE set-gpu is a function (i.e. in .bash_functions)
alias treeless='tree -C | less -R'
