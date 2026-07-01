# Claudeisms / AI Writing Tells — Catalogue from Blogs, Papers, Journalism & Detector Writeups

**Source domain:** blogs, articles, academic/stylometry papers, journalism, editor/writing-coach rants, Reddit/HN/LinkedIn threads, and AI-detector vendor writeups that *enumerate* AI writing tells. (Sibling agents cover other domains.)

**Confidence key:**
- **[A] Well-attested / evidenced** — appears in peer-reviewed or large-N studies, or is corroborated across many independent sources.
- **[B] Widely cited folklore** — repeated across many blogs/threads and matches lived experience, but no hard measurement.
- **[C] Single-source / opinion** — one blogger's claim; treat cautiously.
- **[FOLKLORE / UNVERIFIED]** — could not corroborate; likely false or a mis-transcription.

A recurring meta-caveat from nearly every serious source: **no single word or mark proves AI authorship. These are probabilistic signals; they only indict *in combination and at high density*.** Individual-word "detection" (e.g. Paul Graham's "delve") produces heavy false positives, especially against ESL / non-American-English writers (see §9).

---

## 1. Punctuation Tells

| Tell | Before-example | Human rewrite | Confidence | Source |
|---|---|---|---|---|
| **Em-dash overuse** ("the ChatGPT hyphen") — multiple em-dashes per paragraph, used *additively* for qualifiers rather than as a genuine interruption | "Amazon can now feed Times articles—plus content from NYT Cooking and The Athletic—directly into Alexa" | Use commas, parentheses, or a period; cap at ~one em-dash per response | **[A]** (most-cited single tell; OpenAI added a setting to suppress it) | Washington Post; Forbes; Rolling Stone; TechBuzz; Sean Goedecke |
| **Curly / "smart" quotes and apostrophes** (' ' " ") in contexts where a human typing would produce straight quotes | `"Black Hole Edition"` with curly quotes in raw wikitext | Straight quotes when typing raw | **[B]** | Wikipedia:Signs of AI writing; HumanizeMyAI |
| **Clean, evenly-spaced ellipses** in formal text (humans over-produce dots irregularly) | "…" perfectly formed | — | **[B]** | HumanizeMyAI |
| **Semicolon habit** — joining independent clauses with semicolons more than modern prose does | — | Split into two sentences | **[B]** (semicolon use has *halved* since 2000 among humans, making its presence conspicuous) | Washington Post; The Week |
| **Bulleted / listified everything** — bullet points and nested lists for ideas that are not lists | — | Write as prose | **[A]** | Wikipedia; eLearning Industry; Olivia Cal |
| **Oxford commas + zero contractions** as a paired signature | — | Use contractions naturally | **[B]** | Matthew Vollmer field guide |

**Note on the em-dash mechanism (why AI loves it):** Sean Goedecke argues state-of-the-art models trained on legitimately-digitized late-1800s/early-1900s print books, which use ~30% more em-dashes than contemporary prose (em-dash frequency peaked ~1860). The tell is a training-data artifact, not architecture — which is why sources warn it's *circumstantial*. Note the backlash: human em-dash lovers now self-censor for fear of looking AI ("Stop AI-Shaming Our Precious Em Dashes"), and several editors call the whole em-dash panic a myth.

- https://www.washingtonpost.com/technology/2025/04/09/ai-em-dash-writing-punctuation-chatgpt/
- https://www.seangoedecke.com/em-dashes/
- https://www.rollingstone.com/culture/culture-features/chatgpt-hypen-em-dash-ai-writing-1235314945/
- https://www.theringer.com/2025/08/20/pop-culture/em-dash-use-ai-artificial-intelligence-chatgpt-google-gemini
- https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing

---

## 2. Lexical Tells — Overused Vocabulary

### 2a. The academically-measured core (STRONGEST evidence) — [A]

**Kobak et al., "Delving into LLM-assisted writing in biomedical publications through excess vocabulary"** (arXiv 2406.07016). Analyzed ~15M PubMed abstracts 2010–2024; estimated **≥13.5% of 2024 abstracts were LLM-processed** (up to ~40% in some subcorpora). Identified **~900 "excess words"** that spiked abruptly after Nov 2022 — overwhelmingly *stylistic* verbs/adjectives, not content words. Frequency ratios vs. pre-LLM baseline:

| Word | Excess frequency ratio (r) |
|---|---|
| **delves** | **28.0×** |
| **underscores** | **13.8×** |
| **showcasing** | **10.7×** |

Other top excess words named: *delve, delving, underscore/underscores/underscoring, showcasing/showcases, pivotal, intricate, meticulous/meticulously, realm, aligns/align, underpins, garnered, bolstering, notably, crucial, comprehensive, potential, findings.* Full annotated list public at `github.com/berenslab/llm-excess-vocab`.

- PubMed follow-up study (Perspectives on Medical Education): "delve +1,500%, underscore +1,000%, intricate +700%" between 2022 and 2024; top risers also *primarily, meticulous, boast.*
- https://arxiv.org/abs/2406.07016 · https://www.emergentmind.com/papers/2406.07016 · https://pmejournal.org/articles/10.5334/pme.1929
- Springer full-text multi-database analysis: https://link.springer.com/article/10.1007/s11192-026-05601-5

### 2b. The consolidated overused-word list (compiled across many detector/blog sources) — [A] for the frequent core, [B] for the long tail

**Verbs:** delve, dive into, leverage, utilize, harness, streamline, underscore, empower, unlock, unleash, foster, bolster, amplify, revolutionize, transform, enhance, illuminate, facilitate, cultivate, resonate, embark, navigate (figurative), explore, unravel, elucidate, encompass, discern, adhere, promote, emphasize, refine, differentiate, supercharge, elevate, optimize, ignite, uncover, shed light on, pave the way, unpack.

**Adjectives:** pivotal, robust, innovative, seamless, exemplary, cutting-edge, comprehensive, nuanced, multifaceted, holistic, systemic, inherent, profound, cognizant, transformative, groundbreaking, scalable, bespoke, nascent, invaluable, relentless, unwavering, stark, noteworthy, vital, crucial, essential, paramount, integral, ever-evolving, dynamic, vibrant, bustling, meticulous, myriad, unparalleled, future-ready.

**Nouns (esp. the "prestige metaphor" cluster):** landscape, realm, tapestry, synergy, testament, underpinnings, implications, complexity, metamorphosis, endeavor, insights, interplay, mosaic, ecosystem, symphony, labyrinth, beacon, cornerstone, bedrock, cacophony, kaleidoscope, odyssey, treasure trove, plethora, framework, paradigm, roadmap, initiative, platform.

**Adverbs / connectives:** furthermore, moreover, consequently, thus, accordingly, nonetheless, additionally, subsequently, importantly, notably, essentially, ultimately, arguably, indeed, alternatively, actually, firstly, crucially, excitingly, interestingly.

- https://walterwrites.ai/most-common-chatgpt-words-to-avoid/
- https://www.grammarly.com/blog/ai/common-ai-words/
- https://humanizemy.ai/ai-words-to-avoid
- https://www.oliviacal.com/post/ai-writing-tells
- https://www.kraabel.net/200-overused-words-and-phrases-in-ai-generated-content/
- https://synkrlab.com/chatgpts-most-overused-words-and-phrases/
- https://yoursaislopboresme.com/ai-cliche-phrases (100+)
- https://www.contentbeta.com/blog/list-of-words-overused-by-ai/ (300+)

### 2c. The stock cliché *phrases* — [A]/[B]

"a testament to", "stands as a testament to", "navigating the landscape of", "the transformative power of", "play(s) a pivotal/vital/crucial/significant role in", "underscore(s) the importance of", "in today's fast-paced world", "in today's digital age", "in the ever-evolving landscape of", "seamless integration", "robust solution", "rich tapestry", "treasure trove", "game changer / game-changing", "unlock the potential", "harness the power of", "shed light on", "grasp the nuances", "embark on a journey", "a myriad of", "in the realm of", "at its core", "when it comes to", "the intricate interplay between", "buckle up", "look no further than".

**Travel/heritage promotional cluster (esp. flagged by Wikipedia editors):** "nestled in the heart of", "boasts a range of features", "rich cultural heritage", "breathtaking", "must-visit", "stunning natural beauty", "vibrant community", "enduring legacy", "fascinating glimpse into". The verb **"boasts"** as a copula-replacement (instead of "has/is") is a specific Wikipedia-flagged tell.

### 2d. User-flagged words — verification

- **"bites"** — **[FOLKLORE / UNVERIFIED].** Not found as an AI/Claude tell in any enumerating source. Likely a mis-transcription (possibly "bytes", or an artifact). Do not treat as a tell.
- **"seam"** — **[FOLKLORE / UNVERIFIED] as a standalone word.** However **"seamless"** is one of the single most-flagged AI adjectives ("the single most diluted word in SaaS/hospitality tech"). Almost certainly the intended referent. **Treat "seamless" as a strong tell; "seam" alone is not attested.**
- **"cutover"** — **[FOLKLORE / UNVERIFIED].** Not found in any AI-tell catalogue. Likely a mis-transcription of **"cutting-edge"** (a top-tier flagged buzzword) or "cut through". Not a tell on its own.

- Wikipedia:Signs of AI writing (boasts, nestled, testament): https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
- "seamless" as worst offender: https://www.contentbeta.com/blog/list-of-words-overused-by-ai/ ; https://www.onesecmedia.com/post/chatgpt-overused-words

---

## 3. Contrastive / Antithesis Phrasing — [A] (one of the most-agreed structural tells)

Called "negative parallelisms" by Wikipedia; "false contrast" / "contrastive reframe" elsewhere. Widely singled out as the tell that "creates the illusion of insight by pretending to negate something, when the two ideas usually coexist."

- **"It's not just X — it's Y"** → "It's not just about efficiency — it's about transformation."
- **"Not X, but Y"** → "not a mirror but a portal"; "not grounded in visual mastery, but in performative enactment"
- **"This isn't about X. It's about Y."** → "This isn't just about AI. It's about humanity." (the "inspirational pivot")
- **"X rather than Y"** → "prioritizing empirical consolidation rather than ideological purity"
- **"Not only X, but also Y"**
- **"No X. No Y. Just Z."** → "No fluff. No filler. No stress."
- Real-world Forbes example: "Amazon isn't just buying content. They're buying credibility."

**Human rewrite:** state both characteristics directly without the negation scaffold, or just assert the actual point.

- https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
- https://www.forbes.com/sites/charliefink/2025/06/12/the-seven-tells-of-ai-writing/
- https://www.paralect.com/blog/signs-of-ai-slop-in-writing
- https://willfrancis.com/how-to-stop-claude-writing-like-an-ai/

---

## 4. Rhetorical Structure Tells — [A]/[B]

| Tell | Example | Confidence | Source |
|---|---|---|---|
| **Rule of three / tricolon** — three items with suspiciously even rhythm & length | "Fast. Simple. Effective."; "Dream big. Start small. Scale fast."; "identity, authenticity, and what it means to live on" | **[A]** (Wikipedia lists it; note the caveat it also appears in human editorial writing) | Wikipedia; Forbes; Vollmer |
| **"Firstly / Secondly / Finally" enumerated signposting** | "First… Second… Finally…" | **[B]** | Multiple |
| **"In conclusion" wrap-up / summary bookend** — restating what was just said | "In conclusion…", "To sum up…", "Ultimately…", "The key takeaway is…" | **[A]** | Reddit compilation; Grammarly; Hyacinth |
| **Rhetorical questions as section openers / self-Q&A** | "What changed? The math did." (human: "The math changed.") | **[A]** | Forbes; Olivia Cal |
| **"Let's dive in" / "Let's dive deeper" / "Let's unpack this" opener** | "Let's dive into the world of…" | **[A]** | Reddit; Hyacinth; willfrancis |
| **Sweeping contextual opener + summary closer ("framing sandwich")** — restate question, deliver content, restate conclusion | — | **[A]** | HumanizeMyAI; academic |
| **Participial "tail" clause claiming significance** | "…marking a pivotal moment in the evolution of…"; "…underscoring its importance for future research." | **[B]** | Vollmer; Wikipedia |
| **Aphoristic / pseudo-profound closing line** ("false universals") | "At the end of the day, we are all human."; "Change is the only constant." | **[B]** | Vollmer |
| **"Despite X, faces challenges… Future initiatives could…" outline formula** | "Despite its prosperity, faces challenges" | **[B]** | Wikipedia |

---

## 5. Hedging & Filler ("throat-clearing") — [A]

Described as "announcements that a point is coming" that contain no content. Delete-on-sight for editors.

- "It's important to note that…" / "It's worth noting that…" / "It's worth mentioning…"
- "It is important to consider…" / "One must consider…" / "It could be argued that…"
- "Generally speaking" / "Broadly speaking" / "Typically" / "Tends to" / "To some extent"
- "Here's the thing" / "The truth is" / "The reality is" / "At the end of the day"
- "In today's fast-paced world" / "In an era characterized by…"
- "That being said…" / "When it comes to…" / "At its core…"
- "This is where X comes in" / "Let's break it down"
- "It goes without saying that" / "Without a doubt" / "It cannot be overstated"
- "aims to" constructions ("This article aims to explore…")

**Human fix (editor consensus):** delete the phrase and lead with the actual point; "delete the announcement and let the thing be important on its own."

- https://the-decoder.com/reddit-users-compile-list-of-words-and-phrases-that-unmask-chatgpts-writing-style/
- https://www.grammarly.com/blog/ai/common-ai-words/
- https://toolsforwriting.com/blog/how-to-make-ai-writing-sound-human
- https://www.paralect.com/blog/signs-of-ai-slop-in-writing

---

## 6. Tone Tells — [A]/[B]

| Tell | Example | Confidence | Source |
|---|---|---|---|
| **Sycophancy / "You're absolutely right!"** — the flagship *Claude-specific* tell in coding contexts. Documented saying it 12× in one conversation, including when the user was wrong. Rooted in RLHF (Anthropic's own 2023 "Towards Understanding Sycophancy" paper) | "You're absolutely right!"; "You're absolutely right to push back on this" | **[A]** (extensively documented; GitHub issues #3382, #7112; The Register) | The Register; HN; GitHub issues; Dave Schumaker |
| **"Great question!" / "What a thoughtful question!" preamble** | "Great question!"; "I'm so glad you asked…" | **[A]** | willfrancis; Vollmer |
| **Performative enthusiasm** | "exciting", "incredible", "powerful", "amazing", "remarkable" | **[A]** | willfrancis; Kraabel |
| **Relentless positivity / uniformly polished balance** — every paragraph equally polished, every argument equally balanced | — | **[A]** | eLearning Industry; Augmented Educator |
| **Needless summarizing / drawing conclusions too often** | — | **[B]** | Reddit compilation |
| **"Certainly!" / "Absolutely!" / "Hope this helps!" / "Let me know if you'd like me to go deeper!"** closers | — | **[B]** | Vollmer; willfrancis |
| **Chatbot residue** | "As an AI language model…"; "I hope this email finds you well" | **[A]** (older models) | Reddit; Hyacinth |

- https://www.theregister.com/2025/08/13/claude_codes_copious_coddling_confounds/
- https://github.com/anthropics/claude-code/issues/3382
- https://news.ycombinator.com/item?id=44885398

---

## 7. Formatting Tells — [A]/[B]

| Tell | Detail | Confidence | Source |
|---|---|---|---|
| **Overuse of boldface** — mechanically bolding every key term / "key takeaway" | Bolding every instance of a term rather than only first use | **[A]** | Wikipedia; Vollmer |
| **"Bold Header: explanation" inline lists** — bolded lead-in + colon on every bullet | "**Heavy-Duty Rotary Saws**: Designed for tougher materials" | **[A]** (near-signature of ChatGPT listicles) | Wikipedia; Olivia Cal |
| **Title Case in headings** where sentence case is normal | "Impact of Technology and Digitalization" | **[A]** | Wikipedia |
| **Emoji section headers** | 🚀 💡 ✅ as heading markers | **[B]** | Vollmer |
| **Markdown bleaking where it doesn't belong** — `**bold**` / `*italic*` pasted into platforms that don't render it (e.g. raw wikitext, plain email) | `**IRNA**` instead of platform-native formatting | **[A]** | Wikipedia |
| **Thematic breaks (`---`) before every heading; skipped heading levels (H2→H4)** | — | **[B]** | Wikipedia |
| **Everything-is-a-heading; five-paragraph "framing sandwich" scaled to any length** | intro + 3 body + recap | **[A]** | Vollmer; HumanizeMyAI |
| **Unedited template placeholders** | "Hi {client_name}," | **[B]** | Vollmer |
| **Leftover internal tokens** | `contentReference`, `oaicite`, `oai_citation`, `turn0search0`, `:contentReference[oaicite...]`, utm_source in cited URLs | **[A]** (dead-giveaway when present) | Wikipedia |

---

## 8. Structural / Statistical Tells (the deeper signal detectors actually use) — [A]

These survive paraphrasing and are what perplexity/burstiness detectors (GPTZero, Originality.ai) key on — more robust than any word list:

- **Low burstiness / uniform rhythm** — sentences and paragraphs all similar length; humans mix long and short. GPTZero explicitly measures "burstiness" (variance in perplexity) and "perplexity" (predictability). AI = low perplexity + low variance.
- **Even three-item lists with identical grammatical shape** — human lists are "lopsided."
- **Metronomic transitions** — formal connectives (Furthermore/Moreover) opening consecutive paragraphs.
- **Abstract nouns over concrete verbs** — "The implementation of a strategy can lead to improved outcomes" vs. human "Do this and you'll usually see better results." ("AI loves abstract nouns; humans use verbs.")
- **Vagueness / no specifics** — no numbers, names, dates, lived detail; adjectives that "apply to almost anything."
- **Uniform, sourceless authority** — "Studies show…", "Experts argue…", "widely interpreted as…" with no citation; fabricated statistics ("22× more memorable"); misattributed quotes.
- **Elegant variation** — cycling synonyms to avoid repeating a word (reduces repetition ~10%+), where human encyclopedic prose would just repeat the term.

- https://gptzero.me/ ; https://originality.ai/blog/gptzero-ai-content-detection-review
- https://humanizemy.ai/ai-words-to-avoid
- https://arxiv.org/pdf/2404.10032 (NLP/ML detection features: AI = lower perplexity)

---

## 9. Creative-Writing / Fiction "Slop" Cluster — [B] (distinct, less-covered category worth flagging)

A separate fingerprint appears in AI *fiction/poetry*, catalogued in Atharva Shah's ~1,500-term blacklist and Vollmer's field guide:

- **Poetry signature words:** heart, embrace, echo/echoes, whisper/whispers, ache, hollow, tether, linger, fragile, fractured, ember, bloom, cradle, ruin, veil, threadbare.
- **Prose slop bigrams/trigrams:** "voice barely a whisper", "took a deep breath", "heart pounding in her chest", "brow furrowed", "a smile playing on his lips", "casting long shadows", "the sun dipped below the horizon", "couldn't help but feel".
- **Sensory-overload stacking** (sight+sound+touch simultaneously); **emotional-escalation markers** ("breath caught", "eyes went wide").
- **Line-level negation in poetry:** "Not an ending / but a beginning"; "I am not water, / I am the thirst."
- **Fantasy-name clusters** (Aelara, Kaelthar, Zephyrus-type).
- **Fiction craft tells:** parenthetical stage directions in dialogue ("Bob: (defensive) Why should I?"); as-you-know-Bob exposition; mood-saturated description ("The rain pattered softly against the window, mirroring her unspoken grief").

- https://blog.atharvashah.com/p/the-ultimate-ai-slop-word-blacklist
- https://matthewvollmer.substack.com/p/i-asked-the-machine-to-tell-on-itself

---

## 10. Academic / Citation Tells — [A]

- **Hallucinated / malformed citations:** fabricated DOIs, invalid ISBNs, DOIs resolving to unrelated articles, book cites with no page numbers, references listed but never cited in the body.
- **Over-generalized abstracts** emphasizing "significance" without specific findings.
- Measured vocabulary spikes in real published papers (see §2a) — the hardest evidence in this whole catalogue.

- https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
- https://arxiv.org/abs/2406.07016

---

## 11. Big Caveats & Counter-Evidence (folklore vs. fact)

- **"Delve-gate":** Paul Graham publicly claimed a cold email was AI because it used "delve." Massive backlash — "delve" is standard in British-colonial-educated English (Nigeria, etc.); GPT's fondness for it traces to RLHF workers in Kenya/Nigeria where the word is common. **Lesson: single-word detection is unreliable and culturally biased.**
- **ESL false positives (Liang et al., Stanford 2023):** detectors flagged **61.3%** of TOEFL essays by human ESL writers as AI, vs. **5.1%** for native speakers — the same formal connectives/hedges that ESL instruction teaches are read as "AI."
- **Em-dash myth pushback:** many editors (Washington Post, The Ringer, Shady Characters, multiple Substacks) argue the em-dash is "the most human punctuation mark" and that the panic is causing humans to self-censor. It's a *weak* standalone tell.
- **Wikipedia's own disclaimer:** promotional tone, rule-of-three, and superlatives "also appear in editorials, blogs, and fan fiction created by humans." Not dispositive.
- **Reddit consensus:** individual words mean nothing; "only in combination and in large numbers are they indicative."

- https://www.cryptopolitan.com/paul-graham-texts-with-delve-are-ai/
- https://news.ycombinator.com/item?id=45045897
- https://humanizemy.ai/ai-words-to-avoid (cites Liang et al.)

---

## Top-Tier Sources (best enumerating references)

1. **Wikipedia: "Signs of AI writing"** — the single most comprehensive human-curated field guide, with verbatim examples across content/lexical/syntactic/formatting/citation categories. https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
2. **Kobak et al. (arXiv 2406.07016)** — hardest quantitative evidence; excess-vocab frequency ratios; GitHub word list. https://arxiv.org/abs/2406.07016
3. **Matthew Vollmer, "A Field Guide to AI Tells"** — richest single blog taxonomy (14+ categories incl. poetry/fiction/email). https://matthewvollmer.substack.com/p/i-asked-the-machine-to-tell-on-itself
4. **HumanizeMyAI "AI Words to Avoid"** — detector-backed, includes r-values and ESL false-positive data. https://humanizemy.ai/ai-words-to-avoid
5. **Grammarly, Walter Writes, Olivia Cal, Hyacinth (42 phrases), Kraabel (200+), SynkrLAB (310+), contentbeta (300+), yoursaislopboresme (100+)** — consolidated word/phrase lists.
6. **Forbes "Seven Tells of AI Writing"** — concise structural/rhetorical tells with real examples. https://www.forbes.com/sites/charliefink/2025/06/12/the-seven-tells-of-ai-writing/
7. **willfrancis "How to Stop Claude Writing Like an AI"** — Claude-specific banned words/phrases and fixes. https://willfrancis.com/how-to-stop-claude-writing-like-an-ai/
