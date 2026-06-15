---
name: excalidraw
description: Generate editable Excalidraw (.excalidraw) diagrams from a compact JSON spec — architecture diagrams, data-flow / pipeline diagrams, block diagrams. Use when the user asks for an Excalidraw diagram, an editable/annotated architecture diagram, a "draw.io-style" or "Raschka-style" model diagram, or a visual that should open in excalidraw.com or the Obsidian Excalidraw plugin. Produces clean, annotated boxes-and-arrows with tensor-shape side annotations.
---

# Excalidraw diagram generation

Generate valid **`.excalidraw`** files (Excalidraw scene schema v2, JSON) from a compact
spec, so diagrams are *editable* — the user can open them at https://excalidraw.com or in
Obsidian (Excalidraw plugin) and tweak/export to SVG/PNG. Prefer this over hand-writing
raw Excalidraw JSON: the element schema is verbose and easy to get subtly wrong (bindings,
seeds, bound-text containers).

## When to use
- "Draw me an architecture diagram", "make an Excalidraw / editable / annotated diagram".
- "Sebastian Raschka-style" model diagrams: a clean vertical pipeline of blocks with
  **tensor-shape annotations** beside each block, optional side branches and skip
  connections.
- Any boxes-and-arrows: data flow, pipeline stages, system components.

For diagrams that only need to render inline (no editing), a Mermaid `flowchart` in
Markdown is often enough and complements the Excalidraw source — consider emitting both.

## How to generate

1. Write a spec JSON file (see schema below).
2. Run the generator (it is a [PEP 723](https://peps.python.org/pep-0723/) inline-script,
   so `uv run --script` resolves its deps):

   ```bash
   uv run --script ~/.claude/skills/excalidraw/scripts/excalidraw_gen.py SPEC.json OUT.excalidraw
   ```

3. Tell the user how to open it (excalidraw.com → "Open", or drop into an Obsidian vault
   with the Excalidraw plugin). The file is plain JSON — safe to commit and diff.

## Spec schema (JSON)

```jsonc
{
  "title": "Optional title text drawn at top",
  "grid":  { "col_w": 300, "row_h": 120, "box_w": 220, "box_h": 64 }, // optional; these are defaults
  "nodes": [
    {
      "id": "stft",                 // unique
      "label": "STFT",              // bold-ish centered title (wraps)
      "col": 0, "row": 1,           // grid cell (col→x, row→y); row increases downward
      "wcols": 1,                   // optional: span N columns wide (default 1)
      "shape": "(B, 2, F, T)",      // optional: mono side-annotation drawn to the RIGHT (Raschka-style)
      "kind": "op"                  // optional: io | op | encoder | decoder | bottleneck | aux | dsp | note
    }
  ],
  "edges": [
    { "from": "wav", "to": "stft", "route": "v" },            // straight vertical
    { "from": "stft","to": "erbf", "route": "elbow" },         // down→across→down (cross-column)
    { "from": "a",   "to": "b",    "route": "h" },             // straight horizontal (same row)
    { "from": "enc", "to": "dec",  "route": "around_left",     // route out to the side, around boxes…
      "kind": "skip", "via_x": -410, "label": "skip" }         // …for skip connections; label is BOUND to the arrow
  ],
  "annotations": [                  // free-floating notes (legend, stage caption)
    { "text": "Stage 1: ERB gain", "col": 2, "row": 1, "kind": "note", "dx": 0, "dy": 0 }
  ]
}
```

- **`route`** (the important field) picks the connector shape — keep it orthogonal:
  - `"v"` — straight vertical (same column, top→bottom). Default.
  - `"elbow"` — down → across → down. Use for **all cross-column** edges (splits/merges).
    Never let an arrow go diagonally.
  - `"h"` — straight horizontal (same row).
  - `"around_left"` / `"around_right"` — exit the side, run past the boxes at `via_x`
    (pixel offset from the box edge — make it large enough to clear the target column),
    then come back in. For skip connections.
- `from_side` / `to_side` ∈ `t b l r` override which edge the arrow touches.
- `kind` controls colour; `skip`/`aux` render dashed.
- Edge **labels are bound to the arrow** automatically (`containerId`), so Excalidraw masks
  the line behind the text — no text-over-arrow. Keep labels short.
- `anno_side` on a node ∈ `right | left | bottom` places its `shape` annotation (default
  `right`); use `bottom`/`left` if `right` would collide with an arrow lane.

## Raschka-style conventions (follow these)
- One **vertical column** of blocks = the main data path, top→bottom.
- Put the **tensor shape** for each block in `shape` (mono font, to the right). This is the
  signature of the style — every block is annotated with what flows out of it.
- Use `kind` to colour-group: inputs/outputs, encoder vs decoder, auxiliary heads, DSP ops.
- Side branches (e.g. a second decoder, an auxiliary head) go in an adjacent column with
  arrows merging back.
- Keep `roughness: 0` (clean lines) — the generator already does this.
- Add a short **legend** via `annotations` if you use more than ~3 colours.

## Layout rules (research-backed — these fix the common failure modes)
Distilled from community Excalidraw skills (coleam00/excalidraw-diagram-skill,
robonuggets/excalidraw-skill, the Excalidraw element-skeleton docs):
- **Orthogonal routing only.** Diagonal arrows are the #1 source of ugly diagrams and
  mis-angled arrowheads. Use `route: "elbow"` for every cross-column connection so the
  **final segment is axis-aligned** and the arrowhead enters the box edge square-on. The
  generator already leaves a small gap before the arrowhead.
- **Generous spacing.** Defaults give a ~84 px vertical gap between stacked boxes — enough
  for an arrow plus a bound label. Don't shrink `row_h` below ~150.
- **Bind labels, don't float them.** The generator binds edge labels to the arrow so the
  line is masked behind the text. (Floating a label at a line's midpoint = unreadable.)
- **Keep annotations out of arrow lanes.** Shape annotations default to the right; if a box
  has arrows leaving/entering on the right, set `anno_side: "left"` or `"bottom"`.
- **Route skips wide.** For `around_*` skips, set `via_x` past the far edge of the column
  you're skipping over, or the arrow will cut through the boxes.

## Validate before delivering (you cannot see the canvas)
After generating, run these structural checks (no renderer needed) — they catch exactly the
"text over arrow / bad arrowheads" problems:
```bash
python3 - "OUT.excalidraw" <<'PY'
import json,sys; els=json.load(open(sys.argv[1]))['elements']
# 1) no diagonal segments
for e in els:
    if e['type']=='arrow':
        for (x0,y0),(x1,y1) in zip(e['points'],e['points'][1:]):
            assert abs(x1-x0)<.5 or abs(y1-y0)<.5, f"diagonal in {e['id']}"
# 2) no free text sitting on a box or crossing an arrow segment (see repo for the full check)
print("ok:", len(els), "elements")
PY
```
If you have Playwright/a browser, even better: open the file in excalidraw.com, screenshot,
and eyeball for overlaps — then iterate (two passes is usually enough).

## Notes / gotchas
- Deterministic given the spec (seeds from element index) → stable, diff-friendly files.
- Bound text auto-centres in its box on load; title (normal font) and shape annotation
  (mono) are separate elements so sizes differ.
- Widen a crowded box with `wcols` rather than shrinking the font.
- Output is JSON-validated before writing; a build error names the offending node/edge.

## Sources
- coleam00/excalidraw-diagram-skill — layout best practices, color palette, render pipeline
- robonuggets/excalidraw-skill — elbow routing, label binding, self-correcting via screenshots
- Excalidraw element-skeleton docs — programmatic binding (`start`/`end`, `label`, `containerId`)
