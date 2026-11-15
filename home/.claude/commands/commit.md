---
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git add:*), Bash(git restore --staged:*), Bash(git commit:*)
description: Commit the working tree as atomic commits, following the repo's commit conventions
argument-hint: "[optional guidance, e.g. which changes to leave out]"
---

## Context

- Current branch: !`git branch --show-current`
- Status: !`git status --short --branch`
- Diff (staged and unstaged): !`git diff HEAD`
- Recent commits, for message style: !`git log --oneline -15`

## Your task

Commit the changes above as one or more atomic commits. Extra guidance from the user, if any: $ARGUMENTS

1. Group the changes by concern. Each commit holds one logical change: a feature, a fix, a refactor, a config tweak or one batch of related content. Unrelated changes never share a commit, even small ones.
2. If a single file holds changes for more than one concern, keep them together and say so in your reply. Do not use interactive staging.
3. Order the commits so that each one leaves the repo in a working state, with dependencies first.
4. For each group, stage exactly its files with `git add <paths>` and commit. Check `git status` between commits.
5. Write each message in the style of the recent commits above and follow any commit conventions in CLAUDE.md. Use an imperative subject line of about 72 characters or fewer. Add a body only when the reason for the change is not obvious from the subject.
6. End each message with the attribution lines the session gives for commits, if any.
7. Do not commit files that look like secrets, credentials or local machine state. List anything you skipped.
8. Never amend, rebase, push or force-push. Do not touch commits that already exist.

When done, reply with one line per commit (short hash and subject) and anything you left uncommitted.
