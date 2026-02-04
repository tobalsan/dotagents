---
name: today
description: Start the day and refine today's plan. Use when asked to start the day, check today's schedule, or refine the current plan.
---

---
description: Start the day and refine today's plan
---

# Today

Purpose: a start-of-day command that refreshes context, checks today's schedule, and refines it based on the actual launch time. It is not a clone of `/plan-tomorrow`.

## Gather context from the journal notes

Run `!date`.

Read the two previous week journal notes, and the current week journal note, to extract:
- **Week focus (always)**: reminder of this week's focus, priorities, and explicit deliverables.
- **Week themes (only if Monday)**: main themes for the current week.
- **Previous day's end of day review (if it exists)**: the review of the previous day often gives helpful insights and context for today's plan.
- **Today's themes (always)**: main themes for the current day.
- **Notes for today**: important notes/insights, blockers, constraints, preferences.
- **Today's schedule** (if already written): find the section under today's header.

## Do (if not already done)

- Extract my **todos in the current weekly journal file**. Also check for any potentially lingering unresolved todos in the two previous week notes.
- Review todos in the journal notes (current week + lingering from last two weeks).
- Review project todos via `apm` (todo + in_progress only).
- **Calendar events for today**
- **Important emails** requiring immediate attention

## Important themes discovery phase

Before creating and presenting the plan, you must first discover or confirm with Thinh the most important themes and focus areas for the current day. 
Using the context you gathered, ask Thinh to confirm your understanding of the most important tasks.
**When asking questions, make sure to do it one at a time, and not move on to the next until each step is clear-cut. This an interviewing process**.
If there is an update in focus, new themes or important things resurfacing, make sure to save important info and insights in memory files.

## Output requirements

Present, in this order:
1. **Week focus reminder** (always)
2. **Themes**:
   - **Today's themes** (always)
   - **This week's themes** (only if Monday)
3. **Constraints & signals**: key events, urgent emails, and the most relevant todos (high priority first).
4. **Today's schedule**:
   - If a schedule already exists, show it and propose adjustments based on the current time and constraints.
   - If no schedule exists, create one following the output format and rules in `/plan-tomorrow`.
   - For confirmation, render the schedule in the markdown list format (headers, bold/italics, `code`, and `---` dividers); for final journal write, use tables.

### Schedule rules (same as `./plan-tomorrow.md`)
- **Flexible, not over-timestamped**; no start/end times.
- **Grouped by Morning / Afternoon**.
- **Impact groups**: `High`, `Secondary`, `Bonus (optional)`.
- **Time blocks**: only `15m`, `45m`, `90m` (or combinations like `45m + 15m`).
- **Hard stop at 19:00**.
- **Realistic done criteria**; match project phase.
- **Biased toward the most important project** from the journal.
- **Include learning paths** if present in the journal.
- **Include a short setup/commit block** at the start of the day.
- **Late start adjustment**: if the command is launched late (e.g. afternoon), do not force a Morning table; adapt workload and drop items as needed to stay realistic.
- **Date-tagged todos**: only schedule todos if their due date matches today.

## Interaction flow

1. Present the refresher + proposed schedule/refinement for review in markdown list format (no tables).
2. Confirm with the user whether the plan fits energy/time constraints.
3. Update the current week journal note:
   - If no schedule existed, append it under today's header using the two-table format from `/plan-tomorrow`.
   - If a schedule existed, replace the two tables under today's header with the updated version (leave other notes intact).

$@
