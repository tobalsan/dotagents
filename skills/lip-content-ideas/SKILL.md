---
name: lip-content-ideas
description: Suggest content ideas for #learninpublic based on recent activity (git commits, command history, bookmarks). Use when asked for content ideas, what to post about, or learn in public topics.
---

---
description: "Suggest content ideas for #learninpublic, based on the user's recent activity"
---

Recent activity period: $ARGUMENTS

Review the user's recent activity over the specified period to ground the conversation. 
Use `gglog` and `clistory` to review the user's recent activity. If no period specified, default to today.
Also use `raindrop` to review the user's recent bookmarks as they can be interesting topics to publish about.

After summarizing the themes, run a quick interview instead of listing ideas:
1) Ask 2–4 short questions to converge on a target topic (based on the activity and bookmarks).
2) Once a topic is selected, ask a quick probe to define the angle (tone such as quip/experience sharing/didactic/resource sharing, etc.) and format (short/long/with media).
3) Then present five topic ideas aligned to the chosen topic, angle, and format.

## Commit author check

When using `gglog`, only treat commits as "the user's recent activity" if the commit author is **Thinh**. Ignore commits authored by other people, even if they appear in the log.

## Recent bookmarks

Use `raindrop list --limit <limit> --page <page> --json` to get the list of recent bookmarks.
Limit is 20 by default, can go up to 50. 
Page is a number, starting from 0.
Results are sorted by most recently added first.

You can also use `raindrop list --search <search-term>` to search for a specific topic or theme.

For bookmarks, since there might not be a lot over the specified period, use the following rule:
- if specified period is today, use the bookmarks from the last week
- if specified period is yesterday, use the bookmarks from the last two weeks 
- if specified period is week, use the bookmarks from the last month

## Avoid List

List the already selected topics in `./topics`.
Since these were already chosen, do not suggest them again.

## Examples

User: `/lip-content-ideas`
Assistant: <run `gglog` + `clistory`>, <run `date` + read `~/Documents/vaults/personal/Journal/entries/3. Monthly Notes/2025/202511 November 2025.md`> Today you've been working on X quite a lot. It seems you've also been working on Y, and Z, etc.
  Quick check-in:
  1) Which of these feels most worth sharing this week?
  2) Any problem you just solved that others might hit?
  3) Want to focus on tools, process, or outcomes?
  
Assistant: Great. Let’s define angle + format:
  - Tone: quip, experience sharing, didactic, resource sharing, or other?
  - Format: short, long, with media?
  
Assistant: Here’s a focused approach for the chosen topic:
  **Main idea** — Angle: <angle>
  **Approach** — <2–4 concise bullets describing the narrative/structure>

---

User: `/lip-content-ideas yesterday`
Assistant: <run `gglog yesterday` + `clistory yesterday`>, <run `date` + read last lines of `~/Documents/vaults/personal/Journal/entries/3. Monthly Notes/2025/202511 November 2025.md`> Yesterday you worked on A, also B, C, and D.
  Quick check-in:
  1) What felt most interesting or surprising?
  2) Is there a takeaway you'd want to teach?
  
Assistant: Great. Let’s define angle + format:
  - Tone: quip, experience sharing, didactic, resource sharing, or other?
  - Format: short, long, with media?
  
Assistant: Here’s a focused approach for the chosen topic:
  **Main idea** — Angle: <angle>
  **Approach** — <2–4 concise bullets describing the narrative/structure>

---

User: `/lip-content-ideas week`
Assistant: <run `gglog week` + `clistory week`>, <run `date` + read `~/Documents/vaults/personal/Journal/entries/3. Monthly Notes/2025/202511 November 2025.md`> This week it seems you've been doing X, solving X, and debugging Z.
  Quick check-in:
  1) Which theme do you want to double down on?
  2) Is this more of a lesson, a story, or a quick tip?
  
Assistant: Great. Let’s define angle + format:
  - Tone: quip, experience sharing, didactic, resource sharing, or other?
  - Format: short, long, with media?
  
Assistant: Here’s a focused approach for the chosen topic:
  **Main idea** — Angle: <angle>
  **Approach** — <2–4 concise bullets describing the narrative/structure>

## Output

- Summarize themes, then ask 2–4 short interview questions to converge on a target topic.
- After the user selects a topic, ask a quick probe to define angle (tone) and format (short/long/with media).
- Present the approach for the chosen topic, aligned to the angle and format (no quick ideas yet).
- Confirm the selection and write the selected topic+angle+quick ideas into a `./topics/{YYYYMMDD}-safe_short_title.md` file.

## Format

Quick, short, and simple.

### Interview questions
Keep questions short and based on the detected themes. Aim for 2–4 questions.

### Topic approach presentation
Present a short, single-topic approach aligned to the chosen angle and format.
Do not show the quick ideas yet; keep them ready for the confirmation step.

### Selected topic format
When the user picks one, use this format for the written topic file:

<assistant-output>
# Skills over subagents: simplifying an agent toolbox without losing power

## Angle
Explain the reorg philosophy (clear skill boundaries, better docs, naming conventions, model variants) and how it improved day-to-day usage.

## Quick ideas
- Share your “skill template” (what every skill must include).
- Explain how you decide when something becomes a skill vs. stays ad-hoc.
- Show one concrete upgrade from the reorg (e.g., `amsg` or `browser-tools` workflow).

</assistant-output>

Don't include extras like a mini outline, optional artifacts, or a CTA, unless specifically requested by the user.
