---
name: deslop-code
description: Strip AI tells from code comments, docstrings, commit messages, and PR descriptions — redundant comments that restate code, multi-line narrative comments, ceremonial docstrings, change-narration ("NEW:", "was previously"), and the "This PR does the following:" template. Also flags over-used code-architecture vocabulary (seam, cutover, surface, canonical, load-bearing, "want me to (a/b)?"). Use when cleaning up comments/docstrings on a diff or file, tightening generated commit/PR text, or asked to make code documentation less verbose or less AI-sounding. NOT for prose/essays — use deslop-prose.
---

# deslop-code

## Overview

A delete-first cleanup pass over the *documentation coding agents write for codebases*: comments, docstrings, commit messages, PR descriptions, and the code-architecture register that leaks into technical explanation. It runs as a separate pass because in-line restraint is unreliable — commenting is how the model reasons, so it over-comments by default. Generate, then sweep.

This complements the `senior-mle-reviewer` pithy-comment standard; use it as the standalone cleanup pass. Full detail and the measured vocabulary live in `references/code-register.md`.

## Register gate

If the target is prose (an essay, blog post, email, marketing copy), use `deslop-prose` instead. This skill assumes the reader is a competent practitioner of the language and that terseness is correct.

## Target

Determine what to clean from the user's request or context: a file, a `git diff`, a staged commit message, a PR body, or pasted text. For a diff, only touch lines the change adds or modifies — do not re-comment untouched code.

## The comment standard (the core rules)

1. **Comments answer WHY, never WHAT.** If a comment restates the code, delete it (`i += 1  # increment i`). If the code needs a "what" comment to be understood, fix the code, don't annotate it.
2. **No comment over three lines.** Multi-line narrative comments are generation scaffolding, not documentation. Collapse to one line of *why*, or delete.
3. **No change-narration.** Delete `# NEW:`, `# Updated logic`, `# was previously...`, `# added to fix...`. The comment describes the code as it is now, for a reader who never saw the diff. History lives in git. This is the main comment-rot vector.
4. **Docstrings earn their place.** Delete ones that only restate the signature or re-narrate type annotations. Keep what the signature can't show: units, invariants, side effects, raised exceptions, the non-obvious contract. Don't put full Args/Returns/Raises blocks on trivial helpers. Match the file's existing docstring convention; never introduce a second style.
5. **No decoration.** No `# ==== SECTION ====` banners, no emoji, no "Note:"/"Important:" prefixes, no exclamation marks, no comments teaching the language ("A dict is key-value pairs").
6. **Don't touch what you didn't change.** Never add docstrings/comments/types to untouched code during an edit.

Prefer **deleting** over rewriting. The best fix for a bad comment is usually no comment.

## Commit messages & PR descriptions

- **Commit:** one imperative subject line, why-focused, under ~70 chars. Body only if the why isn't obvious; never a restatement of the diff. Verbs: add (feature), update (enhancement), fix (bug).
- **PR body:** a 1–3 bullet Summary plus a Test plan of what was *actually run*. Kill "This PR does the following:", per-file diff narration, and filler bullets ("improves readability", "ensures backward compatibility").
- **No dramatic-alignment intensifiers** in commit/PR/ticket prose: "exactly where deployment fails", "precisely the case that matters", "the very regime we care about". Perfect-correspondence claims read as hyperbole. State the relationship plainly and let the facts carry the emphasis.
- **No echo restatements.** Don't close a point by re-asserting a fact established a sentence earlier ("the eval set measures this case; training rarely produces it" after opening with training rarely producing it). Every sentence must add information; the reader holds the previous one. Cut the echo.

## Code-architecture register vocabulary (Tier-2 — flag in clusters, never hard-ban)

These are real, useful engineering terms; the tell is *defaulting to the metaphor* and *density*. Measured over 416 local sessions (× = Claude's rate vs the user's own on the same repos): **seam** (2.5×), **cutover** (4.4×), **surface** (2.0×, in a third of sessions), **canonical** (1.5×), **load-bearing** (2.8×, hard-ban — always replace), **fold/collapse** (~2.5–4×), **plumb/converge/tighten** (4–13×), **stale/cleanly/genuinely** (3–7×). Discourse tics: **"Let me [verb]…"** openers, **"want me to (a)… or (b)…?"** offer-closers (46.7×), **"confirmed/confirms"** self-narration (~21×), **"the honest…"**, **"the picture"**, **trap**, **purely**, **caveat**.

When cleaning technical explanation: if a structural metaphor appears where a plain word works ("interface"/"boundary" for *seam*, "the switch" for *cutover*), and especially if several cluster, swap to plain. Leave a single apt use. See `references/code-register.md` for the full table, ratios, and honest negatives (crisp, leverage, orthogonal are *not* over-used — don't flag them).

## Process

1. Identify the target (file / diff / commit / PR).
2. Sweep comments and docstrings against the standard above; **delete first**, trim second.
3. Check commit/PR text against the templates.
4. Flag over-used code-register vocabulary only where it clusters or displaces a plain word.
5. Apply the edits (or report them if the user wants review-only), then list what was removed vs trimmed. A "Recommended removals" list is a first-class outcome.

## Hard guards

- **Never delete a load-bearing *why* comment** to hit a line count. The standard removes noise, not the rationale a maintainer needs.
- **Never invent** a rationale to justify keeping a comment. If you can't state the real why, the comment goes.
- Terseness serves the reader, not a metric. If a genuinely complex invariant needs four lines, it gets four lines — the three-line rule is a default, not a straitjacket.
