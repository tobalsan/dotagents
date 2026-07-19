# /// script
# requires-python = ">=3.10"
# dependencies = ["lzstring"]
# ///
"""Read and write Obsidian Excalidraw (.excalidraw.md) files.

Usage:
  uv run excalidraw_md.py read  <file.excalidraw.md>            # scene JSON to stdout
  uv run excalidraw_md.py write <file.excalidraw.md> <scene.json>
  uv run excalidraw_md.py check <file.excalidraw.md>             # sanity-check scene, exit 1 on issues

`write` accepts a minimal scene ({"elements": [...]}) and fills in all
required Excalidraw boilerplate (ids, seeds, versions, defaults), expands
convenience fields ("label" on shapes/arrows, "start"/"end" element ids on
arrows into real bindings using the current fork's
{elementId, fixedPoint: [fx, fy], mode: "orbit"} format), regenerates the
markdown Text Elements and Element Links sections, and writes an
uncompressed ```json Drawing block (tab-indented, matching the plugin's own
output) that the plugin reads and recompresses on its next save. If the
target file exists, its YAML frontmatter is preserved and the Drawing
section replaced.

`check` reads the scene and reports, on stdout: overlapping text elements,
overlapping shape elements, unbound/line connectors, and dangling
binding/containerId/boundElements references. Exits 1 if any issue found.
"""

import json
import math
import random
import re
import string
import sys
import time

from lzstring import LZString

ID_CHARS = string.ascii_letters + string.digits

FRONTMATTER_DEFAULT = """---

excalidraw-plugin: parsed
tags: [excalidraw]

---
"""

WARNING = (
    "==⚠  Switch to EXCALIDRAW VIEW in the MORE OPTIONS menu of this "
    "document. ⚠== You can decompress Drawing data with the command "
    "palette: 'Decompress current Excalidraw file'. For more info check in "
    "plugin settings under 'Saving'\n"
)

APP_STATE_DEFAULT = {
    "theme": "light",
    "viewBackgroundColor": "#ffffff",
    "currentItemStrokeColor": "#1e1e1e",
    "currentItemBackgroundColor": "transparent",
    "currentItemFillStyle": "solid",
    "currentItemStrokeWidth": 2,
    "currentItemStrokeStyle": "solid",
    "currentItemRoughness": 1,
    "currentItemOpacity": 100,
    "currentItemFontFamily": 5,
    "currentItemFontSize": 20,
    "currentItemTextAlign": "left",
    "currentItemStartArrowhead": None,
    "currentItemEndArrowhead": "arrow",
    "scrollX": 0,
    "scrollY": 0,
    "zoom": {"value": 1},
    "currentItemRoundness": "round",
    "gridSize": 20,
    "gridStep": 5,
    "gridModeEnabled": False,
    "gridColor": {"Bold": "rgba(0,0,0,0.1)", "Regular": "rgba(0,0,0,0.05)"},
    "currentStrokeOptions": None,
    "frameRendering": {"enabled": True, "clip": True, "name": True, "outline": True},
    "objectsSnapModeEnabled": False,
    "activeTool": {
        "type": "selection",
        "customType": None,
        "locked": False,
        "lastActiveTool": None,
    },
}

COMMON_DEFAULTS = {
    "angle": 0,
    "strokeColor": "#1e1e1e",
    "backgroundColor": "transparent",
    "fillStyle": "solid",
    "strokeWidth": 2,
    "strokeStyle": "solid",
    "roughness": 1,
    "opacity": 100,
    "groupIds": [],
    "frameId": None,
    "isDeleted": False,
    "boundElements": [],
    "link": None,
    "locked": False,
}

CHAR_W = 0.6  # crude average glyph width as a fraction of fontSize
LINE_H = 1.25


def new_id() -> str:
    return "".join(random.choices(ID_CHARS, k=8))


def rand_int() -> int:
    return random.randint(1, 2**31 - 1)


# ---------------------------------------------------------------- read


def extract_scene(md: str) -> dict:
    m = re.search(r"```compressed-json\n(.*?)\n```", md, re.DOTALL)
    if m:
        raw = LZString().decompressFromBase64(m.group(1).replace("\n", ""))
        if not raw:
            sys.exit("error: failed to decompress drawing data")
        return json.loads(raw)
    m = re.search(r"```json\n(.*?)\n```", md, re.DOTALL)
    if m:
        return json.loads(m.group(1))
    sys.exit("error: no ```compressed-json or ```json Drawing block found")


# ---------------------------------------------------------------- normalize


def text_dims(text: str, font_size: float) -> tuple[float, float]:
    lines = text.split("\n")
    width = max((len(line) for line in lines), default=1) * font_size * CHAR_W
    return max(width, 10), len(lines) * font_size * LINE_H


def base_fill(el: dict, now: int) -> None:
    el.setdefault("id", new_id())
    el.setdefault("seed", rand_int())
    el.setdefault("version", 1)
    el.setdefault("versionNonce", rand_int())
    el.setdefault("updated", now)
    for k, v in COMMON_DEFAULTS.items():
        el.setdefault(k, json.loads(json.dumps(v)) if isinstance(v, (list, dict)) else v)


def fill_text(el: dict, now: int) -> None:
    base_fill(el, now)
    el.setdefault("fontSize", 20)
    el.setdefault("fontFamily", 5)
    el.setdefault("text", "")
    el.setdefault("originalText", el["text"])
    el.setdefault("rawText", el["text"])
    w, h = text_dims(el["text"], el["fontSize"])
    el.setdefault("width", w)
    el.setdefault("height", h)
    el.setdefault("textAlign", "left")
    el.setdefault("verticalAlign", "top")
    el.setdefault("containerId", None)
    el.setdefault("autoResize", True)
    el.setdefault("lineHeight", LINE_H)
    el.setdefault("roundness", None)


def fill_shape(el: dict, now: int) -> None:
    base_fill(el, now)
    el.setdefault("width", 100)
    el.setdefault("height", 100)
    if el["type"] == "rectangle":
        el.setdefault("roundness", {"type": 3})
    elif el["type"] in ("ellipse", "diamond"):
        el.setdefault("roundness", {"type": 2})
    else:
        el.setdefault("roundness", None)


def fill_linear(el: dict, now: int) -> None:
    base_fill(el, now)
    el.setdefault("points", [[0, 0], [el.get("width", 100), el.get("height", 0)]])
    xs = [p[0] for p in el["points"]]
    ys = [p[1] for p in el["points"]]
    el.setdefault("width", max(xs) - min(xs))
    el.setdefault("height", max(ys) - min(ys))
    el.setdefault("roundness", {"type": 2})
    el.setdefault("startBinding", None)
    el.setdefault("endBinding", None)
    if el["type"] == "arrow":
        el.setdefault("startArrowhead", None)
        el.setdefault("endArrowhead", "arrow")
        el.setdefault("elbowed", False)
    else:
        el.setdefault("startArrowhead", None)
        el.setdefault("endArrowhead", None)


def fill_frame(el: dict, now: int) -> None:
    base_fill(el, now)
    el.setdefault("width", 400)
    el.setdefault("height", 300)
    el.setdefault("name", None)
    el.setdefault("roundness", None)


def center(el: dict) -> tuple[float, float]:
    return el["x"] + el["width"] / 2, el["y"] + el["height"] / 2


def edge_point(el: dict, toward: tuple[float, float], gap: float = 8) -> tuple[float, float]:
    """Point on the boundary of `el` in the direction of `toward`, pushed out by gap."""
    cx, cy = center(el)
    dx, dy = toward[0] - cx, toward[1] - cy
    dist = math.hypot(dx, dy) or 1
    ux, uy = dx / dist, dy / dist
    if el["type"] == "ellipse":
        rx, ry = el["width"] / 2, el["height"] / 2
        denom = math.hypot(ux / rx, uy / ry) if rx and ry else 1
        t = 1 / denom if denom else 0
    else:  # treat everything else as its bounding box
        tx = (el["width"] / 2) / abs(ux) if ux else math.inf
        ty = (el["height"] / 2) / abs(uy) if uy else math.inf
        t = min(tx, ty)
    return cx + ux * (t + gap), cy + uy * (t + gap)


def fixed_point(el: dict, toward: tuple[float, float]) -> list[float]:
    """Normalized (0..1) anchor of the gap-less edge point within el's bbox."""
    ex, ey = edge_point(el, toward, gap=0)
    fx = (ex - el["x"]) / el["width"] if el["width"] else 0.5
    fy = (ey - el["y"]) / el["height"] if el["height"] else 0.5
    return [min(max(fx, 0.001), 0.999), min(max(fy, 0.001), 0.999)]


def expand_arrow_endpoints(el: dict, by_id: dict, now: int) -> None:
    """Turn "start"/"end" element-id shorthands into geometry + bindings."""
    start_el = by_id.get(el.pop("start", None))
    end_el = by_id.get(el.pop("end", None))
    if not (start_el or end_el):
        return
    sc = center(start_el) if start_el else None
    ec = center(end_el) if end_el else None
    start_toward = ec or (el.get("x", 0), el.get("y", 0))
    p0 = edge_point(start_el, start_toward) if start_el else (el.get("x", 0), el.get("y", 0))
    end_toward = sc or p0
    p1 = edge_point(end_el, end_toward) if end_el else (p0[0] + 100, p0[1])
    el["x"], el["y"] = p0
    el["points"] = [[0, 0], [p1[0] - p0[0], p1[1] - p0[1]]]
    el["width"], el["height"] = abs(p1[0] - p0[0]), abs(p1[1] - p0[1])
    for key, target, toward in (
        ("startBinding", start_el, start_toward),
        ("endBinding", end_el, end_toward),
    ):
        if target is not None:
            el[key] = {
                "elementId": target["id"],
                "fixedPoint": fixed_point(target, toward),
                "mode": "orbit",
            }
            target.setdefault("boundElements", [])
            if not any(b.get("id") == el["id"] for b in target["boundElements"]):
                target["boundElements"].append({"id": el["id"], "type": "arrow"})


def expand_label(el: dict, extra: list, now: int) -> None:
    """Turn a "label" shorthand on a shape/arrow into a bound text element."""
    label = el.pop("label", None)
    if label is None:
        return
    txt = {
        "id": new_id(),
        "type": "text",
        "text": label,
        "fontSize": el.get("labelFontSize", 20),
        "textAlign": "center",
        "verticalAlign": "middle",
        "containerId": el["id"],
    }
    fill_text(txt, now)
    if el["type"] == "arrow":
        mx = el["x"] + sum(p[0] for p in el["points"]) / len(el["points"])
        my = el["y"] + sum(p[1] for p in el["points"]) / len(el["points"])
        txt["x"], txt["y"] = mx - txt["width"] / 2, my - txt["height"] / 2
    else:
        cx, cy = center(el)
        txt["x"], txt["y"] = cx - txt["width"] / 2, cy - txt["height"] / 2
    el.setdefault("boundElements", []).append({"id": txt["id"], "type": "text"})
    extra.append(txt)


FILLERS = {
    "text": fill_text,
    "rectangle": fill_shape,
    "ellipse": fill_shape,
    "diamond": fill_shape,
    "arrow": fill_linear,
    "line": fill_linear,
    "frame": fill_frame,
}


def normalize(scene: dict) -> dict:
    now = int(time.time() * 1000)
    elements = scene.get("elements", [])
    for el in elements:
        el.setdefault("id", new_id())
        el.setdefault("x", 0)
        el.setdefault("y", 0)
    by_id = {el["id"]: el for el in elements}

    extra: list = []
    for el in elements:
        filler = FILLERS.get(el["type"])
        if filler is None:
            if "seed" in el:  # already-complete element from an existing drawing
                continue
            sys.exit(f"error: cannot generate element type {el['type']!r} (id {el['id']})")
        if el["type"] in ("arrow", "line"):
            # geometry defaults must exist before bindings are computed
            for other in (by_id.get(el.get("start")), by_id.get(el.get("end"))):
                if other is not None and "width" not in other:
                    FILLERS[other["type"]](other, now)
            if el["type"] == "arrow":
                expand_arrow_endpoints(el, by_id, now)
        filler(el, now)
        expand_label(el, extra, now)
    elements.extend(extra)

    # fractional index: plugin's restoreElements assigns valid indices in
    # array order when this is None, so don't fabricate fake ones here.
    for el in elements:
        el.setdefault("index", None)

    app_state = dict(APP_STATE_DEFAULT)
    app_state.update(scene.get("appState", {}))
    return {
        "type": "excalidraw",
        "version": 2,
        "source": "https://github.com/zsviczian/obsidian-excalidraw-plugin",
        "elements": elements,
        "appState": app_state,
        "files": scene.get("files", {}),
    }


# ---------------------------------------------------------------- write


def text_elements_section(elements: list) -> str:
    out = []
    for el in elements:
        if el["type"] == "text" and not el.get("isDeleted"):
            body = el.get("rawText") or el.get("originalText") or el.get("text", "")
            out.append(f"{body} ^{el['id']}")
    return "\n\n".join(out)


def element_links_section(elements: list) -> str:
    out = []
    for el in elements:
        if not el.get("isDeleted") and el.get("link"):
            out.append(f"{el['id']}: {el['link']}")
    return "\n\n".join(out)


def build_markdown(scene: dict, frontmatter: str) -> str:
    drawing = json.dumps(scene, indent="\t", ensure_ascii=False)
    links = element_links_section(scene["elements"])
    links_block = f"## Element Links\n{links}\n\n" if links else ""
    return (
        f"{frontmatter}"
        f"{WARNING}\n\n"
        f"# Excalidraw Data\n\n"
        f"## Text Elements\n"
        f"{text_elements_section(scene['elements'])}\n\n"
        f"{links_block}"
        f"%%\n"
        f"## Drawing\n"
        f"```json\n"
        f"{drawing}\n"
        f"```\n"
        f"%%"
    )


def existing_frontmatter(path: str) -> str:
    try:
        md = open(path, encoding="utf-8").read()
    except FileNotFoundError:
        return FRONTMATTER_DEFAULT
    m = re.match(r"^---\n.*?\n---\n", md, re.DOTALL)
    return m.group(0) if m else FRONTMATTER_DEFAULT


# ---------------------------------------------------------------- check

SHAPE_TYPES = {"rectangle", "ellipse", "diamond"}


def bbox(el: dict) -> tuple[float, float, float, float]:
    x, y = el.get("x", 0), el.get("y", 0)
    return x, y, x + el.get("width", 0), y + el.get("height", 0)


def bbox_overlap(a: dict, b: dict) -> bool:
    ax1, ay1, ax2, ay2 = bbox(a)
    bx1, by1, bx2, by2 = bbox(b)
    return ax1 < bx2 and bx1 < ax2 and ay1 < by2 and by1 < ay2


def is_bound_pair(a: dict, b: dict) -> bool:
    if a.get("containerId") == b.get("id") or b.get("containerId") == a.get("id"):
        return True
    return bool(set(a.get("groupIds") or []) & set(b.get("groupIds") or []))


def label_of(el: dict) -> str:
    if el["type"] == "text":
        text = el.get("rawText") or el.get("originalText") or el.get("text", "")
        return text.split("\n")[0][:40]
    return el["type"]


def find_overlaps(elements: list) -> list[tuple[dict, dict]]:
    out = []
    for i in range(len(elements)):
        for j in range(i + 1, len(elements)):
            a, b = elements[i], elements[j]
            if is_bound_pair(a, b):
                continue
            if bbox_overlap(a, b):
                out.append((a, b))
    return out


def check(scene: dict) -> int:
    elements = scene.get("elements", [])
    by_id = {el["id"]: el for el in elements}
    visible = [el for el in elements if not el.get("isDeleted")]

    issues: list[str] = []
    warnings: list[str] = []

    texts = [el for el in visible if el["type"] == "text"]
    for a, b in find_overlaps(texts):
        issues.append(
            f"overlapping text: {a['id']} ({label_of(a)!r}) overlaps "
            f"{b['id']} ({label_of(b)!r})"
        )

    shapes = [el for el in visible if el["type"] in SHAPE_TYPES]
    for a, b in find_overlaps(shapes):
        issues.append(f"overlapping shape: {a['id']} ({a['type']}) overlaps {b['id']} ({b['type']})")

    for el in visible:
        if el["type"] == "arrow" and not el.get("startBinding") and not el.get("endBinding"):
            warnings.append(f"unbound connector: arrow {el['id']} has no startBinding or endBinding")
        if el["type"] == "line":
            warnings.append(
                f"line connector: {el['id']} — line elements do not follow shapes when "
                f"moved; prefer arrows with endArrowhead: null"
            )

    for el in visible:
        cid = el.get("containerId")
        if cid is not None and cid not in by_id:
            issues.append(f"dangling containerId: {el['id']} -> {cid}")
        fid = el.get("frameId")
        if fid is not None and fid not in by_id:
            issues.append(f"dangling frameId: {el['id']} -> {fid}")
        for binding_key in ("startBinding", "endBinding"):
            binding = el.get(binding_key)
            if binding and binding.get("elementId") not in by_id:
                issues.append(f"dangling {binding_key}: {el['id']} -> {binding.get('elementId')}")
        for bound in el.get("boundElements") or []:
            bid = bound.get("id")
            if bid not in by_id:
                issues.append(f"dangling boundElements entry: {el['id']} -> {bid}")

    for msg in issues:
        print(f"ERROR: {msg}")
    for msg in warnings:
        print(f"WARNING: {msg}")
    if not issues and not warnings:
        print("check: clean, no issues found")
    return 1 if issues or warnings else 0


def main() -> None:
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cmd, path = sys.argv[1], sys.argv[2]
    if cmd == "read":
        json.dump(extract_scene(open(path, encoding="utf-8").read()), sys.stdout, indent=1)
        print()
    elif cmd == "write":
        if len(sys.argv) < 4:
            sys.exit("usage: excalidraw_md.py write <file.excalidraw.md> <scene.json>")
        scene = normalize(json.load(open(sys.argv[3], encoding="utf-8")))
        md = build_markdown(scene, existing_frontmatter(path))
        with open(path, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"wrote {path}: {len(scene['elements'])} elements")
    elif cmd == "check":
        scene = extract_scene(open(path, encoding="utf-8").read())
        sys.exit(check(scene))
    else:
        sys.exit(f"unknown command {cmd!r}")


if __name__ == "__main__":
    main()
