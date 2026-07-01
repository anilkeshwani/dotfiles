# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Empirical mining of Claude's code-architecture *register* from local Claude Code transcripts.

Method: extract assistant prose (text blocks) and user prose (typed text blocks) from all
~/.claude/projects/**/*.jsonl. Strip fenced code and harness-injected wrappers from both. Compare
each candidate term's rate in Claude's output vs the user's own writing about the SAME codebases —
the ratio isolates *register* (Claude's phrasing) from *domain* (shared jargon). Also rank all
content words by that ratio to DISCOVER register terms beyond the seed list.

Output: JSON + a compact stdout summary. No network, stdlib only.
"""
from __future__ import annotations
import json, glob, os, re, collections, math

PROJ = os.path.expanduser("~/.claude/projects")
OUT = os.path.dirname(os.path.abspath(__file__))

# ---- text cleaning -----------------------------------------------------------------------------
FENCE = re.compile(r"```.*?```", re.DOTALL)
INLINE = re.compile(r"`[^`]*`")
# harness-injected wrappers that are NOT user-authored prose
INJECT = re.compile(
    r"<system-reminder>.*?</system-reminder>"
    r"|<command-name>.*?</command-name>"
    r"|<command-message>.*?</command-message>"
    r"|<command-args>.*?</command-args>"
    r"|<local-command-stdout>.*?</local-command-stdout>"
    r"|<task-notification>.*?</task-notification>"
    r"|<function_results>.*?</function_results>"
    r"|<local-command-caveat>.*?</local-command-caveat>",
    re.DOTALL,
)

def clean(text: str) -> str:
    text = INJECT.sub(" ", text)
    text = FENCE.sub(" ", text)
    text = INLINE.sub(" ", text)
    return text

WORD = re.compile(r"[a-z][a-z]+")
def words(text: str):
    return WORD.findall(text.lower())

# ---- candidate terms (seed §9A + prose anchors + discovery extras) ------------------------------
# display -> regex (case-insensitive, word-boundaried)
def rx(p): return re.compile(p, re.IGNORECASE)
SINGLE = {
    # code-architecture register (the §9A seeds + extras)
    "seam": rx(r"\bseams?\b"),
    "cutover": rx(r"\bcut[- ]?overs?\b"),
    "surface (n/v)": rx(r"\bsurfaced?\b|\bsurfaces\b|\bsurfacing\b"),
    "canonical": rx(r"\bcanonical\b"),
    "downstream": rx(r"\bdownstream\b"),
    "upstream": rx(r"\bupstream\b"),
    "converge": rx(r"\bconverge[sd]?\b|\bconverging\b|\bconvergence\b"),
    "entrench": rx(r"\bentrench(?:e[sd]|ing)?\b"),
    "repoint": rx(r"\brepoints?\b|\brepointing\b"),
    "plumb": rx(r"\bplumb(?:ed|ing|s)?\b"),
    "wire (up/in)": rx(r"\bwire[ds]?\b|\bwiring\b"),
    "thread (through)": rx(r"\bthread(?:ed|ing|s)?\b"),
    "collapse": rx(r"\bcollapse[sd]?\b|\bcollapsing\b"),
    "fold (into)": rx(r"\bfold(?:ed|ing|s)?\b"),
    "footprint": rx(r"\bfootprints?\b"),
    "envelope": rx(r"\benvelopes?\b"),
    "stale": rx(r"\bstale\b"),
    "spurious": rx(r"\bspurious\b"),
    "gnarly": rx(r"\bgnarly\b"),
    "hairy": rx(r"\bhairy\b"),
    "crisp/crisply": rx(r"\bcrisp(?:ly|er)?\b"),
    "tighten": rx(r"\btighten(?:ed|ing|s)?\b"),
    "genuinely": rx(r"\bgenuinely\b"),
    "honest(ly)": rx(r"\bhonest(?:ly)?\b"),
    "essentially": rx(r"\bessentially\b"),
    "effectively": rx(r"\beffectively\b"),
    "namely": rx(r"\bnamely\b"),
    "concretely": rx(r"\bconcretely\b"),
    "cleanly": rx(r"\bcleanly\b"),
    "squarely": rx(r"\bsquarely\b"),
    "idiomatic": rx(r"\bidiomatic(?:ally)?\b"),
    "orthogonal": rx(r"\borthogonal\b"),
    "cohesive": rx(r"\bcohesive\b"),
    "load-bearing": rx(r"\bload[- ]bearing\b"),
    "first-class": rx(r"\bfirst[- ]class\b"),
    "hot path": rx(r"\bhot[- ]paths?\b"),
    "nuance(d)": rx(r"\bnuanced?\b|\bnuances\b"),
    "robust": rx(r"\brobust(?:ness)?\b"),
    # prose anchors (cross-check known tells)
    "seamless": rx(r"\bseamless(?:ly)?\b"),
    "delve": rx(r"\bdelve[sd]?\b|\bdelving\b"),
    "leverage": rx(r"\bleverage[sd]?\b|\bleveraging\b"),
    "underscore": rx(r"\bunderscore[sd]?\b|\bunderscoring\b"),
    "holistic": rx(r"\bholistic(?:ally)?\b"),
    "pivotal": rx(r"\bpivotal\b"),
    "tapestry": rx(r"\btapestry\b"),
}
PHRASE = {
    "blast radius": rx(r"\bblast radius\b"),
    "source of truth": rx(r"\bsources? of truth\b"),
    "the canonical": rx(r"\bthe canonical\b"),
    "lives in": rx(r"\blives in\b"),
    "in (exactly) one place": rx(r"\bin (?:exactly )?one place\b"),
    "the honest ...": rx(r"\bthe honest\b"),
    "let me be honest": rx(r"\blet me be honest\b"),
    "to be honest": rx(r"\bto be honest\b"),
    "in all honesty": rx(r"\bin all honesty\b"),
    "the honest truth": rx(r"\bthe honest truth\b"),
    "want me to": rx(r"\bwant me to\b"),
    "the right amount of": rx(r"\bthe right amount of\b"),
    "wire up/in/it": rx(r"\bwire (?:up|in|it|them|these)\b"),
    "paper over": rx(r"\bpaper over\b"),
    "bake(d) in": rx(r"\bbaked? in\b"),
    "carve out": rx(r"\bcarve[sd]? out\b|\bcarving out\b"),
    "rip out": rx(r"\brip(?:s|ped|ping)? out\b"),
    "escape hatch": rx(r"\bescape hatch\b"),
    "the live (consumer/...)": rx(r"\bthe live\b"),
    "to be clear": rx(r"\bto be clear\b"),
    "worth noting/flagging": rx(r"\bworth (?:noting|flagging|calling out|mentioning)\b"),
    "here's the thing": rx(r"\bhere'?s the thing\b"),
    "the thing is": rx(r"\bthe thing is\b"),
    "you're absolutely right": rx(r"\byou'?re absolutely right\b"),
    "you're right": rx(r"\byou'?re right\b"),
    "great question": rx(r"\bgreat question\b"),
    "net:": rx(r"\bnet:"),
    "bottom line": rx(r"\bbottom line\b"),
    "the cleanest": rx(r"\bthe cleanest\b"),
    "no-op": rx(r"\bno[- ]ops?\b"),
    "same three lines": rx(r"\bthe same\b"),  # control-ish common phrase
}
LETME = re.compile(r"\blet me (\w+)", re.IGNORECASE)

STOP = set("""the a an and or but if then else of to in on at for with by from as is are was were be
been being it its this that these those i you he she they we me my your our his her their them us he's
do does did done have has had having will would shall should can could may might must not no nor so
than too very just also only own same s t re ve ll d m o y up out off over under again further here
there when where why how all any both each few more most other some such into through during before
after above below between about against because until while of at by for with what which who whom
whose this these those am been being if is it be do does did having get got make made use used using
one two three now new see like via per within without across around upon among whether either neither
we're it's that's there's let us your you're i'm i've we've they're he's she's don't doesn't can't
won't isn't aren't wasn't weren't hasn't haven't hadn't wouldn't shouldn't couldn't mustn't
""".split())

def is_text_block(b):
    return isinstance(b, dict) and b.get("type") == "text" and isinstance(b.get("text"), str)

def main():
    files = sorted(glob.glob(os.path.join(PROJ, "**", "*.jsonl"), recursive=True))
    asst_word_freq = collections.Counter()
    user_word_freq = collections.Counter()
    asst_total = 0
    user_total = 0
    asst_sessions_with = collections.defaultdict(set)  # term -> set(session)
    asst_term_occ = collections.Counter()
    user_term_occ = collections.Counter()
    asst_phrase_occ = collections.Counter()
    user_phrase_occ = collections.Counter()
    letme_cont = collections.Counter()
    n_sessions = 0
    n_asst_blocks = 0

    for f in files:
        sess = os.path.basename(f)
        seen_any = False
        try:
            fh = open(f, errors="replace")
        except OSError:
            continue
        with fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                t = d.get("type")
                if t not in ("assistant", "user"):
                    continue
                msg = d.get("message", {})
                if not isinstance(msg, dict):
                    continue
                content = msg.get("content")
                texts = []
                if isinstance(content, str):
                    if t == "user":
                        texts.append(content)
                elif isinstance(content, list):
                    for b in content:
                        if is_text_block(b):
                            texts.append(b["text"])
                if not texts:
                    continue
                raw = "\n".join(texts)
                prose = clean(raw)
                ws = words(prose)
                if t == "assistant":
                    seen_any = True
                    n_asst_blocks += 1
                    asst_total += len(ws)
                    asst_word_freq.update(ws)
                    for term, r in SINGLE.items():
                        c = len(r.findall(prose))
                        if c:
                            asst_term_occ[term] += c
                            asst_sessions_with[term].add(sess)
                    for term, r in PHRASE.items():
                        c = len(r.findall(prose))
                        if c:
                            asst_phrase_occ[term] += c
                    for m in LETME.finditer(prose):
                        letme_cont[m.group(1).lower()] += 1
                else:  # user
                    user_total += len(ws)
                    user_word_freq.update(ws)
                    for term, r in SINGLE.items():
                        c = len(r.findall(prose))
                        if c:
                            user_term_occ[term] += c
                    for term, r in PHRASE.items():
                        c = len(r.findall(prose))
                        if c:
                            user_phrase_occ[term] += c
        if seen_any:
            n_sessions += 1

    # rates per 100k words; ratio with add-0.5 smoothing on user side
    def rate(occ, total):
        return (occ / total * 100000) if total else 0.0
    def ratio(a_occ, u_occ):
        ar = rate(a_occ, asst_total)
        ur = rate(u_occ, user_total)
        return ar / ur if ur > 0 else (float("inf") if ar > 0 else 0.0), ar, ur

    def build(occ_a, occ_u, cov=None):
        rows = []
        for term in occ_a:
            rt, ar, ur = ratio(occ_a[term], occ_u.get(term, 0))
            row = dict(term=term, asst=occ_a[term], user=occ_u.get(term, 0),
                       asst_rate=round(ar, 2), user_rate=round(ur, 2),
                       ratio=(round(rt, 1) if rt != float("inf") else "inf"))
            if cov is not None:
                row["sessions"] = len(cov.get(term, ()))
                row["session_pct"] = round(len(cov.get(term, ())) / n_sessions * 100, 1) if n_sessions else 0
            rows.append(row)
        rows.sort(key=lambda r: (r["ratio"] == "inf", r["ratio"] if r["ratio"] != "inf" else 0, r["asst"]), reverse=True)
        return rows

    singles = build(asst_term_occ, user_term_occ, asst_sessions_with)
    phrases = build(asst_phrase_occ, user_phrase_occ)

    # DISCOVERY: content words ranked by asst/user ratio, min asst occurrences
    MIN_OCC = 40
    disc = []
    for w, c in asst_word_freq.items():
        if c < MIN_OCC or w in STOP or len(w) < 4:
            continue
        rt, ar, ur = ratio(c, user_word_freq.get(w, 0))
        # require it to be genuinely skewed to Claude, not just common
        if (rt == float("inf")) or rt >= 2.5:
            disc.append(dict(word=w, asst=c, user=user_word_freq.get(w, 0),
                             asst_rate=round(ar, 2), ratio=(round(rt, 1) if rt != float("inf") else "inf")))
    disc.sort(key=lambda r: (r["ratio"] == "inf", r["ratio"] if r["ratio"] != "inf" else 0, r["asst"]), reverse=True)

    results = dict(
        corpus=dict(files=len(files), sessions=n_sessions, asst_text_blocks=n_asst_blocks,
                    asst_words=asst_total, user_words=user_total),
        singles=singles, phrases=phrases,
        letme_top=letme_cont.most_common(25),
        discovery_by_ratio=disc[:120],
    )
    with open(os.path.join(OUT, "claude_code_register_findings.json"), "w") as fh:
        json.dump(results, fh, indent=2)

    # ---- compact stdout summary ----
    def show(rows, k, n=100):
        print(f"\n{'term':38} {'asst':>7} {'user':>6} {'a_rate':>8} {'ratio':>7} {k}")
        for r in rows[:n]:
            extra = f" {r.get('session_pct','')}%" if 'session_pct' in r else ""
            print(f"{r['term']:38} {r['asst']:>7} {r['user']:>6} {r['asst_rate']:>8} {str(r['ratio']):>7}{extra}")
    c = results["corpus"]
    print(f"CORPUS: {c['sessions']} sessions | {c['asst_text_blocks']:,} assistant text blocks")
    print(f"        {c['asst_words']:,} assistant prose words | {c['user_words']:,} user prose words")
    print(f"        (ratio = Claude's per-100k rate / user's per-100k rate; >1 = Claude over-uses)")
    print("\n=== SEEDED SINGLE-WORD TERMS (by ratio) ===  [session_pct = % of sessions where Claude used it]")
    show(singles, "sess%")
    print("\n=== SEEDED PHRASES (by ratio) ===")
    show(phrases, "")
    print("\n=== 'Let me ___' top continuations (assistant) ===")
    print(", ".join(f"{w}:{n}" for w, n in results["letme_top"]))
    print("\n=== DISCOVERY: content words Claude over-uses vs user (ratio>=2.5, asst>=40) ===")
    show(disc, "", 120)
    print("\nWrote:", os.path.join(OUT, "claude_code_register_findings.json"))

if __name__ == "__main__":
    main()
