# Claudeisms Research 02 — Humanize Skills & Anti-Slop Tools

**Mission:** Dissect *existing* artifacts that already detect/remove "Claudeisms" / AI-writing tells — Claude Skills, agent-skill repos, prompt collections, linters, and detector-calibrated style guides. Priority deliverable is **verbatim, reusable rule text** we can adapt.

**Bottom line:** This is a crowded, mature space. There are at least a dozen public agent-skills doing exactly "humanize / deslop / anti-slop," most as portable `SKILL.md` files. They converge hard on the same tells (em dash, "not just X but Y", "delve", rule-of-three, filler transitions, uniform sentence length) but diverge in *method*: naive banlists vs. tiered/density-aware banlists vs. detector-calibrated (perplexity/burstiness) vs. corpus-derived voice-matching vs. eval-driven hillclimbing. The two most methodologically interesting are `celestialdust/humanize-prose` (empirically calibrated against real GPTZero score trajectories, and it warns that over-editing *raises* AI score) and `adewale/anti-slop-writing` (eval-harness-driven, with a documented failure mode where the rewriter invents facts to fill a required output slot).

---

## PART A — LOCAL MACHINE SEARCH (result: NOTHING relevant exists)

Searched `/home/anilkeshwani/.claude/`, `/home/anilkeshwani/dotfiles/`, and all `.claude` dirs under `$HOME`. Methods: filename glob (`humaniz*`, `deslop`, `*slop*`, `*style*`, `*prose*`, `*writing*`, `*tone*`) and content grep (`humaniz|deslop|slop|em[ -]?dash|"not just"|delve`) over skills/agents/plugins/CLAUDE.md, excluding `.venv`/`node_modules`/`site-packages`.

**No humanize / anti-slop / deslop skill exists locally.** The user's own skills are only `excalidraw` and `journal`; agents are `architect-reviewer`, `journal-scribe`, `researcher-reviewer`, `senior-mle-reviewer`. Keyword hits were all coincidental / unrelated:

- `/home/anilkeshwani/.claude/CLAUDE.md` and `/home/anilkeshwani/dotfiles/home/.claude/CLAUDE.md` — match "not just" only in the file-naming guidance ("think globally, **not just** locally"). Not about prose.
- `/home/anilkeshwani/dotfiles/home/.claude/agents/senior-mle-reviewer.md` — matches "not just" in code-review context ("matching idiom, **not just** working"). Not about prose.
- `/home/anilkeshwani/.claude/plugins/marketplaces/claude-plugins-official/plugins/hookify/skills/writing-rules/SKILL.md` — this is `writing-hookify-rules`, about authoring *hookify hook rules* (YAML/regex hook config), **not** prose writing. False positive on "writing".

**Conclusion:** If the user wants a humanize skill, it must be built or installed — there is no pre-existing local one to reuse. The Part B artifacts below are the raw material to adapt.

---

## PART B — WEB ARTIFACTS (dissected)

### Artifact index (by method)

| Artifact | Type | Method | Standout feature |
|---|---|---|---|
| `blader/humanizer` | Claude Code skill | 33-pattern banlist + 3-step self-review + voice calibration | The most-cited/popular one; strict "zero em/en dashes in final output" |
| `jalaalrd/anti-ai-slop-writing` | Multi-agent skill (Claude/Codex/Cursor/Gemini) | Banlist + structural rules + per-model first-word tells | **Model-specific first-word tells**; parataxis rule; era-tagged vocab |
| `NousResearch/autonovel/ANTI-SLOP.md` | Fiction-pipeline reference doc | Tiered banlist + detection-signal theory + tone-by-context tables | Best *theory* (perplexity/burstiness/Pangram), cites primary data sources |
| `stephenturner/skill-deslop` | Claude Code skill (scientific/blog) | 10 core rules + quick-checks + 5-dim × 10pt rubric + reference catalogs | 50-pt rubric; sci-vs-blog register split; sources tropes.fyi |
| `aplaceforallmystuff/the-antislop` | Claude Code skill | 3-tier detection + numeric scoring + editor mode | Explicit **point-scored risk levels** (0-5/6-12/13+) |
| `conorbronsdon/avoid-ai-writing` | Claude Code skill (2.1k★) | 3-tier vocab (replace / cluster / density %) + 3 modes + P0/P1/P2 severity | Density-threshold tier (flag at 3%+ of words) |
| `realrossmanngroup/no_ai_slop_writing_rules` | 2 skills (`no-ai-slop` + `rossmann-voice`) | Banlist + **corpus-derived voice fingerprint** (513k words) | Data-driven voice matching w/ measured statistical targets |
| `celestialdust/humanize-prose` | Claude skill + Python scanner | Detector-calibrated workflow from an 8-draft GPTZero trajectory | **"Cutting beats rewriting"; over-editing raises AI score**; ESL-bias framing; watermark caveat |
| `adewale/anti-slop-writing` | Claude skill + eval harness | Eval-driven "hillclimbing"; held-out split; documented failure cases | **Fabrication trap** — rewriter invents facts to fill a required field |
| `Byk3y/no-slop` | Prose linter (code) | 13 regex-category detector, from Wikipedia:Signs of AI writing | Programmatic; authoritative source lineage |
| Wikipedia:Signs of AI writing | Community style guide | Categorized catalog of tells | The upstream authority most skills cite |
| Commercial "Humanize AI"/"Undetectable AI" | SaaS | NLP rewrite tuning perplexity + burstiness | Marketing confirms the two metrics detectors use |

Primary data sources these skills cite: **Wikipedia:Signs of AI writing** (WikiProject AI Cleanup), **sam-paech/slop-forensics** (word/trigram overrepresentation), **EQ-Bench Slop Score**, **Pangram Labs** (classifier), **tropes.fyi** (ossama.is), Stanford HAI TOEFL false-positive study (~61%), and the arXiv "Measuring AI Slop" paper (2509.19163).

---

## THE VERBATIM RULE TEXT (the load-bearing output)

### 1. `blader/humanizer` — 33 AI-writing tells + 3-step process
Source: https://github.com/blader/humanizer (SKILL.md)

The full 33 named patterns (grouped):

- **Content:** (1) Undue Emphasis on Significance/Legacy/Broader Trends ("stands as," "testament," "pivotal," "reflects broader"); (2) Undue Emphasis on Notability/Media Coverage; (3) Superficial Analyses with -ing Endings ("highlighting," "symbolizing," "reflecting"); (4) Promotional/Advertisement-like Language ("nestled," "vibrant," "breathtaking," "showcasing"); (5) Vague Attributions / Weasel Words ("Experts argue," "Observers have cited"); (6) Outline-like "Challenges and Future Prospects" sections.
- **Language & Grammar:** (7) Overused "AI Vocabulary" ("landscape," "tapestry," "interplay," "underscore," "delve"); (8) Copula Avoidance ("serves as," "boasts," "features" instead of "is/are"); (9) Negative Parallelisms / Tailing Negations ("It's not just...it's..."); (10) Rule of Three Overuse; (11) Elegant Variation (synonym cycling); (12) False Ranges ("from X to Y"); (13) Passive Voice / Subjectless Fragments.
- **Style:** (14) **"Em Dashes: Cut Them" — "no em dashes (—) or en dashes (–)" in final output**; (15) Overuse of Boldface; (16) Inline-Header Vertical Lists; (17) Title Case in Headings; (18) Emojis; (19) Curly Quotation Marks.
- **Communication:** (20) Collaborative Artifacts ("I hope this helps," "Let me know"); (21) Knowledge-Cutoff Disclaimers / Speculative Gap-Filling; (22) Sycophantic/Servile Tone.
- **Filler & Hedging:** (23) Filler Phrases ("Due to the fact that," "In order to"); (24) Excessive Hedging ("could potentially possibly"); (25) Generic Positive Conclusions; (26) Hyphenated Word-Pair Overuse ("cross-functional," "data-driven"); (27) Persuasive Authority Tropes ("The real question is," "at its core," "what really matters"); (28) Signposting ("Let's dive in," "here's what you need to know"); (29) Fragmented Headers; (30) Diff-Anchored Writing (narrating changes vs describing current state); (31) Manufactured Punchlines / Staccato Drama; (32) Aphorism Formulas ("X is the Y of Z"); (33) Conversational Rhetorical Openers ("Honestly?", "Look," "Here's the thing").

**Its process (verbatim intent):** three-step — (a) identify every pattern instance; (b) write a draft that reads naturally, varies sentence length, uses simple constructions; (c) **ask "What makes this obviously AI?" then revise to a final version with zero dashes.** Deliverables: draft rewrite + "still-AI" bullets + final rewrite + optional change summary.

**Two clever bits worth stealing:**
- **False-positives-to-avoid list** (do NOT flag): isolated perfect grammar, single transition word, one short sentence, curly quotes if auto-corrected, quoted material, unsourced claims alone, "honestly/look" *mid*-sentence.
- **"Preserve human signals":** specific hard-to-invent detail, mixed feelings, dated references, defensible editorial choices, varied sentence length, genuine asides, **pre-November-2022 dates**. Also a register caveat: for encyclopedic/technical/legal text, "neutral and plain *is* the correct human voice" — don't inject personality there.

---

### 2. `jalaalrd/anti-ai-slop-writing` — the most complete portable directive
Source: https://github.com/jalaalrd/anti-ai-slop-writing (SKILL.md + references/banned-words.md). Works across Claude Code, Codex, Cursor, Gemini CLI + others.

**Structural rules (verbatim, condensed):**
- **No Rule of Three.** "AI defaults to threes. Break it. Use two, four, one, five."
- **No uniform sentence length.** "No three consecutive sentences of the same length. Ever... This is the single most measurable AI detection signal."
- **No parataxis.** "Parataxis is the AI default: short sentence. Then another. Then another... Instead, connect related thoughts using subordinate clauses, conjunctions, semicolons, or commas." (Best articulation of this tell I found.)
- **No hedging seesaw.** "Pick a side. State it plainly."
- **No identical paragraph structure.** "AI follows: topic sentence → explanation → example → transition. Break it."
- **No "As [role], I..." openers.** "Real people just say the thing without announcing credentials."
- **No passive construction.** "AI defaults to passive to sound measured; it sounds dead instead."
- **Let paragraphs end abruptly.** "Not every paragraph needs a summary or transition."

**Punctuation rules (verbatim, note the *rates*):**
- **Em dashes: Maximum ONE per 500 words.** "The single most cited AI tell in existence."
- **Exclamation marks: Maximum one per 1,000 words.**
- **Ellipses: Only when genuinely trailing off. Never as transition. Max one per piece.**
- **Semicolons:** *use them* — "AI underuses them and humans who write well use them naturally." (Note: directly contradicts `humanize-prose`, which bans semicolons for detector reasons — see §8.)

**11-point self-check (verbatim):** 1. banned words? 2. three consecutive same-length sentences? 3. parataxis (3+ short declaratives in a row)? 4. grouped in threes? 5. hedging instead of committing? 6. >1 em dash? 7. passive? 8. every paragraph ends w/ a transition? 9. fabricated specifics? 10. could any AI have written this for any person? 11. sounds like ChatGPT? → rewrite. Final meta-rule: **"Apply all rules silently. Never mention them."**

**Banned vocabulary (verbatim list):** delve/delves/delving, tapestry, landscape (figurative), testament, vibrant, pivotal, crucial, intricate/intricacies, meticulous(ly), bolster(ed), garner(ed), underscore(s), interplay, multifaceted, nuanced (as filler), foster(ing), leverage (verb), utilize, commence, facilitate, encompass(ing), paramount, groundbreaking, cutting-edge, game-changing/game-changer, transformative, revolutionize, seamless(ly), robust (outside engineering), comprehensive (of own output), endeavor, aforementioned, harnessing, spearheading, navigating (figurative), showcasing, highlighting, emphasizing, enhancing, unprecedented, remarkable, stunning, profound, epic (non-literal), in essence, thought leader(ship), synergy/synergies, pain points, value add/value proposition, moving forward, touch base/circle back, rest assured, it goes without saying.

**Banned phrases (verbatim):** "In today's [adj] [noun]...", "It's worth noting that...", "It's important to note that...", "Let's dive in/deeper/delve into", "At its core...", "In the realm of...", "When it comes to...", "A testament to...", "Not just X, but Y", "It's not just about X — it's about Y", "This is where X comes in", "Whether you're a [X] or a [Y]...", "From X to Y" (range opener), "At the end of the day...", "The bottom line is...", "Here's the thing/deal...", "Without further ado...", "In a nutshell...", "Buckle up", "Take it to the next level", "Unlock the power of...", "Empower(ing)", "Elevate your...", "Streamline your...", "Supercharge your...", "Bridge the gap", "Move the needle", "In conclusion", "Overall," (para starter), "Firstly... Secondly... Thirdly...", "I hope this helps", "I hope this email finds you well", "As per my last email", "Please don't hesitate to reach out".

**Banned openers (verbatim):** "Certainly," "Absolutely," "Sure," "Great question!", "That's a great point!", "I'd be happy to...", "As an AI...", "As a language model...", "However, it's important to...", "Moreover," "Furthermore," "Additionally," "Interestingly," "Notably," "Importantly," "Indeed,".

**UNIQUE — Model-specific first-word tells (verbatim, "avoid starting responses with these"):**
- ChatGPT: "as," "yes," "sure," "here," "in," "to," "creating," "certainly," "title," "the"
- **Claude: "in," "from," "this," "how," "yes," "title," "according," "the," "based," "here"**
- Grok: "step," "introduction," "yes," "creating," "to," "title," "in," "certainly"
- Gemini: "my," "creating," "while," "here," "yes," "this," "the"
- DeepSeek: "based," "yes," "step," "comprehensive," "here," "to," "creating," "title," "certainly"

**UNIQUE — Era-tagged AI vocabulary:** GPT-4 era (2023–mid-2024): additionally, boasts, bolstered, crucial, delve, emphasizing, enduring, garner, intricate, interplay, key, landscape, meticulous, pivotal, underscore, tapestry, testament, valuable, vibrant. GPT-4o era (mid-2024–mid-2025): align with, bolstered, crucial, emphasizing, enhance, enduring, fostering, highlighting, pivotal, showcasing, underscore, vibrant. GPT-5 era (mid-2025+): emphasizing, enhance, highlighting, showcasing. (Sources it cites: CMU 2025, Wikipedia, Buffer 52M-post analysis.)

---

### 3. `NousResearch/autonovel/ANTI-SLOP.md` — best theory + tiered banlist + tone tables
Source: https://github.com/NousResearch/autonovel/blob/master/ANTI-SLOP.md

Tiered banlist (each with a plain replacement column):
- **Tier 1 (kill on sight):** delve→dig into; utilize→use; leverage(v)→use; facilitate→help/enable; elucidate→explain; embark→start; endeavor→try; encompass→include; multifaceted→complex; tapestry→(describe the actual thing); testament→shows/proves; paradigm→model; synergy→(delete & restart); holistic→whole; catalyze→trigger; juxtapose→compare; nuanced(filler)→cut it; realm→area; landscape(metaphor)→field/space; myriad→many; plethora→many.
- **Tier 2 (suspicious in clusters — "three in one paragraph = rewrite"):** robust, comprehensive, seamless(ly), cutting-edge, innovative, streamline, empower, foster, enhance, elevate, optimize, scalable, pivotal, intricate, profound, resonate, underscore, harness, navigate(metaphor), cultivate, bolster, galvanize, cornerstone, game-changer.
- **Tier 3 (filler phrases — delete all):** "It's worth noting that", "Importantly/Notably/Interestingly", "Let's dive into/explore", "In this section, we will", "As we can see", "As mentioned earlier", "In conclusion", "To summarize", "Furthermore/Moreover/Additionally", "In today's [fast-paced/digital/modern] world", "At the end of the day", "It goes without saying", "Without further ado", "When it comes to", "In the realm of", "One might argue that", "It could be suggested that", "This begs the question", "A [comprehensive/holistic/nuanced] approach to", and **"Not just X, but Y" — labelled "the #1 LLM rhetorical crutch."**

Structural patterns (verbatim names): **The "topic sentence" machine** (topic→elaboration→example→wrap-up, every paragraph); **List abuse** (esp. lists of exactly 3 or 5 items — "LLMs gravitate to these counts"); **Symmetry addiction** ("Real writing is lumpy"); **The hedge parade** ("can/may/might/could potentially"); **Transition word addiction** (scan paragraph openings for However/Furthermore/Additionally/Moreover/Consequently/Nevertheless chains); **the "not just X, but Y" construction** ("appears in nearly every model's top trigram lists per slop-forensics"); **Em dash overload** ("One or two per page is fine. Five per paragraph is a tell"); **Sycophantic openings / "glazing"**; **the false-depth pattern** (restate problem in fancier words → list obvious considerations → vague call to action).

**UNIQUE — detection-signal theory (what detectors actually measure):**
- *Statistical:* **Low perplexity** ("perplexity < 50 flags synthetic"); **Low burstiness** (uniform sentence lengths — coefficient of variation of sentence length); **Uniform entropy** (constant information density); token-probability alignment.
- *Vocabulary:* slop-word frequency (60% of EQ-Bench composite), low MATTR vocabulary diversity, trigram overrepresentation (15% of slop score).
- *Structural:* consistent paragraph template, list-heavy formatting, balanced section lengths, opening/closing formulae, missing personal markers.
- *Pangram specifically:* deep-learning classifier on ~1M docs (not perplexity heuristics); tokenizes → embeds → classifies human/AI/AI-assisted → highlights phrases by how-much-more-common in AI output.
- *Limitations (honest):* all detectors have non-trivial false positives; <100-word texts unreliable; newer models harder; **non-native English writers over-flagged**; paraphrased AI text much harder; heavy LLM users spot AI ~90%, tools do worse.

**UNIQUE — tone-by-context DO/DON'T tables** for Academic paper, Blog post, README, Notebook/tutorial. E.g. README DO: `pip install thing && thing run` / code example in first 10 lines; DON'T: "To get started with this powerful tool..." / "leverages cutting-edge Python features." Notebook DO: "Here's the weird part —" / leave mistakes visible; DON'T: "Interestingly, the results deviate from our initial hypothesis."

**The "smell test" (verbatim):** read aloud (person or press release?); would you be embarrassed if asked "did AI write this?"; **"Does it say anything specific? Or could you swap the topic and the text would still work? Specificity is the antidote to slop."**; **"Is there a single surprising sentence? Human writing surprises. Slop never does."**

---

### 4. `stephenturner/skill-deslop` — 10 rules + 50-point rubric (scientific + blog)
Source: https://github.com/stephenturner/skill-deslop (SKILL.md + references/{phrases,structures,tropes,examples}.md). Sources tropes.fyi.

**10 core rules (verbatim headings):** 1. Cut filler phrases; 2. Break formulaic structures (binary contrasts "Not X. Y.", negative listings "Not a X. Not a Y. A Z.", dramatic fragmentation "Speed. That's it. That's the tradeoff.", self-posed rhetorical questions "The result? Devastating.", anaphora/tricolon abuse); 3. Eliminate AI tropes; 4. **Use active voice with human subjects** ("The complaint becomes a fix" is wrong; "The team fixed it" is right); 5. Be specific (no vague declaratives, no lazy extremes "every/always/never", no vague attributions — "If you cannot name the expert, you do not have a source"); 6. Match register to context (blog: "You" beats "People"; science: keep formality, use "we", cite specific authors not "researchers have shown"); 7. Vary rhythm ("Two items beat three... No em dashes"); 8. Trust readers ("No fractal summaries — telling the reader what you're about to say, saying it, then summarizing"); 9. Watch formatting tells (no bold-first bullets, no unicode arrows, no em dashes, no "Despite these challenges..."); 10. Do not dilute ("One point per section... Do not stack historical analogies for false authority").

**UNIQUE — 5-dimension × 10-point rubric (verbatim), "Below 35/50: revise":**
| Dimension | Question |
|---|---|
| Directness | Statements or announcements? |
| Rhythm | Varied or metronomic? |
| Trust | Respects reader intelligence? |
| Authenticity | Sounds like a specific human wrote it? |
| Density | Anything cuttable? |

**Its `tropes.md` catalog** adds sharply-named heuristics (from tropes.fyi):
- **"Quietly" and Other Magic Adverbs** — AI reaches for "quietly / deeply / fundamentally / remarkably / arguably" to make mundane descriptions feel significant.
- **The "Serves As" Dodge** — copula avoidance; explicitly attributes it to the repetition penalty pushing toward fancier constructions.
- **Negative Parallelism** ("It's not X — it's Y") — "The single most commonly identified AI writing tell... One in a piece can be effective; ten in a blog post is a genuine insult to the reader. Before LLMs, people simply did not write like this at scale." Variants: causal ("not because X, but because Y"), em-dash dismissal ("X — not Y"), cross-sentence reframe ("The question isn't X. The question is Y.").
- **"Not X. Not Y. Just Z."** (dramatic countdown); **"The X? A Y."** (self-posed rhetorical Q answered immediately); **Anaphora Abuse**; **Tricolon Abuse** ("A single tricolon is elegant; three back-to-back are a pattern-recognition failure"); **Superficial Analyses** (trailing "-ing" significance phrases); **False Ranges** ("from X to Y" where nothing meaningful is between — "what's in between???? Nothing!").

---

### 5. `aplaceforallmystuff/the-antislop` — numeric point-scored risk levels
Source: https://github.com/aplaceforallmystuff/the-antislop

Same tell families, but its distinctive contribution is an explicit **numeric scoring table + risk levels**:
| Pattern Type | Points |
|---|---|
| Tier 1 phrase | +3 |
| Tier 2 (repeated) | +2 |
| Tier 3 cluster (3+) | +2 |
| Failed "horoscope test" | +5 |
| Staccato fragments | +4 |
| Sentence uniformity | +3 |

Risk levels: 0-5 low, 6-12 medium, **13+ high**. Editor-mode workflow: apply fixes via Edit tool → report before/after → remove Tier-1 phrases first → break up staccato fragments → vary sentence lengths. Note the **"horoscope test"** (would this apply to anything? = failed) as a named heuristic, and **"staccato fragment spam = 3+ consecutive short declarative sentences."**

---

### 6. `conorbronsdon/avoid-ai-writing` — density-threshold tiers + P0/P1/P2 severity (2.1k★)
Source: https://github.com/conorbronsdon/avoid-ai-writing

Distinctive **3-tier vocabulary system by *action*:**
- **Tier 1 (Always Replace):** delve, leverage, landscape, tapestry, realm, paradigm, embark, beacon, testament to, robust, comprehensive, cutting-edge, seamless, game-changer, utilize, watershed moment, thriving, deep dive, unpack, holistic, actionable, impactful, thought leader, best practices, synergy.
- **Tier 2 (Flag in clusters of 2+):** harness, navigate, foster, elevate, unleash, streamline, empower, bolster, spearhead, resonate, revolutionize, facilitate, nuanced, crucial, ecosystem, myriad, plethora, encompass, catalyze, reimagine, galvanize, cultivate, illuminate.
- **Tier 3 (Flag at 3%+ density):** significant, innovative, effective, dynamic, scalable, compelling, unprecedented, exceptional, remarkable, sophisticated, world-class, state-of-the-art. (The **density-percentage threshold** is the clever bit — accepts that any single instance is fine.)

**3 operating modes:** Rewrite (default: flag → rewrite → diff → second-pass audit), Detect (flag + severity only), Edit (minimal in-place file changes + verification).
**Severity tiers:** **P0** credibility killers (cutoff disclaimers, chatbot artifacts, vague attributions); **P1** obvious AI smell (word-list violations, template phrases, bold overuse, social closers); **P2** stylistic polish (generic conclusions, uniform paragraph length, copula avoidance).
Also flags **reasoning leakage** ("Let me think step by step", "Step 1:"), **infomercial hooks** ("The catch?", "The kicker?", "Plot twist:"), and **unfilled placeholders** ("[Your Name]", "[INSERT URL]", "2025-XX-XX").
**Key principle (verbatim):** *"Signals, not proof. Worth acting on; not worth ruining someone's day over."*

---

### 7. `realrossmanngroup/no_ai_slop_writing_rules` — corpus-derived VOICE MATCHING
Source: https://github.com/realrossmanngroup/no_ai_slop_writing_rules (skills `no-ai-slop` + `rossmann-voice`).

`no-ai-slop` is a standard banlist-plus-worked-examples skill, but its 24 numbered rules are stated with **before/WRONG → after/RIGHT pairs**, and every fix follows one meta-principle: *"replace the vague claim with a specific, checkable fact."* Examples: Rule 4 (no intensifiers) — "significantly higher than the cost of the part" → "They charged $1,200 for a repair that needed a $5 chip." Rule 16 (no dramatic headings) — "The Hidden Cost of Planned Obsolescence" → "Economic impact of shortened product lifespans." Its 10-step self-check leads with "Search for the emdash character. Remove every one."

**`rossmann-voice` is the standout, unique-in-the-corpus approach: a data-driven voice fingerprint** built from 513,683 words (5,632 entries, 2014–2026). Instead of "sound generically human," it gives **measured statistical targets**:
- Ground every claim in a testable number (corpus: 32.0 dollar amounts / 10k words ≈ 1 verifiable reference per 200 words).
- **Sentence-length variance target:** mean 18.34, median 15, std dev 15.27, p10=4, p90=36; 10.8% of sentences are fragments <5 words. Rule: "at least one sentence under 10 words and one over 20 words per 3-paragraph block."
- **Contraction rate 83.6%** ("does not four times in a paragraph is drift").
- Paragraph length avg 2.1 sentences.
- Question-to-statement ratio 4.3% (2.2% mature).
- **Voice-drift prevention** section: names the failure ("LLMs revert to 'average internet tone' over long outputs") and gives mid-piece correction steps.

The general lesson (topic-independent): the best voice-matching is *measured against a real corpus*, producing checkable numeric targets, not vibes. This directly generalizes the "voice calibration" feature that `blader/humanizer` and `jalaalrd` gesture at but don't quantify.

---

### 8. `celestialdust/humanize-prose` — DETECTOR-CALIBRATED, empirically derived (most sophisticated)
Source: https://github.com/celestialdust/humanize-prose (SKILL.md + scripts/ai_tell_scan.py + references/trajectory.md)

Distilled from an **8-draft iteration of one essay repeatedly graded against GPTZero** (documented trajectory: 75% → 68% → **21%** → 56% → 66%). Its insights contradict the naive banlist approach in valuable ways:

**Core insight (verbatim):** *"The enemy is lexical-syntactic smoothness, not length or topic."* An essay scored 21% AI; the *same essay lightly refined for tighter phrasing* scored 66% AI. Three corollaries:
1. **Evidence density is human** — proper nouns, dated events, quotes with page citations are the strongest human signals a detector reads.
2. **Cutting beats rewriting** — "Rewriting the same content in tighter phrasing tends to *increase* AI register by smoothing the prose further."
3. **Asymmetry beats polish.**

**The named traps (verbatim, extremely valuable and rarely stated elsewhere):**
- **The refinement trap:** "'Surgical improvements' that feel editorial — tightening phrasing, sharpening word choice, combining related short sentences for smoothness, making parallel structures cleaner — are the exact operations that push prose toward AI register. Copy-editor intuition is often anti-human-register."
- **The more-effort trap:** "Scores do not move monotonically with effort." (75→68→21→56→66.)
- **The rewrite-what's-working trap:** "Once a paragraph reads human, do not edit it — not even to tighten." (In the trajectory, all 4 rewritten paragraphs regressed; the 2 left untouched stayed green.)
- **The chase-the-noise trap:** "A single 10-point movement across one detector run is not signal... Detector variance across runs is ±10–20 points."

**Its find/replace table (verbatim) is stricter than others — bans semicolons too:**
| Pattern | Fix |
|---|---|
| Em-dashes (—) | Replace with periods or parentheses. |
| Semicolons (;) | Split into two sentences. |
| Cleft ("It is X that Y") | "X does Y." |
| Neat tricolons | Cut to two terms. |
| Causal fusion ("A, because B") | Keep them apart. |
| Crisp metaphor verbs | Flatter verbs. |
| Adjective stacks ("soft, flat, childlike, pastel") | Pick two. |
| "illustrates/underscores/demonstrates/highlights" | Plainer verb. |

**2026 vocabulary clusters (verbatim), flag on *co-occurrence density*, not single use:** Abstract verbs (delve, leverage, underscore, streamline, unleash, foster, harness, facilitate); Inflated adjectives (pivotal, robust, seamless, innovative, cutting-edge, multifaceted, comprehensive, holistic); Flowery metaphors (tapestry, landscape, realm, symphony, beacon, journey, ecosystem, fabric); Formal transitions (furthermore, moreover, additionally, notably, in conclusion).

**Ship-readiness checklist (verbatim highlights):** zero em-dashes; zero semicolons; zero furthermore/moreover/additionally/thus/indeed/notably; no paragraph with 2+ abstract verbs / 2+ inflated adjectives; no identical-ending tricolons; paragraph word counts within 2–3× of each other; each paragraph has ≥1 proper noun/date/quote; no two adjacent sentences same length (±3 words).

**UNIQUE — honesty about scope (things others omit entirely):**
- **ESL/detector-bias framing:** cites Stanford HAI (~61% of legit TOEFL essays flagged); reassures the user that a high score often means the *detector* is biased, not their writing; suggests process verification (draft trails, oral defense) as a better bar than a probability number.
- **Watermark caveat:** "does not defeat cryptographic watermarks" — SynthID / C2PA survive paraphrasing; prose humanization only addresses the stylometric (perplexity/burstiness/stylometry) stack.
- Explicitly says it **does not apply to fiction** (already human-register), <300-word text, or heavy-jargon technical writing.

**Programmatic scanner (`ai_tell_scan.py`)** — a working, adaptable Python detector. It computes: em/en-dash + semicolon counts; regex hits for AI-tell phrases, weak analytic verbs, and the 3 vocabulary clusters (per-paragraph, flags 2+ in one paragraph); causal "X, because Y" fusions; "neat tricolons" (`\w+ing, \w+ing, and \w+ing` / `\w+ly, \w+ly, and \w+ly`); sentence-length distribution (min/median/max/stdev, % short/medium/long, flags low burstiness); proper-nouns-per-paragraph (flags 0 = add evidence); paragraph max-to-min word-count ratio (flags >2.5×). Outputs a readiness summary with a priority order: **punctuation > AI-tell phrases > paragraph balance > vocabulary clusters > evidence density > sentence-length distribution.** This is the single most directly reusable *code* artifact found.

---

### 9. `adewale/anti-slop-writing` — eval-driven, with a documented FAILURE MODE
Source: https://github.com/adewale/anti-slop-writing (SKILL.md + evals/ + docs/)

Distinctive for being **eval-harness-driven ("hillclimbing")** rather than hand-authored: held-out/tune split, statistical gating (`score_delta.py --holdout-only`, require ACCEPT), a blinded judge protocol, and a rule that **"Never edit doctrine in response to a holdout failure; write a new tune case instead."** Its authoring discipline (verbatim): *"Do not add broad writing advice without a concrete failure case or before/after example... Do not optimize for sounding wise. Optimize for the next agent producing a better concrete rewrite."*

**The most valuable finding here — a documented failure mode of humanize skills** (`evals/failures/rewrite-reuses-flagged-pattern.md`):
- **The fabrication trap (Pattern A):** When the output format requires a `Concrete rewrite` field and the legitimate fix needs a fact the source didn't supply, **the model invents the fact to fill the slot.** Real example: source said "current coding tools"; the skill's rewrite shipped "Claude Code turned the cover-image generator..." as fact, though the post never named a tool. *"The replacement reads more concrete but is more wrong than the abstract version it replaced."* **Fix added:** a new `ask-author` verdict, and a rule that the rewrite must not name a fact (tool/person/number/mechanism) absent from the source paragraph.
- **The self-defeat trap (Pattern B):** the rewriter *reuses the very pattern it just flagged* — flags "compressed antithesis" then rewrites "That's not incidental. It's the design." into "Portability is the design, not a future feature." (same `X, not Y` shape). **Fix:** a "Rewrite check: passes self-detectors — no X-not-Y cadence" step, and a self-check moved so the model circles back.
- **Doctrine-ambiguity trap (Pattern C):** its "compressed antithesis" definition was ambiguous between "topic was evidenced" and "both sides evidenced"; clarified to require *both sides* of a contrast be evidenced in prior prose.

These are exactly the pitfalls a new humanize skill must design around: **never let a required output field force invention, and always re-scan the rewrite against the same detectors.**

---

### 10. `Byk3y/no-slop` — a prose linter (regex categories) from Wikipedia's guide
Source: https://github.com/Byk3y/no-slop. 13 detection categories: banned vocabulary (40+ words); simple-copula replacement ("serves as/stands as/boasts"); promotional tone; vague attributions ("experts say"); structural formulas (rule-of-three + "not just X but Y"); participle chains ("-ing" filler); elegant variation (synonym swapping); overstating significance ("marks a turning point"); em-dash overuse (>1 per paragraph triggers); collaborative language; knowledge-cutoff disclaimers; formatting excess; missing human habits (contractions, varied length, specifics). All rules derive from **Wikipedia:Signs of AI writing**.

---

### 11. Wikipedia:Signs of AI writing — the upstream authority
Source: https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing (WikiProject AI Cleanup, "based on observations of thousands of AI-generated texts"). This is what most skills above ultimately cite. Categories: **Content** (undue emphasis on significance/legacy — "stands/serves as, testament, vital/significant/crucial/pivotal/key role, underscores/highlights its importance"; canned notability/media coverage; superficial analyses; promotional language — "boasts a, vibrant, rich, profound, nestled, groundbreaking, renowned, diverse array"; vague attributions; outline-like "Challenges and Future Prospects" conclusions). **Language/Grammar** (AI-vocabulary density with the same era lists; copula avoidance; **negative parallelisms** — "Not just X, but also Y", "Not X, but Y", "X rather than Y"; rule of three; elegant variation driven by AI's repetition-penalty code). **Style/Formatting** (title-case headings; boldface overuse; inline-header vertical lists; **em-dash overuse**; unusual tables; curly quotes; skipped heading levels). **Markup** (leftover `contentReference`, `oaicite`, `oai_citation`, `:contentReference` tokens; broken wikitext; invalid DOIs/ISBNs; utm_source params). **Conduct** (canned assurances; "I am an AI language model..." disclaimers; abrupt mid-sentence cut-offs).

---

### 12. Commercial "Humanize AI" / "Undetectable AI" — the RULES behind the marketing
Sources: stealthgpt.ai, thehumanizeai.pro, quillbot.com/blog, walterwrites.ai, decopy.ai. Stripped of marketing, their entire technical claim reduces to two levers detectors use: **Perplexity** (predictability of the next token — low = AI; they inject "unexpected word choices" to raise it) and **Burstiness** (variation in sentence length/complexity — AI is uniform; they restructure to alternate short/long). This *confirms from the vendor side* the two metrics the open-source skills target with the "vary sentence length" and "less-obvious word" rules. They add no novel rule content beyond that; the open-source skills above are far richer.

---

## SYNTHESIS — what to steal, where they agree, where they conflict

**Universal consensus tells (appear in essentially every artifact):**
1. **Em dashes** — the #1 named tell. (Strictest: `blader` & `humanize-prose` = *zero* in final output; moderate: `jalaalrd` = max 1 per 500 words, autonovel = 1–2 per page.)
2. **"Not just X, but Y" / negative parallelism** — near-universally called the #1 *structural* crutch; "Not X. Not Y. Just Z." and "It's not X, it's Y" variants.
3. **"Delve" + the vocab family** — delve, tapestry, landscape, leverage, robust, seamless, pivotal, underscore, harness, foster, utilize, comprehensive, etc.
4. **Rule of three / tricolon abuse** — "use two or four instead."
5. **Uniform sentence length / low burstiness** — "the single most measurable AI detection signal."
6. **Filler transitions** — "It's worth noting", "Furthermore/Moreover/Additionally", "In conclusion".
7. **Copula avoidance** — "serves as / stands as / boasts" instead of "is/are."
8. **Superficial trailing "-ing" analyses** — "highlighting its importance."
9. **Sycophantic openers / chatbot artifacts** — "Great question!", "I hope this helps", "Certainly!".
10. **Vague attributions & vague significance** — "experts argue", "has a significant impact"; fix = name a specific checkable fact.
11. **Formatting tells** — bold-first bullets, title-case headings, emoji-as-bullets, curly quotes, unicode arrows.

**Design ideas worth adopting (the higher-order stuff):**
- **Two-pass self-review** (`blader`, `avoid-ai-writing`): after rewriting, ask "what still makes this obviously AI?" and **re-scan the rewrite against the same detectors** (the `adewale` self-defeat fix).
- **Density/cluster thresholds, not absolute bans** (`avoid-ai-writing` Tier 3 at 3%+, `humanize-prose` "2+ per paragraph", autonovel "3 in one paragraph") — avoids false positives on single legitimate uses.
- **Register-awareness** (`deslop`, autonovel, `blader`): the correct "human voice" for encyclopedic/technical/legal/scientific text is neutral & plain — do NOT inject personality or contractions there. A humanize skill must branch on genre.
- **Specificity as the antidote** (`no-ai-slop`, autonovel, `humanize-prose`): the deepest fix isn't word-swapping, it's anchoring vague claims to a name/number/date/mechanism. "If you cannot name the expert, you do not have a source."
- **Corpus-derived, numeric voice targets** (`rossmann-voice`): the strongest voice-matching uses measured statistics (sentence-length variance, contraction rate, evidence density) rather than a vibe.
- **Rubric scoring** (`deslop` 5-dim×10; `the-antislop` point system; `humanize-prose` GPTZero calibration; `unslop` 8-criterion 32/40) — gives a stop condition.
- **Silent application** (`jalaalrd`): "Apply all rules silently. Never mention them."

**Real conflicts (a new skill must decide):**
- **Semicolons:** `jalaalrd` says *use them* (humans who write well do; AI underuses them). `humanize-prose` says *ban them, split into two sentences* (detector-driven). This is genre/audience dependent: semicolons help human register for a reader but may or may not help a stylometric detector.
- **Detector-passing vs. genuinely-human:** `humanize-prose` is optimized to lower a *detector score* and openly admits over-editing (chasing the score) makes prose worse and that the real fix is authentic content; `deslop`/`blader` optimize for reading well to a *human*. These can diverge — the "refinement trap" shows detector-optimization and copy-editing pull in opposite directions.

**Notable gaps / things they get wrong (useful cautionary notes):**
- Most banlist-only skills **over-ban** — they'll strip "robust" from an engineering doc or "comprehensive" where it's accurate. Only `avoid-ai-writing`, `humanize-prose`, and autonovel handle this with density/cluster thresholds + a false-positive list (`blader`).
- **The fabrication trap** (`adewale`): a rewriter told to "be specific" will *invent* specifics (fake tools, fake anecdotes, fake numbers) to satisfy the instruction — actively harmful. `jalaalrd` and `no-ai-slop` mitigate with explicit "never invent data/quotes/anecdotes; say 'roughly' or flag as hypothetical."
- **The self-defeat trap** (`adewale`): rewrites reproduce the exact cadence they flagged unless a re-scan step is enforced.
- **Watermarks** (`humanize-prose`): no prose edit defeats SynthID/C2PA — worth stating so users don't expect it.
- Chasing detector scores is noisy (±10–20 pts/run) and detectors are biased against ESL and technical writers — a humanize skill should say so rather than treat the score as truth.

---

## Sources
- https://github.com/blader/humanizer
- https://github.com/jalaalrd/anti-ai-slop-writing (SKILL.md + references/banned-words.md)
- https://github.com/NousResearch/autonovel/blob/master/ANTI-SLOP.md
- https://github.com/stephenturner/skill-deslop (SKILL.md + references/tropes.md)
- https://github.com/aplaceforallmystuff/the-antislop
- https://github.com/conorbronsdon/avoid-ai-writing
- https://github.com/realrossmanngroup/no_ai_slop_writing_rules (no-ai-slop + rossmann-voice skills)
- https://github.com/celestialdust/humanize-prose (SKILL.md + scripts/ai_tell_scan.py)
- https://github.com/adewale/anti-slop-writing (SKILL.md + evals/failures/rewrite-reuses-flagged-pattern.md)
- https://github.com/Byk3y/no-slop
- https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
- https://blog.stephenturner.us/p/deslop
- https://github.com/sam-paech/slop-forensics ; https://eqbench.com/slop-score.html ; https://www.pangram.com/ ; https://tropes.fyi (primary data sources cited by the above)
- Commercial: stealthgpt.ai, thehumanizeai.pro, quillbot.com/blog, walterwrites.ai (perplexity/burstiness confirmation only)
- https://www.marketingideas.com/p/the-anti-ai-writing-cheat-sheet (Tom Orbach "Anti-AI writing cheat sheet" — content paywalled; previews "13 patterns + 100+ banned words + copy/paste prompt")
