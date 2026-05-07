---
name: save-conversation
description: Save the current chat as a conversation thread. Use when asked to "save this conversation", "capture this chat", "save this thread", or similar. Transforms the ongoing exchange into a structured markdown file stored in ~/projects/.conversations/.
---

# Save Conversation

Save the current session's chat as a reusable conversation file.

## Steps

1. Use `sessions_history` (current session, `includeTools: false`, `limit: 100`) to pull recent messages.
2. Identify the relevant portion — usually the full conversation, but the user may specify a topic or range.
3. Auto-generate a short slug from the main topic (lowercase, hyphens, max 5 words). Example: `agent-orchestration-ui-ideas`.
4. Format the conversation as markdown (see Format below).
5. Create folder `~/projects/.conversations/<YYYY-MM-DD>_<slug>/` and save as `THREAD.md` inside it. Attachments (images, files referenced in the conversation) go in the same folder.
6. Confirm to the user with the folder path.

## Format

```markdown
---
title: "<Descriptive title>"
date: "YYYY-MM-DD"
participants:
  - <Name or role>
  - <Name or role>
source: <channel name, e.g. WhatsApp, Discord, Telegram>
tags:
  - <tag>
  - <tag>
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
- If no topic is specified, include the full meaningful conversation (skip greetings/heartbeats).
