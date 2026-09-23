#!/usr/bin/env python3
"""deslop_guard.py -- hard binary gate against AI-slop tells in prose.

Deterministic only. No judgement. A file PASSes only if it has zero HARD
violations. WARN items are reported but do not fail the file: they are
register terms that also occur as legitimate vocabulary ("honest majority",
"canonical identification", "stale block"), so a human or reviewer decides
whether a given use is the slop sense.

Sources: deslop-prose/references/prose-banlist.md,
deslop-code/references/code-register.md.

Quoted material is exempt: text inside double quotes on a single line is
removed before scanning, because a quotation must keep its source's exact
characters.

Usage:  uv run --script deslop_guard.py FILE...
Exit 0 if every file passes, 1 on any HARD violation, 2 on usage error.
"""
import re, sys, pathlib

# --- HARD FAILS: unambiguous slop. Zero tolerance. -------------------------

# Banned characters. The em-dash is the single most-cited tell; the en-dash is
# banned too so ranges get rewritten with a hyphen or "to".
BANNED_CHARS = {
    "—": "em-dash",
    "–": "en-dash",
}

# Tier-1 prose vocabulary: almost always replace. Single words, matched on
# word boundaries, case-insensitive.
TIER1_WORDS = [
    "delve", "delves", "delving", "tapestry", "realm", "testament",
    "leverage", "leveraging", "utilize", "utilizes", "harness", "harnesses",
    "underscore", "underscores", "underscoring", "showcasing", "showcase",
    "seamless", "seamlessly", "pivotal", "intricate", "meticulous",
    "meticulously", "cutting-edge", "game-changer", "synergy", "holistic",
    "paradigm", "embark", "embarks", "endeavor", "myriad", "plethora",
    "facilitate", "facilitates", "elucidate",
    # code-register hard bans (deslop-code): always replace
    "load-bearing", "seam", "seams", "cutover",
]

# Banned multi-word phrases (case-insensitive substring on lowercased text).
BANNED_PHRASES = [
    # cliches
    "a testament to", "navigating the landscape", "the transformative power",
    "plays a pivotal role", "play a pivotal role", "underscores the importance",
    "in today's fast-paced", "ever-evolving landscape", "seamless integration",
    "rich tapestry", "treasure trove", "unlock the potential",
    "harness the power", "shed light on", "embark on a journey", "a myriad of",
    "in the realm of", "at its core", "when it comes to",
    # promotional / heritage cluster (Wikipedia-flagged)
    "nestled in the heart of", "boasts a range of", "rich cultural heritage",
    "breathtaking", "must-visit", "vibrant community", "enduring legacy",
    # hedging / filler
    "it's important to note", "it is important to note", "it's worth noting",
    "it is worth noting", "it could be argued", "generally speaking",
    "broadly speaking", "that being said", "it goes without saying",
    "here's the thing", "the reality is", "aims to explore",
    # sycophancy / servile closers / chatbot residue
    "great question", "you're absolutely right", "you are absolutely right",
    "what a thoughtful", "hope this helps", "let me know if you'd like",
    "let me know if you would like", "as an ai", "i hope this email finds you",
    # faux-candor
    "to be honest", "let me be honest", "i'll be honest", "in all honesty",
    "the honest truth", "the honest answer", "the honest name",
    # openers / closers / signposting
    "let's dive in", "let's unpack", "let's explore", "let us dive in",
    "in conclusion", "to summarize", "in summary",
    # offer-closer and self-narration tics (code register, 46.7x / 21x)
    "want me to", "let me check", "let me verify", "let me confirm",
    "let me look", "let me read",
]

# Negative parallelism: the top structural tell. Regex on lowercased text.
# NT covers the contracted forms (isn't/aren't/won't/shouldn't...) that the
# bare "not X" patterns miss.
NT = (r"(?:isn|aren|wasn|weren|don|doesn|didn|can|couldn|won|wouldn|shouldn)"
      r"'?t")
NEG_PARALLELISM = [
    r"\bnot just\b", rf"\b{NT} just\b",
    r"\bnot only\b", rf"\b{NT} only\b",
    r"\b(?:is|are)(?:n't| not) about\b",
    r"\bnot [a-z]+, but\b", rf"\b{NT} [a-z]+, but\b",
    r"\bnot [a-z]+\. it'?s\b", rf"\b{NT} [a-z]+\. it'?s\b",
    r"\brather than\b",
    r"\bno [a-z]+\. no [a-z]+\.",
    r"\bthe question isn't\b",
]

# Oxford / serial comma: the comma before and/or/nor closing a list of three
# or more items. The pattern matches the tail of a list, "word, word, and", so
# it needs two commas and does not fire on a comma that joins two clauses.
OXFORD_COMMA = [
    r"[a-z0-9]+,\s+[a-z0-9]+,\s+(?:and|or|nor)\b",
]

# --- WARNINGS: register terms that may be legitimate vocabulary. -----------
# Reported, never fatal. Reviewer decides if the use is the slop sense.
WARN_WORDS = [
    # code register (deslop-code/references/code-register.md): tier-2
    "canonical", "stale", "surface", "robust", "comprehensive", "honest",
    "confirmed", "confirms", "purely", "trap", "caveat", "genuinely",
    "cleanly", "tighten", "converge", "fold", "plumb", "wire", "blast radius",
    "first-class", "empirically", "the picture", "full picture", "wording",
    "intact", "headline", "lanes", "spine", "defensible", "spurious",
    "entrench", "escape hatch", "guardrail", "hot path", "source of truth",
    "bottom line", "net:", "mild misnomer", "gnarly",
    # prose tier-2/3 (deslop-prose/references/prose-banlist.md)
    "nuanced", "crucial", "foster", "bolster", "garner", "unleash",
    "spearhead", "resonate", "revolutionize", "ecosystem", "cultivate",
    "illuminate", "catalyze", "galvanize", "streamline", "empower", "elevate",
    "transformative", "multifaceted", "profound", "vibrant", "bustling",
    "significant", "innovative", "dynamic", "scalable", "compelling",
    "remarkable", "sophisticated",
]

def strip_code(text, suffix):
    """Remove code so identifiers and samples do not trip the prose scan.
    Kept minimal on purpose."""
    if suffix in (".html", ".htm"):
        text = re.sub(r"<script\b.*?</script>", " ", text, flags=re.S | re.I)
        text = re.sub(r"<code\b.*?</code>", " ", text, flags=re.S | re.I)
        text = re.sub(r"<style\b.*?</style>", " ", text, flags=re.S | re.I)
    elif suffix in (".md", ".markdown"):
        text = re.sub(r"```.*?```", " ", text, flags=re.S)
        text = re.sub(r"`[^`\n]*`", " ", text)
    return text

def strip_quotes(text):
    """Remove single-line double-quoted spans (straight or curly). Quotations
    are verbatim, so their dashes and wording are not the author's to fix."""
    text = re.sub(r'"[^"\n]*"', " ", text)
    text = re.sub(r"\u201c[^\u201d\n]*\u201d", " ", text)
    return text

def scan(path):
    path = pathlib.Path(path)
    raw = path.read_text(encoding="utf-8")
    text = strip_quotes(strip_code(raw, path.suffix.lower()))
    low = text.lower()
    hard, warns = [], []

    for ch, name in BANNED_CHARS.items():
        n = text.count(ch)
        if n:
            hard.append("%s x%d" % (name, n))

    for w in TIER1_WORDS:
        if re.search(r"(?<![\w-])" + re.escape(w) + r"(?![\w-])", low):
            hard.append("tier1 word: %s" % w)

    for p in BANNED_PHRASES:
        if p in low:
            hard.append("banned phrase: %s" % p)

    for pat in NEG_PARALLELISM:
        m = re.search(pat, low)
        if m:
            hard.append("negative parallelism: %r" % m.group(0))

    for pat in OXFORD_COMMA:
        for m in re.finditer(pat, low):
            hard.append("serial comma \", and/or\": %r" % m.group(0))

    for w in WARN_WORDS:
        if re.search(r"(?<![\w-])" + re.escape(w) + r"(?![\w-])", low):
            warns.append(w)

    return hard, warns

def main():
    files = sys.argv[1:]
    if not files:
        print("usage: deslop_guard.py FILE...")
        return 2
    failed = False
    for f in files:
        try:
            hard, warns = scan(f)
        except Exception as e:
            print("ERROR %s: %s" % (f, e))
            failed = True
            continue
        if hard:
            failed = True
            print("FAIL  %s" % f)
            for h in hard:
                print("      [hard] %s" % h)
            if warns:
                print("      [warn] %s" % ", ".join(sorted(set(warns))))
        else:
            print("PASS  %s%s" % (f, ("  (warn: %s)" % ", ".join(sorted(set(warns)))) if warns else ""))
    return 1 if failed else 0

if __name__ == "__main__":
    sys.exit(main())
