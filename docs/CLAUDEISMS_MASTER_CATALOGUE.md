# Claudeisms — Master Catalogue

Consolidated from three research passes (detection blogs & stylometry papers · existing
humanize/anti-slop skills · code-comment & docs guidance). Built as source material for a
downstream Claude Skill or Agent that improves text quality.

Raw source reports live alongside this file:
- `CLAUDEISMS_01_blogs_and_detection_guides.md`
- `CLAUDEISMS_02_humanize_skills_and_antislop_tools.md`
- `CLAUDEISMS_03_code_comments_and_docs.md`

**Evidence key:** **[A]** measured/corroborated across many sources · **[B]** widely-cited
folklore, matches experience, unmeasured · **[C]** single-source opinion · **[?]** unverified.

**Master caveat (repeated by every serious source):** no single word or mark proves AI
authorship. These are *probabilistic signals* that only indict in **combination and at density**.
Single-word detection is unreliable and culturally biased against ESL / non-American-English
writers (Stanford: ~61% of human TOEFL essays flagged as AI). A good tool flags clusters, not
lone instances, and states this openly.

---

## 0. Your flagged words — verdicts

| You said | Verdict | Detail |
|---|---|---|
| **em-dashes** | **[A] confirmed — the #1 tell** | Most-cited single marker across all sources. OpenAI shipped a setting to suppress it. Mechanism (per Goedecke): training on digitized ~1900 print books that used ~30% more em-dashes. Note the backlash — many editors call the em-dash "the most human mark" and the panic overblown; it's strong *in density*, weak as a lone signal. |
| **contrastive phrasing** ("not X, it's Y") | **[A] confirmed — the #1 *structural* tell** | Called "negative parallelism." "One in a piece can be effective; ten is an insult to the reader. Before LLMs, people did not write like this at scale." |
| **"seam"** | **[A] CONFIRMED — code-architecture register** *(corrected — first pass was wrong)* | A real term (Feathers, *Working Effectively with Legacy Code*: a "seam" is a place to change behavior without editing in place) that Claude over-reaches to mean *any* interface/boundary/integration point. Invisible to prose-detection blogs because it's software-engineering register, not essay/SEO slop — which is why Pass 1 wrongly dismissed it. **Empirically: Claude used it 238× across the transcripts, 2.5× the user's own rate, in ~12% of sessions** (§9A). ("seamless" is *also* a separate prose tell, but you meant the code word, and you were right.) |
| **"cutover"** | **[A] CONFIRMED — code-architecture register** *(corrected — first pass was wrong)* | A systems/migration term (the moment you switch from the old system to the new). Same register as "seam" — a real word Claude reaches for by default. **Empirically: 17× in the transcripts, 4.4× the user's rate** (§9A). It is **not** a mis-transcription of "cutting-edge"; that dismissal failed for the same corpus-blindness reason. |
| **"bites"** | **[?] still unverified — left open** | No corroboration in any register. Possibly a dictation artifact, or a code-register word not yet pinned. Held open rather than dismissed, given the two misses above. |

---

## 1. Punctuation tells [A]

- **Em-dashes (—/–).** Cut aggressively. Strictest existing skills demand *zero* in final output; moderate ones cap at **1 per 500 words** / 1–2 per page. Replace with commas, parentheses, or a period.
- **Curly/smart quotes** (' ' " ") where a human typing raw would produce straight quotes.
- **Semicolon habit** — joining clauses with semicolons more than modern prose does (human semicolon use has roughly halved since 2000). ⚠️ **Conflict, see §11.**
- **Perfectly-formed ellipses** in formal text; ellipsis used as a transition.
- **Bulleted/listified everything** — bullets for ideas that aren't lists.

## 2. Lexical tells — the vocabulary banlist [A] core / [B] tail

**Hardest evidence (Kobak et al., ~15M PubMed abstracts):** frequency vs. pre-ChatGPT baseline —
**delves 28×**, **underscores 13.8×**, **showcasing 10.7×**; ~900 words spiked post-Nov-2022,
overwhelmingly *stylistic* not content words. Full list: `github.com/berenslab/llm-excess-vocab`.

**Tier the banlist by action (best practice, from `avoid-ai-writing` / `humanize-prose` / autonovel) — do NOT hard-ban single instances:**

- **Tier 1 — almost always replace:** delve/delving, tapestry, landscape (figurative), realm,
  testament (to), leverage (v), utilize, harness, underscore, showcasing, seamless, robust
  (outside engineering), pivotal, intricate, meticulous, comprehensive (of one's own output),
  cutting-edge, game-changer, synergy, holistic, paradigm, embark, endeavor, myriad, plethora,
  facilitate, elucidate.
- **Tier 2 — flag only in clusters (≥2 in a paragraph):** foster, bolster, garner, navigate
  (figurative), elevate, unleash, streamline, empower, spearhead, resonate, revolutionize,
  nuanced (filler), crucial, ecosystem, cultivate, illuminate, catalyze, galvanize, transformative,
  multifaceted, profound, vibrant, bustling.
- **Tier 3 — flag only at density (≈3%+ of words):** significant, innovative, effective, dynamic,
  scalable, compelling, unprecedented, exceptional, remarkable, sophisticated, world-class,
  state-of-the-art.

**Cliché phrases:** "a testament to", "navigating the landscape of", "the transformative power
of", "plays a pivotal/crucial role in", "underscores the importance of", "in today's fast-paced
world", "in the ever-evolving landscape of", "seamless integration", "rich tapestry", "treasure
trove", "unlock the potential", "harness the power of", "shed light on", "embark on a journey",
"a myriad of", "in the realm of", "at its core", "when it comes to".

**Promotional/heritage cluster (Wikipedia-flagged):** "nestled in the heart of", "boasts a range
of", "rich cultural heritage", "breathtaking", "must-visit", "vibrant community", "enduring
legacy".

## 3. Contrastive / negative-parallelism tells [A]

The #1 structural crutch. All variants:
- "It's not just X — it's Y" · "Not X, but Y" · "This isn't about X. It's about Y."
- "X rather than Y" · "Not only X, but also Y"
- "No X. No Y. Just Z." (dramatic countdown)
- "The question isn't X. It's Y." (cross-sentence reframe)
- Em-dash dismissal: "X — not Y." · Causal: "not because X, but because Y."

**Fix:** state both things directly without the negation scaffold, or just assert the point.

## 4. Rhetorical-structure tells [A]/[B]

- **Rule of three / tricolon abuse** — three items with suspiciously even rhythm. "Use two or four."
- **"Firstly / Secondly / Finally"** enumerated signposting.
- **"In conclusion" / summary bookends** — restating what was just said ("fractal summaries").
- **Rhetorical question as section opener / self-Q&A** — "The result? Devastating."
- **"Let's dive in / unpack this / explore"** openers.
- **Framing sandwich** — restate the question, deliver, restate the conclusion.
- **Trailing "-ing" significance clauses** — "…marking a pivotal moment", "…underscoring its importance."
- **Aphoristic pseudo-profound closer** — "At the end of the day, we are all human."
- **"Despite X, faces challenges… Future initiatives could…"** outline formula.

## 5. Hedging & filler ("throat-clearing") [A]

Delete-on-sight; announcements that a point is coming, containing no content:
"It's important/worth noting that", "It could be argued that", "Generally/broadly speaking",
"Here's the thing", "The reality is", "In today's fast-paced world", "That being said", "When it
comes to", "It goes without saying", "aims to explore". **Fix:** delete the announcement and lead
with the point.

## 6. Tone tells [A]/[B]

- **Sycophancy — the flagship *Claude-specific* tell.** "You're absolutely right!" (documented 12×
  in one session, including when the user was wrong; rooted in RLHF). "Great question!", "What a
  thoughtful question!"
- **Performative enthusiasm:** exciting, incredible, powerful, amazing, remarkable.
- **Relentless positivity / uniformly polished balance** — every paragraph equally polished.
- **Servile closers:** "Hope this helps!", "Let me know if you'd like me to go deeper!", "Certainly!"
- **Chatbot residue:** "As an AI language model…", "I hope this email finds you well."
- **Faux-candor / performative honesty** [B] — signalling "now I'm being real with you", which is
  itself the tell: "Let me be honest", "To be honest", "Honestly," / "Honestly?", "I'll be honest
  (with you)", "In all honesty", "The honest truth is", "Frankly". Also the framing form **"The
  honest [answer/version/name] is/of…"** (this shades into the code-architecture register — see §9A
  "the honest/accurate name"). Attested as a conversational-rhetorical-opener tell in existing
  anti-slop skills (`blader/humanizer` #33). **Fix:** just say the thing — the candor should be in
  the content, not announced.

## 7. Formatting tells [A]/[B]

- **Boldface overuse** — mechanically bolding every key term.
- **"Bold lead-in: explanation" bullets** — near-signature of ChatGPT listicles.
- **Title Case In Headings** where sentence case is normal.
- **Emoji as section headers / in prose.**
- **Markdown bleeding** where it won't render (raw wikitext, plain email).
- **Leftover tokens:** `contentReference`, `oaicite`, `turn0search0`, `utm_source` in URLs; unfilled
  placeholders `[Your Name]`, `{client_name}`.

## 8. Statistical / structural tells [A] — what detectors actually key on (survives paraphrasing)

- **Low burstiness** — uniform sentence & paragraph length. Called "the single most measurable AI
  detection signal." Humans mix long and short. (`rossmann-voice` measured target from a 513k-word
  human corpus: mean 18.3 words, std-dev 15.3, ~11% fragments <5 words; rule of thumb: no three
  consecutive same-length sentences; ≥1 sentence <10 words and ≥1 >20 per 3-paragraph block.)
- **Low perplexity** — too-predictable word choice (< ~50 flags synthetic).
- **Parataxis** — "Short sentence. Then another. Then another." Connect with subordinate clauses.
- **Abstract nouns over concrete verbs** — "The implementation of a strategy can lead to improved
  outcomes" vs. "Do this and you'll usually see better results."
- **Copula avoidance** — "serves as / stands as / boasts" instead of "is/are."
- **Elegant variation** — cycling synonyms to dodge repetition (driven by the repetition penalty),
  where a human would just repeat the term.
- **Vagueness / no specifics** — no names, numbers, dates, lived detail.
- **Uniform sourceless authority** — "Studies show…", "Experts argue…" with no citation;
  fabricated statistics.

## 9. Code-specific tells (comments, docstrings, commits, PRs)

The distinct fingerprint in generated *code* — highest-priority for your stated meta-problem.

- **Redundant comments restating code:** `i += 1  # increment i`. → delete.
- **Ceremonial docstrings** that re-state the signature/types. → delete or keep only units,
  invariants, side effects, raised exceptions.
- **WHAT instead of WHY** — the enduring rule. Comment motive/trade-off/constraint, never operation.
- **Multi-line narrative comments** — a paragraph over a 3-line function. LLMs "think out loud in
  comments" because "producing tokens is how it reasons"; that scaffolding must not survive.
- **Change-narration / history comments:** `# NEW:`, `# Updated logic`, `# was previously…` — the
  primary comment-rot vector. History lives in git.
- **Decorative banners** — `# ==== HELPERS ====`.
- **Teaching-the-language comments** — "A dictionary is key-value pairs."
- **Emoji / "Note:" / "Important:" / exclamation spam** in comments.
- **Over-templated docstrings** — full Args/Returns/Raises on trivial helpers; mixed styles in one file.
- **PR/commit template:** "This PR does the following:" + bulleted per-file diff narration + filler
  bullets ("improves readability", "ensures backward compatibility").

**Verbatim rule text to reuse (highest-value output):**
- Your own `senior-mle-reviewer` pithy standard: *"No comment over three lines. No comment that
  narrates history… Comments only for the why… never restating what the code plainly says. No
  wasted words."*
- Anthropic official default: *"Don't add docstrings, comments, or type annotations to code you
  didn't change. Only add comments where the logic isn't self-evident."*
- Commit/PR: *"concise (1–2 sentences)… focuses on the why rather than the what"; Summary = 1–3
  bullets + a Test plan of what was actually run.*

**Why it's hard & what works (your meta-problem, confirmed):** in-line restraint is unreliable
because commenting is generation scaffolding and training bias favors tutorial register; explicit
CLAUDE.md rules get dropped. Reliable fixes: **(1)** a *hard numeric* standing rule ("no comment
over three lines" beats "be concise" — a number can't be rationalized away); **(2)** a *separate
delete-first review pass* (what your `comment-analyzer` agent already does — generate, then sweep
and delete).

---

## 9A. Code-architecture / systems register — the category the prose research missed

**Why this section exists (a documented research failure):** Passes 1–3 catalogued *prose* tells
(marketing/essay/SEO slop) and *comment-quality* tells. None searched Claude's **software-
architecture explanatory register** — the vocabulary it defaults to when explaining code design,
migrations, and refactors. That register is invisible to AI-detection blogs, so "seam" and
"cutover" were wrongly dismissed as "not attested." They are real, frequent Claudeisms; the corpus
was just blind to them. This is the single most relevant category to the user's stated goal
(improving the text/comments/docs Claude writes *for codebases*).

**Evidence: [A] — empirically measured.** Mined **416 local Claude Code sessions** (710k words of
Claude prose vs 368k words of the *user's own* prose about the same codebases). Method: rate of
each term in Claude's output ÷ its rate in the user's writing — holding the *domain* constant
(same projects, same jargon) isolates the *register* (Claude's phrasing habit). **ratio > 1 = Claude
over-uses it relative to the human working on the same code.** Script + raw findings committed
beside this file (`mine_claude_code_register.py`, `claude_code_register_findings.json`).

**Critical nuance — these are Tier-2, not Tier-1.** Most are *legitimate, useful* engineering
terms (a "seam" is a genuine design concept; "hot path" is precise). The tell is **over-reach and
density** — reaching for the structural metaphor by default when a plain word ("interface",
"boundary", "the switch-over") would do, and doing it repeatedly. Flag in clusters, never hard-ban
— especially here, where the surrounding context is code and some uses are correct.

**Measured — your flagged words and the seeds, ranked by over-representation (× vs user):**

| term / phrase | Claude uses | ratio ×user | in % of sessions |
|---|---|---|---|
| "want me to (a…/b…)?" (offer-closer) | 180 | **46.7×** | — |
| tighten | 50 | 13.0× | 7% |
| converge(s) | 62 | 10.7× | 5% |
| "the honest …" | 54 | 9.3× | — |
| "bottom line" / "net:" | 65 | ~5× | — |
| stale | 317 | 6.6× | 18% |
| honest(ly) | 157 | 5.4× | 8% |
| the live (consumer/…) | 131 | 4.5× | — |
| **cutover** | 17 | **4.4×** | — |
| fold (into) | 161 | 4.2× | 10% |
| plumb | 54 | 4.0× | 6% |
| cleanly | 318 | 3.5× | 20% |
| genuinely | 285 | 3.1× | **26%** |
| load-bearing | 101 | 2.8× | 13% |
| **seam** | 238 | **2.5×** | 12% |
| collapse | 153 | 2.5× | 11% |
| blast radius | 18 | 2.3× | — |
| surface (n./v.) | 428 | 2.0× | **33%** |
| wire (up/in) | 448 | 1.9× | 26% |
| canonical | 204 | 1.5× | 19% |
| first-class / holistic | 27 | ∞ (user: 0) | — |
| "you're (absolutely) right" | 20 | ∞ (sycophancy) | — |

So **"seam" and "cutover" are confirmed** — Claude reaches for them 2.5× and 4.4× more than the
human on the same projects; "seam" surfaces in ~1 of every 8 sessions. Your instinct was right.

**Newly discovered this pass** (curated from ratio-ranked words Claude over-uses vs the user;
these were *not* in the seed list): **confirmed/confirms/confirming** (886+, ~21×; Claude narrates
its own verification), **empirically** (∞), **the picture / full picture** (27×), **wording**
(22×), **trust/trusted** (19×), **intact** ("leaves X intact", 18×), **trap** ("the X trap", 16×),
**harmless / cosmetic** (risk-triage vocab, ~12–17×), **purely** ("purely mechanical/cosmetic",
14×), **couple** ("a couple of things", 14×), **defensible** (11×), **lanes** (11×), **spine**
(11×), **slightly / subtle / literally** (~8×), **caveat** (6×), **neutral** (6×), **headline**
("the headline is…", 7×), **composes / inherits** (~6×). Discourse openers: **"Let me [verb]…"** is
pervasive (check 772 · read 712 · verify 605 · confirm 387 · look 216) — the single most frequent
narration tic; and the **"Want me to (a)… or (b)…?"** offer-closer (46.7×).

**Honest negatives** (seeds that did *not* over-index against this user — drop or demote): crisp/
crisply (0.4× — the user uses it *more*), envelope (0.8×), leverage (0.9×), orthogonal (0.9×),
concretely (1.0×); thread/upstream/footprint/downstream only mildly (~1.2–1.4×). These are either
shared domain vocabulary or this user's own register, not Claude tells here.

**Caveats on the method (stated plainly, having over-claimed once already):** the baseline is *this
user's* prose, not general English — a strong control for domain but a small, noisier sample (some
of it is Claude text the user pasted). The raw discovery list was polluted by (a) background-task/
harness words (notification, poll, waiting, background, completion), (b) security-review vocab
(source/sink, attacker, allowlist), and (c) *this very session's* research words (wikipedia,
vocabulary, clusters, verdicts, tier) — all hand-filtered out. Treat ratios as directional, not
exact; the *ranking* is robust, the decimal isn't.

**Structural-metaphor nouns:** seam · surface (n., "the API surface / public surface / surface
area") · home / **canonical home** ("X lives in Y, the canonical home") · blast radius · source of
truth / single source of truth · hot path · escape hatch · guardrail · **load-bearing** ("a
load-bearing assumption/comment") · envelope ("the `{…, recordings}` envelope") · footprint ·
seam (again — it recurs).

**Move/change verbs:** cutover (n./v.) · repoint · wire up / wire in / wiring · thread (through) /
plumb ("thread the value down") · land ("once this lands", "land it on main") · converge /
converges ("converges the naming") · collapse / fold (into) · carve out · rip out · paper over ·
bake in / baked in · tighten ("tighten the phrasing") · entrench ("entrenching a misnomer").

**Framing adjectives / adverbs:** canonical · **honest / accurate name** · **mild misnomer** ·
first-class ("a first-class outcome") · **genuinely** ("genuinely different", "genuinely distinct")
· crisp / crisply · gnarly / hairy (complex code) · spurious · stale · downstream / upstream (heavy
use) · "in exactly one place" / "one X in one home".

**Discourse tics in technical explanation:** "Concretely:" · "Net:" / "Bottom line:" · "The honest
answer is…" · "the live consumer" · YAGNI / "YAGNI trim" · "the right amount of complexity is the
minimum needed" (Anthropic's own phrasing) · staccato decision framing ("Decision you need to
make:", "Want me to (a)… or (b)…?").

**Reproducing / extending this:** `mine_claude_code_register.py` (committed beside this file) globs
`~/.claude/projects/**/*.jsonl`, extracts assistant vs user prose (stripping code fences and
harness-injected blocks), and ranks terms by the user-baseline ratio. Re-run with `uv run --script`
to refresh as the corpus grows, or add candidate terms to its `SINGLE`/`PHRASE` dicts. A stronger
future baseline would be external human engineering prose (curated commit messages, design docs,
RFCs) rather than one user — that would turn the directional ratios here into absolute density
thresholds. Findings snapshot: `claude_code_register_findings.json`.

---

## 10. Design principles for the downstream Skill/Agent (the higher-order lessons)

1. **Density/cluster thresholds, not absolute bans.** One "robust" in an engineering doc is fine.
   Flag Tier-1 always, Tier-2 in clusters, Tier-3 at % density. Ship a false-positives-to-ignore
   list (isolated perfect grammar, one transition word, one short sentence, auto-corrected curly
   quotes, quoted material).
2. **Register-awareness — branch on genre.** For encyclopedic / technical / legal / scientific
   text, *neutral and plain IS the correct human voice*. Do not inject personality or contractions
   there. This is critical for your codebase-docs use case.
3. **Specificity is the deepest fix** — anchor vague claims to a name/number/date/mechanism. BUT
   see the fabrication trap below.
4. **Two-pass self-review + re-scan.** After rewriting, ask "what still makes this obviously AI?"
   and re-run the *same* detectors on the rewrite.
5. **Numeric targets beat adjectives** — "no comment over three lines", "1 em-dash per 500 words",
   "no three consecutive same-length sentences."
6. **Apply rules silently** — never announce them in the output.
7. **State the caveats** — signals not proof; detector scores are noisy (±10–20 pts/run) and biased
   against ESL/technical writers. "Worth acting on; not worth ruining someone's day over."

### Failure modes a naive humanizer WILL hit (design around these)
- **The refinement trap** — copy-editing (tightening phrasing, smoothing parallelism) *raises* AI
  register. Empirical trajectory: an essay went 75→68→**21**→56→66% AI as it was "improved."
  **Cutting beats rewriting; once a passage reads human, stop editing it.**
- **The fabrication trap** — a required "concrete rewrite" slot makes the model *invent* facts
  ("current tools" → "Claude Code turned…"). **Rule: never introduce a fact — tool/person/number/
  mechanism — absent from the source.** Add an "ask the author" escape hatch.
- **The self-defeat trap** — the rewrite reproduces the very cadence it flagged (flags "X, not Y"
  then ships "Portability is the design, not a future feature"). Enforce a self-check pass.

### Conflicts the Skill must decide (§11)
- **Semicolons:** `jalaalrd` says *use them* (well-writing humans do; AI underuses them);
  `humanize-prose` says *ban them, split sentences* (detector-driven). → **Decide by genre.**
- **Goal:** optimize to pass a *detector* vs. read well to a *human*. These pull apart (that's what
  the refinement trap proves). → Recommend **optimize for the human reader**; treat detector scores
  as a noisy secondary check, not the objective.

---

## 11. Existing artifacts worth mirroring (no local humanize skill exists — confirmed)

Local search found **nothing** — must be built. Best web references to adapt:
- **`blader/humanizer`** — the popular one; 33 named patterns + false-positive list + "preserve
  human signals."
- **`jalaalrd/anti-ai-slop-writing`** — most complete portable directive; per-model first-word
  tells (Claude avoids opening with: "in, from, this, how, yes, title, according, the, based,
  here"); era-tagged vocab; "apply silently."
- **`NousResearch/autonovel/ANTI-SLOP.md`** — best *theory* (perplexity/burstiness/Pangram) +
  tone-by-context DO/DON'T tables (README, notebook, paper, blog).
- **`stephenturner/skill-deslop`** — 10 rules + a 5-dimension × 10-point rubric (revise below 35/50).
- **`conorbronsdon/avoid-ai-writing`** (2.1k★) — the density-tier banlist + P0/P1/P2 severity.
- **`celestialdust/humanize-prose`** — detector-calibrated; documents the refinement trap; ships a
  reusable Python scanner (`ai_tell_scan.py`) — the most directly adaptable *code* artifact.
- **`adewale/anti-slop-writing`** — eval-harness-driven; documents the fabrication & self-defeat traps.
- **`Byk3y/no-slop`** — 13-category regex prose linter.
- **Upstream authority:** Wikipedia:Signs of AI writing (WikiProject AI Cleanup).
- **Primary data:** Kobak et al. (arXiv 2406.07016); `sam-paech/slop-forensics`; EQ-Bench Slop
  Score; Pangram Labs; tropes.fyi.
