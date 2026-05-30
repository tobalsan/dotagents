---
name: reflect
description: Review the current chat for mistakes, friction, and unclear outputs, then propose concrete improvements and ask which to remember. Also audits any skills used in the chat for self-check criteria, conciseness, and other upgrades. Triggers on "reflect", "/reflect", or when the user requests a retrospective on the current session.
---

# Reflect

Retrospective on current chat. Surface friction, propose fixes, capture lessons.

## Success criteria

Before presenting output, verify ALL of:
1. Reviewed actual chat history (not generic advice).
2. Listed specific mistakes/friction/unclear outputs with concrete examples from this chat (or stated "none observed").
3. Proposed short, concrete improvements — each actionable, not vague.
4. Asked user which improvements to remember (memory entries) — exact question, not implied.
5. If skills were used this chat: each audited for (a) self-check section, (b) conciseness, (c) other improvements. Proposals listed; user asked before applying.
6. If repeated similar tasks observed: suggested new reusable skill, asked confirmation.

## Steps

1. **Scan chat.** Identify: corrections user made, clarifications repeated, outputs user rejected/reworded, signs of frustration, tool misuse, missed context.
2. **List findings.** Bullet form. Each ≤1 line. Cite the turn briefly.
3. **Propose improvements.** Concrete behaviors to change. Each one rememberable as a memory entry.
4. **Audit skills used.** For each skill invoked this chat:
   - Read its SKILL.md.
   - Check for explicit success criteria + final self-check instruction (up to 5 iterations). If missing, propose adding.
   - Scan for verbose phrasing, redundant sections, unused examples. Propose cuts.
   - Note any other clarity/correctness improvements.
5. **Detect repeated tasks.** If user asked for similar work ≥3 times this chat, propose new skill.
6. **Ask the user** three questions:
   - Which improvements to save to memory?
   - Which skill edits to apply?
   - Create new skill? (only if repetition detected)

## Output shape

```
## Friction observed
- <thing> (turn N): <one-line>
- ...

## Proposed improvements
1. <concrete behavior change>
2. ...

## Skills used this chat
### <skill-name>
- self-check: [present | missing → propose adding]
- conciseness: [cuts proposed | already tight]
- other: [...]

## Questions
1. Which improvements should I remember?
2. Apply which skill edits?
3. [if applicable] Create skill `<name>` for <pattern>?
```

If no friction and no skills used: say so in one line, ask if anything specific to reflect on.

## Proactive trigger

Suggest user type `reflect` when you notice:
- User corrected you in this turn.
- User asked same clarification twice.
- User shows frustration ("no", "again", "you keep…", terse replies after long outputs).

Phrase: "Want to `reflect`? Saw <signal>."

## Final self-check

Before sending output, walk success criteria 1–6. If any fail, iterate (max 5). If still failing after 5, send what you have and flag which criterion unmet.
