## Setup dotfiles

Dotfiles live in `home/` and are installed as symlinks into `$HOME` via `install.py`. Existing files are backed up to `~/.local/state/dotfiles-backups/` before being replaced.

```bash
uv run --script install.py [-h] [--source SOURCE] [--dry-run]
```

## SSH Keys

When spinning up a new machine, you need to set up SSH keys to authenticate with GitHub

1. Create a new SSH public-private key pair:
  
  ```bash 
  ssh-keygen -t ed25519 -C "anilkeshwani@hotmail.com" &&
      cat "${HOME}/.ssh/id_ed25519.pub"
  ```
  
2. [Add the public key as a new SSH key on GitHub](https://github.com/settings/keys)

## Bootstrapping Machines

Bootstrap and install scripts live in `scripts/`:

| Script | Purpose |
|---|---|
| `bootstrap_ubuntu.sh` | Full Ubuntu instance setup (apt packages, Rust, uv, delta, NVM, Claude Code) |
| `install_conda.sh` | Install Miniconda and create a clean `main` environment |
| `install_delta.sh` | Install delta (git diff pager) |

Bootstrap a fresh cloud instance:

```bash
bash scripts/bootstrap_ubuntu.sh
```

Hints:
- [Reload the tmux config mid-session](https://superuser.com/questions/580992/how-do-i-reload-tmux-configuration) with `(ctrl + B), :` then `source-file ~/.tmux.conf`
- Always handy: `exec zsh` 
