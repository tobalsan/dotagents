---
name: mvp-task-planner
description: Transform vague project ideas into actionable, bite-sized tasks that can be shipped quickly. Use when user asks to plan a project/feature, break down a large task, mentions feeling overwhelmed, unsure where to start, or wants to iterate and get feedback quickly. Excels at breaking ambitious goals into minimum viable demos, preventing scope creep, and maintaining rapid iteration cycles.
---

# MVP Task Planner

Transform fuzzy ideas and existing codebases into laser-focused demo plans with bite-sized, shippable tasks. Ruthlessly cut scope, prioritize learning over polish, ensure rapid iteration.

## Core Principles

- **Process over prize**: Measure success by demos shipped, not plans written
- **Small bets**: Decompose into 1-2 hour loops, never multi-day epics
- **Wabi-Sabi defaults**: Embrace rough edges; polish goes to backlog
- **Kaizen cadence**: Always define next concrete step
- **Truth over optimism**: Surface blockers and unknowns immediately

## Workflow

### 1. Frame the Intent
Extract:
- One-line goal (what success looks like)
- Hard constraints (time, energy, tools available)
- Target audience
- Smallest possible "proof it works" demo
- Key unknowns and risks to test first

### 2. Scan the Project State
Read-only inventory:
- Existing code, docs, data, configs, tests
- Tech stack (languages, frameworks, package files)
- Runnable entrypoints (make, npm scripts, docker-compose)
- What works, what's broken, what's missing
- Contradictions (outdated README vs actual code)
- TODOs, open issues, abandoned branches

### 3. Define the Walking Skeleton
Propose simplest end-to-end path that:
- Proves core value in ≤1-2 hours
- Tests riskiest assumption first
- Uses stubs/mocks if real implementation exceeds budget
- Explicitly excludes all nice-to-haves

### 4. Create Concrete Tasks
Produce 3-7 tasks (never more) where each:
- Has clear, measurable outcome
- Includes specific acceptance criteria
- Defines how to verify completion
- Has hard timebox (45-90 minutes max)
- Links to relevant files/lines
- Is ordered by dependency and risk

Always include:
- A "First Demo" milestone
- A "Feedback Checkpoint" task

### 5. Anti-Cathedral Checks
Prevent scope creep:
- Flag any feature not required for first demo
- Move all polish/refactoring to dated backlog
- Enforce hard stops on each task
- Cap active tasks at 7 maximum
- Add explicit "what NOT to do" guidance

## Output Structure

1. **Project Intent** (one line)
2. **Demo Definition** (what will exist after first iteration)
3. **Current State Summary** (2-3 bullets)
4. **Key Risks/Unknowns** (what to test first)
5. **Task Queue** (3-7 ordered tasks with timeboxes)
6. **Stop Rules** (what NOT to do)
7. **Next Checkpoint** (when to reassess)

## Failure Detection

Flag these anti-patterns:
- Tasks exceeding 90 minutes
- Adding dependencies before proving need
- Writing tests for non-skeleton features
- Multiple parallel "firsts"
- "Polish" appearing in active tasks
- Plans without demo milestones
- More than 7 active tasks

## Example

**Input:** "I want to build a note-taking app"

**Intent:** CLI tool that saves and searches plain text notes
**Demo:** Run `note add 'my thought'` and `note search 'thought'` successfully
**Tasks:**
1. Create CLI skeleton with add/search commands (stub output) - 45m
2. Implement file storage for notes (append to .txt) - 60m
3. Add basic keyword search (grep wrapper) - 45m
4. Write quickstart README with examples - 30m
5. Test with 5 real notes, document failures - 20m

**Stop Rules:** No UI, no sync, no formatting, no tags (all go to backlog)
**Checkpoint:** After task 5, decide between search improvements or note editing
