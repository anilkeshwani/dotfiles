## Set up dotfiles

Dotfiles live in `home/` and are installed as symlinks into `$HOME` via `install.py`. Existing files are backed up to `~/.local/state/dotfiles-backups/` before being replaced.

On macOS, the installer also links `apps/vscode/settings.json` to VS Code's user settings path under `~/Library/Application Support/Code/User/`.

Codex-facing skills live under `agents/codex/skills`. The installer links the
maintained personal skills into `~/.agents/skills`; Claude Code skills remain
separate under `home/.claude/skills`. Files under `home/.codex/agents` are custom
subagent profiles, not skills.

Codex configuration is machine-local. The installer does not read, modify or
link `~/.codex/config.toml`.

The Codex `AGENTS.md` file is tracked separately at `home/.codex/AGENTS.md` so
Claude Code configuration is never used as its installation source. Changed
Codex files are backed up under `~/.local/state/dotfiles-backups/` before the
installer updates them.

```bash
uv run --script install.py [-h] [--source SOURCE] [--dry-run] [--codex-only]
```

Use `--codex-only` to repair or refresh Codex without changing any Claude Code
path, VS Code setting or general shell dotfile.

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

## Using these skills and configs on your own machine

This section is for anyone who is not me. It assumes you want the skills and
maybe the agent profiles, without adopting my shell, git or editor config.

### What is shareable

| Path | What it is | Applies to |
|---|---|---|
| `home/.claude/skills/` | Personal Claude Code skills: `deslop-prose`, `deslop-code`, `excalidraw`, `journal` | Claude Code (CLI, desktop, IDE) |
| `home/.claude/agents/` | Subagent profiles: `architect-reviewer`, `senior-mle-reviewer`, `researcher-reviewer`, `journal-scribe` | Claude Code |
| `home/.claude/output-styles/` | Output styles, including `deslop` | Claude Code |
| `home/.claude/settings.json` | Permission allow/deny lists, enabled plugins, sandbox rules | Claude Code |
| `home/.claude/CLAUDE.md` | My personal preferences. Read it for ideas, do not install it verbatim | Claude Code |
| `agents/codex/skills/` | Codex skills: `deslop-prose`, `deslop-code`, `gh-fix-ci`, `gh-address-comments`, `pdf`, `git-commit-staged` | Codex (CLI, IDE extension, ChatGPT desktop) |
| `home/.codex/AGENTS.md`, `home/.codex/agents/` | Codex instructions and subagent profiles | Codex |
| `docs/` | Research behind the deslop skills: the Claudeisms catalogue and register findings | Background reading |

Prerequisites: [Claude Code](https://code.claude.com/docs/en/quickstart)
(`curl -fsSL https://claude.ai/install.sh | bash`), and/or
[Codex](https://learn.chatgpt.com/docs/codex/cli)
(`curl -fsSL https://chatgpt.com/codex/install.sh | sh`). The skill scripts run
under [uv](https://docs.astral.sh/uv/), so install that too.

### Take only the skills

Clone anywhere, then symlink the skills you want. Symlinks mean `git pull`
updates them in place.

```bash
git clone git@github.com:anilkeshwani/dotfiles.git ~/src/anilkeshwani-dotfiles
DOTFILES=~/src/anilkeshwani-dotfiles
```

Claude Code reads personal skills from `~/.claude/skills/<name>/SKILL.md`:

```bash
mkdir -p ~/.claude/skills
for skill in deslop-prose deslop-code excalidraw; do
    ln -sfn "${DOTFILES}/home/.claude/skills/${skill}" ~/.claude/skills/"${skill}"
done
```

Codex reads user skills from `~/.agents/skills/<name>/SKILL.md`:

```bash
mkdir -p ~/.agents/skills
for skill in deslop-prose deslop-code gh-fix-ci gh-address-comments pdf; do
    ln -sfn "${DOTFILES}/agents/codex/skills/${skill}" ~/.agents/skills/"${skill}"
done
```

Subagents and output styles work the same way, from
`home/.claude/agents/` into `~/.claude/agents/` and `home/.claude/output-styles/`
into `~/.claude/output-styles/`.

Two skills have dependencies you may not have. `journal` targets an Obsidian
vault at `~/journal` (`~/Desktop/journal` on macOS) and dispatches the
`journal-scribe` agent, so install both or neither. `excalidraw` shells out to
`uv run --script`.

### Using them

In Claude Code, run `/skills` to confirm they loaded. Claude picks a skill up on
its own when a task matches the description, or you can force it by typing
`/deslop-prose`. Edits to a `SKILL.md` are picked up live, without restarting
the session.

In Codex, reference a skill with `$deslop-prose` in the CLI and IDE extension,
or `@deslop-prose` in ChatGPT. Implicit selection by description works the same
as in Claude Code.

### Terminal or desktop app

Claude Code's desktop app (download from [claude.com/download](https://claude.com/download),
then open the **Code** tab) runs the same engine as the CLI and reads the same
`~/.claude` tree, so skills, agents, output styles, `settings.json` and
`CLAUDE.md` all apply with no extra setup. One caveat: personal skills load in
local and SSH sessions only, so Cowork and cloud sessions will not see them. You
can hand a session across with `/desktop` from the CLI, or `/resume` in the
desktop app.

The same holds on the Codex side. The CLI, the IDE extension and the ChatGPT
desktop app all read `~/.agents/skills`, so one symlink covers all three.

### Or install everything

If you actually want my whole setup, including zsh, git, tmux and nvim config:

```bash
uv run --script install.py --dry-run   # inspect the plan first
uv run --script install.py
```

Everything under `home/` is symlinked into `$HOME`. Anything it would replace is
moved to `~/.local/state/dotfiles-backups/<timestamp>/` first, so the run is
reversible. `--codex-only` restricts it to Codex instructions, agent profiles
and skills.
