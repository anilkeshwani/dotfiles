# some more ls aliases
if [[ "$(uname)" == "Darwin" ]]; then
    alias ll='ls -vAFlh' # macOS
else
    alias ll='ls -vAFlh --group-directories-first' # linux
fi
alias la='ls -A'
alias l='ls -lF'
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias .....='cd ../../../..'

# Add an "alert" alias for long running commands.  Use like so:
#   sleep 10; alert
alias alert='notify-send --urgency=low -i "$([ $? = 0 ] && echo terminal || echo error)" "$(history|tail -n1|sed -e '\''s/^\s*[0-9]\+\s*//;s/[;&|]\s*alert$//'\'')"'

# Git Aliases
alias gs='git status'
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
alias gpl='git pull'
alias gplap='git pull --all --prune '
alias gp='git push'
alias gpp='git pull && git push'

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

# Code
# alias code='code-insiders' # remember that you're using Insiders ;)

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
alias hafh='cd "$HAFH"'

# Utils
alias fzfp='fzf --preview "cat {}"'
alias fzfpo='open "$(fzf --preview "cat {}")"'
