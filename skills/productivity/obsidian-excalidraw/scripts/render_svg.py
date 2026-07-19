# /// script
# requires-python = ">=3.10"
# dependencies = ["lzstring"]
# ///
"""Render an Obsidian Excalidraw scene to a static SVG.

Usage:
  uv run render_svg.py <file.excalidraw.md or scene.json> <out.svg>

This is a preview/QA renderer, not pixel-faithful to Excalidraw's hand-drawn
look — but element geometry and positions are exact, so layout problems
(overlaps, misalignment, off-canvas elements) are visible. Supports
rectangle, ellipse, diamond, frame, line, arrow and text elements.
"""

import json
import math
import os
import sys


def _load_extract_scene():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from excalidraw_md import extract_scene

    return extract_scene


extract_scene = _load_extract_scene()

MARGIN = 40


def load_scene(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if path.endswith(".md"):
        return extract_scene(text)
    return json.loads(text)


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def dasharray(el: dict) -> str:
    style = el.get("strokeStyle")
    w = el.get("strokeWidth", 2) or 2
    if style == "dashed":
        return f' stroke-dasharray="{w * 4},{w * 2}"'
    if style == "dotted":
        return f' stroke-dasharray="{w},{w * 2}"'
    return ""


def common_attrs(el: dict) -> str:
    stroke = el.get("strokeColor") or "#1e1e1e"
    fill = el.get("backgroundColor")
    fill = "none" if fill in (None, "transparent") else fill
    width = el.get("strokeWidth", 2)
    opacity = (el.get("opacity", 100) or 0) / 100
    return (
        f' stroke="{stroke}" fill="{fill}" stroke-width="{width}"'
        f' opacity="{opacity}"{dasharray(el)}'
    )


def bbox_of(el: dict) -> tuple[float, float, float, float]:
    x, y = el.get("x", 0), el.get("y", 0)
    if el["type"] in ("line", "arrow"):
        pts = el.get("points") or [[0, 0]]
        xs = [x + p[0] for p in pts]
        ys = [y + p[1] for p in pts]
        return min(xs), min(ys), max(xs), max(ys)
    w, h = el.get("width", 0), el.get("height", 0)
    return x, y, x + w, y + h


def render_rect(el: dict) -> str:
    x, y = el.get("x", 0), el.get("y", 0)
    w, h = el.get("width", 0), el.get("height", 0)
    rx = 12 if el.get("roundness") else 0
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"{common_attrs(el)} />'


def render_ellipse(el: dict) -> str:
    x, y = el.get("x", 0), el.get("y", 0)
    w, h = el.get("width", 0), el.get("height", 0)
    cx, cy = x + w / 2, y + h / 2
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{w / 2}" ry="{h / 2}"{common_attrs(el)} />'


def render_diamond(el: dict) -> str:
    x, y = el.get("x", 0), el.get("y", 0)
    w, h = el.get("width", 0), el.get("height", 0)
    pts = [(x + w / 2, y), (x + w, y + h / 2), (x + w / 2, y + h), (x, y + h / 2)]
    pts_str = " ".join(f"{px},{py}" for px, py in pts)
    return f'<polygon points="{pts_str}"{common_attrs(el)} />'


def render_frame(el: dict) -> str:
    x, y = el.get("x", 0), el.get("y", 0)
    w, h = el.get("width", 0), el.get("height", 0)
    out = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" '
        f'stroke="#808080" stroke-width="1" stroke-dasharray="4,4" />'
    ]
    name = el.get("name")
    if name:
        out.append(
            f'<text x="{x}" y="{y - 6}" font-size="12" font-family="monospace" '
            f'fill="#808080">{esc(name)}</text>'
        )
    return "\n".join(out)


def _arrow_triangle(tip: tuple[float, float], direction: tuple[float, float], color: str, size: float = 12) -> str:
    dx, dy = direction
    dist = math.hypot(dx, dy) or 1
    ux, uy = dx / dist, dy / dist
    px, py = -uy, ux
    back_x, back_y = tip[0] - ux * size, tip[1] - uy * size
    left = (back_x + px * size * 0.4, back_y + py * size * 0.4)
    right = (back_x - px * size * 0.4, back_y - py * size * 0.4)
    pts = f"{tip[0]},{tip[1]} {left[0]},{left[1]} {right[0]},{right[1]}"
    return f'<polygon points="{pts}" fill="{color}" />'


def render_linear(el: dict) -> str:
    x, y = el.get("x", 0), el.get("y", 0)
    pts = el.get("points") or [[0, 0], [el.get("width", 0), el.get("height", 0)]]
    abs_pts = [(x + p[0], y + p[1]) for p in pts]
    pts_str = " ".join(f"{px},{py}" for px, py in abs_pts)
    stroke = el.get("strokeColor") or "#1e1e1e"
    width = el.get("strokeWidth", 2)
    opacity = (el.get("opacity", 100) or 0) / 100
    out = [
        f'<polyline points="{pts_str}" fill="none" stroke="{stroke}" '
        f'stroke-width="{width}" opacity="{opacity}"{dasharray(el)} />'
    ]
    if el.get("endArrowhead") and len(abs_pts) >= 2:
        tip, prev = abs_pts[-1], abs_pts[-2]
        out.append(_arrow_triangle(tip, (tip[0] - prev[0], tip[1] - prev[1]), stroke))
    if el.get("startArrowhead") and len(abs_pts) >= 2:
        tip, nxt = abs_pts[0], abs_pts[1]
        out.append(_arrow_triangle(tip, (tip[0] - nxt[0], tip[1] - nxt[1]), stroke))
    return "\n".join(out)


def render_text(el: dict) -> str:
    text = el.get("rawText") or el.get("originalText") or el.get("text", "")
    lines = text.split("\n")
    font_size = el.get("fontSize", 20)
    line_h = el.get("lineHeight", 1.25)
    align = el.get("textAlign", "left")
    stroke = el.get("strokeColor") or "#1e1e1e"
    opacity = (el.get("opacity", 100) or 0) / 100
    x, y = el.get("x", 0), el.get("y", 0)
    w = el.get("width", 0)
    if align == "center":
        tx, anchor = x + w / 2, "middle"
    elif align == "right":
        tx, anchor = x + w, "end"
    else:
        tx, anchor = x, "start"
    out = []
    for i, line in enumerate(lines):
        ty = y + font_size * line_h * (i + 0.8)
        out.append(
            f'<text x="{tx}" y="{ty}" font-size="{font_size}" '
            f'font-family="monospace" text-anchor="{anchor}" fill="{stroke}" '
            f'opacity="{opacity}">{esc(line)}</text>'
        )
    return "\n".join(out)


RENDERERS = {
    "rectangle": render_rect,
    "ellipse": render_ellipse,
    "diamond": render_diamond,
    "line": render_linear,
    "arrow": render_linear,
    "text": render_text,
}


def render_svg(scene: dict) -> str:
    elements = [el for el in scene.get("elements", []) if not el.get("isDeleted")]
    if not elements:
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" '
            'viewBox="0 0 100 100"><rect width="100" height="100" fill="#ffffff"/></svg>\n'
        )

    boxes = [bbox_of(el) for el in elements]
    min_x = min(b[0] for b in boxes)
    min_y = min(b[1] for b in boxes)
    max_x = max(b[2] for b in boxes)
    max_y = max(b[3] for b in boxes)
    vb_x, vb_y = min_x - MARGIN, min_y - MARGIN
    vb_w, vb_h = (max_x - min_x) + 2 * MARGIN, (max_y - min_y) + 2 * MARGIN

    frames = [el for el in elements if el["type"] == "frame"]
    others = [el for el in elements if el["type"] != "frame"]

    body = [render_frame(el) for el in frames]
    for el in others:
        renderer = RENDERERS.get(el["type"])
        if renderer is not None:
            body.append(renderer(el))

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{vb_x} {vb_y} {vb_w} {vb_h}" width="{vb_w}" height="{vb_h}">\n'
        f'<rect x="{vb_x}" y="{vb_y}" width="{vb_w}" height="{vb_h}" fill="#ffffff" />\n'
        + "\n".join(body)
        + "\n</svg>\n"
    )


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    in_path, out_path = sys.argv[1], sys.argv[2]
    scene = load_scene(in_path)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(render_svg(scene))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
