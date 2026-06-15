# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Generate an editable .excalidraw file from a compact JSON spec.

    uv run --script excalidraw_gen.py SPEC.json OUT.excalidraw

Schema: see ../SKILL.md. Design goals (from Excalidraw-skill best practices):
  - ORTHOGONAL routing only (down->across->down elbows), never diagonal, with
    axis-aligned final segments so arrowheads enter a box edge cleanly.
  - Edge labels are BOUND to the arrow (containerId) so Excalidraw masks the
    line behind the text — no text-over-arrow.
  - Generous spacing + a small gap before each arrowhead.
Deterministic: seeds derive from element index, so re-runs diff cleanly.
"""

import json
import sys

# Flexoki-ish palette, clean look. (stroke, fill)
KINDS = {
    "io": ("#1c1b1a", "#e6e4d9"),
    "op": ("#1c1b1a", "#ffffff"),
    "dsp": ("#3d3d2c", "#dde2b2"),
    "encoder": ("#24837b", "#cfe9e5"),
    "bottleneck": ("#a02f6f", "#f1d3e0"),
    "decoder": ("#bc5215", "#fce0c8"),
    "aux": ("#5e409d", "#e2d9f3"),
    "note": ("#6f6e69", "#f2f0e5"),
}
EDGE_KINDS = {
    "flow": ("#1c1b1a", "solid"),
    "skip": ("#6f6e69", "dashed"),
    "aux": ("#5e409d", "dashed"),
}
FONT_NORMAL, FONT_CODE = 2, 3
GAP = 5  # gap before arrowhead so it doesn't jam into the box


def _rng(i: int) -> int:
    return (i * 2654435761 + 1013904223) % 2_000_000_000


class Scene:
    def __init__(self) -> None:
        self.els: list[dict] = []
        self._i = 0

    def _base(self, typ, x, y, w, h, **kw) -> dict:
        self._i += 1
        seed = _rng(self._i)
        el = {
            "id": kw.pop("id", f"el{self._i}"),
            "type": typ, "x": x, "y": y, "width": w, "height": h, "angle": 0,
            "strokeColor": kw.pop("strokeColor", "#1c1b1a"),
            "backgroundColor": kw.pop("backgroundColor", "transparent"),
            "fillStyle": "solid", "strokeWidth": kw.pop("strokeWidth", 2),
            "strokeStyle": kw.pop("strokeStyle", "solid"),
            "roughness": 0, "opacity": 100, "groupIds": [], "frameId": None,
            "roundness": kw.pop("roundness", None), "seed": seed, "version": 1,
            "versionNonce": _rng(seed), "isDeleted": False,
            "boundElements": kw.pop("boundElements", None), "updated": 1,
            "link": None, "locked": False,
        }
        el.update(kw)
        return el

    def rect(self, x, y, w, h, stroke, fill, _id) -> dict:
        el = self._base("rectangle", x, y, w, h, id=_id, strokeColor=stroke,
                        backgroundColor=fill, roundness={"type": 3})
        self.els.append(el)
        return el

    def text(self, x, y, w, h, s, *, size=14, font=FONT_NORMAL, align="center",
             valign="top", color="#1c1b1a", container=None) -> dict:
        el = self._base("text", x, y, w, h, strokeColor=color, strokeWidth=1,
                        text=s, originalText=s, fontSize=size, fontFamily=font,
                        textAlign=align, verticalAlign=valign, containerId=container,
                        lineHeight=1.25, baseline=round(size * 0.9))
        self.els.append(el)
        return el

    def arrow(self, pts, *, stroke, style, _id) -> dict:
        x0, y0 = pts[0]
        rel = [[p[0] - x0, p[1] - y0] for p in pts]
        xs = [p[0] for p in rel]
        ys = [p[1] for p in rel]
        el = self._base("arrow", x0, y0, max(xs) - min(xs), max(ys) - min(ys),
                        id=_id, strokeColor=stroke, strokeStyle=style,
                        roundness=None, points=rel, lastCommittedPoint=None,
                        startBinding=None, endBinding=None,
                        startArrowhead=None, endArrowhead="arrow")
        self.els.append(el)
        return el

    def dump(self) -> dict:
        return {"type": "excalidraw", "version": 2,
                "source": "claude-code:excalidraw-skill", "elements": self.els,
                "appState": {"gridSize": None, "viewBackgroundColor": "#ffffff"},
                "files": {}}


def edge_center(box, side):
    x, y, w, h = box["x"], box["y"], box["width"], box["height"]
    return {"t": (x + w / 2, y), "b": (x + w / 2, y + h),
            "l": (x, y + h / 2), "r": (x + w, y + h / 2)}[side]


def route_points(src, dst, e):
    route = e.get("route", "v")
    if route == "v":
        p0 = edge_center(src, e.get("from_side", "b"))
        pe = edge_center(dst, e.get("to_side", "t"))
        return [p0, (p0[0], pe[1] - GAP)]
    if route == "h":
        fs = e.get("from_side", "r")
        ts = e.get("to_side", "l")
        p0 = edge_center(src, fs)
        pe = edge_center(dst, ts)
        endx = pe[0] - GAP if ts == "l" else pe[0] + GAP
        return [p0, (endx, p0[1])]
    if route == "elbow":
        p0 = edge_center(src, e.get("from_side", "b"))
        pe = edge_center(dst, e.get("to_side", "t"))
        mid = (p0[1] + pe[1]) / 2
        return [p0, (p0[0], mid), (pe[0], mid), (pe[0], pe[1] - GAP)]
    if route in ("around_left", "around_right"):
        fs = e.get("from_side", "l" if route == "around_left" else "r")
        ts = e.get("to_side", fs)
        p0 = edge_center(src, fs)
        pe = edge_center(dst, ts)
        fx = p0[0] + e.get("via_x", -70 if route == "around_left" else 70)
        endx = pe[0] - GAP if ts == "l" else pe[0] + GAP
        return [p0, (fx, p0[1]), (fx, pe[1]), (endx, pe[1])]
    raise SystemExit(f"unknown route '{route}' on edge {e}")


def build(spec: dict) -> dict:
    g = {"col_w": 380, "row_h": 168, "box_w": 290, "box_h": 84}
    g.update(spec.get("grid", {}))
    sc = Scene()
    boxes: dict[str, dict] = {}
    ox, oy = 110, 120

    if spec.get("title"):
        sc.text(ox, 36, 820, 36, spec["title"], size=26, align="left")

    def cell_xy(col, row):
        return ox + col * g["col_w"], oy + row * g["row_h"]

    for n in spec["nodes"]:
        try:
            x, y = cell_xy(n["col"], n["row"])
            w = g["box_w"] + (n.get("wcols", 1) - 1) * g["col_w"]
            h = g["box_h"]
            stroke, fill = KINDS.get(n.get("kind", "op"), KINDS["op"])
            box = sc.rect(x, y, w, h, stroke, fill, n["id"])
            boxes[n["id"]] = box
            t = sc.text(x + 8, y + h / 2 - 10, w - 16, 20, n["label"], size=14,
                        align="center", valign="middle", container=n["id"])
            box["boundElements"] = [{"type": "text", "id": t["id"]}]
            if n.get("shape"):
                side = n.get("anno_side", "right")
                if side == "right":
                    sc.text(x + w + 16, y + h / 2 - 9, 250, 18, n["shape"],
                            size=12, font=FONT_CODE, align="left",
                            valign="middle", color="#6f6e69")
                elif side == "left":
                    sc.text(x - 266, y + h / 2 - 9, 250, 18, n["shape"], size=12,
                            font=FONT_CODE, align="right", valign="middle",
                            color="#6f6e69")
                else:  # bottom
                    sc.text(x, y + h + 8, w, 18, n["shape"], size=12,
                            font=FONT_CODE, align="center", color="#6f6e69")
        except Exception as ex:  # noqa: BLE001
            raise SystemExit(f"error building node {n.get('id', '?')}: {ex}")

    for a in spec.get("annotations", []):
        x, y = cell_xy(a["col"], a["row"])
        stroke, _ = KINDS.get(a.get("kind", "note"), KINDS["note"])
        sc.text(x + a.get("dx", 0), y + a.get("dy", 0), a.get("w", 300), 22,
                a["text"], size=13, align="left", color=stroke)

    for i, e in enumerate(spec.get("edges", [])):
        src, dst = boxes.get(e["from"]), boxes.get(e["to"])
        if src is None or dst is None:
            raise SystemExit(f"edge references unknown node: {e}")
        stroke, style = EDGE_KINDS.get(e.get("kind", "flow"), EDGE_KINDS["flow"])
        arr = sc.arrow(route_points(src, dst, e), stroke=stroke, style=style,
                       _id=f"edge{i}")
        if e.get("label"):
            # Bind label to the arrow so Excalidraw masks the line behind it.
            lt = sc.text(arr["x"], arr["y"], 130, 18, e["label"], size=12,
                         font=FONT_CODE, align="center", valign="middle",
                         color=stroke, container=arr["id"])
            arr["boundElements"] = [{"type": "text", "id": lt["id"]}]

    return sc.dump()


_OBSIDIAN_WARNING = (
    "==⚠  Switch to EXCALIDRAW VIEW in the MORE OPTIONS menu of this document. ⚠== "
    "You can decompress Drawing data with the command palette: 'Decompress current "
    "Excalidraw file'. For more info check in plugin settings under 'Saving'"
)


def to_obsidian_md(scene: dict) -> str:
    """Wrap a scene in the Obsidian Excalidraw plugin's native .excalidraw.md format.

    A raw .excalidraw (pure JSON) opens read-only in the plugin's "compatibility
    mode"; this Markdown form (frontmatter excalidraw-plugin: parsed, a Text
    Elements mirror, and the scene JSON under ## Drawing inside %% comments) is
    the editable native format. The ## Drawing JSON is authoritative.
    """
    texts = [e for e in scene["elements"] if e["type"] == "text"]
    text_block = "\n\n".join(f'{e["text"]} ^{e["id"]}' for e in texts)
    scene_json = json.dumps(scene, indent=2)
    return (
        "---\n\nexcalidraw-plugin: parsed\ntags: [excalidraw]\n\n---\n"
        f"{_OBSIDIAN_WARNING}\n\n\n"
        "# Excalidraw Data\n\n"
        f"## Text Elements\n{text_block}\n\n"
        "%%\n## Drawing\n"
        f"```json\n{scene_json}\n```\n%%\n"
    )


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: excalidraw_gen.py SPEC.json OUT.{excalidraw|excalidraw.md}")
    with open(sys.argv[1]) as f:
        spec = json.load(f)
    scene = build(spec)
    out_path = sys.argv[2]
    if out_path.endswith(".md"):  # Obsidian-native format
        payload = to_obsidian_md(scene)
    else:  # raw .excalidraw JSON (excalidraw.com / compatibility mode)
        payload = json.dumps(scene, indent=2)
        json.loads(payload)
    with open(out_path, "w") as f:
        f.write(payload)
    print(f"wrote {out_path}: {len(scene['elements'])} elements")


if __name__ == "__main__":
    main()
