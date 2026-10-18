---
name: pele
description: Add Mermaid diagrams to reports with Pele (pele.run), a small renderer that turns Mermaid text into themeable SVG. Use this skill every time you write a report, plan, explainer, status update, incident review, PR writeup, or any HTML or Markdown artifact for the user that describes a flow, a sequence of calls, states, an architecture, a timeline, a schedule, a hierarchy, or numbers. Use it even if the user does not ask for a diagram — when one picture explains faster than a paragraph, add it. Also use it when the user mentions Mermaid, Pele, or diagrams in a report.
---

# Pele diagrams in reports

Pele renders Mermaid syntax to SVG in about 1 ms, with no dependencies. Colors come from CSS variables, so a diagram can match the report palette. It supports every Mermaid 12 diagram type except ZenUML.

The user reads reports fast. A good diagram replaces a paragraph of "A calls B, which then…". Add a diagram when the content has structure: steps, actors, states, dependencies, time, or proportions. Do not add a diagram only for decoration. One to three diagrams in a report is the normal range.

## Workflow

1. Pick the diagram type (table below). Keep it small: about 15 nodes or fewer, labels of 1–4 words. Split a large diagram into two.
2. Write the diagram into the report:
   - **HTML report** (the default report format): copy the style block and the two script tags from `assets/pele-embed.html` into the page. Put each diagram in `<pre class="mermaid">…</pre>`. Pele renders in the browser on page load.
   - **Markdown report**: use a fenced code block with the `mermaid` language tag. GitHub and Obsidian render it.
   - **Offline or static output** (PDF, email, no network): run `node scripts/pele.mjs svg diagram.mmd diagram.svg` and paste the SVG into the page. Set the same CSS variables on a parent element.
3. Check every diagram before you give the report to the user:
   ```bash
   node <skill-dir>/scripts/pele.mjs check report.html   # also accepts .md and .mmd files
   ```
   It prints `OK` or `FAIL` with the line and column for each diagram, and exits 1 on any failure. Fix and run it again until all diagrams show `OK`. A broken diagram shows red error text in the report, so this check is not optional.

The script installs `pele@1` into `~/.cache/pele-skill` on first use (needs Node 20+ and npm).

## Pick a diagram type

| Content | Mermaid keyword |
| --- | --- |
| Process, decision, data flow, dependency graph | `flowchart LR` or `flowchart TD` |
| Calls between services, agents, or people over time | `sequenceDiagram` |
| Lifecycle of one thing (ticket, job, PR) | `stateDiagram-v2` |
| Schedule, plan with dates | `gantt` |
| Events in order, no exact durations | `timeline` |
| Database tables and relations | `erDiagram` |
| Classes, types, modules | `classDiagram` |
| System components and hosting | `architecture-beta` or `C4Container` |
| Share of a total | `pie` |
| Trend or comparison of numbers | `xychart` |
| Two-axis prioritization (effort vs impact) | `quadrantChart` |
| Flow volumes (cost, traffic) | `sankey` |
| Branches and merges | `gitGraph` |
| Topic breakdown | `mindmap` |
| Root-cause analysis | `ishikawa` |
| Work board | `kanban` |

The full list and examples are at https://pele.run/examples. Use `scripts/pele.mjs check` to test a type that you do not know well.

## Syntax rules that prevent most errors

- Put a label in quotes if it contains `( ) [ ] { } : ; , #` or other punctuation: `A["Retry (3x)"]`.
- In HTML, escape `<` as `&lt;` and `&` as `&amp;` inside `<pre class="mermaid">`. The `>` in `-->` is safe.
- Use short node IDs and long labels: `db[(Orders DB)]`, not `OrdersDatabase`.
- Pele does not support HTML labels. Use `<br>` (escaped in HTML as `&lt;br&gt;`) for a line break. For bold or italic text, use a Markdown string in backticks: ``A["`**Fail** fast`"]``.
- Mermaid themes and `themeVariables` have no effect. Change colors with the CSS variables in `assets/pele-embed.html`.
- To highlight one node, use a class: `classDef hot fill:#D97757,color:#fff` and `B:::hot`. Fixed colors do not follow the theme, so use them only for emphasis.

## Theming

`assets/pele-embed.html` maps the Pele variables to the palette of `~/dotagents/resources/html_templates` (ivory, slate, clay, olive). If the report uses a different palette, change the `--pele-*` values in the style block. The most important variables: `--pele-bg`, `--pele-fg`, `--pele-line`, `--pele-surface`, `--pele-border`, `--pele-accent`, and `--pele-series-1` to `--pele-series-8` for charts. Keep `--pele-font` the same as the body font, because Pele measures label width with that font. All variables: https://pele.run/theming.

## Example

```html
<pre class="mermaid">flowchart LR
  req[Request] --&gt; cache{Cache hit?}
  cache -- Yes --&gt; ret[Return]
  cache -- No --&gt; fetch[Fetch from origin] --&gt; ret</pre>
```
