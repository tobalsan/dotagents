---
name: linctl
description: "Use the linctl CLI to manage Linear projects, milestones, updates, issues, sub-issues/parents, and comments. Trigger when a task requires listing/getting/creating/updating Linear items via linctl." 
---

# linctl

## Overview
Run linctl commands for Linear project/issue management.

## Projects
```bash
# List
linctl project list --team ENG

# Get
linctl project get PROJECT-UUID

# Create
linctl project create --name "Q1 Backend" --team ENG --state planned --target-date 2024-12-31

# Update
linctl project update PROJECT-UUID --name "New Name" --state started
```

## Project milestones
```bash
# List
linctl milestone list PROJECT-UUID

# Get
linctl milestone get MILESTONE-UUID

# Create
linctl milestone create PROJECT-UUID --name "Alpha Release" --target-date 2024-06-30

# Update
linctl milestone update MILESTONE-UUID --name "Beta Release" --target-date 2024-07-15
```

## Project updates
```bash
# Create status update
linctl project update-post create PROJECT-UUID --body "Weekly progress" --health onTrack
# health: onTrack | atRisk | offTrack
```

## Issues
```bash
# List
linctl issue list --team ENG --assignee me --state "In Progress"

# Get
linctl issue get LIN-123

# Create
linctl issue create --title "Bug fix" --team ENG --assignee me --priority 2

# Update
linctl issue update LIN-123 --title "New title" --state "In Review" --assignee john@example.com
```

## Sub-issues / parent
```bash
# Set parent (make LIN-124 a sub-issue of LIN-123)
linctl issue update LIN-124 --parent LIN-123

# Remove parent
linctl issue update LIN-124 --parent none

# Create sub-issue directly
linctl issue create --title "Sub-task" --team ENG --parent LIN-123
```

## Comments
```bash
# List
linctl comment list LIN-123

# Get comment ID (for update/delete)
linctl comment list LIN-123 --json | jq '.[0].id'
# Note: [0] = most recent comment

# Create
linctl comment create LIN-123 --body "This is fixed"

# Update
linctl comment update COMMENT-UUID --body "Updated text"

# Delete
linctl comment delete COMMENT-UUID
```

## Output flags
- `--json` / `-j` JSON output
- `--plaintext` / `-p` plain text
