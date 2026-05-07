# User Preferences

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
