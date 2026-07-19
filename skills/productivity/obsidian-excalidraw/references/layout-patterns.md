# Layout patterns — worked examples

All examples are minimal-scene shorthand (`{"elements": [...]}`) — the form
you actually write to a temp file and pass to
`scripts/excalidraw_md.py write`. Ids are given explicitly wherever an
element is referenced by `start`/`end` or where the walkthrough needs to
name it; omit ids on unreferenced elements and let the script generate
them.

## Flowchart (top-down, with a decision + labeled loop-back)

CI/CD pipeline: commit → tests → build → deploy staging → manual approval
(diamond) → deploy prod, plus a labeled "fail: fix & retry" loop from
tests back to commit. Nodes are 180×70, stacked with a 80px gap (`y` steps
of 150); the diamond is wider (220) to fit its text.

```json
{
  "elements": [
    {"id": "commit01", "type": "rectangle", "x": 110, "y": 0,   "width": 180, "height": 70, "label": "Commit"},
    {"id": "tests001", "type": "rectangle", "x": 110, "y": 150, "width": 180, "height": 70, "label": "Tests"},
    {"id": "build001", "type": "rectangle", "x": 110, "y": 300, "width": 180, "height": 70, "label": "Build"},
    {"id": "staging1", "type": "rectangle", "x": 110, "y": 450, "width": 180, "height": 70, "label": "Deploy Staging"},
    {"id": "approve1", "type": "diamond",   "x": 90,  "y": 600, "width": 220, "height": 100, "label": "Approved?"},
    {"id": "deploypr", "type": "rectangle", "x": 110, "y": 780, "width": 180, "height": 70, "label": "Deploy Prod"},

    {"type": "arrow", "start": "commit01", "end": "tests001"},
    {"type": "arrow", "start": "tests001", "end": "build001", "label": "pass"},
    {"type": "arrow", "start": "build001", "end": "staging1"},
    {"type": "arrow", "start": "staging1", "end": "approve1"},
    {"type": "arrow", "start": "approve1", "end": "deploypr", "label": "yes"},

    {"type": "arrow", "start": "tests001", "end": "commit01", "label": "fail: fix & retry"}
  ]
}
```

Notes:

- Every arrow above uses `start`/`end` alone — the script computes
  edge-to-edge geometry (`points`, `x`, `y`, `width`, `height`) from the two
  referenced elements' current positions and **always overwrites** them,
  even if you also pass a `points` array yourself. There is no shorthand
  for a bent/routed connector — `start`/`end` only ever produces a straight
  line between the two shapes' edges.
- Consequence for the retry loop: since `commit01` sits directly above
  `tests001`, the straight `tests001 → commit01` line lands exactly on top
  of the forward `commit01 → tests001` arrow, reversed — both render
  correctly as independent arrows (each keeps its own label), just visually
  coincident. That's an acceptable, honest rendering for most flowcharts.
  If a loop must be visually offset (e.g. it spans several rows and would
  otherwise cut through intermediate shapes), skip the `start`/`end`
  shorthand for that one arrow: hand-write `x`, `y`, a multi-point `points`
  path, and the full `startBinding`/`endBinding` objects (format in
  `element-schemas.md` under Bindings) — then manually append `{"id":
  <arrowId>, "type": "arrow"}` to the two bound shapes' own `boundElements`
  arrays, since only the shorthand does that step for you.

## Mind map (radial)

Central topic plus N branches at equal angles, formula:
`angle = 2*pi*i/N`, `x = cx + r*cos(angle)`, `y = cy + r*sin(angle)`.
Center `(cx, cy) = (600, 400)`, `r = 300`, `N = 5`, node size 180×60
(position is the computed point minus half width/height, since `x,y` is
top-left not center). Connectors below are `arrow` elements with both
arrowheads set to `null`, not `line` — a bound arrow re-routes if a node
is later dragged, while a `line` can never bind to a shape in this fork
and would just sit there disconnected.

| i | angle | cos, sin | center (x, y) | top-left (x, y) |
|---|---|---|---|---|
| 0 | 0° | 1.000, 0.000 | 900, 400 | 810, 370 |
| 1 | 72° | 0.309, 0.951 | 693, 685 | 603, 655 |
| 2 | 144° | -0.809, 0.588 | 357, 576 | 267, 546 |
| 3 | 216° | -0.809, -0.588 | 357, 224 | 267, 194 |
| 4 | 288° | 0.309, -0.951 | 693, 115 | 603, 85 |

```json
{
  "elements": [
    {"id": "center01", "type": "ellipse", "x": 510, "y": 370, "width": 180, "height": 60, "label": "Learning in Public"},

    {"id": "branch01", "type": "ellipse", "x": 810, "y": 370, "width": 180, "height": 60, "label": "Blogging"},
    {"id": "branch02", "type": "ellipse", "x": 603, "y": 655, "width": 180, "height": 60, "label": "Open Source"},
    {"id": "branch03", "type": "ellipse", "x": 267, "y": 546, "width": 180, "height": 60, "label": "Social Media"},
    {"id": "branch04", "type": "ellipse", "x": 267, "y": 194, "width": 180, "height": 60, "label": "Feedback"},
    {"id": "branch05", "type": "ellipse", "x": 603, "y": 85,  "width": 180, "height": 60, "label": "Consistency"},

    {"type": "arrow", "start": "center01", "end": "branch01", "startArrowhead": null, "endArrowhead": null},
    {"type": "arrow", "start": "center01", "end": "branch02", "startArrowhead": null, "endArrowhead": null},
    {"type": "arrow", "start": "center01", "end": "branch03", "startArrowhead": null, "endArrowhead": null},
    {"type": "arrow", "start": "center01", "end": "branch04", "startArrowhead": null, "endArrowhead": null},
    {"type": "arrow", "start": "center01", "end": "branch05", "startArrowhead": null, "endArrowhead": null},

    {"id": "sub00001", "type": "rectangle", "x": 1298, "y": 248, "width": 150, "height": 50, "label": "Twitter/X threads"},
    {"id": "sub00002", "type": "rectangle", "x": 1298, "y": 502, "width": 150, "height": 50, "label": "Newsletter"},
    {"type": "arrow", "start": "branch01", "end": "sub00001", "startArrowhead": null, "endArrowhead": null},
    {"type": "arrow", "start": "branch01", "end": "sub00002", "startArrowhead": null, "endArrowhead": null}
  ]
}
```

Sub-nodes fan out from each branch at a **smaller radius around that
branch's own angle**, not around the center — but check for collisions
before picking numbers: estimate each sub-node label's width as
`0.6 * fontSize * charcount`, then require the chord between adjacent
sub-nodes at radius `r2` (`chord ≈ 2 * r2 * sin(Δangle/2)`) to be at least
`max(label widths) + 30`px. If it isn't, grow `r2` rather than shrinking
`Δangle` — squeezing the angle instead is exactly what produces
overlapping labels. Shown above for branch 0 (`branch01`, angle 0°): 2
sub-nodes at ±15° (`Δangle` 30°) around that same angle — "Twitter/X
threads" (18 chars) estimates to `0.6*20*18 = 216px` at the default
fontSize 20, so the 246px budget (216 + 30) needs `r2 ≈ 490`
(`2*490*sin(15°) ≈ 254px`), not the ~175px a naive radius would use.
Repeat the pattern (own angle ± spread, budgeted radius from the branch's
center) for each of the other 4 branches, then run `excalidraw_md.py
check` on the written file and nudge any position it still flags as
overlapping.

Never bind an `arrow`'s `start` and `end` to the same element id — the
script computes a direction vector between the two centers to place the
edge point, and a zero-length vector (same element on both ends) produces
`NaN` coordinates, which is not valid JSON and will break the file.

## Tree / org chart (BFS layers, width-budget siblings)

Each subtree gets a horizontal width budget = max(own node width, sum of
children's budgets); lay siblings left-to-right within their parent's
span, then center the parent over its children. Node 160×60, sibling gap
40 (→ per-leaf budget 200), layer gap 140 (`y` steps).

Example: CEO → 2 directors → 4 managers (2 per director).

```
layer 2 (y=280) leaf centers:  80   280   480   680      (i*200 + 80)
layer 1 (y=140) director centers: avg of its 2 children:  180        580
layer 0 (y=0)   CEO center: avg of the 2 directors:              380
```

```json
{
  "elements": [
    {"id": "ceo00001", "type": "rectangle", "x": 300, "y": 0,   "width": 160, "height": 60, "label": "CEO"},

    {"id": "dir00001", "type": "rectangle", "x": 100, "y": 140, "width": 160, "height": 60, "label": "Director, Eng"},
    {"id": "dir00002", "type": "rectangle", "x": 500, "y": 140, "width": 160, "height": 60, "label": "Director, Sales"},

    {"type": "rectangle", "id": "mgr00001", "x": 0,   "y": 280, "width": 160, "height": 60, "label": "Mgr, Backend"},
    {"type": "rectangle", "id": "mgr00002", "x": 200, "y": 280, "width": 160, "height": 60, "label": "Mgr, Frontend"},
    {"type": "rectangle", "id": "mgr00003", "x": 400, "y": 280, "width": 160, "height": 60, "label": "Mgr, SMB"},
    {"type": "rectangle", "id": "mgr00004", "x": 600, "y": 280, "width": 160, "height": 60, "label": "Mgr, Enterprise"},

    {"type": "arrow", "start": "ceo00001", "end": "dir00001"},
    {"type": "arrow", "start": "ceo00001", "end": "dir00002"},
    {"type": "arrow", "start": "dir00001", "end": "mgr00001"},
    {"type": "arrow", "start": "dir00001", "end": "mgr00002"},
    {"type": "arrow", "start": "dir00002", "end": "mgr00003"},
    {"type": "arrow", "start": "dir00002", "end": "mgr00004"}
  ]
}
```

Every hand-picked id above (`ceo00001`, `dir00001`, `mgr00003`, ...) is
exactly 8 characters — count before using an invented id rather than
eyeballing it; a 7- or 9-char id still works locally but gets silently
rewritten (with all its bindings) the first time the file opens in
Obsidian, per the id rule in `file-format.md`.

## Editing an existing drawing: append relative to an anchor

Never rebuild a scene from scratch to add one element — `read`, locate the
anchor element you're placing new content relative to, compute a position
offset from it, and `write` the **full** elements array (untouched old
elements + new ones appended).

```bash
uv run <skill-dir>/scripts/excalidraw_md.py read Excalidraw/mini.excalidraw.md > /tmp/scene.json
```

In the JSON, find the anchor by its rendered text (e.g. search elements
for `"text": "Done"` on a `text` element, then note its `containerId` —
that's the actual ellipse/shape id) or by inspecting extents (max `x +
width` across all elements gives the current right edge of the drawing, a
safe place to add new content without overlapping anything).

Then edit `/tmp/scene.json`: keep every existing element as-is (they
already carry a `seed` field, so the script passes them through
unmodified), and append new minimal-shorthand elements that reference the
anchor's id:

```json
{
  "elements": [
    /* ...unchanged elements from read, including the "Done" ellipse
       whose id is e.g. "dOne0001"... */
    {"type": "rectangle", "id": "ship0001", "x": 620, "y": 140, "width": 160, "height": 70, "label": "Ship it"},
    {"type": "arrow", "start": "dOne0001", "end": "ship0001", "label": "celebrate"}
  ]
}
```

`x` above is picked as `<Done ellipse's x + width> + 80` (a clear gap to
its right) — compute it from the actual anchor's fields you read, don't
guess. Write it back to the same path:

```bash
uv run <skill-dir>/scripts/excalidraw_md.py write Excalidraw/mini.excalidraw.md /tmp/scene.json
```

Then `read` again to confirm the element count grew by exactly 2 (the
rectangle + its label text) plus 1 arrow, and that nothing pre-existing
disappeared.
