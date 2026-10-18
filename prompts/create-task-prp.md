---
description: Create Task PRP for bug fixes or small code changes
---

# Create Task PRP

Focus: $ARGUMENTS

## Task PRP Purpose

Start by reading and understanding the PRP concepts `~/.agents/resources/prp/README.md`

Create a **focused, lightweight PRP** for targeted changes like bug fixes, refactors, or small enhancements.

**Key Difference from Project/Scope PRP**: Task PRPs prioritize *precision over comprehensiveness*. The goal is surgical accuracy, not exhaustive context.

## Research Process

> Use subagents when helpful—for example, to parallelize searching for related code while you analyze the main issue. Don't over-engineer; match research effort to task complexity.

1. **Understand the Full Context of the Issue**
   - If the issue has a parent project, make sure to read the project description
   - If the issue is a subtask, make sure to read the parent task description
   - If the issue has comments, read them
   - Review the recent commits if they're related to the issue.

2. **Locate the Problem**
   - Identify the exact file(s) and function(s) involved
   - Trace the code path related to the issue
   - Find any related tests that exist or should be modified
   - If the issue spans multiple areas, spawn subagents to investigate each in parallel

3. **Understand the Pattern**
   - Check how similar code is structured nearby
   - Note naming conventions and style in the affected files
   - Identify dependencies that might be impacted

4. **External Lookup** (if needed)
   - Only if the fix involves unfamiliar APIs or libraries
   - Spawn a subagent for doc research if you need to stay focused on code analysis
   - Keep it targeted—one or two searches, not broad exploration

## Task PRP Structure

### Problem Statement
- What is broken or needs changing?
- How to reproduce (for bugs) or current behavior (for changes)?

### Root Cause / Change Location
- Exact file(s) and line numbers or function names
- Why this is the right place to change

### Proposed Fix
- Specific code changes needed
- Any edge cases to handle

### Files to Modify
- List each file with its role in the fix

### Validation
- How to verify the fix works
- Existing tests to run or new test to add

## Output

Update the acknowledgment comment with PRP: `linctl comment update <COMMENT_ID> --body "{PRP markdown}"`
Update issue status: `linctl issue update $ARGUMENTS --state "Todo"`

## Task PRP Quality Gates

- [ ] Problem is clearly stated and reproducible
- [ ] Exact change location(s) identified
- [ ] Fix approach is specific, not vague
- [ ] Validation steps are concrete and runnable

## Success Metrics

**Target**: Enable fix implementation in a single focused session without needing additional research.
