## Set up dotfiles

Dotfiles live in `home/` and are installed as symlinks into `$HOME` via `install.py`. Existing files are backed up to `~/.local/state/dotfiles-backups/` before being replaced.

On macOS, the installer also links `apps/vscode/settings.json` to VS Code's user settings path under `~/Library/Application Support/Code/User/`.

## Agent instructions and writing style

`agents/AGENTS.md` holds the global instructions for every coding agent: the writing style first, then working preferences (dictation, Python, git, file naming). Claude Code, Codex and agy each load it through a symlink:

| Agent | Loads | Tracked as |
|---|---|---|
| Claude Code | `~/.claude/CLAUDE.md` | `home/.claude/CLAUDE.md`, a symlink to `agents/AGENTS.md` |
| Codex | `~/.codex/AGENTS.md` | `home/.codex/AGENTS.md`, a symlink to `agents/AGENTS.md` |
| agy | `~/.gemini/AGENTS.md` | `home/.gemini/AGENTS.md`, a symlink to `agents/AGENTS.md` |

Claude Code has no user-level `AGENTS.md`, hence the `CLAUDE.md` name on its side. Codex reads one global file and can't import another, which is why the writing rules live in this file and not in a separate one.

Skills shared by all agents live under `agents/skills`. The installer links each one into `~/.agents/skills` (Codex), `~/.gemini/config/skills` (agy) and the `skills/` dir of every Claude Code config dir. `deslop` is the cleanup pass for existing text; its `scripts/deslop_guard.py` checks a file or stdin against the mechanical rules (dashes, banned words and phrases, negative parallelism, serial comma). Its word lists mirror `agents/AGENTS.md`, so change both together.

Claude Code-only skills stay under `home/.claude/skills`. `agents/codex/skills` holds Codex system and vendored skills, which the installer does not link. Files under `home/.codex/agents` are custom subagent profiles, not skills.

Codex configuration is machine-local. The installer does not read, modify or
link `~/.codex/config.toml`.

Changed Codex files are backed up under `~/.local/state/dotfiles-backups/` before the
installer updates them.

```bash
uv run --script install.py [-h] [--source SOURCE] [--dry-run] [--codex-only]
```

Use `--codex-only` to repair or refresh Codex without changing any Claude Code
path, VS Code setting or general shell dotfile.

## Antigravity CLI (agy) with Gemini 4 Argon

| Tracked file | Installed at | How |
|---|---|---|
| `home/.gemini/AGENTS.md` | `~/.gemini/AGENTS.md` | Symlink. In the repo it points at `agents/AGENTS.md`, the global instructions shared with Claude Code and Codex. agy loads `~/.gemini/AGENTS.md` in every workspace. |
| `home/.gemini/antigravity-cli/settings.json` | `~/.gemini/antigravity-cli/settings.json` | Merged, not linked. agy rewrites this file on every start (it re-sorts the keys and replaces the file), which would turn a symlink into a detached copy. The installer does a three-way merge against the tracked file it applied last time, kept under `~/.local/state/dotfiles-merge-base/`. Tracked values win, entries agy added (such as `trustedWorkspaces` or extra permission rules) are kept, and entries deleted from the tracked file are deleted from the installed one. A run backs the installed file up only when the merge changes it, into the same timestamped directory under `~/.local/state/dotfiles-backups/` as the run's other backups. Rerun the installer after changing the tracked file. |

The settings start agy in `auto` mode with the terminal sandbox on, default to `gemini-4-argon` (resolved to `gemini-4-argon-medium`) and mirror the Claude Code deny list: no `sudo`, force pushes, branch or tag deletion, `git remote` changes, `git reset --hard`, `git clean`, restoring files from `main`/`master`, or `gh pr merge`/`close`. `git switch` is allowed, as it is for Claude Code and Codex. `git push` and `rm -rf` ask first. Reasoning effort has no settings key; the `argon` launcher in [antigravity-argon-gcp](https://github.com/anilkeshwani/antigravity-argon-gcp) passes `--effort medium` and signs in with GCP ADC.

On Linux, auto mode needs unprivileged user namespaces for the sandbox. Ubuntu's default `kernel.apparmor_restrict_unprivileged_userns = 1` blocks them, and agy then starts in default mode.

## Multiple Claude Code accounts

Claude Code reads its entire config tree from `$CLAUDE_CONFIG_DIR`, defaulting to `~/.claude`. That tree includes `.claude.json`, which stores `oauthAccount` — so pointing the variable at a second directory gives a second, independent login, and the subscriptions can run at the same time in different terminals.

`.env` names one config dir per account, overridable per host in `.env_linux` / `.env_macos`:

| Variable | Default | Command |
|---|---|---|
| `CLAUDE_CONFIG_DIR_WORK` | `~/.claude` | `claude` |
| `CLAUDE_CONFIG_DIR_EXTRA` | `~/.claude-extra` | `claude-extra`, the second ai-coustics seat |
| `CLAUDE_CONFIG_DIR_PERSONAL` | `~/.claude-personal` | `claude-personal`, reserved for a personal account |

The commands are shell functions in `home/.functions` that run `claude` with `CLAUDE_CONFIG_DIR` set.

`install.py` reads those two variables and installs everything under `home/.claude/` into each extra config dir as well, so `settings.json`, `CLAUDE.md`, agents, skills and output styles stay identical across accounts. `plugins/` is symlinked to the one in `~/.claude` — it is local state rather than a tracked dotfile, but the marketplace clones are bulky and the enabled plugin set is already pinned by the shared `settings.json`.

Everything account-specific is left for Claude Code to create per dir and is never linked: `.credentials.json` (on macOS a Keychain entry keyed by the config dir), `.claude.json`, `history.jsonl`, `sessions/` and the various caches. Unset a variable on a host where that account is not needed and the installer skips it.

The extra profile is a second seat in the same ai-coustics org, so it also links `projects/`, `file-history/` and `plans/` to `~/.claude`. Auto-memory and session transcripts are then common to both seats, and `claude-extra --resume` can pick up a session started under `claude`. `PROFILE_SHARED_CLAUDE_LOCAL_STATE` in `install.py` sets this per profile; the personal profile keeps its own. The extra seat is for usage only and gets no MCP servers of its own; sessions on it fetch integration data through the main seat, as `agents/AGENTS.md` describes.

Two caveats. User-scoped MCP servers added with `claude mcp add -s user` live in `.claude.json` and so do not carry across: re-add them per account, or use project scope. And because `plugins/` is shared, two instances installing or updating plugins concurrently can race; do plugin management from one account at a time.

### Perplexity Computer MCP server

`scripts/register_perplexity_computer_mcp.sh` registers the Perplexity Computer MCP server (`perplexity-computer`, `https://www.perplexity.ai/rest/computer/mcp`) with the main Claude Code seat. Run it once per host, then sign in with `/mcp` inside `claude`. It skips the server if it exists. The extra seat doesn't get it.

Computer is Perplexity's general-purpose agent. Its usage spends Perplexity account credits, and the Max plan includes a monthly allowance. Perplexity's search API server (`https://api.perplexity.ai/mcp`) is left out because it bills API credits, which the subscription doesn't cover.

On a remote host the OAuth callback goes to `localhost` on that host, so the browser shows a connection error after you approve. Copy the full address from the browser's address bar and paste it into the box `/mcp` shows. `agents/AGENTS.md` tells agents when to delegate to Computer.

## Secrets

`~/.secrets` holds API keys as shell variables and is sourced by `.zshrc` and `.bashrc`. It is never committed. `secrets-sync` generates it on each machine from a folder in my personal Bitwarden vault, giving each machine only the items tagged for it, and a pre-commit guard blocks commits that stage secret values. [docs/secrets-sync.md](docs/secrets-sync.md) has the storage model, the migration checklist, rotation and the threat model.

```bash
secrets-sync check   # compare ~/.secrets with Bitwarden by name
secrets-sync pull    # rewrite ~/.secrets from Bitwarden (unlocks, then locks)
secrets-sync doctor  # report risky states without unlocking
```

Tests for the tool and the guard run with `uv run --with pytest pytest tests`.

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
| `bootstrap_ubuntu.sh` | Full Ubuntu instance setup (apt packages, Rust, uv, Python CLI tools, mise, Claude Code) |
| `install_conda.sh` | Install Miniconda and create a clean `main` environment |

Bootstrap a fresh cloud instance:

```bash
bash scripts/bootstrap_ubuntu.sh
```

System packages come from apt when the script can use sudo, and from Homebrew otherwise. If you are in the `sudo`, `admin` or `wheel` group and sudo needs a password, the script asks for it once at the start; a refused password falls back to Homebrew. Set `BOOTSTRAP_SUDO=yes` or `BOOTSTRAP_SUDO=no` to skip the detection.

Hints:
- [Reload the tmux config mid-session](https://superuser.com/questions/580992/how-do-i-reload-tmux-configuration) with `(ctrl + B), :` then `source-file ~/.tmux.conf`
- Always handy: `exec zsh` 

### Tool versions

Node and standalone CLIs such as delta and television are managed by [mise](https://mise.jdx.dev), configured in `home/.config/mise/config.toml`. To add a tool, add a line there and run `mise install`. A `latest` entry means the newest version at install time; `mise upgrade` moves installed tools forward.

We use mise in place of nvm, which slows every shell start. Volta has been unmaintained since November 2025 and its maintainers recommend mise. Python stays with uv and Rust with rustup.

## Using these skills and configs on your own machine

This section is for anyone who is not me. It assumes you want the skills and
maybe the agent profiles, without adopting my shell, git or editor config.

### What is shareable

| Path | What it is | Applies to |
|---|---|---|
| `agents/AGENTS.md` | My global instructions, including the writing style. Read it for ideas, do not install it verbatim | Claude Code, Codex, agy |
| `agents/skills/` | Skills for every agent: `deslop` | Claude Code, Codex, agy |
| `home/.claude/skills/` | Claude Code skills: `excalidraw`, `journal` | Claude Code (CLI, desktop, IDE) |
| `home/.claude/agents/` | Subagent profiles: `architect-reviewer`, `senior-mle-reviewer`, `researcher-reviewer`, `journal-scribe` | Claude Code |
| `home/.claude/output-styles/` | Output styles | Claude Code |
| `home/.claude/settings.json` | Permission allow/deny lists, enabled plugins, sandbox rules | Claude Code |
| `agents/codex/skills/` | Codex skills: `gh-fix-ci`, `gh-address-comments`, `pdf`, `git-commit-staged` | Codex (CLI, IDE extension, ChatGPT desktop) |
| `home/.codex/agents/` | Codex subagent profiles | Codex |

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
ln -sfn "${DOTFILES}/agents/skills/deslop" ~/.claude/skills/deslop
for skill in excalidraw journal; do
    ln -sfn "${DOTFILES}/home/.claude/skills/${skill}" ~/.claude/skills/"${skill}"
done
```

Codex reads user skills from `~/.agents/skills/<name>/SKILL.md`:

```bash
mkdir -p ~/.agents/skills
ln -sfn "${DOTFILES}/agents/skills/deslop" ~/.agents/skills/deslop
for skill in gh-fix-ci gh-address-comments pdf; do
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
`/deslop`. Edits to a `SKILL.md` are picked up live, without restarting
the session.

In Codex, reference a skill with `$deslop` in the CLI and IDE extension,
or `@deslop` in ChatGPT. Implicit selection by description works the same
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
