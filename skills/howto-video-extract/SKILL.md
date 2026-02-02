---
name: howto-video-extract
description: "Use when tasked with extracting step-by-step how-to guides from screen recordings (videos or GIFs) with minimal token usage."
---

# Screen Recording Process Extraction

Extract step-by-step how-to guides from screen recordings (videos or GIFs) with minimal token usage.

## When to Use

- User uploads a screen recording and asks for a how-to guide
- User wants to document a workflow they recorded
- User needs written instructions extracted from a video demonstration

## Source Format Recommendations

If the user hasn't recorded yet, recommend:
- **MP4/WebM over GIF**: 3-5x smaller files, better quality
- **1080p or lower**: Higher resolutions waste tokens without adding clarity for UI workflows
- **15-60 seconds ideal**: Longer recordings should be split into logical segments

## Extraction Strategy

### Step 1: Extract Frames Efficiently

Always create a working directory and use **scene detection** first:

```bash
mkdir -p /tmp/claude # or user-specified directory

# Scene detection - captures frames only when visual changes occur
ffmpeg -i INPUT_FILE -vf "select='gt(scene,0.08)'" -vsync vfr /tmp/claude/scene_%03d.png 2>&1 | tail -5
```

Check how many frames were captured:
```bash
ls /tmp/claude/*.png | wc -l
```

**Fallback strategies if scene detection produces too few/many frames:**

```bash
# If too few frames (< 5): lower threshold
ffmpeg -i INPUT_FILE -vf "select='gt(scene,0.03)'" -vsync vfr /tmp/claude/scene_%03d.png

# If too many frames (> 30): raise threshold
ffmpeg -i INPUT_FILE -vf "select='gt(scene,0.15)'" -vsync vfr /tmp/claude/scene_%03d.png

# Alternative: fixed interval (1 fps for slow workflows, 2 fps for fast)
ffmpeg -i INPUT_FILE -r 1 /tmp/claude/interval_%03d.png
```

### Step 2: Get Recording Metadata

```bash
ffprobe -v quiet -print_format json -show_format -show_streams INPUT_FILE | jq '{duration: .format.duration, frames: .streams[0].nb_frames}'
```

### Step 3: Strategic Frame Viewing

**Do NOT view all frames.** Use this approach:

1. View first frame (starting state)
2. View last frame (end state)  
3. View ~5-8 evenly distributed middle frames
4. If a transition is unclear, view adjacent frames to that point

Example for 20 extracted frames:
```
View: 1, 3, 6, 9, 12, 15, 18, 20
```

### Step 4: Identify Key State Changes

While viewing, note:
- UI elements that appear/disappear
- Menu openings/closings
- Text being typed
- Selections being made
- Confirmations/notifications

## Output Format

Structure the how-to guide as:

```markdown
## [Action Title]

**Prerequisites:** [Starting state/requirements]

**Steps:**

1. **[Action verb] [target]** — [Brief context if needed]
2. **[Action verb] [target]** — [Result of action]
3. ...

**Result:** [End state confirmation]
```

### Example Output

```markdown
## Add a Connection to a Notion Database

**Prerequisites:** Open your Notion database page

**Steps:**

1. **Click the ••• menu** in the top-right corner of the database
2. **Hover over "Connections"** to reveal the submenu
3. **Click "Add connection"** to open the integration picker
4. **Search for your integration** by typing its name
5. **Click the integration** to add it to your database

**Result:** The integration now has access to this database and appears in the Connections list.
```

## Token Optimization Summary

| Approach | Frames Viewed | Relative Cost |
|----------|---------------|---------------|
| View all frames | 100% | Highest |
| Fixed interval (1fps) | ~15-60 frames | Medium |
| Scene detection + strategic viewing | 5-10 frames | **Lowest** |

## Handling Edge Cases

**Recording is too long (> 2 min):**
- Ask user to identify the approximate timestamp range of interest
- Extract only that segment: `ffmpeg -i INPUT -ss 00:00:30 -t 00:00:45 -c copy segment.mp4`

**Recording has no clear UI changes (e.g., terminal work):**
- Use interval extraction at 0.5 fps
- Focus on text content changes rather than visual state

**Multiple workflows in one recording:**
- Identify breakpoints by scanning frames
- Document each workflow separately with clear headings

**Low quality or small text:**
- Note limitations in the guide
- Ask user to clarify specific steps if unreadable

## Quick Reference

```bash
# Full efficient extraction workflow
mkdir -p /tmp/claude
ffmpeg -i INPUT -vf "select='gt(scene,0.08)'" -vsync vfr /tmp/claude/f_%03d.png
ls /tmp/claude/*.png | wc -l
```

Then view strategically: first, last, and ~6 evenly-spaced middle frames.
