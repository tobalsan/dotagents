---
name: codex-imagegen
description: Generate images by delegating to Codex imagegen. Use when user asks to generate/create a raster image, JPG/PNG, diagram, infographic, visual, mockup, or other bitmap asset via codex exec, with output saved to a user-specified directory or ~/Downloads by default.
---

# Codex Imagegen

Use user-specified output dir. If none given, default to `~/Downloads`.

```bash
OUT_DIR="<user-dir-or-~/Downloads>"
codex exec --model gpt-5.5 -c model_reasoning_effort=low --add-dir "$OUT_DIR" "Generate an image: <image request>. Use the image generation skill / imagegen path. Output final file exactly to $OUT_DIR/<name>.jpg. <constraints>."
```

Rules:
- Start prompt with `Generate an image:`.
- Include `Use the image generation skill / imagegen path`.
- Include exact output path in chosen `OUT_DIR`.
- Include `--add-dir "$OUT_DIR"` so Codex can write there.
- Prefer `gpt-5.5` and `model_reasoning_effort=low`.
- If Codex saves PNG under `~/.codex/generated_images/...`, convert/copy to requested filename:

```bash
sips -s format jpeg ~/.codex/generated_images/<session>/<file>.png --out "$OUT_DIR/<name>.jpg"
```

After run, verify:

```bash
file "$OUT_DIR/<name>.jpg" && ls -lh "$OUT_DIR/<name>.jpg"
```
