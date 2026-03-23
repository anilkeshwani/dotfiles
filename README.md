# dotfiles

Feel at home and work fast no matter which host you're working on. 

## Setup

Dotfiles live in `home/` and are installed as symlinks into `$HOME` via `install.py`. Existing files are backed up to `~/.local/state/dotfiles-backups/` before being replaced.

Preview what would change:

```bash
uv run --script install.py --dry-run
```

Apply:

```bash
uv run --script install.py
```

## SSH Keys

When spinning up a new machine, you need to set up SSH keys to authenticate with GitHub

1. Create a new SSH public-private key pair:
  
  ```bash 
  ssh-keygen -t ed25519 -C "anilkeshwani@hotmail.com" &&
      cat "${HOME}/.ssh/id_ed25519.pub"
  ```
  
2. [Add the public key as a new SSH key on GitHub](https://github.com/settings/keys)

## Bootstrapping New Instances / Machines

### Hints - Bootstrapping

- A good old `exec bash` is always handy
- Vast instances throw you into tmux by default - nice but the tmux config needs reloading once dotfiles are in: **press the old prefix (CtrlB), :`source-file ~/.tmux.conf`**
  - Source: [How do I reload TMUX configuration?](https://superuser.com/questions/580992/how-do-i-reload-tmux-configuration)

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
