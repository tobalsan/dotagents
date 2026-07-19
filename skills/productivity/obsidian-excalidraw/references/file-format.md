# .excalidraw.md file format

A `.excalidraw.md` file is an ordinary Obsidian markdown note that the
obsidian-excalidraw-plugin recognizes and renders as a drawing canvas
instead of (or alongside) prose. Understanding its anatomy matters mainly
for debugging — normal creation/editing should go through the script, not
hand-editing this structure.

## Recognition

A file **is** an Excalidraw file if and only if its YAML frontmatter has an
`excalidraw-plugin` key, with any value. The `.excalidraw.md` filename
suffix is pure convention that humans and tools rely on for discoverability
— the plugin itself never checks the filename. Renaming a file to drop the
suffix does not stop the plugin from opening it; adding the suffix without
the frontmatter key does not make the plugin recognize it either.

Frontmatter value meaning:

| Value | Effect |
|---|---|
| `parsed` | Text elements render as parsed Obsidian markdown — `[[wiki-links]]`, `**bold**`, etc. all work inside the drawing. This is what the script writes by default. |
| `locked` | Same as `parsed` but the file/drawing is locked from casual edits in the plugin UI. |
| `raw` | Text elements render as literal text, no markdown parsing. |

## Section layout

Top to bottom, in the order the plugin's own generator produces (and the
reader tolerates missing sections in this order too — nothing here is
strictly required except the Drawing block):

```
---
excalidraw-plugin: parsed
tags: [excalidraw]
---
<warning banner text>


# Excalidraw Data

## Text Elements
<one entry per text element>

## Element Links
<one entry per non-text element carrying a "link">

%%
## Drawing
```json
{ ...scene JSON... }
```
%%
```

- `# Excalidraw Data` is H1; `## Text Elements`, `## Element Links`,
  `## Embedded Files`, `## Drawing` are H2. The reader's heading match is
  actually `##?` (accepts H1 or H2) plus some legacy header spellings, so
  don't rely on exact heading level when parsing by hand — but always
  *generate* the H1/H2 split above to match the plugin's own output.
- The `%%` line right before `## Drawing`, and the trailing `%%` right after
  the closing fence, wrap **only** the Drawing block in an Obsidian block
  comment. In Obsidian's reading view this hides the raw JSON from view —
  users see the rendered drawing (in Excalidraw view) or nothing (in normal
  markdown reading view), not a wall of JSON. Text Elements and Element
  Links stay outside the comment, so they remain visible/searchable/
  linkable as ordinary markdown text — this is what makes wiki-links inside
  a drawing show up in Obsidian's graph view and search.
- A brand-new/blank drawing legitimately has only frontmatter + the Drawing
  block — no Text Elements, no Element Links section at all. The reader
  tolerates their absence entirely. The script only emits an Element Links
  section when at least one element has a `link`.

## Text Elements section

One entry per non-deleted `text` element:

```
<raw text content> ^<8-char-id>

<raw text content of next element> ^<8-char-id>
```

Entries are separated by a blank line. The `^<id>` suffix is an Obsidian
block reference anchor — it's what lets the plugin's reader match markdown
text back to the JSON element by id (regex hardcoded to exactly 8 chars,
see below). Multi-line text content stays as literal multi-line text
before the `^id` marker.

## Element Links section

One entry per non-deleted, non-text element that carries a `link`:

```
<8-char-id>: [[Some Note]]
```

or a bare URL instead of a wiki-link. Text elements don't appear here even
if they have a link set — a text element's clickable content is its own
rendered markdown (which can itself contain `[[links]]`), not this field.

## Embedded Files section

One entry per file referenced in the scene's `files` dict:

```
<fileId>: [[attachment.png]]
```

Equations use `$$latex$$` instead of a wiki-link; some entries can be a
bare hyperlink. This skill does not generate embedded files — see
`element-schemas.md` for the JSON shape if you need to construct one by
hand.

## The Drawing block

Tab-indented (`json.dumps(..., indent="\t")` — matches the plugin's own
serializer) JSON, fenced as either:

- ` ```json ` — plain, human-readable, always safely readable by the plugin
- ` ```compressed-json ` — `LZString.compressToBase64(jsonString)`, then
  hard-wrapped into 256-char lines (each followed by a blank line —
  cosmetic only, decompression strips all whitespace first)

**Which one is present is determined purely by content** — the plugin
detects compression by checking which fence tag is on the block, not by
reading a setting. The user's "compress on save" plugin setting only
controls what the plugin writes the *next time it saves the file from
inside Obsidian* — it has no bearing on what a file already contains or on
what any external tool is allowed to write.

Practical consequence: **this skill's write path always emits
` ```json ` (uncompressed)**, regardless of the target vault's plugin
settings. The plugin reads it correctly either way, and will silently
recompress it (or not) the next time the user saves inside Obsidian. There
is no reason for a generator to implement compression.

**This skill's read path handles both** — `scripts/excalidraw_md.py read`
checks for a `compressed-json` fence first, decompresses via LZString if
found, and falls back to a plain `json` fence otherwise. You never need to
think about which one a given file has; just call `read`.

## IDs: exactly 8 characters

The plugin's reader matches text-element block refs with a regex hardcoded
to 8 characters: `\s\^(.{8})[\n]+`. The plugin's own id generator is
`nanoid customAlphabet(base62, 8)`. Any element `id` longer or shorter than
8 characters gets **rewritten** to a fresh 8-char id the first time the file
loads in Obsidian (`updateElementIdsInScene`), and every binding, container
reference, and boundElements entry pointing at the old id is patched to
match. This is silent and non-destructive, but means an id you chose won't
survive a round-trip through the Obsidian UI unless it was already 8 chars.
The bundled script always generates compliant 8-char ids — only worry about
this if hand-writing an id yourself.

## Frontmatter keys

`excalidraw-plugin` is the only key that matters for recognition. Others
the plugin understands (all optional, all prefixed `excalidraw-`):

| Key | Purpose |
|---|---|
| `excalidraw-plugin` | **Required.** `parsed`, `locked`, or `raw` (see above). |
| `excalidraw-export-transparent` | Export PNG/SVG with transparent background. |
| `excalidraw-export-dark` | Export using dark theme colors. |
| `excalidraw-export-padding` | Padding (px) around exported image. |
| `excalidraw-export-pngscale` | PNG export scale factor. |
| `excalidraw-onload-script` | JS run automatically when the drawing opens. |
| `excalidraw-link-prefix` | Prefix stripped/added for element links. |
| `excalidraw-default-mode` | Default view mode when opening. |
| `excalidraw-font` | Default font override for the drawing. |
| `excalidraw-font-color` | Default font color override. |
| `excalidraw-open-md` | Open the markdown side instead of the drawing view. |

`tags: [excalidraw]` is convention (helps vault search/tag views find
drawings), not required for plugin recognition.

## Markdown/JSON sync semantics

The two representations aren't fully independent — on load, the plugin
reconciles them with **markdown as authoritative for text content**:

- A text element's `rawText` gets overwritten from what's in the Text
  Elements markdown section, keyed by the `^id` anchor — so if a human
  hand-edits the visible text in Obsidian's markdown view, that edit wins
  over whatever the JSON `rawText`/`text` field said.
- The JSON is authoritative for **structure and existence** — geometry,
  bindings, which elements exist at all. Editing the Text Elements section
  can't add or remove an element, only change existing text content tied
  to a matching id.
- If a text element exists in the JSON but its Text Elements entry is
  missing (e.g. someone deleted the line), that's non-fatal — the plugin
  regenerates the missing entry from JSON on its next save.

Practical consequence: the script always regenerates the full Text
Elements section from the JSON elements on every `write`, so this sync
concern is handled for you — you never need to hand-edit the Text Elements
section separately from the JSON.

## Complete minimal example

```markdown
---

excalidraw-plugin: parsed
tags: [excalidraw]

---
==⚠  Switch to EXCALIDRAW VIEW in the MORE OPTIONS menu of this document. ⚠== You can decompress Drawing data with the command palette: 'Decompress current Excalidraw file'. For more info check in plugin settings under 'Saving'


# Excalidraw Data

## Text Elements
Hello world ^aB3xK9pQ

%%
## Drawing
```json
{
	"type": "excalidraw",
	"version": 2,
	"source": "https://github.com/zsviczian/obsidian-excalidraw-plugin",
	"elements": [
		{
			"id": "Rq7mN2eZ",
			"type": "rectangle",
			"x": 100,
			"y": 100,
			"width": 160,
			"height": 70,
			"angle": 0,
			"strokeColor": "#1e1e1e",
			"backgroundColor": "transparent",
			"fillStyle": "solid",
			"strokeWidth": 2,
			"strokeStyle": "solid",
			"roughness": 1,
			"opacity": 100,
			"groupIds": [],
			"frameId": null,
			"index": null,
			"roundness": {"type": 3},
			"seed": 123456789,
			"version": 1,
			"versionNonce": 987654321,
			"isDeleted": false,
			"boundElements": [{"id": "aB3xK9pQ", "type": "text"}],
			"updated": 1737331200000,
			"link": null,
			"locked": false
		},
		{
			"id": "aB3xK9pQ",
			"type": "text",
			"x": 114,
			"y": 122.5,
			"width": 132,
			"height": 25,
			"angle": 0,
			"strokeColor": "#1e1e1e",
			"backgroundColor": "transparent",
			"fillStyle": "solid",
			"strokeWidth": 2,
			"strokeStyle": "solid",
			"roughness": 1,
			"opacity": 100,
			"groupIds": [],
			"frameId": null,
			"index": null,
			"roundness": null,
			"seed": 234567891,
			"version": 1,
			"versionNonce": 876543219,
			"isDeleted": false,
			"boundElements": [],
			"updated": 1737331200000,
			"link": null,
			"locked": false,
			"text": "Hello world",
			"rawText": "Hello world",
			"originalText": "Hello world",
			"fontSize": 20,
			"fontFamily": 5,
			"textAlign": "center",
			"verticalAlign": "middle",
			"containerId": "Rq7mN2eZ",
			"autoResize": true,
			"lineHeight": 1.25
		}
	],
	"appState": {
		"gridSize": 20,
		"viewBackgroundColor": "#ffffff"
	},
	"files": {}
}
```
%%
```

This matches what `scripts/excalidraw_md.py write` produces from the
minimal input `{"elements": [{"type": "rectangle", "x": 100, "y": 100,
"width": 160, "height": 70, "label": "Hello world"}]}` — field names,
the bidirectional `boundElements`/`containerId` binding, and the computed
text `width`/`height`/position (verified against actual script output)
are exact. Two things are trimmed here for readability: the real
`appState` carries ~15 more cosmetic default fields (current tool, zoom,
grid color, etc. — all optional, all backfilled), and real ids/`seed`/
`versionNonce`/`updated` are randomly generated per run rather than the
fixed illustrative values shown above.
