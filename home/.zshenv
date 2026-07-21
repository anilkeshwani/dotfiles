# ~/.zshenv — sourced by every zsh, before /etc/zsh/zshrc and ~/.zshrc.

# Debian/Ubuntu's /etc/zsh/zshrc runs its own compinit (writing a stray ~/.zcompdump)
# unless this is set; ~/.zshrc runs compinit itself with the dump under ~/.cache.
skip_global_compinit=1
