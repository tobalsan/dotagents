# Excalidraw element schemas

Full field reference for the scene JSON's `elements` array. This documents
what the plugin actually expects/reads; `scripts/excalidraw_md.py` fills
most of it in for you when you write minimal-scene shorthand (see SKILL.md).
Read this file when the shorthand contract doesn't cover a field you need,
or when hand-inspecting/debugging JSON read back from an existing drawing.

## Auto-fill note

Columns marked **auto** below are filled by the script's `normalize()` step
when omitted from your minimal-scene input — you never need to supply them
unless you want a non-default value. Everything else is either required or
has a shorthand.

## Base fields (every element)

| Field | Type | Auto | Notes |
|---|---|---|---|
| `id` | string, 8 chars | yes | random if omitted |
| `type` | string | — | required, see per-type tables below |
| `x`, `y` | number | yes → 0 | top-left corner, absolute px |
| `width`, `height` | number | yes (type-dependent default) | |
| `angle` | number | yes → 0 | radians |
| `strokeColor` | hex string | yes → `#1e1e1e` | |
| `backgroundColor` | hex string | yes → `transparent` | |
| `fillStyle` | enum | yes → `solid` | `solid`\|`hachure`\|`cross-hatch` |
| `strokeWidth` | number | yes → 2 | |
| `strokeStyle` | enum | yes → `solid` | `solid`\|`dashed`\|`dotted` |
| `roughness` | number 0-2 | yes → 1 | 0=architect (clean), 1=artist, 2=cartoonist (sketchier) |
| `opacity` | number 0-100 | yes → 100 | |
| `seed` | number | yes | random int; presence of this field is how the script detects an already-complete element and passes it through untouched |
| `version` | number | yes → 1 | |
| `versionNonce` | number | yes | random int |
| `index` | fractional-index string \| null | yes → `null` | leave `null` — the plugin's own loader (`restoreElements`) assigns a valid fractional index from array order; don't fabricate one |
| `isDeleted` | boolean | yes → `false` | set `true` to soft-delete instead of removing from the array (preserves bindings/history) |
| `groupIds` | string[] | yes → `[]` | shared id(s) across all elements in a group — see Groups below |
| `frameId` | string \| null | yes → `null` | id of the `frame` element this belongs to — see Frames below |
| `boundElements` | `{id, type}[]` \| null | yes → `[]` | reverse pointers — see Bindings below |
| `updated` | epoch ms | yes | |
| `link` | string \| null | yes → `null` | URL or `[[wiki-link]]`; non-text elements only meaningfully use this (see Element Links section in file-format.md) |
| `locked` | boolean | yes → `false` | |
| `roundness` | `null` \| `{type, value?}` | yes (type-dependent default) | see Roundness below |

## Type-specific fields

### text

| Field | Notes |
|---|---|
| `text` | current display text (may equal `rawText` if `parsed` mode with no unresolved markdown) |
| `rawText` | source-of-truth text content; the Text Elements markdown section is generated from this and can overwrite it back on next Obsidian load |
| `originalText` | pre-wrap text, same content as `rawText` in practice for generated files |
| `fontSize` | default 20 |
| `fontFamily` | default 5 (Excalifont) — see Font families below |
| `textAlign` | `left`\|`center`\|`right`, default `left` (script sets `center` for shape/arrow labels) |
| `verticalAlign` | `top`\|`middle`\|`bottom`, default `top` (script sets `middle` for labels) |
| `containerId` | id of the shape this text is bound inside, or `null` for a free-floating text element |
| `autoResize` | `true` — box grows to fit text |
| `lineHeight` | default 1.25 |
| `roundness` | always `null` for text |

Width/height for a `text` element should reflect the rendered text size, or
the plugin's self-healing will look wrong until it's resized. Estimate:
`width ≈ max_line_len_chars * fontSize * 0.6`, `height ≈ num_lines * fontSize * 1.25`.

### rectangle / diamond / ellipse

| Field | Notes |
|---|---|
| `width`, `height` | default 100×100 |
| `roundness` | rectangle default `{"type": 3}`; diamond/ellipse default `{"type": 2}` |

No other type-specific fields — these are pure containers. Use the `label`
shorthand to attach centered bound text (see SKILL.md), or set
`boundElements`/a separate `text` element with matching `containerId`
manually.

### arrow / line

| Field | Applies to | Notes |
|---|---|---|
| `points` | both | array of `[x, y]` **relative to the element's own `x,y`** (local points), first is always `[0,0]` |
| `startBinding`, `endBinding` | both | `null` or binding object (see Bindings below); `line` can bind too, not just `arrow` |
| `startArrowhead`, `endArrowhead` | both | arrowhead type or `null` — see Arrowheads below. `line` defaults both to `null` (no heads); `arrow` defaults `startArrowhead: null, endArrowhead: "arrow"` |
| `polygon` | line only | boolean, whether the line is a closed polygon |
| `elbowed` | arrow only | boolean, whether it routes with right-angle elbow bends instead of a straight/curved line — default `false` |
| `roundness` | both | default `{"type": 2}` (curved corners on multi-point lines) |

Use the `start`/`end` shorthand (element ids) to have the script compute
`points`, `x`/`y`, `width`/`height`, and both bindings for you — see
SKILL.md and Bindings below. Hand-write `points` only for a free-floating
arrow/line not touching any shape, or a multi-segment path.

### freedraw (advanced — not generated by this skill)

`points`, `pressures`, `simulatePressure`, `strokeOptions`. Hand-drawn ink
strokes; there's no sensible way to synthesize these programmatically. The
script exits with an error if asked to fill a `freedraw` element missing a
`seed` (i.e. not already-complete). If a `read` result contains one, leave
it in the array untouched when you write back.

### image (advanced — not generated by this skill)

| Field | Notes |
|---|---|
| `fileId` | key into the top-level `files` dict |
| `status` | `pending`\|`saved`\|`error` |
| `scale` | `[1, 1]` |
| `crop` | `null` or crop rect |

Requires a matching entry in the scene's top-level `files` dict:
`{fileId: {mimeType, id, dataURL, created}}`, and typically an Embedded
Files markdown section entry. The script does not fill `image` elements
(no `seed` → error) — construct these by hand only if truly needed, or
have the user drag the image in via the Obsidian UI, which is far simpler.

### embeddable / iframe

`scale` field for embedded web content. Not covered by this skill's
shorthand; rare in practice.

### frame

| Field | Notes |
|---|---|
| `name` | string label shown on the frame, or `null` |
| `width`, `height` | default 400×300 |
| `roundness` | always `null` |

Frames are visual/organizational grouping containers (like a labeled
region). **Frames do not list their children** — membership is the reverse:
each child element sets its own `frameId` to the frame's id. To put shapes
in a frame, create the `frame` element with an explicit `id`, then set
`"frameId": "<that id>"` on every element that should be inside it.

## Bindings

### Arrow ↔ shape (current fork format)

```json
"startBinding": {"elementId": "<shapeId>", "fixedPoint": [0.5, 1.0], "mode": "orbit"},
"endBinding":   {"elementId": "<shapeId>", "fixedPoint": [0.5, 0.0], "mode": "orbit"}
```

- `fixedPoint` is a **normalized [0..1] anchor within the bound element's
  own bounding box** — `[0,0]` is the shape's top-left corner, `[1,1]` its
  bottom-right, `[0.5,0.5]` its center. This is how the arrow endpoint
  stays attached to the correct edge point as the shape moves/resizes.
- `mode` is `"inside"` (arrow tip touches the shape's edge, standard),
  `"orbit"` (small gap maintained, what the plugin's own `addArrow` and
  this skill's script both emit), or `"skip"` (binding recorded but no
  visual snap).
- An older `{elementId, focus, gap}` shape exists in files created by very
  old plugin versions — the plugin's loader (`restoreElements`) migrates
  it automatically to the `fixedPoint`/`mode` format on load. Never emit
  the old format yourself.

**Bidirectional consistency is required**: whenever an arrow has a
`startBinding`/`endBinding` pointing at a shape, that shape's own
`boundElements` array must contain `{"id": "<arrowId>", "type": "arrow"}`.
If you hand-edit bindings instead of using the `start`/`end` shorthand, you
must update both sides yourself or the plugin's rendering/dragging behavior
will be inconsistent (arrow may not follow the shape).

### Text-in-container

```json
// on the container (rectangle/diamond/ellipse/arrow):
"boundElements": [{"id": "<textId>", "type": "text"}]

// on the text element:
"containerId": "<containerShapeId>"
```

Exactly **one** text binding per container — the plugin prunes duplicates
on load if more than one text element claims the same `containerId`. Valid
container types: `rectangle`, `diamond`, `ellipse`, `arrow` (a label on the
arrow's midpoint). Use the `label` shorthand rather than constructing this
by hand.

## Groups

`groupIds: string[]` — elements sharing an id in this array are grouped
together in the Excalidraw UI (select one, select all). An element can be
in multiple nested groups (array order = nesting, outermost last... consult
actual plugin behavior if nesting matters; for a flat single group, all
members just share one id). There's no separate "group" element type — the
grouping is purely this shared-id convention across ordinary elements.

## appState

Only two fields are truly required; everything else is backfilled by the
plugin's own defaults on load:

```json
{"gridSize": null, "viewBackgroundColor": "#ffffff"}
```

Add `"theme": "dark"` to open the drawing in dark mode. The script's
default `appState` includes many more cosmetic fields (current tool
selection, zoom, grid settings) matching what the plugin itself writes —
you don't need to supply any of them; `normalize()` merges your `appState`
over its defaults.

## files

Top-level dict, `{}` if the drawing has no images/embeds:

```json
"files": {
  "<fileId>": {
    "mimeType": "image/png",
    "id": "<fileId>",
    "dataURL": "data:image/png;base64,...",
    "created": 1737331200000
  }
}
```

## Value enums

| Field | Values |
|---|---|
| `fillStyle` | `solid`, `hachure` (sketchy diagonal lines), `cross-hatch` |
| `strokeStyle` | `solid`, `dashed`, `dotted` |
| `roughness` | `0` (architect, clean/precise), `1` (artist, default hand-drawn feel), `2` (cartoonist, very sketchy) |
| `roundness` | `null` (sharp corners) or `{"type": N}` — `2` = shapes/lines (adaptive radius), `3` = rectangles (fixed radius); text is always `null` |
| `fontFamily` | `1` Virgil (old hand-drawn font), `2` Helvetica, `3` Cascadia (code), `4`-`8` additional bundled fonts; **`5` is the default (Excalifont)** — use unless the user asks for a specific look |
| `startArrowhead` / `endArrowhead` | `null` (none), `"arrow"`, `"triangle"`, `"bar"`, `"dot"`, `"circle"`, `"diamond"` |
| `textAlign` | `left`, `center`, `right` |
| `verticalAlign` | `top`, `middle`, `bottom` |
