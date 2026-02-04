---
name: shape-up
description: Manage project, scopes, and tasks using plain text files. Use proactively whenever dealing with projects, scopes, and tasks.
---

# Shape Up Project Methodology

This skill explains the foundations of the Shape Up methodology to manage and accomplish our projects.

Work starts by fixing time, not promises. Problems are shaped until the risky parts are exposed, the scope is reduced, and the solution is rough but believable. Only end-to-end value is considered, never layers or busywork. There is no backlog to hide in: work is either worth a bet or ignored. Clarity comes from boundaries, not detail, and progress comes from finishing meaningful slices inside a hard appetite.

1. **Fixed time, variable scope** — the appetite is set first; everything else bends.
2. **Shaping beats planning** — reduce unknowns before committing people.
3. **Problem over solution** — define the pain clearly, resist premature design.
4. **Fat markers only** — rough, directional ideas; no fine-grained specs.
5. **Vertical slices win** — end-to-end value, not layers or components.
6. **No backlogs** — work is either shaped and bet on, or ignored.
7. **Risk first** — hunt rabbit holes before they hunt you.
8. **Explicit no-gos** — deciding what *not* to do is part of the work.

## Behavioral Rules

1. **Set the appetite immediately** — refuse discussion without a time box.
2. **Interrogate the problem, not the implementation.**
3. **Cut scope aggressively** before adding structure.
4. **Speak in outcomes and flows**, never tasks or components.
5. **Surface risks early** and make them explicit.
6. **Force no-gos** to protect the appetite.
7. **Ban backlogs** — only shaped bets are allowed.
8. **Stop refining once it’s buildable**, not “perfect.”
9. **Strive for single-run high confidence** — if a scope risks overrunning one agent run, split it until confidence is high.

Project shaping always goes through the following cycle:

```
Inception -> Shaping -> Implementation
```

All projects live in `~/projects`.
To interact with projects, always use the `apm` command line tool.

## `apm` reference

```
Usage: apm list [options]

Options:
  --status <status>  Filter by status
  --owner <owner>    Filter by owner
  --domain <domain>  Filter by domain
  -j, --json         JSON output
  -h, --help         display help for command


Usage: apm get [options] <id>

Arguments:
  id          Project ID

Options:
  -j, --json  JSON output
  -h, --help  display help for command


Usage: apm create [options]

Options:
  -t, --title <title>      Project title
  --domain <domain>        Domain (life|admin|coding)
  --owner <owner>          Owner
  --execution-mode <mode>  Execution mode
                           (manual|exploratory|auto|full_auto)
  --appetite <appetite>    Appetite (small|big)
  --status <status>        Status


Usage: apm update [options] <id>

Arguments:
  id                       Project ID

Options:
  --title <title>          Title
  --domain <domain>        Domain (life|admin|coding)
  --owner <owner>          Owner
  --execution-mode <mode>  Execution mode
                           (manual|exploratory|auto|full_auto)
  --appetite <appetite>    Appetite (small|big)
  --status <status>        Status
  --content <content>      Content string or '-' for stdin


Usage: apm move [options] <id> <status>

Arguments:
  id          Project ID
  status      New status   (not_now|maybe|shaping|todo|in_progress|review|done)

```

## Project shaping

Every project with status `shaping` is a new project that must be be shaped within two weeks of its creation date. 
If a project is older than two weeks, move it to `not_now` status and inform Thinh.

## Project scoping

Once a project is shaped, the next phase is to scope it. 
You will create a **scope** markdown file for it, which will contain all the defined scopes for the given project. 

Favor smaller, independent slices so a single agent can complete one scope per run without blowing the context window or token budget.

Use [Scoping][reference/scoping.md] for detailed guidance on scoping.

The scope file must named after the project file, with the following format: `{PROJECT_NAME}.scopes.md`, inside the project folder.

ULTIMATE GOAL: Scopes are meant to be picked up by any AI coding agent, so they can decide what to work on next simply by reading the main project file and corresponding scope files.
