---
name: calendar-management
description: Manage Google Calendar using the `gog` CLI tool. Use when the user asks to view calendar events, check schedule, create/update/delete events, respond to invitations, or check availability. Triggers on requests like "what's on my calendar", "schedule a meeting", "am I free tomorrow", "create an event", "decline invitation".
---

# Calendar Management

Manage Google Calendar via the `gog` CLI tool.

## Quick Reference

```bash
# List calendars (get calendar IDs)
gog calendar calendars

# List events for today
gog calendar events --all --from 2025-01-15T00:00:00Z --to 2025-01-16T00:00:00Z

# List events for a date range
gog calendar events --all --from 2025-01-15T00:00:00Z --to 2025-01-22T00:00:00Z

# Create event
gog calendar create <calendarId> \
  --summary "Meeting title" \
  --from 2025-01-15T10:00:00Z \
  --to 2025-01-15T11:00:00Z

# Create event with attendees
gog calendar create <calendarId> \
  --summary "Team Sync" \
  --from 2025-01-15T14:00:00Z \
  --to 2025-01-15T15:00:00Z \
  --attendees "alice@example.com,bob@example.com" \
  --location "Zoom"

# Update event
gog calendar update <calendarId> <eventId> \
  --summary "Updated title" \
  --from 2025-01-15T11:00:00Z \
  --to 2025-01-15T12:00:00Z

# Delete event
gog calendar delete <calendarId> <eventId>

# Respond to invitation
gog calendar respond <calendarId> <eventId> --status accepted|declined|tentative

# Check availability
gog calendar freebusy --calendars "primary,work@example.com" \
  --from 2025-01-15T00:00:00Z --to 2025-01-16T00:00:00Z

# Find conflicts
gog calendar conflicts --calendars "primary,work@example.com" \
  --from 2025-01-15T00:00:00Z --to 2025-01-22T00:00:00Z

# Search events
gog calendar search "meeting" --from 2025-01-01T00:00:00Z --to 2025-01-31T00:00:00Z
```

## Defaults

- **Calendar ID**: `tobalsan@gmail.com` (when unspecified)
- **Date format**: Always use full ISO format `2025-01-15T00:00:00Z`
- **`--from` date**: Almost always use today's date as the start

## Common Workflows

### View upcoming events
1. Determine date range (today, this week, etc.)
2. Run `gog calendar events --all --from <start> --to <end>`

### Schedule new event
1. Get calendar ID if needed: `gog calendar calendars`
2. Create event with `gog calendar create`

### Check if free at a time
1. Run `gog calendar freebusy` for the time range
2. Or list events and check manually
