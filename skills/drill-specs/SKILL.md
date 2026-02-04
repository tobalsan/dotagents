---
name: drill-specs
description: Build comprehensive specs for a project idea by asking probing questions. Use when asked to drill specs, flesh out a project idea, or interview for requirements.
---

---
description: Build comprehensive specs for the given base specs by asking probing questions
---

# Drill Specs

Your task is to first help me build comprehensive specs for the following project idea:

<base-specs>
$ARGUMENTS
</base-specs>

First, if we are inside an existing codebase, use up to 10 subagents in parallel to explore the codebase and understand the current state of the project.

Then, if the `AskUserQuestionTool` is available, use it to help build the specs by interviewing me and gathering requirements and details about the project implementation, UI & UX, tech stack, concerns, tradeoffs, etc.
If the tool is not available, just start interviewing me, asking questions in a sequential manner (not all at once).

Make sure questions are not obvious and probe deeper into the underlying needs and constraints.

Interview me continually and systematically until the spec is complete. Document all responses and insights to create a comprehensive and well-structured specification that serves as the foundation for the project. 
Write the defined specs into the project file.

IMPORTANT: Plan only. Do NOT implement anything. We're focusing on specs. Do NOT assume functionality is missing; confirm with code search first.
