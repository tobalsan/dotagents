---
name: minimal-report
description: Write a minimal, practical HTML report in a black-and-white Apple-style theme. The report has short modules of one-line rows (mistake → fix, finding → action, option → verdict), with no prose and no decoration. Use this skill as the DEFAULT for every report, summary, plan, audit, review, analysis, status update, comparison, or best-practice page that needs more than three sentences. Use it also when the user asks for a "minimal", "no-bullshit", "practical", "simple", or "brief" report, or asks to make a report shorter. Do not use it only when the user explicitly asks for a detailed, complex, or long report.
---

# Minimal report

Make one HTML page that a busy reader can scan in 2 minutes and act on.
The model: a page that lists what goes wrong and what to do instead, grouped in a few clear modules.

## Rules for the content

1. Start from the action. Each row answers "what do I do with this?".
2. Use 2 to 6 modules. Give each module a title of 2 to 4 words.
3. Put 2 to 6 rows in each module. Write one idea per row, and one line per side when possible.
4. Write no paragraphs. The only prose is the one-sentence intro under the title.
5. Use a stats strip only for 2 to 4 numbers that carry the message. Leave it out if no number matters.
6. Show a concrete example in a `<code>` chip: a prompt, a command, a file path, a value.
7. Do not write a recap, a conclusion, a methodology section, caveats, or "next steps" unless the reader must act on them.
8. Write one source line in the footer: data source, period, and sample size.
9. Keep the names of people out, unless the reader needs them.
10. Cut every row that the reader cannot act on, and every adjective.

## Pick the block for each module

| Content | Block | Column labels |
|---|---|---|
| Mistakes and correct practice | A, pair rows, `x` / `v` marks | Mistake / Do this |
| Problems and fixes, risks and mitigations | A, pair rows | Problem / Fix |
| Options and decision | A, pair rows, no marks | Option / Verdict |
| Before and after | A, pair rows | Before / After |
| Findings, facts, decisions | B, single rows | (none) |
| Actions in order | C, numbered steps | (none) |
| Reference data (status, numbers) | D, table | your columns |

For a pair row without marks, remove the `x` and `v` classes. Keep `l` and `r`.

## Design

Copy `assets/template.html` (relative to this skill folder) and fill it. Keep the theme:

- Black, white, and grays are the base (`#1d1d1f`, `#6e6e73`, `#d2d2d7`, `#f5f5f7`).
- Use color when it makes the page easier to read: chart series, diagram parts, status, diff lines. Use the Apple system colors: blue `#0071e3`, green `#34c759`, orange `#ff9f0a`, red `#ff3b30`, purple `#af52de`, teal `#30b0c7`. Do not use color for decoration.
- No gradients, no shadows, no cards, no icons other than ✕ and ✓.
- System font stack (SF Pro), large bold titles with tight letter spacing, a lot of white space, hairline row separators.
- One static file. No JavaScript, no external fonts, no external CSS.
- Delete the blocks you do not use. Delete all the HTML comments.

## Workflow

1. Get the facts first: collect and analyze the data before you write. Keep raw analysis outside the report.
2. Draft the modules as a plain list of rows. Cut until each row passes rule 1 and rule 10.
3. Fill the template. Save to `~/Documents/artifacts/<slug>.html`, unless the report belongs to a repo or the user names a path.
4. Render a check screenshot, then read the image and fix any layout fault:
   `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --screenshot=/tmp/check.png --window-size=1200,1600 "file://<path>"`
5. Open the file for the user with `open <path>`. Reply in 1 to 3 sentences with the path.

## Languages

When the user asks for more than one language, write one file for each language: `<slug>-en.html`, `<slug>-fr.html`.
Translate the meaning, not word for word. Set `<html lang>`. In French, put a space before `:` and `%`, and use the formal "vous" in instructions.

## Example rows

Good, specific and actionable:
- ✕ "You send only a ticket link, or one word." → ✓ "Say what you want." + `Ticket 27971: find the root cause and draft a reply in English.`
- ✕ "You ask for the same report by hand every week." → ✓ "Ask for a scheduled task: what, when, where to send it."

Bad, vague or decorative:
- "Prompting is a key skill that unlocks the full potential of AI." (no action)
- "Consider improving communication." (no concrete fix)
