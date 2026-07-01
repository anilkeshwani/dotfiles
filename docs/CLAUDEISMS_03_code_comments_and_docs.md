# Claudeisms 03 — Code Comments, Docstrings & Code-Adjacent Docs

Scope: the code-specific "tells" of LLM-authored comments, docstrings, commit messages, and PR
descriptions — and the concrete rule text that suppresses them. Prioritizes verbatim, reusable
rule text and before/after code examples over prose.

---

## 0. The single most important finding: verbatim rule text you can paste

These are the highest-signal, drop-in-ready rules. Everything below is supporting evidence.

### 0.1 Anthropic's OWN official wording (this is the actual Claude Code default behavior)
From Claude's official *Prompting best practices* doc, "Sample prompt to minimize overengineering":
> **Documentation: Don't add docstrings, comments, or type annotations to code you didn't
> change. Only add comments where the logic isn't self-evident.**

The same block also constrains the adjacent Claudeisms (scope creep, defensive-coding bloat,
speculative abstractions) that tend to arrive with verbose comments:
> - **Scope**: Don't add features, refactor code, or make "improvements" beyond what was asked.
>   A bug fix doesn't need surrounding code cleaned up.
> - **Defensive coding**: Don't add error handling, fallbacks, or validation for scenarios that
>   can't happen. Trust internal code and framework guarantees. Only validate at system boundaries.
> - **Abstractions**: Don't create helpers, utilities, or abstractions for one-time operations.
>   The right amount of complexity is the minimum needed for the current task.

Source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

### 0.2 The user's OWN "pithy comment standard" (already encoded locally — reuse verbatim)
From `/home/anilkeshwani/dotfiles/home/.claude/agents/senior-mle-reviewer.md`, check #6:
> **Comment quality — enforce the pithy standard.** No comment over three lines. No comment that
> narrates history or the decision-making process ("changed this because we used to…", "step 3
> of…"). Comments only for the *why* (motive, trade-off, non-obvious constraint), caveats, and
> gotchas — never restating what the code plainly says. No wasted words. Flag every violation with
> the trimmed version.

This is the single best rule text in the local material. It is already the house style; a
comment-quality skill should treat it as the canonical statement and reuse its exact clauses:
"No comment over three lines" / "no comment that narrates history" / "only for the *why*" /
"never restating what the code plainly says" / "no wasted words."

### 0.3 The nuclear option people report actually works (from HN)
> **"YOU ARE FORBIDDEN FROM ADDING ANY COMMENTS OR DOCSTRINGS. The only code accepted will be
> self-documenting code."**

Reported to work on HN (item 43929768). Blunt, all-caps, absolute. Downside: also kills the
valuable *why* comments. Use as a corrective/de-slopping pass, not a permanent standard.

### 0.4 The moderate phrasing people report works
> **"Write self-documenting code and only leave comments when it's essential for understanding."**

(HN 43929768.) Softer than 0.3, preserves the good comments.

---

## 1. The catalogue of code-specific tells

For each: pattern name · bad example · good rewrite (often *delete*) · principle · source · usable rule text.

### Tell 1 — Redundant comments that restate the code
**Bad:**
```python
i += 1  # increment i
count = count + 1  # add one to the count
users = []  # initialize an empty list of users
return result  # return the result
```
**Good:** delete all of them. The code already says this.

- **Principle:** A comment that a competent reader could regenerate from the line below it is pure
  cost — screen space now, comment-rot risk later, and (specific to LLMs) wasted context tokens on
  every future read.
- **Sources:** HN 45624429 ("LLMs tend to write comments answering 'what?', sometimes to a silly
  extent … useful to the LLM in writing code, but when an LLM reads that code later it's just a
  waste of context"); DEV.to "7 signs" (below).
- **Rule text:** *"Never write a comment that restates what the code plainly says. If the line
  below it makes the comment redundant, delete the comment, not the line."*

### Tell 2 — Obvious / ceremonial docstrings
**Bad** (verbatim from DEV.to "7 signs to spot LLM-generated code"):
```python
def add_numbers(a: int, b: int) -> int:
    """
    Adds two numbers and returns the result.
    Parameters:
        a (int): The first number.
        b (int): The second number.
    Returns:
        int: The sum of a and b.
    """
    return a + b
```
**Good:**
```python
def add_numbers(a: int, b: int) -> int:
    return a + b
```
- **Principle:** The docstring restates the signature. The article's line: *"no human writes a
  docstring to explain that `a + b = c` unless they're on their very best behavior (or on
  ChatGPT)."* Type info is already in the annotations — re-narrating it as prose is duplication.
- **Source:** https://dev.to/dev_tips/was-this-python-written-by-a-human-or-an-ai-7-signs-to-spot-llm-generated-code-3370
- **Rule text:** *"Don't write a docstring that only re-states the function name, signature, or type
  annotations. A docstring earns its place by adding what the signature can't show: units,
  invariants, side effects, raised exceptions, or the non-obvious contract."*

### Tell 3 — Comments explaining WHAT instead of WHY (the enduring rule)
**Bad:**
```python
# Loop over the items and process each one
for item in items:
    process(item)

# use our newly created Foo model      <- verbatim bad example from HN 43929768
foo = Foo(...)
```
**Good:** delete the "what" comment; keep only a "why" if one exists:
```python
# Foo (not Bar) because Bar's validation rejects legacy IDs still in prod
foo = Foo(...)
```
- **Principle:** The durable distinction. Comments about *intent* and *the why* matter; *the how*
  comments are "dross" (HN 45624429). Good "why" content: business-rule rationale, performance
  trade-offs, security implications, edge-case reasoning, third-party API gotchas, integration
  notes, maintenance warnings.
- **Sources:** HN 45624429 (*"A comment should only explain what the following thing does if it's
  hard to parse … otherwise it should add information: why something is as it is"*); usetusk.ai
  comment-driven-development; multiple.
- **Rule text:** *"Comments answer WHY, never WHAT. If a comment describes what the code does,
  either the code should be made clearer or the comment should be deleted. Reserve comments for
  motive, trade-off, non-obvious constraint, and gotchas."*

### Tell 4 — Multi-line narrative comments (a paragraph over a 3-line function)
**Bad:**
```python
# This function is responsible for taking the raw user input, which may contain
# leading and trailing whitespace as well as mixed casing, and normalizing it so
# that downstream comparison logic can treat equivalent strings as equal. We do
# this by first stripping the string and then lowercasing it before returning.
def normalize(s: str) -> str:
    return s.strip().lower()
```
**Good:** delete entirely — the body is self-evident. If a *why* exists, one line:
```python
def normalize(s: str) -> str:
    return s.strip().lower()  # case-insensitive because usernames are matched loosely
```
- **Principle:** LLMs "think out loud in comments" — token generation is how the model reasons, so
  it narrates (HN 43929768: *"Producing tokens is how it thinks"*). That narration is scaffolding
  for the model, not documentation for the reader; it should not survive into the file.
- **Rule text (reuse the local standard):** *"No comment over three lines. No comment that narrates
  the code's operation step by step."*

### Tell 5 — Change-narration / history comments (comment-rot bombs)
**Bad:**
```python
# NEW: added this to fix the race condition
# Updated logic here to handle the null case
# Changed from list to set for performance (was previously O(n))
# TODO(2024): remove after migration    <- may already be done
```
**Good:** delete. History belongs in git, not in the source. Keep only the *durable* reason:
```python
# set, not list: membership check is hot-path and inputs can be large
```
- **Principle:** Comments that describe the *diff* or the *edit* are stale the moment the next
  change lands — the code moves on, the narration doesn't, and now the comment lies. This is the
  primary comment-rot vector. Git blame/PRs already hold the history.
- **Sources:** local `senior-mle-reviewer` #6 (*"No comment that narrates history … 'changed this
  because we used to…'"*); `comment-analyzer` agent (*"Avoid comments that reference temporary
  states or transitional implementations"*; *"TODOs or FIXMEs that may have already been
  addressed"*).
- **Rule text:** *"Never write comments about the change itself — no 'NEW', 'Updated', 'Added to
  fix…', 'was previously…'. The comment describes the code as it is now, for a reader who never saw
  the diff. History lives in git."*

### Tell 6 — Section-divider / decorative comment banners
**Bad:**
```python
# ============================================================
# HELPER FUNCTIONS
# ============================================================

# ------------------- Main Logic -------------------
#############  CONFIGURATION  #############
```
**Good:** delete. If a file needs banners to be navigable, it's too big — split it. Function/class
names are the section headers.
- **Principle:** Decorative separators are visual noise that duplicate structure the language
  already expresses (defs, classes, modules). They also drift out of sync when code is reordered.
- **Rule text:** *"No decorative banners or `# ====` / `# ----` separators. Structure the code so
  its own declarations are the navigation."*

### Tell 7 — Over-defensive / teaching comments (explaining the language, not the code)
**Bad:**
```python
# A dictionary is a collection of key-value pairs
cache = {}
# List comprehension: iterate and build a new list
squares = [x * x for x in nums]
# The 'with' statement ensures the file is closed automatically
with open(path) as f:
    ...
```
**Good:** delete. The reader knows the language.
- **Principle:** LLMs default to tutorial mode. Medium ("Why AI Can't Write Optimized Code"):
  over-commenting is *"like reviewing code written by an overly polite intern trying to get a
  full-time offer … LLMs pollute production code with redundant tutorial-style code comments
  explaining basic syntax unnecessarily."*
- **Source:** https://medium.com/@abhishek97.edu/why-ai-cant-write-optimized-code-the-verbosity-problem-and-how-to-solve-it-d9339bb9b290
- **Rule text:** *"Never explain the programming language or standard-library behavior to the
  reader. Assume a competent practitioner of the language. Comment the domain, not the syntax."*

### Tell 8 — Emoji, over-enthusiasm, "Note:"/"Important:" spam
**Bad:**
```python
# 🚀 Blazing-fast lookup! ✨
# ✅ All done! Now we handle the edge case 🎉
# Note: This is important! ⚠️ Make sure to read this carefully!!!
# 🔥 Pro tip: you can also pass a custom key here
```
**Good:** delete the decoration and the hype; keep only a bare factual note if one is warranted:
```python
# lookup is O(1); callers rely on this in the render loop
```
- **Principle:** Emoji and exclamation-driven enthusiasm are a chat-assistant register leaking into
  source. `Note:`/`Important:` prefixes are usually filler — if it weren't worth reading it
  wouldn't be a comment. The problem is common enough that dedicated tools exist purely to strip it
  ("Emoji Eraser" VS Code extension: *"cleans AI-generated code by removing emojis, debug
  statements, AI comments"*; HN 46651671: *"clean up AI comments riddled with stupid emojis"*).
- **Sources:** https://marketplace.visualstudio.com/items?itemName=DabwitsoMweemba.emoji-eraser ;
  HN 46651671.
- **Rule text:** *"No emoji in comments or docstrings. No exclamation marks, no 'Pro tip', no
  cheerleading. Drop 'Note:' / 'Important:' prefixes — state the fact plainly or delete it."*

### Tell 9 — Docstring / formatting-convention tells
- **Over-templated uniformity:** every function gets the full Args/Returns/Raises block regardless
  of whether it has anything non-obvious to say. Humans write full docstrings for the public/hard
  functions and skip them for the trivial ones; uniform templating is an LLM tell.
- **Type info duplicated in prose:** `a (int): The first number.` restates the annotation.
- **Mixed styles in one file/PR:** Google-style next to NumPy-style next to reST — a sign the model
  pattern-matched the prompt instead of the file.
- **Source:** DEV.to "7 signs" ("Structural Perfection … textbook patterns with no pragmatic
  shortcuts … formal correctness regardless of scope").
- **Rule text:** *"Match the docstring convention already used in the file; never introduce a second
  style. Don't restate type annotations in prose. Reserve full Args/Returns/Raises blocks for
  public or non-obvious functions — trivial internal helpers don't need them."*

### Tell 10 — Commit messages & PR descriptions (the "This PR does the following:" template)
**Bad PR body (the LLM template):**
```
## Summary
This PR does the following:
- Adds a new function to handle user authentication
- Updates the existing login flow to use the new function
- Adds comprehensive test coverage for the new functionality
- Improves code readability and maintainability
- Ensures backward compatibility

## Changes
- Modified `auth.py` to add `authenticate_user()`
- Modified `login.py` to call `authenticate_user()`
...
```
Tells: bulleted-everything, restating each file's diff, filler bullets ("improves readability",
"ensures backward compatibility"), over-structured sections nobody reads.

**Good (matches Claude Code's own actual instructions):**
- Commit: *"Draft a concise (1-2 sentences) commit message that focuses on the 'why' rather than
  the 'what'."* Use accurate verbs: **add** (new feature), **update** (enhancement), **fix** (bug).
- PR body: **Summary = 1-3 bullet points**, then a **Test plan** as a bulleted checklist. Title
  under 70 chars. Describe what was *actually tested*, not what *should* be.

- **Principle:** Commit/PR text is documentation too; the same why-not-what and no-filler rules
  apply. The model's instinct is to enumerate the diff (which the diff already shows) and pad with
  virtuous-sounding bullets.
- **Sources:** Claude Code's own git instructions (Piebald-AI mirror of the Claude Code system
  prompt: *"concise (1-2 sentences)"*, *"focuses on the 'why' rather than the 'what'"*, *"Summary
  … 1-3 bullet points"*, *"Test plan … bulleted markdown checklist"*, *"title short (under 70
  characters)"*); nova-labs.dev blog notes community reports of *"overly verbose commit messages
  being generated by Claude Code."*
  https://github.com/Piebald-AI/claude-code-system-prompts/blob/main/system-prompts/tool-description-bash-git-commit-and-pr-creation-instructions.md
- **Rule text:** *"Commit subject: one line, imperative, why-focused, under ~70 chars. Body only if
  the why isn't obvious, and never a restatement of the diff. PR description: a 1-3 bullet Summary
  and a Test plan of what you actually ran — no 'This PR does the following', no per-file
  narration, no filler bullets like 'improves readability' or 'ensures backward compatibility'."*

---

## 2. The META-PROBLEM: why it's HARD to make Claude concise, and what actually works

The user's observation is well-supported: instructions to be concise in comments are frequently
ignored, and it takes strong measures.

**Why it's hard (root causes, from the sources):**
1. **Comments are generation scaffolding, not output.** *"Producing tokens is how it thinks"* /
   *"thinking out loud in comments"* (HN 43929768). The model emits comments as part of reasoning,
   then leaves them in. They help the model *write* but pollute the file for the next *reader*
   (which is often the model itself, burning context — HN 45624429).
2. **Training bias toward "best practices" / tutorial register.** Models are trained on didactic,
   heavily-commented teaching code and polite documentation, so verbose commenting is the default
   prior. (Medium "verbosity problem"; DEV.to "7 signs".)
3. **Instructions get ignored.** Multiple reports that even explicit `AGENTS.md`/`CLAUDE.md` rules
   are dropped (HN 45624429: a user's explicit AGENTS.md rule *"was ignored by the LLM anyway"*).
   Anthropic's own guidance warns bloated CLAUDE.md files make Claude ignore actual instructions —
   so the comment rule competes with everything else in the file.

**Phrasings/tactics people report ACTUALLY WORK (ranked):**
1. **Absolute prohibition, all-caps, as a corrective pass** — 0.3 above:
   *"YOU ARE FORBIDDEN FROM ADDING ANY COMMENTS OR DOCSTRINGS. The only code accepted will be
   self-documenting code."* Strong, but over-broad (kills good *why* comments too). Best used as a
   de-slopping cleanup instruction rather than a standing rule.
2. **A concrete, bounded standard with a hard numeric limit** — the local "pithy standard" (0.2):
   *"No comment over three lines … only for the why … never restating what the code plainly says …
   no wasted words."* A number ("no comment over three lines") is more enforceable than an
   adjective ("be concise"), which the model can rationalize away.
3. **Anthropic's own default framing** (0.1): *"Only add comments where the logic isn't
   self-evident"* + *"Don't add docstrings, comments, or type annotations to code you didn't
   change."* The second clause is powerful and under-used: it stops the model from *decorating
   untouched code* during an edit.
4. **Self-documenting-code framing** (0.4): *"write self-documenting code and only leave comments
   when it's essential for understanding."*
5. **A dedicated review/cleanup pass rather than trusting generation.** HN consensus:
   *"Prompting to remove redundant comments works quite well"* (as a separate step). The local
   toolkit already institutionalizes this — the `comment-analyzer` agent and the
   `senior-mle-reviewer`'s comment check exist precisely because a post-hoc sweep is more reliable
   than in-line restraint. Lean on it: **generate, then run a comment-quality pass that deletes.**

**Practical recommendation for a skill/agent:** combine a *hard-numeric standing rule* (the pithy
standard, 0.2) with a *separate delete-first review pass* (comment-analyzer style), because
generation-time restraint alone is unreliable. Phrase the standing rule with a number and an
explicit "prefer deleting over explaining."

---

## 3. Cross-cutting principles (the reusable one-liners)

- **Comments must earn their keep.** (comment-analyzer: *"Every comment should earn its place in
  the codebase by providing clear, lasting value."*)
- **Prefer deleting over explaining.** The best fix for a bad comment is usually no comment. If the
  code needs a "what" comment to be understood, fix the code (names, structure), don't annotate it.
- **WHY, never WHAT.** *"Comments explaining 'why' are more valuable than those explaining 'what'."*
  (comment-analyzer.)
- **Write for the future maintainer who never saw the diff.** No history narration, no "NEW", no
  transitional-state comments. (comment-analyzer: *"written for the least experienced future
  maintainer … Avoid comments that reference temporary states or transitional implementations."*)
- **A comment that will rot is worse than no comment.** Inaccurate/stale comments are technical
  debt that compounds. (comment-analyzer: the whole agent exists *"to protect codebases from
  comment rot."*)
- **Don't touch what you didn't change.** No adding docstrings/comments/types to untouched code.
  (Anthropic official.)
- **No wasted words.** (senior-mle-reviewer.)
- **A number beats an adjective.** "No comment over three lines" is enforceable; "be concise" is not.

---

## 4. Local material — verbatim standards already encoded (quote these directly)

**`/home/anilkeshwani/dotfiles/home/.claude/agents/senior-mle-reviewer.md` (check #6) — the house
"pithy comment standard":**
> No comment over three lines. No comment that narrates history or the decision-making process
> ("changed this because we used to…", "step 3 of…"). Comments only for the *why* (motive,
> trade-off, non-obvious constraint), caveats, and gotchas — never restating what the code plainly
> says. No wasted words. Flag every violation with the trimmed version.

**`pr-review-toolkit` `comment-analyzer` agent** (path:
`/home/anilkeshwani/.claude/plugins/marketplaces/claude-plugins-official/plugins/pr-review-toolkit/agents/comment-analyzer.md`)
— key verbatim standards:
> - "Comments that merely restate obvious code should be flagged for removal"
> - "Comments explaining 'why' are more valuable than those explaining 'what'"
> - "Comments that will become outdated with likely code changes should be reconsidered"
> - "Avoid comments that reference temporary states or transitional implementations"
> - "TODOs or FIXMEs that may have already been addressed" (flag these)
> - "Every comment should earn its place in the codebase by providing clear, lasting value."
>
> Its output structure includes a **"Recommended Removals"** section — i.e. deletion is a
> first-class review outcome, not an afterthought.

**`pr-review-toolkit` `code-simplifier` agent** — includes among its simplifications:
> "Removing unnecessary comments that describe obvious code"

**`researcher-reviewer` agent** (`dotfiles/home/.claude/agents/researcher-reviewer.md`, #4) —
comment-as-claim verification (relevant to comment *accuracy*, a rot vector):
> "If the change (or its message/comment) asserts a scientific property — 'skips X,' 'invariant to
> Y,' 'matches the reference' — verify the code delivers it… A stated property that isn't actually
> enforced is a finding."

**User's global `CLAUDE.md`** (`/home/anilkeshwani/.claude/CLAUDE.md`): contains no comment-style
rule (it covers dictation, `uv run`, rebase-over-merge, and file naming). The file-naming rule is
tangentially relevant — its "think globally, not just locally" test ("if I saw only this in a
search result a year from now, would I know what it is?") is the same forward-looking-maintainer
lens the comment standard uses, and could be echoed in comment guidance.

---

## 5. Sources

- Anthropic — Prompting best practices (official; the verbatim "Only add comments where the logic
  isn't self-evident" rule):
  https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- Claude Code system prompt — git commit / PR creation instructions (Piebald-AI mirror):
  https://github.com/Piebald-AI/claude-code-system-prompts/blob/main/system-prompts/tool-description-bash-git-commit-and-pr-creation-instructions.md
- HN — "Your LLMs get rid of comments? Mine add them incessantly." (why-not-what; context-waste):
  https://news.ycombinator.com/item?id=45624429
- HN — "The most common thing that makes agentic code ugly is the overuse of comments" (the
  "FORBIDDEN" directive; "producing tokens is how it thinks"):
  https://news.ycombinator.com/item?id=43929768
- HN — cleaning up AI comments riddled with emojis: https://news.ycombinator.com/item?id=46651671
- DEV.to — "7 signs to spot LLM-generated code" (the `add_numbers` docstring; over-commenting;
  structural perfection):
  https://dev.to/dev_tips/was-this-python-written-by-a-human-or-an-ai-7-signs-to-spot-llm-generated-code-3370
- Medium — "Why AI Can't Write Optimized Code: The Verbosity Problem" ("overly polite intern";
  tutorial-style comment pollution):
  https://medium.com/@abhishek97.edu/why-ai-cant-write-optimized-code-the-verbosity-problem-and-how-to-solve-it-d9339bb9b290
- Justin Searls — "Why LLMs can't stop adding useless code comments" (LinkedIn; "one of the most
  pernicious habits of LLMs"): https://www.linkedin.com/posts/searls_one-of-the-most-pernicious-habits-of-llms-activity-7369698571178188802-d7SZ
- Giuseppe Gurgone — "Comment Directives for Claude Code" (`@implement`/`@docs` pattern: use inline
  comments as prompts, then convert to docs): https://giuseppegurgone.com/comment-directives-claude-code
- Emoji Eraser (VS Code) — evidence emoji-in-comments is a common enough tell to warrant tooling:
  https://marketplace.visualstudio.com/items?itemName=DabwitsoMweemba.emoji-eraser
- Nova Labs — Claude Code git workflows (community reports of verbose commit messages):
  https://nova-labs.dev/blog/claude-code-git-workflows/
- Tusk — "The Case for Comment-Driven Development" (what good why-comments contain):
  https://www.usetusk.ai/resources/the-case-for-comment-driven-development

**Local paths:**
- `/home/anilkeshwani/dotfiles/home/.claude/agents/senior-mle-reviewer.md` (pithy comment standard, #6)
- `/home/anilkeshwani/dotfiles/home/.claude/agents/researcher-reviewer.md` (comment-as-claim, #4)
- `/home/anilkeshwani/.claude/plugins/marketplaces/claude-plugins-official/plugins/pr-review-toolkit/agents/comment-analyzer.md`
- `/home/anilkeshwani/.claude/plugins/marketplaces/claude-plugins-official/plugins/pr-review-toolkit/agents/code-simplifier.md`
- `/home/anilkeshwani/.claude/CLAUDE.md` (no comment rule; file-naming rule shares the forward-looking lens)
