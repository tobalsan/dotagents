---
name: todo-management
description: Manage todos / tasks using plain text files. Use when you need to track and manage todos, list, add, update, or delete tasks.
---

# Todo Management

I write all my todos in plain text files, in my Obsidian journal note, for convenience, but they are not meant to be kept there.
Some todos are just personal home/admin tasks, and some are project-related.

Project/tasks/todos are all stored in the `~/projects` folder as plain folders and files. 
Though, to manage and interact with them, you must always use the `apm` command line tool.
To create a new project: 

```bash
apm create -t "title"
```

## `apm` reference

```
Usage: apm list [options]

Options:
  --status <status>  Filter by status
  --owner <owner>    Filter by owner
  --domain <domain>  Filter by domain
  -j, --json         JSON output
  -h, --help         display help for command


Usage: apm get [options] <id>

Arguments:
  id          Project ID

Options:
  -j, --json  JSON output
  -h, --help  display help for command


Usage: apm create [options]

Options:
  -t, --title <title>      Project title
  --domain <domain>        Domain (life|admin|coding)
  --owner <owner>          Owner
  --execution-mode <mode>  Execution mode
                           (manual|exploratory|auto|full_auto)
  --appetite <appetite>    Appetite (small|big)
  --status <status>        Status


Usage: apm update [options] <id>

Arguments:
  id                       Project ID

Options:
  --title <title>          Title
  --domain <domain>        Domain (life|admin|coding)
  --owner <owner>          Owner
  --execution-mode <mode>  Execution mode
                           (manual|exploratory|auto|full_auto)
  --appetite <appetite>    Appetite (small|big)
  --status <status>        Status
  --content <content>      Content string or '-' for stdin


Usage: apm move [options] <id> <status>

Arguments:
  id          Project ID
  status      New status   (not_now|maybe|shaping|todo|in_progress|review|done)

```

## Todo Extraction

You will regularly need to "extract" the todos from my journal files and turn them into new projects.

### Locate TODOs in the Obsidian journal notes

To determine which files to use, start by looking at the current date: `!date +%Y-%m-%d`

Then locate the relevant journal file in the Obsidian vault.
- Locate and read current week journal file. All weekly journal notes are stored in the folder `/Users/thinh/Documents/vaults/personal/Journal/entries/2. Weekly Notes/<year>`. The file format is `YYYY-WXX.md` where `XX` is the week number.
- Also read the previous week file. There could be unresolved todos from the past week that must be resurfaced. Any unresolved todo past two weeks is considered dropped.

For instance, if the date is `2025-01-31`, the weekly journal file is `/Users/thinh/Documents/vaults/personal/Journal/entries/2. Weekly Notes/2025/2025-W04.md` (or `2025-W05.md` depending on certain months/years). 

Make sure that you do not skip any unresolved todos (within this week or the last). Some todos may be isolated or not related to a particular theme, but must still be included.
Perform a second pass to check you haven't missed any unresolved todos.

Weekly journal files, while being plain text, can be quite large. To avoid overloading the context, use the following simple commands to retrieve only the todos:

```bash
# All todo lines (done + undone)
cat weekly_journal_file.md | rg -n '\- \[[ x]\]'

# Done items only
cat weekly_journal_file.md | rg -n '\- \[x\]'

# Todo items only
cat weekly_journal_file.md | rg -n '\- \[ \]'
```

Once you have identified all the todo items in the target journal files, upon request, extract them using the `apm` command line tool.
Once you have extracted all the todos, remove them from the journal file. Prefer line-by-line deletions.
Always end with a report of the extracted todos and the parameters you used, using a simple bullet list. 

## Adding/Updating/Deleting todos

### Adding todos

When Thinh requests adding a new todo, assess what's the domain for the todo (life, admin, or coding).
Again, if 80% confident or more, create todo project directly using `--domain`. Otherwise, ask Thinh for confirmation.
If the title is long or detailed, create a concise title and store the full original request in the project `--content` (no prefix text).
Report once the todo is added.

### Updating todos

To update a todo use `apm update` command.
To mark a todo as done, use `apm move <id> done`.


