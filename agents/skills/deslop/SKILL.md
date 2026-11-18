---
name: deslop
description: Clean up existing text so it reads as plainly written by a person, applying the house writing rules. Covers prose (docs, READMEs, emails, Slack and Linear text, essays, PR narrative) and code text (comments, docstrings, commit messages, PR descriptions). Use when asked to deslop, humanize, de-AI, tighten or edit text for AI tells, or to check a draft or diff against the writing rules. Ships a deterministic checker for dashes, banned words and phrases, negative parallelism and the serial comma.
---

# deslop

A cleanup pass over text that already exists. The rules themselves are the "Writing" sections of the global instructions (`agents/AGENTS.md` in the dotfiles repo, loaded as `~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md` and `~/.gemini/AGENTS.md`). They are already in context; this skill is the procedure for applying them to a target.

## Process

1. **Find the target**: a file, a `git diff`, a commit message, a PR body or pasted text. For a diff, touch only lines the change adds or modifies.
2. **Pick the register.**
   - Code text (comments, docstrings, commits, PRs): terse and plain is the human voice. Prefer deleting a comment over rewriting it.
   - Technical, reference or scientific prose: neutral and plain. Don't add personality or warmth.
   - General prose (emails, essays, posts): apply everything.
3. **Check clarity first**, against "Make it clear": is the point in the first sentence, is the actor the subject, is every claim concrete, does every sentence add something? These faults matter more than any banned word.
4. **Cut before rewriting.** Delete filler, restatements, bookends and comments that say what the code does. Deletion never introduces a new tell.
5. **Rewrite minimally** where cutting isn't enough. Use only facts already in the source.
6. **Run the checker** and fix what it reports outside quotations:
   ```bash
   uv run --script ~/.agents/skills/deslop/scripts/deslop_guard.py FILE...
   pbpaste | uv run --script ~/.agents/skills/deslop/scripts/deslop_guard.py -
   ```
   HARD hits fail the file. WARN hits are words that are often fine; judge each in context. Files that list the banned words on purpose, such as `AGENTS.md`, fail by design.
7. **Report** the cleaned text, then a short list of what changed and why. Keep meta-commentary out of the text itself.

## Guards

- **Quotations stay verbatim**, dashes, serial commas and spelling included. Changing a quote to pass the checker falsifies it.
- **Never invent facts.** If a concrete detail isn't in the source, keep the abstract wording or ask.
- **Stop once it reads plainly.** Further polishing pushes text back toward machine register.
- **Density over zeal.** One legitimate "robust" or a single short sentence is fine. A false positive costs more than a missed tell.
