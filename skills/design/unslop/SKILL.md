---
name: unslop
description: >-
  Use when asked to unslop a website, or to make a landing page stop looking AI-generated, vibecoded or templated.
  Takes a URL, a file or the project you are in, and fixes it in ten ordered passes.
---
# Unslop

Takes a website that looks generated and makes it look like someone meant it. The work is ten passes, in order,
each with a test for "done". Run it as `/unslop`, `/unslop https://example.com` or `/unslop path/to/site`.

The site to work on is whatever came with the request: a URL, a file, a folder. If nothing came, it is the project in
the working directory.

**What you leave behind:** the fixed page, a before and after picture, the audit score before and after, and a short
list of what you could not do without the owner (facts to confirm, pictures to supply).

## Rules that hold through every pass

1. **Never invent facts.** No customer counts, logos, testimonials, awards, ratings, uptime or savings that the site's
   owner has not given you. If a claim on the page cannot be checked, cut it or ask. An honest gap beats a made-up number.
2. **Do not swap slop for different slop.** No new gradient, glow, glass card, blob, emoji icon, stock illustration,
   AI-generated picture or 3D blob. If you are reaching for decoration, the pass is not finished.
3. **Keep what works.** Routes, forms, analytics, structured data, accessibility attributes, and the brand's own
   name, logo, colours and typeface if it has them. This is a redesign of the surface, not of the business.
4. **One pass, one change set.** If the project is in git, commit after each pass with the pass's name. Small diffs can
   be reviewed and undone; one giant rewrite cannot. A pass that changes nothing gets no commit: say in the hand-over
   that you skipped it and why.
5. **Ask once, early, briefly.** At most one round of questions before you start (see step 0). If the answers are not
   there, go ahead with the cautious choice and list the open point in the hand-over.
6. **The owner's word beats the page.** If they tell you the name, the offer or the audience and the page says
   something else, use what they said and list the difference in the hand-over.
7. **The home page first.** Work on the first screen and the section under it. Ask before touching other pages.

## 0. Look before touching anything

Find out which case you are in:

- **You have the code** (the usual case). Find the page's entry (`index.html`, `app/page.tsx`, `pages/index.*`,
  `src/App.*`, a template) and how to run it (`package.json` scripts, or open the file).
- **You only have a URL.** You cannot edit their site. Rebuild the page as static HTML and CSS in a new `unslopped/`
  folder, carrying over their real content, and hand over the list of changes for them to apply.
- **You only have a picture.** Do the audit by eye and hand over a prioritised list of changes. No code.

Then capture the "before" and read the tells:

```bash
node <skill-dir>/scripts/audit.mjs <url | file | folder>          # add --browser if the page is built by JavaScript
node <skill-dir>/scripts/shots.mjs <url | file> unslop-out --name before
```

(`<skill-dir>` is the folder of this file. Examples: `~/.pi/agent/skills/unslop`, `~/.agents/skills/unslop`.
`shots.mjs`, `check.mjs` and `--browser` need a Playwright package that Node can find. If Node cannot find one, do
not install it. Use your browser testing skill or tool instead, for example `buu`. Take the same screenshots and do
the same checks with it. With no browser tool, skip the pictures and say so.)

`unslop-out/` is your working folder, not part of the site: add it to `.gitignore` before the first commit. Take more
pictures whenever you want to see a pass (`--name pass-7`). The mobile picture is taken at 2x, so it is 780 px wide
for a 390 px screen.

Look at `before-desktop.png` and `before-mobile.png` yourself. The audit reads text, not pixels; it will not notice a
weak picture or a page with no hierarchy. [tells.md](tells.md) lists every tell, why it reads as generated, and which
pass removes it.

Before you start, you need three things. Read them off the site if you can; ask only for what you cannot find:

1. What does this business do, for whom, in one plain sentence?
2. What is true and checkable about it (numbers, customers, results) that may be said?
3. What real material exists: product screens, photos, a 3D model, data, a logo, brand colours, a typeface?

## The passes

Do them in this order. The first five are the basics and every site gets them. The last five are what separate
"cleaned up" from "designed".

### 1. Declutter
Remove what is there because a template had a slot for it. The announcement pill above the headline. Emoji. The
second and third call to action. Blurred colour blobs and glass cards. The fast / secure / scalable feature cards,
unless each one says something only this product could say. Stars, "trusted by" lines and stat rows nobody can check.
Navigation beyond five items. The made-up dashboard in the hero goes now too: leave its space empty, or a plain box
that says what will go there, until pass 6.

Links that go nowhere (`href="#"`): point them at the real page or section if there is one, and remove the rest. A
button with no destination yet stays only if it is the primary action, and goes on the owner's list.
**Done when:** the first screen has one headline, one supporting line, one primary action (at most one quiet second
one), and at most five navigation items, and nothing on it would survive being moved to a competitor's site unchanged.
The same action repeated in the header and in the hero counts as one.

### 2. Copy
The headline says what it does for whom, in about eight words, with a concrete noun and a verb. The supporting line
is one sentence with one specific in it. The button says what happens next ("Book a demo", "Get a quote", "See
pricing"), not "Get Started". Cut every word on the banned list in [tells.md](tells.md). Rename things that were
named by a template.

Before launch, the honest button is the one that is true: "Join the waitlist" or "Request early access", and only if
pressing it does that (a form, a mailto, a booking link). If nothing is wired up, say so in the hand-over; do not
leave a button that pretends.

The page title and meta description are copy too. Keep the tags, rewrite the words to match the new headline, and
add a description if there is none.
**Done when:** you can cover the logo and still tell which company this is, and no sentence would be equally true of
a different product. Facts you could not confirm are gone or marked for the owner, never smoothed over.

### 3. Font
One family carries the voice; a monospace for small labels is optional. Two or three weights. A real scale with big
steps (for example 14, 16, 20, 32, 56, 88), not six sizes within four pixels of each other. Display sizes set tight
(letter-spacing around -0.02em to -0.035em, line-height near 1). If the brand owns a typeface, keep it and fix how it
is set.

If the brand has no typeface, there are two honest choices. Self-host one open-licensed family that has a point of
view (one `woff2` variable file, `font-display: swap`, its licence file beside it), or set a deliberate system stack
and let scale and spacing do the work. Do not link a font service just to swap one default for another. The audit's
"default typeface" line is a prompt to decide, not a ban: a common family set with care is fine, and you can say so
in the hand-over.
**Done when:** the headline, body and labels are visibly three different jobs, and there are at most two families.

### 4. Color
A ground (warm white, paper, or the brand's own), an ink, and one accent. The accent is a decision: it marks the
primary action and at most one other thing. Remove gradient fills, gradient text and coloured glows. Dark is a
section, not a mood for the whole site, unless the brand is dark already. Check text contrast (4.5:1 for body).
**Done when:** squinting at the page shows ground, ink, and exactly one colour, and that colour is on the thing you
most want pressed.

### 5. Spacing
Pick the page margins (for example 48 px on desktop, 20 on a phone) and put every left edge on them. One spacing unit
(8 px) and its multiples. One or two corner radii for the whole site. Hairlines instead of shadows to separate
things. Line length 45 to 75 characters for running text.
**Done when:** you can draw three vertical lines that most things start on, and no two neighbours have "almost the
same" gap.

### 6. The made thing
Every generated page has the same picture: a gradient card with a fake dashboard. Replace it with one thing only
this business could show. In order of preference: the real product (a true screen, a real photo); something they own
drawn clearly (their data, their route, their process as a diagram); a rendering of what they make or move; drawn
lettering or a wordmark. [made-thing.md](made-thing.md) has how to make each, including a script that renders a 3D
model as a product shot.

If nothing real exists yet, two things are still honest: a diagram of how the product works, drawn plainly and
captioned as an illustration ("How it works. Not real data."), or an empty, labelled slot with a note to the owner
about what to supply. A screen full of invented numbers is neither. Do not fake it.
**Done when:** the main picture would be wrong on any other company's site.

### 7. Layout
One thing dominates each screen: the headline or the made thing, sized so it could carry the page alone. Then let
the two meet. Ways to do that, easiest first:

- **Off the edge.** Make the picture wider than its column and let the page clip it on one side
  (`overflow: clip` on the section, a negative margin or a `translate` on the picture).
- **Pinned caption.** A small label joined to a part of the picture by a hairline, positioned inside the picture's
  own box so it moves with it.
- **Behind and in front.** Set the headline twice in the same place: once under the picture, once over it with a
  `clip-path` that shows only the part meant to pass in front. Hide the copy from screen readers (`aria-hidden`).

Touching is enough. If an overlap makes a word hard to read at any width, pull it back until the two share an edge.
Centre things on purpose or not at all. Check it at 390, 768 and 1440 wide.
**Done when:** the first screen has an obvious biggest thing, a second thing, and everything else is small.

### 8. Motion
One entrance, once: the first screen arrives in under about 1.2 seconds, staggered, easing out. At most one thing
keeps moving afterwards, and it should mean something (the product doing what it does). No scroll hijacking, no hover
wobble on every card. Honour `prefers-reduced-motion`. `check.mjs` (pass 10) measures all three; run it here too.
**Done when:** turning animation off loses nothing a visitor needs, and with it on nothing moves without a reason.

### 9. Proof
Replace the template's run of sections (features, testimonials, pricing teaser, FAQ) with one section that shows the
thing working: the interface in a real state, numbers the owner stands behind, a map or a log of what it did. If
there is nothing real to show yet, a shorter page is better than a padded one: skip this pass and say so.
**Done when:** the second screen answers "does it actually do that?" with evidence instead of adjectives.

### 10. Check and hand over
```bash
node <skill-dir>/scripts/check.mjs <the fixed page>
node <skill-dir>/scripts/audit.mjs <the fixed page>
node <skill-dir>/scripts/shots.mjs <the fixed page> unslop-out --name after
node <skill-dir>/scripts/shots.mjs --pair unslop-out/before-desktop.png unslop-out/after-desktop.png unslop-out/before-after.png
```
`check.mjs` loads the page at 390, 768 and 1440 wide and reports sideways scrolling, console errors, the heading
outline, images with no alt text, links that go nowhere, how many different actions the first screen asks for,
whether keyboard focus can be seen, and what still moves. Fix every FAIL. Read every WARN and either fix it or put it
in the hand-over. `--pair` takes any two pictures of the same shape, so make a mobile pair too if the phone layout
changed a lot.

Then look at the pictures yourself, and confirm what no script can: forms still submit, analytics and structured
data are untouched, and the page did not get heavier for no reason.

Hand over, in this order:
1. `before-after.png`, and the audit score before and after (say plainly that the score is rough).
2. What changed, one line per pass. Name the passes you skipped and why.
3. **What needs the owner:** every fact you cut or marked, every picture you need, every button with nowhere to go,
   every choice you made for them.
4. What you would do next with more material.

## Judging your own result

Hold the "after" against the "before" and ask: would a stranger think the same tool made both? If yes, you
rearranged the template instead of leaving it. The usual causes, in order: the copy is still generic (pass 2), the
picture is still a placeholder for a picture (pass 6), nothing is big (pass 7).

A score of 0 means the known tells are gone. It does not mean the page is good.

`example/slop.html` is a made-up vibecoded page to practise on. `preview.jpg` shows one before and after: the
"after" there took a modelled and rendered 3D scene and hand-drawn lettering, which is the far end of pass 6. Most
sites need less. All of them need the first five.
