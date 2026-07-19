---
name: obsidian-excalidraw
version: "1.0.0"
description: >
  Use this skill whenever the user wants Claude to create or edit an Excalidraw
  drawing that lives inside an Obsidian vault — a mind map, flowchart, diagram,
  sketch, whiteboard, visual map, or org chart saved as a .excalidraw.md file
  (obsidian-excalidraw-plugin format). Treat "make a mind map / flowchart /
  diagram of X in my vault/Obsidian", "sketch this out in Excalidraw", "add a
  node to my <name>.excalidraw.md drawing", or any request to visually map
  ideas, processes, or hierarchies inside Obsidian as a trigger — the user
  wants an actual file written, not a description. Also trigger for editing,
  extending, or fixing an existing .excalidraw.md drawing (adding shapes,
  rewiring arrows, relabeling nodes) without breaking elements the request
  doesn't mention. Skip for: plain Mermaid diagrams embedded in a normal
  markdown note (no .excalidraw.md involved), questions about the excalidraw.com
  web app or desktop app unrelated to Obsidian, and general Obsidian vault
  operations that don't involve drawings (use obsidian-cli for those).
triggers:
  - "excalidraw"
  - "mind map"
  - "flowchart"
  - "flow chart"
  - "diagram"
  - "sketch"
  - "whiteboard"
  - "visual map"
  - "org chart"
  - "org chart in obsidian"
  - "draw this in obsidian"
  - "excalidraw.md"
  - "excalidraw plugin"
  - "add a node to my drawing"
  - "connect these with an arrow"
---

# Obsidian Excalidraw

Creates and edits `.excalidraw.md` files — Obsidian notes that the
[obsidian-excalidraw-plugin](https://github.com/zsviczian/obsidian-excalidraw-plugin)
renders as a drawing. The file is markdown with an embedded Excalidraw scene
(JSON), so it works whether or not the plugin is installed, but only renders
visually inside Obsidian.

All reading and writing goes through the bundled script — never hand-write
the markdown or JSON yourself. The script fills in required boilerplate
(ids, seeds, versions, bindings) that the plugin needs to load the file
without errors.

```bash
uv run <skill-dir>/scripts/excalidraw_md.py read  <target>.excalidraw.md
uv run <skill-dir>/scripts/excalidraw_md.py write <target>.excalidraw.md <scene.json>
uv run <skill-dir>/scripts/excalidraw_md.py check <target>.excalidraw.md
```

`uv run` picks up the script's inline dependency metadata — no install step,
no venv setup. Replace `<skill-dir>` with this skill's absolute path.

## Workflow

**1. Locate the vault and target path.** Ask or infer the vault root, then
check whether the vault already has an `Excalidraw/` folder or existing
`.excalidraw.md` files (`find <vault> -name '*.excalidraw.md'`) — put new
drawings alongside them for consistency. If nothing exists yet, `Excalidraw/`
at the vault root is the common convention. The plugin recognizes a file as
a drawing by the `excalidraw-plugin` frontmatter key (any value), not by the
filename — `.excalidraw.md` is convention only, but keep it: users and other
tools rely on it too. Never hardcode a specific vault path in anything you
write; always take it from context or ask.

**2. Design the scene as minimal JSON.** Write `{"elements": [...]}` using
the shorthand contract below — absolute pixel coordinates you compute
yourself (see Layout, this is where most agent-generated diagrams go wrong).

**3. Write it.**

```bash
uv run <skill-dir>/scripts/excalidraw_md.py write <target>.excalidraw.md /tmp/scene.json
```

If `<target>` doesn't exist yet, the script creates it with default
frontmatter (`excalidraw-plugin: parsed`). If it exists, frontmatter is
preserved untouched and only the Drawing section is replaced.

**4. For edits to an existing drawing:** `read` first, modify the returned
JSON, `write` back the full element list (old elements you didn't touch,
plus new/changed ones).

```bash
uv run <skill-dir>/scripts/excalidraw_md.py read <target>.excalidraw.md > /tmp/scene.json
# edit /tmp/scene.json
uv run <skill-dir>/scripts/excalidraw_md.py write <target>.excalidraw.md /tmp/scene.json
```

`read` always emits plain JSON on stdout regardless of whether the file's
Drawing block was compressed — the script decompresses transparently.
**Never delete or drop an element you don't understand** (e.g. `freedraw`
strokes, `image` elements — see Scope below): the script passes already-complete
elements through untouched (it detects them by the presence of a `seed`
field) as long as they stay in the array you write back. If the user asks
to remove something, set `"isDeleted": true` on it instead of omitting it —
this matches how the plugin itself soft-deletes, and avoids orphaning
bindings that still reference the element's id.

## Why uncompressed JSON is always safe to write

The plugin detects compression by which fence tag is present
(` ```compressed-json ` vs ` ```json `), not by a setting. It reads either
one on load, and only *writes* compressed on the user's next in-app save if
their settings say to compress. So this skill always writes a plain
` ```json ` block — simpler to generate and to reason about — and lets the
plugin recompress it later if the user's settings want that. You never need
to compress anything yourself.

## The minimal-scene contract

Every element needs only `type` plus the fields particular to it — the
script fills defaults for everything else (colors, stroke settings, seeds,
version numbers, etc.). Full per-type field tables are in
`references/element-schemas.md`; the essentials:

| Field | Applies to | Notes |
|---|---|---|
| `type` | all | `rectangle`, `diamond`, `ellipse`, `text`, `arrow`, `line`, `frame` |
| `x`, `y` | all | absolute px, top-left corner. Required — you compute these. |
| `width`, `height` | shapes, frames | default 100×100 if omitted |
| `text` | text elements | required for `type: text` |
| `id` | any | optional — auto-generated 8 chars if omitted. **Give explicit ids to anything you'll reference** (as an arrow endpoint, frame child, etc.) so you can wire it up in the same scene. |
| `label` | rectangle/diamond/ellipse/arrow | shorthand: generates a bound, centered text child automatically — do not hand-build the text element + binding yourself |
| `start`, `end` | arrow | shorthand: element **ids** (not coordinates) of what the arrow connects. Expands to real geometry, `fixedPoint` bindings on both ends, and reverse `boundElements` entries on the bound shapes. |

Styling fields (`strokeColor`, `backgroundColor`, `fillStyle`, `strokeWidth`,
`roughness`, `opacity`, `fontSize`, `fontFamily`, `startArrowhead`/
`endArrowhead`, `strokeStyle`) are all optional with sane Excalidraw
defaults — only set them when the user asks for a specific look (e.g. "red
error box", "dashed arrow").

### Why 8-char ids matter

The plugin's markdown reader locates each text element's block-ref anchor
with a regex hardcoded to exactly 8 characters (`^${id}` at 8 chars). Any
id longer or shorter gets silently rewritten to a fresh 8-char id when the
file loads in Obsidian, and every binding pointing at the old id is repaired
along with it — but only if the plugin's own reconciliation runs, which
means round-tripping through Obsidian once. Save yourself the surprise:
the script always generates correct 8-char ids, so only pass explicit `id`
values that are exactly 8 base62 characters (letters+digits) if you set them
by hand, and prefer letting the script generate them.

## Layout guidance

Nothing validates overlaps or off-canvas placement — bad coordinates just
produce a broken-looking drawing with no error. Compute layout explicitly;
don't eyeball it.

**Text width budget**: estimate a text/label's width as
`0.6 * fontSize * max_line_length_chars` (matches the script's own
estimate) so containers you size by hand don't clip their label.

**Flowchart (top-down)**: nodes ~160-220w × 60-80h, stacked with ~80-100px
vertical gap between rows. Decision nodes (`diamond`) run wider (~200-260)
to fit yes/no text without crowding. Branches that must re-converge (e.g. a
retry loop back to an earlier node) route as a separate arrow with explicit
`start`/`end` ids — do not try to reuse or bend an existing arrow.

**Mind map (radial)**: one central node at `(cx, cy)`. Place N branch nodes
at equal angles around it: `angle = 2*pi*i/N`, `x = cx + r*cos(angle)`,
`y = cy + r*sin(angle)`, with `r` ≈ 250-350. Connect center→branch with
`arrow` and `startArrowhead: null, endArrowhead: null` (looks like a plain
line but stays bound — `line` elements can never bind to shapes in this
fork, so a `line` connector won't follow a node the user drags later). Fan
sub-nodes out further from each branch at a smaller radius (~150-200)
around that branch's own angle, not around the center — but budget for
label width first (see `references/layout-patterns.md`): if a branch's
sub-node labels are wide, grow that branch's radius rather than shrinking
the angles between them, or labels overlap.

**Tree / org chart**: BFS by layer — root at top, each layer y += ~120-150.
Within a layer, give each subtree a horizontal width budget (max of its own
node width and the sum of its children's budgets) and lay siblings out
left-to-right without their budgeted ranges overlapping.

See `references/layout-patterns.md` for worked scene JSON for all three
patterns, plus an editing example (append to an existing drawing).

## Wiki-links

Put `[[Note Name]]` directly inside a `text`/`label` string — the frontmatter
sets `excalidraw-plugin: parsed`, so the plugin renders these as live
Obsidian links (clickable, appear in graph view, resolve on rename). For a
link on a *non-text* element (e.g. clicking a rectangle navigates
somewhere), set that element's `"link"` field instead — the script writes
it into the Element Links markdown section automatically.

## Scope

In scope: rectangles, diamonds, ellipses, text, arrows, lines, bound
container labels, arrow bindings, frames, groups (`groupIds`), wiki-links,
editing existing drawings.

Out of scope / advanced: `freedraw` (hand-drawn strokes) and `image`/
embedded-file elements cannot be generated by the script (it exits with an
error if asked to fill a type it doesn't recognize) — `references/element-schemas.md`
documents their JSON shape for reference, but construct them manually if
truly needed, or tell the user to add these in the Obsidian UI instead.

## Verify

After every `write`, run the checker and fix whatever it reports:

```bash
uv run <skill-dir>/scripts/excalidraw_md.py check <target>.excalidraw.md
```

It reports overlapping element bounding boxes and connectors that didn't
bind — nudge positions or fix ids until it comes back clean. For a complex
diagram, or one the user will scrutinize closely, also render a quick
visual check:

```bash
uv run <skill-dir>/scripts/render_svg.py <target>.excalidraw.md preview.svg
```

Also `read` the file back and sanity-check: element count matches
expectations, no error on stdout, ids referenced by `start`/`end` or
`containerId` actually resolve. Tell the user the path written and
suggest opening it in Obsidian (switch to Excalidraw view if it opens as
raw markdown first).

## Reference files

- `references/file-format.md` — full `.excalidraw.md` anatomy: sections,
  frontmatter keys, compression, markdown/JSON sync rules. Read when
  something about file structure or recognition is unclear, or you're
  debugging why a file won't open.
- `references/element-schemas.md` — complete field reference per element
  type, binding formats, frames, groups, style enums. Read when you need a
  field the shorthand contract above doesn't cover.
- `references/layout-patterns.md` — worked example scenes (flowchart, mind
  map, tree) and an edit-existing-drawing pattern. Read before building
  anything beyond a trivial 2-3 node drawing.
