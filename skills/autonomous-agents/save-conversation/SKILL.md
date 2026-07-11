---
name: save-conversation
description: Save the current chat as a conversation thread. Use when asked to "save this conversation", "capture this chat", "save this thread", or similar. Transforms the ongoing exchange into a structured markdown file, saving it to the user-provided location.
---

# Save Conversation

Save the current session's chat as a reusable conversation file.

## Steps

1. Gather history:
  - If you have any session history tool (e.g. `sessions_history` with current session, `includeTools: false`) use it to pull recent messages.
  - Otherwise, simply use your current context window.
2. Identify the relevant portion — usually the full conversation, but the user may specify a topic or range.
3. Auto-generate a short slug from the main topic (lowercase, hyphens, max 5 words). Example: `agent-orchestration-ui-ideas`.
4. Format the conversation as markdown (see Format below).
5. If the user provided a save location, use it, otherwise ask them. Save the conversation as a markdown file at that location. 

## Format

```markdown
---
title: "<Descriptive title>"
date: "YYYY-MM-DD"
participants:
  - <Name or role>
  - <Name or role>
source: <channel name, e.g. CLI, WhatsApp, Discord, Telegram>
---

# <Title>

**<Speaker>** (<HH:MM>):
Message content here.

**<Speaker>** (<HH:MM>):
Response content here.

**<Speaker>** (<HH:MM>):
Another message.
```

## Rules

- Strip tool calls, system events, heartbeats, and internal noise — only keep human and assistant messages that are part of the actual conversation.
- Preserve links, code blocks, and formatting from original messages.
- Keep assistant messages concise if they were very long — summarize verbose tool-result explanations, but keep the substance.
- If the user specifies a topic, only include messages relevant to that topic.
- If no topic is specified, include the full meaningful conversation (skip greetings, pings, system stuff).
