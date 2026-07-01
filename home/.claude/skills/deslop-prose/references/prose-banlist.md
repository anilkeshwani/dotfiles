# Prose AI-tell reference

The full catalogue behind `deslop-prose`. Evidence tiers: **[A]** measured/corroborated, **[B]** widely-cited, **[C]** single-source. Master caveat: no single item proves AI authorship; they indict in combination and at density. Single-word detection is culturally biased (Stanford: ~61% of human ESL TOEFL essays flagged as AI).

## 1. Punctuation [A]

- **Em-dashes (—/–)** — the most-cited single tell. Target ≤1 per 500 words; prefer zero. Replace with commas, parentheses, or a period.
- **Curly/smart quotes** where straight quotes are expected.
- **Semicolons** joining independent clauses more than modern prose does. (Judgment call: well-written humans do use them; ban only when detector-passing is the goal.)
- **Bulleted/listified** ideas that aren't lists.

## 2. Vocabulary — tiered by action

Do not hard-ban single instances; a lone legitimate use is human. Measured evidence (Kobak et al., ~15M PubMed abstracts): delve 28×, underscore 13.8×, showcasing 10.7× vs pre-2022 baseline.

**Tier 1 — almost always replace:** delve/delving, tapestry, landscape (figurative), realm, testament (to), leverage (v), utilize, harness, underscore, showcasing, seamless, robust (outside engineering), pivotal, intricate, meticulous, comprehensive (of one's own output), cutting-edge, game-changer, synergy, holistic, paradigm, embark, endeavor, myriad, plethora, facilitate, elucidate.

**Tier 2 — flag when 2+ cluster in a paragraph:** foster, bolster, garner, navigate (figurative), elevate, unleash, streamline, empower, spearhead, resonate, revolutionize, nuanced (filler), crucial, ecosystem, cultivate, illuminate, catalyze, galvanize, transformative, multifaceted, profound, vibrant.

**Tier 3 — flag only at ~3%+ density:** significant, innovative, effective, dynamic, scalable, compelling, unprecedented, exceptional, remarkable, sophisticated, world-class, state-of-the-art.

**Cliché phrases:** "a testament to", "navigating the landscape of", "the transformative power of", "plays a pivotal role in", "underscores the importance of", "in today's fast-paced world", "in the ever-evolving landscape of", "seamless integration", "rich tapestry", "unlock the potential", "harness the power of", "shed light on", "embark on a journey", "a myriad of", "in the realm of", "at its core", "when it comes to".

## 3. Negative parallelism [A] — the #1 structural tell

"It's not just X, it's Y" · "Not X, but Y" · "This isn't about X. It's about Y." · "X rather than Y" · "Not only X, but also Y" · "No X. No Y. Just Z." · "The question isn't X. It's Y." · em-dash dismissal ("X — not Y"). Fix: assert the point directly without the negation scaffold.

## 4. Rhetorical structure [A]/[B]

- Rule of three / tricolon with even rhythm. Use two or four.
- "Firstly / Secondly / Finally" signposting.
- "In conclusion" / summary bookends (fractal summaries).
- Rhetorical question as a section opener ("The result? Devastating.").
- "Let's dive in / unpack this / explore" openers.
- Framing sandwich: restate question, deliver, restate conclusion.
- Trailing "-ing" significance clauses ("...marking a pivotal moment", "...underscoring its importance").
- Aphoristic pseudo-profound closer ("At the end of the day, we are all human.").

## 5. Hedging & filler [A]

"It's important/worth noting that", "It could be argued that", "Generally/broadly speaking", "Here's the thing", "The reality is", "In today's fast-paced world", "That being said", "When it comes to", "It goes without saying", "aims to explore". Fix: delete the announcement, lead with the point.

## 6. Tone (general prose only — skip for technical/encyclopedic) [A]/[B]

- Sycophancy: "You're absolutely right!", "Great question!", "What a thoughtful question!"
- Performative enthusiasm: exciting, incredible, powerful, amazing, remarkable.
- Relentless positivity / uniformly polished balance.
- Servile closers: "Hope this helps!", "Let me know if you'd like me to go deeper!", "Certainly!"
- Chatbot residue: "As an AI language model...", "I hope this email finds you well."
- **Faux-candor / performative honesty:** "Let me be honest", "To be honest", "Honestly," "I'll be honest", "In all honesty", "The honest truth is", "Frankly", and the framing form "The honest [answer/name] is...". The candor belongs in the content, not the announcement.

## 7. Formatting [A]/[B]

Boldface overuse; "Bold lead-in: explanation" bullets; Title Case In Headings; emoji section headers; markdown bleeding where it won't render; leftover tokens (`contentReference`, `oaicite`, `utm_source`); unfilled placeholders (`[Your Name]`, `{client_name}`).

## 8. Statistical / structural [A] — survives paraphrasing

- **Low burstiness** — uniform sentence and paragraph length. The most measurable signal. Aim for ≥1 sentence <10 words and ≥1 >20 words per few sentences.
- **Low perplexity** — too-predictable word choice.
- **Parataxis** — "Short sentence. Then another. Then another." Connect with subordinate clauses.
- **Abstract nouns over concrete verbs** — "The implementation of a strategy can lead to improved outcomes" vs "Do this and you'll usually see better results."
- **Copula avoidance** — "serves as / stands as / boasts" instead of "is/are".
- **Elegant variation** — cycling synonyms to dodge repetition; a human repeats the term.
- **Vagueness** — no names, numbers, dates, lived detail.
- **Sourceless authority** — "Studies show...", "Experts argue..." with no citation.

## 9. Vague abstraction over concrete mechanism [B] — applies even in technical/encyclopedic text

A clause gestures at something ("sits behind several checks", "has safeguards in place", "handles this carefully") where the concrete mechanism belongs, and often two hazy halves get strung together with a floaty ", and". Name the mechanism inline, state how the halves actually relate, and make each sentence stand on its own without the surrounding context. Note: the tell is the vagueness and the loose syntax, not any single adjective — "conservative", "robust", and the like are fine once the sentence says what they refer to.

Worked example:
- Vague: "Real money sits behind several checks, and the defaults are conservative."
- Concrete: "Trading with real money is guarded by several checks that require explicit flags; the default runs only against the demo (paper) environment."

Tells:
- **Hand-wavy summary instead of the mechanism.** "several checks", "safeguards in place", "a number of steps", "properly handled", "sits behind checks" — say which checks, which flags, which default, which value. The reader wants the mechanism, not the assurance that one exists.
- **Floaty comma coordination.** Two vague clauses joined by ", and" / ", but" with the relationship left implicit. Usually the second clause explains or conditions the first; make that explicit with "requiring", "because", "so that", "unless", or subordinate it, instead of the loose comma.
- **Not standalone.** The sentence only resolves once you have read the list or paragraph it introduces. A reader landing on it cold should still understand it.
- **Telegraphic fragment lead.** A slogan-like fragment standing in for the actual rule ("Secrets stay out of git.", "Paper by default.") where the reader needs the mechanism. Expand it into a full sentence that says how, e.g. "Credentials live in `.env`, which is git-ignored, and gitleaks scans every commit."
- Test: could someone act on this sentence alone? If they would have to read on to learn what the "checks" or "defaults" actually are, inline the specifics. Concreteness beats brevity here.

## Source

Distilled from `docs/CLAUDEISMS_MASTER_CATALOGUE.md` (§1–§8) in this repo, which carries full citations and the existing-skill lineage (blader/humanizer, humanize-prose, avoid-ai-writing, Wikipedia:Signs of AI writing, Kobak et al. arXiv 2406.07016).
