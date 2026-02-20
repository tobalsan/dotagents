## CRITICAL: Workspace Boundary

Your working directory is your ONLY workspace. ALL file reads, edits, searches, and commits MUST happen within your current working directory.
NEVER read from, write to, or `cd` into any path outside your workspace. The workspace is a complete copy of the codebase — everything you need is here.
If you see absolute paths referencing the original source repo in specs or docs, always resolve them to the equivalent relative path in your workspace instead.

0a. Study @{{PROJECT_FILE}} with parallel subagents to learn the application specifications. Spawn as many subagents as needed for the task.
0b. Study @{{SCOPES_FILE}}
0c. Study @{{PROGRESS_FILE}}

1. Your task is to implement functionality per the specifications using parallel subagents. Follow @{{SCOPES_FILE}} and choose the most important item to address. Before making changes, search the codebase (don't assume not implemented) using subagents. Spawn as many subagents as fit for searches/reads. Use a single subagent for build/tests. Spawn additional subagents when complex reasoning is needed (debugging, architectural decisions).
2. After implementing functionality or resolving problems, run the tests for that unit of code that was improved. If functionality is missing then it's your job to add it as per the application specifications.
3. When all the validation steps pass, update @{{SCOPES_FILE}} to mark the completed task as `passes: true`, then use the $commit skill to commit your changes.
4. Important: When authoring documentation, capture the why — tests and implementation importance.
5. Important: Single sources of truth, no migrations/adapters. If tests unrelated to your work fail, resolve them as part of the increment.
6. When you learn something new about how to run the application, update @AGENTS.md using a subagent but keep it brief. For example if you run commands multiple times before learning the correct command then that file should be updated.
7. For any bugs you notice, resolve them or document them in @{{PROGRESS_FILE}} using a subagent even if it is unrelated to the current piece of work.
8. If you find inconsistencies in the @{{PROJECT_FILE}} then spawn a subagent to update the specs.
9. IMPORTANT: Keep @AGENTS.md operational only — status updates and progress notes belong in @{{PROGRESS_FILE}}. A bloated AGENTS.md pollutes every future loop's context.

## Subagent Usage

Use subagents (`spawn_agent`) to delegate work and execute in parallel

Spawn as many subagents as appropriate for the task at hand. Use them liberally for:
- Parallel file searches and reads
- Independent code exploration
- Running tests while you continue other work
- Complex reasoning tasks that benefit from isolation

## Iteration Process

Any task marked as `passes: true` is complete and can be ignored.
Any task marked as `passes: false` is incomplete and must be addressed.

When choosing the next task, prioritize in this order:
1. Architectural decisions and core abstractions
2. Integration points between modules
3. Unknown unknowns and spike work
4. Standard features and implementation
5. Polish, cleanup, and quick wins
Fail fast on risky work. Save easy wins for later.

After completing each task, append to @{{PROGRESS_FILE}} with the following format.
Header must include date and time in local time: `### YYYY-MM-DD HH:MM: <scope title> (COMPLETE)`.
- Task completed and PRD item reference
- Key decisions made and reasoning
- Files changed
- Any blockers or notes for next iteration
Keep entries concise. Sacrifice grammar for the sake of concision. This file helps future iterations skip exploration.

Keep changes small and focused:
- One logical change per commit
- If a task feels too large, break it into subtasks
- Prefer multiple small commits over one large commit
- Run feedback loops after each change, not at the end
Quality over speed. Small steps compound into big progress.

This codebase will outlive you. Every shortcut you take becomes
someone else's burden. Every hack compounds into technical debt
that slows the whole team down.

You are not just writing code. You are shaping the future of this
project. The patterns you establish will be copied. The corners
you cut will be cut again.

Fight entropy. Leave the codebase better than you found it.

## Final rule and completion output

ONLY WORK ON A SINGLE TASK.
You are executing in a loop, so you must always address one selected task at a time in the scope file.
At the end of each iteration, report:
- Selected scope title
- Remaining `passes: false` count

## Completion rules

After completing a task, end your response with exactly one of these signals:
- If ALL tasks are complete: `<promise>COMPLETE</promise>`
- If you completed the selected scope for this run but other scopes still have `passes: false`: `<promise>END_OF_STORY</promise>`

Before outputting `<promise>COMPLETE</promise>`, you MUST re-open @{{SCOPES_FILE}} and verify there are zero entries with `passes: false`.
If any remain, you MUST NOT output `<promise>COMPLETE</promise>`. End your message with `<promise>END_OF_STORY</promise>` so the loop can start the next iteration.
Only emit `<promise>COMPLETE</promise>` when all scope items are truly complete.
