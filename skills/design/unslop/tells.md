# The tells

What makes a page read as generated, why, and the pass that removes it. `scripts/audit.mjs` looks for the ones that
can be found in text; the rest need eyes.

A tell is not a rule against a technique. A gradient is fine when someone chose it. These are the marks of a page
where nobody chose anything: the default came out of the model and stayed.

## On the first screen

| Tell | Why it reads as generated | Fix | Pass |
| --- | --- | --- | --- |
| Purple, indigo or pink gradient (buttons, cards, backgrounds) | It is the most common default palette there is | Ground, ink, one accent | Color |
| Gradient-filled headline | Decoration standing in for something to say | Solid ink; put the effort in the words | Color |
| Blurred colour blobs behind everything | Fills space with no subject | Remove; let the ground be the ground | Declutter |
| Frosted glass cards | An effect applied to every container | Plain surfaces, hairlines | Declutter |
| Coloured glow under buttons and cards | Same | One soft neutral shadow at most, or none | Color |
| A pill above the headline ("✨ New: ... 2.0 →") | A template slot, usually with nothing to announce | Cut, unless there is real news | Declutter |
| Emoji as icons | Fastest way to fill an icon slot | Cut; if an icon is needed, draw or choose one set | Declutter |
| Three buttons ("Get Started Free", "Watch Demo", "Learn More") | Hedging: the page has not decided what it wants | One primary action, at most one quiet second | Declutter |
| Five stars and "Trusted by 10,000+ companies" | Unverifiable, and identical on every such page | Cut, or replace with something checkable the owner provides | Copy |
| A gradient card holding a made-up dashboard | A placeholder for a product picture | The made thing | The made thing |
| Seven or more navigation links | Every template section got a link | Five or fewer; the rest go in the footer | Declutter |
| Everything centred, everything the same size | No decision about what matters | One dominant thing; an edge to align to | Layout |

## Further down

| Tell | Why | Fix | Pass |
| --- | --- | --- | --- |
| Three cards: Lightning Fast, Secure & Reliable, Scalable | True of any software, so it says nothing | Cut, or say what only this product does | Declutter |
| Stat row: 99.9% uptime, 10,000+ customers, 24/7 support | Round numbers nobody can check | Real numbers with a source, or cut | Copy |
| Features, How it works, Testimonials, Pricing, FAQ, in that order | The template's order, not the argument's | One section that shows it working | Proof |
| Testimonials from people with no surname or company | Placeholder people | Real, attributed, with permission; or none | Proof |
| A wall of grey logos | Often invented | Only real customers who agreed | Proof |
| Icons in tinted rounded squares on every card | One icon set stamped everywhere | Fewer cards; let text carry it | Declutter |
| Large radius on every box, button and image | A default that makes everything the same object | One or two radii for the site | Spacing |
| Many things animating at once | Motion as filler | One entrance; one meaningful loop at most | Motion |

## In the words

Words to cut on sight. Each can be deleted from its sentence without losing any information, which is the test.

> revolutionize, unlock (the potential, the power), supercharge, seamless, seamlessly, cutting-edge, next-generation,
> AI-powered (as the whole pitch), elevate, empower, streamline, leverage, game-changing, transform the way,
> all-in-one, state-of-the-art, world-class, best-in-class, robust, effortless, take it to the next level,
> drive growth, innovative solutions, the future of, reimagine, blazing fast, lightning fast, enterprise-grade,
> harness the power, at scale, unleash

Patterns to rewrite:

- **The headline that fits any company.** "Revolutionize Your Supply Chain with AI-Powered Logistics Solutions."
  Replace with what it does for whom: "Freight that finds its own way."
- **The supporting sentence that lists three abstractions.** "Streamline workflows, empower teams and drive growth."
  Replace with one concrete thing it does and when: "Reroutes every vessel around weather, port queues and fuel
  cost, hour by hour."
- **Buttons that describe clicking.** "Get Started", "Learn More". Say what happens: "Book a demo", "See pricing".
- **Title Case On Every Heading.** Sentence case, unless the brand's style says otherwise.
- **Three adjectives in a row**, and sentences built as "not just X, but Y".
- **A feature name with a version number nobody asked for** ("Route Optimization 2.0").

## What the audit cannot see

- Whether the picture is any good, or is a stock picture with a clean filename.
- Hierarchy: whether anything is big.
- Whether the copy is true.
- Alignment and rhythm.
- Whether the page looks like the same tool made it as a thousand others, which is the real question. Look.
