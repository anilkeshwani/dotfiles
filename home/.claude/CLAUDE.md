# User Preferences

## Communication: I use dictation

I talk to you through dictation software, so my messages may contain
transcription artifacts: homophones, mis-split or run-together words, dropped
punctuation, and proper nouns/code identifiers rendered phonetically (e.g.
"Onyx" for `ONNX`, "worktrips" for "worktrees"). When a term looks off but a
nearby technical word fits the context, prefer that reading. If a likely
mis-transcription changes what I'm actually asking, verify against the code
before acting rather than taking the literal string at face value.

## Running Python scripts

Always run Python scripts directly with `uv run --script`, not by `chmod +x` + executing them. Example:

```bash
uv run --script path/to/script.py
```

## Git: prefer rebase over merge

When integrating upstream changes (e.g. bringing `main` into a feature branch), always use `git rebase`, never `git merge`. This applies whether the user asks to "merge in main", "sync with main", "update from main", or similar — interpret these as rebase requests.

Rationale: keeps branch history linear and the eventual squash-merge clean; avoids merge commits cluttering the log; makes `git log --oneline main..HEAD` continue to show only this branch's actual work.

When a rebase has conflicts, resolve them, `git add`, and `git rebase --continue` — do NOT abort and fall back to `git merge`.

## File naming: think globally, not just locally

When creating new files (especially reports, analyses, docs, scripts), pick a name that's clear *outside* the current task. The parent directory makes the context obvious to you right now, but the file gets linked from PR descriptions, referenced in other docs months later, surfaced in `grep` results, attached to memory entries, or moved between repos — and its name is what travels.

- Avoid generic names like `REPORT.md`, `findings.md`, `notes.md`, `output.csv`, `script.py` even when the directory makes them locally unambiguous.
- Encode the *topic* in the name, not just the file's role. `PREP_DETERMINISM_REPORT.md` beats `REPORT.md`; `silero_vad_calibration.py` beats `calibrate.py`.
- Match the conventions of sibling files in the same directory before deciding (e.g. if peers use `UPPER_SNAKE_CASE.md` for reports, follow suit).
- Before settling on a name, ask: "if I saw only this filename in a search result a year from now, would I know what it is?" If not, rename.

## Linear: write comments and descriptions for the readers

When commenting on a Linear ticket, ground the comment in the ticket's stated aims: address its goals, acceptance criteria, and definition of done — not just the work performed. A comment that narrates activity without connecting it back to what the ticket set out to achieve leaves the reader to do that mapping themselves.

Write comments and new-ticket descriptions for the readers, not the author. A teammate without the immediate project context must be able to follow them: expand or anchor internal shorthand (config names, node shapes, metric keys) on first use.

Where possible, take context on the team — colleagues' roles, backgrounds, and profiles — and let that shape what each reader can be assumed to know. Notes on colleagues live in `~/journal/ai-coustics/`.
