# The made thing

Pass 6: one picture only this business could show, where the gradient card with the fake dashboard used to be. Pick
the first of these the business can actually support.

## 1. The real product

The best picture of a product is the product.

- **Software:** a true screen in a real, interesting state (a route being changed, an invoice half-reconciled), not
  the empty state and not a redrawn "dashboard". Capture it at 2x from the running app. Crop to the part that
  matters; a whole browser window shrinks to mush. If you rebuild the interface in HTML so it can be live on the
  page, copy the real one: real labels, real units, plausible values the owner approves.
- **Physical things:** the owner's own photographs, on one consistent ground. Ask for them. One good photograph
  beats a carousel.
- Never an AI-generated picture of a product that exists. It will be wrong in ways the owner's customers notice.

## 2. Something they own, drawn

If there is no product to photograph, there is usually data or a process.

- A map of where they operate, with their real routes or sites. Dots and lines in SVG, one accent.
- Their process as a diagram with their real step names and real durations.
- A log or a table of what the product did, with true-looking rows the owner signs off.

Draw it in SVG or plain HTML and CSS so it stays sharp and can move a little (a line that draws in, a counter). Keep
it to ground, ink and the accent.

**Before launch, with no data yet:** draw how the product works rather than what it has done. A schematic of the
mechanism (inputs, the decision, the result) with the real names of the steps is honest as long as it cannot be
mistaken for a record. Use shapes and labels, not rows of figures, and caption it as what it is: "How it works.
Not real data." If you find yourself typing a plausible number, stop.

## 3. A rendering of what they make or move

When the subject is physical and there are no photographs, a rendered object can carry the page: a container for a
freight company, a part for a machine shop, the bottle for a drink.

If the owner has a 3D model (`.glb`, `.obj`, `.fbx`, `.stl`, a CAD export), and Blender is installed:

```bash
blender -b -P <skill-dir>/scripts/studio-render.py -- --model product.glb --out hero.png --res 1600 --turn 30
```

That writes a transparent PNG: the model centred, soft key light from the upper left, a rim, a low fill. `--turn`
spins it, `--tilt` raises the camera, `--tint FF4A12` paints an untextured model one colour. It uses Cycles on the
CPU, so it runs anywhere Blender does, slowly (minutes per still). Put a soft shadow under it in CSS
(`filter: drop-shadow(0 22px 26px rgba(40,20,5,.2))`) so it sits on the page.

For a sequence (a slow turn), render `--turn` from 0 to 360 in steps and play the frames; for a loop that has to be
seamless, turn by exactly the model's symmetry (a quarter turn for a box).

If there is no model, building one is a real job. Simple, recognisable objects are within reach of a script (a box
with pressed sides, a bottle, a sign); organic or branded shapes are not. Say which it is before starting, and do not
render a vague blob to fill the space.

## 4. Drawn lettering

When the brand is new and has nothing, the name itself can be the made thing: a wordmark or a headline drawn as
shapes rather than typed in a font, so the forms can be whatever the page needs.

- Build each letter from a few arcs and stems of one weight on a shared grid (an x-height, one stroke width, one bowl
  radius). Lowercase geometric letters need surprisingly few parts.
- Give it two or three decisions a font would not make: a leaning bar on the e, a ligature, a mark for the dot.
- Output SVG paths. Set the rest of the page in an ordinary, well-chosen family; the lettering is for the one line.
- Only draw the letters you need.

This is slower than it sounds. If the brand already has a typeface or a logo, use it and skip this.

## What does not count

- A gradient, a mesh, an abstract 3D shape, particles, a globe. They are about nothing.
- Stock photography of people pointing at laptops.
- A generated illustration in the house style of every other generated illustration.
- A product screen that was invented for the page.

## Putting it on the page

- Let it be large. If it is the made thing, it should be the biggest object on the first screen or share that with
  the headline.
- Let it touch the type: crop it off an edge, pin a caption to a part of it, or run a line of the headline behind
  it. Pass 7 in SKILL.md says how to build each.
- Give it one true caption if it needs explaining, in the small label style.
- Export at 2x, compress (WebP or AVIF), set width and height so the layout does not jump, and write a real `alt`.
