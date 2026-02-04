---
name: plan-tomorrow
description: Plan the next day based on journal notes, calendar, todos, and priorities. Use when asked to plan tomorrow, prepare tomorrow's schedule, or set up the next day.
---

---
description: Plan the next day
---

# Plan the next day

Start reading my journal files to gather info about:
- **This week’s focus, priorities, and explicit deliverables.** When planning a day, always include any explicit weekly deliverables or focuses mentioned in the journal so they are tracked in the daily plan.
- **Notes for today**: important notes/insights, blockers, and any constraints/preferences that affect tomorrow’s plan.
- **Current day's end of day review (if it exists)**: the review of the current day often gives helpful insights and context for tomorrow's plan.

If it is early in the week (Monday/Tuesday), use the last week’s journal note to gather context.

Do (if not already done):
- Extract my **todos in the current weekly journal file**. Also check for any potentially lingering unresolved todos in the two previous week notes.
- Review todos in the journal notes (current week + lingering from last two weeks).
- Review project todos via `apm` (todo + in_progress only).
- Any **calendar events for the next day**
- Important **emails in my inbox** requiring immediate attention

## Important themes discovery phase

Before creating and presenting the plan, you must first discover or confirm with Thinh the most important themes and focus areas for the next day. 
Using the context you gathered, ask Thinh to confirm your understanding of the most important tasks.
**When asking questions, make sure to do it one at a time, and not move on to the next until each step is clear-cut. This an interviewing process**.
If there is an update in focus, new themes or important things resurfacing, make sure to save important info and insights in memory files.

## Output requirements (incorporate user feedback)

Create a plan for the next day that is:
- **Flexible, not over-timestamped**: avoid a minute-by-minute schedule. The plan should not make me feel “behind” if the day shifts.
- **Grouped by day half**: structure into **Morning** and **Afternoon** sections.
- **Sub-grouped by impact** (2–3 groups max per half-day), e.g.:
  - **Most important / high impact**
  - **Secondary**
  - **Bonus** (optional)
- **Time-block aware**: suggest block sizes using only **15m / 45m / 90m**, but do not over-specify exact start/end times.
- **Hard-stops at 19:00**.
- **Realistic**: done criteria must match the project’s current phase.
  - If a project is still mostly research/planning, the “done” criteria should be a research artifact (notes, summary, decision, list of issues), not an end-to-end product outcome.
  - Avoid assigning oversized blocks to tasks that should be quick; keep “bonus” tasks small by default.
- **Biased toward the most important project** as stated in the journal notes (and reinforced by Linear priorities/due dates).
  - If Content Creation is the top priority, schedule explicit tasks for it (not just implied).
  - If the journal specifies a publishing cadence (e.g. **Mon/Wed/Fri first thing**), schedule it explicitly when applicable.
- **Includes learning paths** explicitly (when present in the journal), with small, concrete blocks.
  - Default pattern (unless overridden by the journal): **MIT Probability lecture (45m)** + **EBTA reading (15m)**.
- **Includes a short “setup/commit” block** at the start of the day even if the plan is already written.
  - Purpose: confirm priorities, lock done criteria, choose the specific option for any forks, and make sure the first block is truly executable.

## Format (scan-friendly, adaptable)

For **confirmation**, present the plan using the **markdown list format** (headers, bold/italics, `code`, and `---` dividers) instead of tables. Separate clearly morning from afternoon.

For **final journal write**, use **two Markdown tables**, one for **Morning** and one for **Afternoon**.

Required shape (confirmation view):
- `## Proposed adjustment` (or `## Plan` when not adjusting)
- `**Plan (done by 19:00)**` (include any key constraints like late events / hard stop at 19:00)
- `**Morning**` section (unless omitted by constraints)
- `**Afternoon**` section (unless omitted by constraints)

Required shape (journal write):
- `**Plan (done by 19:00)**`
- `**Morning**` table
- `**Afternoon**` table

Each table must have exactly these columns:
- `Impact`
- `Block (size)`
- `Outcome (done criteria)`

Rules:
- `Impact` must be one of: `High`, `Secondary`, `Bonus (optional)`.
- `Block (size)` must use only: `15m`, `45m`, `90m` (or combinations like `45m + 15m`). No start/end timestamps.
- If there is a fork, include `pick ONE` in `Block (size)` and keep options short inside the `Outcome` cell.
- **Partial-day adjustment**: only omit Morning or Afternoon when a calendar event or explicit constraint blocks that half-day; otherwise keep both and adapt the workload.
- **Date-tagged todos**: only schedule todos with if their due date matches the planned day.

## Flow

1. Present the plan to me for review.
2. Upon confirmation, add the plan at the end of my current week journal file:
   - Add the day’s header first (e.g. `### Tuesday Dec 30, 2025`) if it is not already present.
   - Append the plan under that header using the **two-table format** (Morning table + Afternoon table).
