# Alias definitions.

# You may want to put all your additions into a separate file like
# ~/.bash_aliases, instead of adding them here directly.
# See /usr/share/doc/bash-doc/examples in the bash-doc package.

# some more ls aliases
if [[ "$(uname)" == "Darwin" ]]; then
    # macOS
    alias ll='ls -vAFlh'
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
alias gd='git diff'
alias gdd='git diff | delta --side-by-side --line-numbers'
alias gddl='git diff | delta --side-by-side --line-numbers --light'
alias gds='git diff --staged'
alias gdsd='git diff --staged | delta --side-by-side --line-numbers'
alias gl='git log'
alias glo='git log --oneline'
alias gldog='git log --decorate --oneline --graph' # remember that tig is also an option
alias gsh='git show'
alias gst='git stash'
alias gstl='git stash list'
alias gstls='git stash list' # doesn't adhere to the first letter-only rule but I always think it's this
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
alias tmls='tmux ls'
alias tmlsw='tmux list-windows' # NOTE this is already aliases _by tmux_ as tmux lsw
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

# Sardine
alias artemis='ssh artemis'
alias poseidon='ssh poseidon'
alias dionysus='ssh dionysus'
alias hafh='cd "$HAFH"'

# Utils
alias watch='watch --color --interval 0.1' # NOTE appending subsequent intervals with -n is valid; overrides -n 0.1 here
alias fzfp='fzf --preview "cat {}"'
alias fzfpo='open "$(fzf --preview "cat {}")"'
alias dog='pygmentize -g' # requires pygmentize from the python package python-pygments: `pip install Pygments`
