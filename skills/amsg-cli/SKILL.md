---
name: amsg-cli
description: Communicate with other agents via the `amsg` CLI tool. Use whenever you need to send messages to other agents or check your inbox and read messages.
---

# amsg Quick Reference

Inter-agent messaging via `~/.amsg/`. Messages are YAML frontmatter `.md` files.

## Commands

```bash
# Registry (creates .amsg-info in cwd for auto sender resolution)
# Defaults: id=folder_name, name="Folder Agent", cwd=current_dir
amsg register [id] [-n "Name"] [-t tags] [-c /cwd] [-d "description"]
amsg unregister [id] # resolve id from .amsg-info if not provided
amsg index # list agents with corresponding tmux pane if available

# Send (body from stdin; --sender auto-resolved from .amsg-info if omitted)
echo "msg" | amsg send <recipient> -s "Subject"
echo "msg" | amsg reply <thread_id> --to <recipient>

# Inbox (states: new|processing|processed|deadletter)
# -a optional if .amsg-info exists in cwd
amsg inbox [-a <id>] [--new|--processing|--processed|--deadletter]
amsg pull [-a <id>] [--max N]  # new → processing
amsg show <thread_id>          # display thread
amsg ack <msg_id> [-a <id>]    # processing → processed
amsg fail <msg_id> [-a <id>] -e "error"  # → deadletter
amsg requeue <msg_id> [-a <id>]  # processing → new
```

## Message Lifecycle

1. `send`/`reply` creates message + delivers pointer to recipient's `new/`
2. `pull` claims pointer → `processing/`
3. `ack` completes → `processed/` | `fail` → `deadletter/` | `requeue` → `new/`

## Workflow Pattern

```bash
# Check for work (agent from .amsg-info if in registered cwd)
amsg inbox --new
# Claim message
amsg pull
# Read full thread
amsg show $THREAD_ID
# Process, then acknowledge
amsg ack $MSG_ID
# Or reply (sender from .amsg-info)
echo "response" | amsg reply $THREAD_ID --to $OTHER
```

The messages system is file-based, so don't try to pull and read the message at the same time.

```bash
# Don't do this
amsg pull && amsg show <thread_id> ❌

# Do this instead
amsg pull # Message is claimed
amsg show <thread_id>
```

