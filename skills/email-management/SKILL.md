---
name: email-management
description: Manage email with the gog CLI (Gmail). Use when you need to search, read, summarize, label, draft, or send email; manage threads, labels, drafts, or attachments; or produce machine-readable Gmail output via gog.
---

# Email Management

You have access to the `gog` cli tool to interact with my Gmail inbox.

## Base Instructions

Always operate only on the emails in the **Inbox**, unless the user explicitly requests a broader or different scope.
When the user asks to search by label, do not auto-add the `INBOX` label unless they explicitly include it.
Make sure you fetch ALL emails inside the inbox, adjusting the max results parameters of the API if needed.
When the action is **archive**, archive directly from the inbox.
When an action involves adding a label, use the following top-level labels:
- For emails requiring action, use the `action-required` label.
- To place an email for review, use the `review` label.
- For newsletters I want to keep/read, use the `newsletter` label.
- To trash an email, use the `trashed` label.

Once an email has been processed, you must mark it as read.

## Inbox Triage Decisions

All the reference information to decide how to triage an email are in the [triage-decisions.md](references/triage-decisions.md) file.

## gogcli use

### Overview

Use `gog` to authenticate a Gmail account and perform email operations (read, search, label, draft, send) with safe defaults and explicit confirmations for destructive actions.

### Quick start
1. Verify access by listing labels:
   - `gog gmail labels list`

### Read and search email (non-destructive)
- Search threads with Gmail query syntax:
  - `gog gmail search 'newer_than:7d' --max 20`
  - `gog gmail search 'from:billing@stripe.com is:unread' --max 10`
- Inspect a thread:
  - `gog gmail thread get <threadId>`
- Get a single message (metadata or full):
  - `gog gmail get <messageId> --format metadata`
  - `gog gmail get <messageId> --format full`
- Emit URLs for quick web access:
  - `gog gmail url <threadId>`

### Labels
- List labels:
  - `gog gmail labels list`
- Get label details (includes counts):
  - `gog gmail labels get INBOX`
- Modify labels on threads (confirm before running):
  - `gog gmail labels modify <threadId> --add IMPORTANT --remove UNREAD`

### Drafts
- List drafts:
  - `gog gmail drafts list`
- Get a draft:
  - `gog gmail drafts get <draftId>`
- Create a draft (review before sending):
  - `gog gmail drafts create --to you@example.com --subject "Hello" --body "Draft body"`
- Send a draft (confirm before running):
  - `gog gmail drafts send <draftId>`
- Delete a draft (confirm before running):
  - `gog gmail drafts delete <draftId>`

### Send email (destructive)
- Send an email (confirm recipients and body):
  - `gog gmail send --to you@example.com --subject "Subject" --body "Body"`

### Attachments
- Download a single attachment:
  - `gog gmail attachment <messageId> <attachmentId> --out ./attachment.bin`

### Output formats
- Use JSON output for scripting:
  - `gog --json gmail search 'newer_than:1d' --max 5`

### Safety checklist
- Confirm the target account (`--account` or `GOG_ACCOUNT`) before any send/modify/delete action.
- Prefer `search`, `thread`, `get`, `labels list`, and `drafts list/get` for read-only work.
- Ask for explicit confirmation before `send`, `drafts send`, `drafts delete`, or `labels modify`.
