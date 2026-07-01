---
name: deslop-prose
description: Rewrite prose to remove AI-writing tells — em-dashes, "not X, but Y" antithesis, overused vocabulary (delve, seamless, robust...), rule-of-three, hedging, sycophancy, vague abstraction over concrete detail, and uniform sentence rhythm. Use when asked to humanize, de-slop, or "de-AI" writing, make text sound less like an LLM, or edit an essay/doc/blog post/email/PR narrative for AI tells. NOT for code comments, docstrings, or commit messages — use deslop-code for those.
metadata:
  short-description: De-slop prose (essays, docs, emails, PR narrative)
---

# deslop-prose

## Overview

Remove the stylistic fingerprints that mark prose as LLM-generated, while preserving meaning and the author's real voice. This is prose only: essays, docs, blog posts, emails, PR/issue narrative, marketing copy. The full tell catalogue with evidence lives in `references/prose-banlist.md`.

The core belief, which shapes everything below: **the enemy is lexical-syntactic smoothness, not length or topic.** Cutting beats rewriting. The signals are probabilistic, never proof.

## Register gate — check this first

- If the text is **code comments, docstrings, commit messages, or PR/commit prose**, stop and use `deslop-code` instead. The correct "human" voice there is terse and plain; this skill's instincts would over-edit it.
- If the text is **encyclopedic, technical, legal, or scientific**, neutral-and-plain *is* the human register. Do not inject personality, contractions, or "voice." Apply the punctuation, banned-vocabulary, and structure rules, and **prefer the concrete mechanism over vague abstraction (§9)** — technical docs especially should name the actual mechanism and read standalone. Skip only the tone/warmth rules.
- Otherwise (general prose), apply everything.

## Process

1. **Scan** the text against the tells in `references/prose-banlist.md`. Note every hit with its category.
2. **Cut first.** Delete filler, hedging throat-clearing, summary bookends, and redundant sentences outright. Most slop dies here, and deletion never introduces new slop. Do not rewrite what you can remove.
3. **Rewrite minimally**, only where cutting isn't enough: break antithesis scaffolds ("not X, but Y" → state both directly), swap Tier-1 vocabulary for plain words, vary sentence length, replace a vague claim with the specific fact **already present in the source**.
4. **Re-scan the rewrite** against the same list. Rewrites reproduce the cadence they just removed (you will write "X, not Y" while deleting "not Y, but X"). Fix what the second pass finds.
5. **Report**: the cleaned text, then a short bulleted list of what you changed and why. Apply the rules silently *in the output itself* — never leave meta-commentary in the prose.

## Rules (condensed — full lists and examples in references/prose-banlist.md)

- **Punctuation.** Cut em-dashes hard (target ≤1 per 500 words; prefer zero — use commas, parentheses, or a period). Straight quotes. Don't listify ideas that aren't lists.
- **Vocabulary — tiered, not banned outright.** Tier-1 (delve, tapestry, leverage, seamless, robust-outside-engineering, pivotal, underscore, showcase, myriad...): almost always replace. Tier-2 (foster, bolster, elevate, streamline, nuanced, crucial...): flag only when 2+ cluster in a paragraph. Tier-3 (significant, innovative, dynamic...): flag only at ~3%+ density. One legitimate use is fine.
- **Negative parallelism** ("It's not just X, it's Y" / "not X, but Y" / "No X. No Y. Just Z."): the #1 structural tell. Assert the point directly without the negation scaffold.
- **Structure.** Break the rule-of-three (use two or four). Kill "In conclusion" bookends and framing sandwiches. Drop "Let's dive in" openers and rhetorical-question section headers.
- **Hedging/filler.** Delete "It's worth noting", "It's important to", "Generally speaking", "In today's fast-paced world", "That being said". Lead with the point.
- **Tone** (general prose only). Cut sycophancy ("Great question!", "You're absolutely right!"), performative enthusiasm, servile closers, and **faux-candor** ("Let me be honest", "To be honest", "Honestly," "The honest truth is") — the candor belongs in the content, not the announcement.
- **Concrete over vague** (§9, applies even to technical text). Name the mechanism instead of gesturing at it ("sits behind several checks" → which checks, which flags, which default), and don't string two vague clauses together with a floaty ", and" — state how they relate. Each sentence should read standalone.
- **Formatting.** No mechanical bolding, no "Bold lead-in: explanation" bullets, no title-case headings, no emoji headers.
- **Rhythm.** Vary sentence length: at least one short (<10 words) and one long (>20) per few sentences. Uniform length is the most measurable machine signal.

## Hard guards

- **Never invent facts.** "Be specific" must draw on the source only. If the concrete detail (a name, number, tool, mechanism) isn't in the text, keep it abstract or ask the author. A specific-sounding fabrication is worse than the vague phrasing it replaced.
- **Refinement trap.** Once a passage reads human, stop editing it. "Improving" clean prose — tightening, smoothing, making parallels neat — pushes it *back* toward machine register.
- **Density, not zeal.** Ship a false-positives list: one em-dash, one transition word, one short sentence, quoted material, a single legitimate "robust" — leave them.
- **Signals, not proof.** Detector scores are noisy and biased against ESL and technical writers. Optimize for a human reader, not a detector number. Say so if the user is chasing a score.
