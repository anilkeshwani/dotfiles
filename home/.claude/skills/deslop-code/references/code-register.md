# Code-comment & code-register reference

The full detail behind `deslop-code`. Two parts: comment/docstring tells (§A) and the empirically-measured code-architecture vocabulary (§B).

## §A — Comment, docstring, commit & PR tells

For each: bad → fix, with the principle.

- **Redundant restatement.** `i += 1  # increment i`; `users = []  # empty list of users`. → delete.
- **Ceremonial docstring** restating the signature/types → delete, or keep only units/invariants/side-effects/exceptions.
- **WHAT not WHY.** `# loop over items` → delete; keep only rationale a reader can't infer.
- **Multi-line narrative** (a paragraph over a 3-line function) → one line of why, or delete. LLMs "think out loud in comments"; that scaffolding shouldn't survive.
- **Change-narration / history.** `# NEW:`, `# Updated logic`, `# was previously O(n)`, `# added to fix race` → delete. History is in git. Primary comment-rot vector.
- **Decorative banners** `# ==== HELPERS ====` → delete; declarations are the navigation.
- **Teaching the language** ("A dictionary is key-value pairs") → delete; assume a competent practitioner.
- **Emoji / "Note:" / "Important:" / exclamation spam** → state the fact plainly or delete.
- **Over-templated docstrings** (full Args/Returns/Raises on trivial helpers; mixed styles in one file) → reserve full blocks for public/non-obvious functions; match the file's one convention.
- **PR/commit template** ("This PR does the following:" + per-file narration + filler bullets) → 1–3 bullet Summary + real Test plan; concise why-focused commit subject under ~70 chars.

**Verbatim standards to align with (already in this repo):**
- `senior-mle-reviewer` pithy standard: "No comment over three lines. No comment that narrates history... Comments only for the *why*... never restating what the code plainly says. No wasted words."
- Anthropic default: "Don't add docstrings, comments, or type annotations to code you didn't change. Only add comments where the logic isn't self-evident."

**Why in-line restraint fails, and what works:** commenting is generation scaffolding and training favors tutorial register, so "be concise" gets ignored. Reliable fixes: a *hard numeric* rule (a number can't be rationalized away) plus a *separate delete-first pass* (this skill). A number beats an adjective.

## §B — Code-architecture register vocabulary (measured)

Mined from 416 local Claude Code sessions: 710k words of Claude prose vs 368k of the user's own prose on the same repos. **ratio = Claude's per-100k rate ÷ the user's** — same codebases, so domain jargon cancels and the ratio isolates register. Over-use, not existence, is the tell. These are **Tier-2**: flag in clusters or when displacing a plain word; never hard-ban.

| term / phrase | ratio ×user | note |
|---|---|---|
| "want me to (a…/b…)?" | 46.7× | offer-closer; just do the obvious thing or ask one plain question |
| tighten | 13.0× | |
| converge(s) | 10.7× | |
| "the honest …" | 9.3× | faux-candor leaking into code talk |
| stale | 6.6× | |
| honest(ly) | 5.4× | |
| "the live (consumer/…)" | 4.5× | |
| **cutover** | 4.4× | prefer "the switch"/"the migration step" unless it's genuinely a cutover |
| fold (into) | 4.2× | |
| plumb | 4.0× | prefer "pass"/"thread" or just name it |
| cleanly | 3.5× | |
| genuinely | 3.1× | (26% of sessions) |
| load-bearing | 2.8× | **hard-ban** — always replace; name what depends on it, or "critical"/"essential" |
| **seam** | 2.5× | (12% of sessions) prefer "interface"/"boundary"/"integration point" |
| collapse | 2.5× | |
| blast radius | 2.3× | prefer "scope"/"how much this touches" |
| surface (n./v.) | 2.0× | (33% of sessions) |
| wire (up/in) | 1.9× | |
| canonical | 1.5× | |
| first-class, holistic | ∞ (user: 0) | |
| "you're (absolutely) right" | ∞ | sycophancy |

**Hard-ban (overrides the Tier-2 "never hard-ban" default): `load-bearing`.** It reads as pure Claude. Always replace it rather than merely flagging: name what actually depends on the thing, or use "critical"/"essential".

**Discovered discourse tics (not in the original seed list):** "confirmed/confirms/confirming" (~21×, narrating one's own verification) · "the picture / full picture" (27×) · "wording" (22×) · "trust/intact" (~18×) · "trap" ("the X trap", 16×) · "harmless/cosmetic/purely" (risk-triage, ~12–17×) · "couple", "defensible", "lanes", "spine", "caveat", "neutral", "slightly/subtle/literally". And the pervasive **"Let me [verb]…"** opener (check/read/verify/confirm/look).

**Honest negatives — do NOT flag these** (they did not over-index against the user; some the user uses *more*): crisp/crisply (0.4×), envelope (0.8×), leverage (0.9×), orthogonal (0.9×), concretely (1.0×). thread/upstream/downstream/footprint only mild (~1.2–1.4×).

**Caveat:** baseline is one user's prose, not general English — a strong domain control but a small, slightly noisy sample. Treat the ranking as robust, the decimals as directional. Reproduce with `docs/mine_claude_code_register.py`.

## Source

Distilled from `docs/CLAUDEISMS_MASTER_CATALOGUE.md` §9 and §9A in this repo.
