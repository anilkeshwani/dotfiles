## Set up dotfiles

Dotfiles live in `home/` and are installed as symlinks into `$HOME` via `install.py`. Existing files are backed up to `~/.local/state/dotfiles-backups/` before being replaced.

On macOS, the installer also links `apps/vscode/settings.json` to VS Code's user settings path under `~/Library/Application Support/Code/User/`.

Codex-facing skills live under `agents/codex/skills`. The installer links the
maintained personal skills into `~/.agents/skills`; Claude Code skills remain
separate under `home/.claude/skills`. Files under `home/.codex/agents` are custom
subagent profiles, not skills.

```bash
uv run --script install.py [-h] [--source SOURCE] [--dry-run]
```

## Multiple Claude Code accounts

Claude Code reads its entire config tree from `$CLAUDE_CONFIG_DIR`, defaulting to `~/.claude`. That tree includes `.claude.json`, which stores `oauthAccount` — so pointing the variable at a second directory gives a second, independent login, and the subscriptions can run at the same time in different terminals.

`.env` names one config dir per account, overridable per host in `.env_linux` / `.env_macos`:

| Variable | Default | Command |
|---|---|---|
| `CLAUDE_CONFIG_DIR_WORK` | `~/.claude` | `claude` |
| `CLAUDE_CONFIG_DIR_PERSONAL` | `~/.claude-personal` | `ccp` (`claude-personal`) |
| `CLAUDE_CONFIG_DIR_WORK_EXTRA` | `~/.claude-work-extra` | `ccwe` (`claude-work-extra`) |

`install.py` reads those two variables and installs everything under `home/.claude/` into each extra config dir as well, so `settings.json`, `CLAUDE.md`, agents, skills and output styles stay identical across accounts. `plugins/` is symlinked to the one in `~/.claude` — it is local state rather than a tracked dotfile, but the marketplace clones are bulky and the enabled plugin set is already pinned by the shared `settings.json`.

Everything account-specific is left for Claude Code to create per dir and is never linked: `.credentials.json`, `.claude.json`, `projects/`, `history.jsonl`, `sessions/`, and the various caches. Unset a variable on a host where that account is not needed and the installer skips it.

Two caveats. User-scoped MCP servers added with `claude mcp add -s user` live in `.claude.json` and so do not carry across — re-add them per account, or use project scope. And because `plugins/` is shared, two instances installing or updating plugins concurrently can race; do plugin management from one account at a time.

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
