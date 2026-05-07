---
name: notion-cli 
description: Use the custom `notion` CLI tool to interact with Notion databases and pages.
---

# Using custom Notion CLI tool

## Instructions

Whenever:

- asked to interact with Notion databases or pages,
- the request mentions page IDs such as `AI-3`, `PRO-19` or `SCO-34`

Use the custom `notion` CLI tool. This tool allows you to perform various operations such as querying databases, viewing properties, retrieving existing page content, creating and updating pages.

You can use `notion --help`, `notion {command} --help`, and `notion {command} {operation} --help` to explore available commands and options.

ALWAYS use the `--json` for every command.

For the complete command line reference, see [reference.md](reference.md).

## Viewing a page

To view a page, use the command:

```bash
notion page view "{PAGE_TITLE}" # markdown output

notion page view "{PAGE_TITLE}" --json # JSON output
```

## Finding Notion Pages Efficiently

### Quick Lookup Pattern
1. Use `notion db list --json` to identify database names
2. Use `notion db show {DATABASE_NAME} --json` to view entries (shows titles)
3. Use `notion page view "{PAGE_TITLE}" --json` to get full content and properties (including ID)

## Page Updates
- When using `page view` with `--json`, it returns simplified blocks, don't mimic this structure. In reality, `--blocks` requires full Notion API format
- To-do: `{"object":"block","type":"to_do","to_do":{"rich_text":[{"text":{"content":"text"}}],"checked":true}}`
- Paragraph: `{"object":"block","type":"paragraph","paragraph":{"rich_text":[{"text":{"content":"text"}}]}}`
- Heading: `{"object":"block","type":"heading_2","heading_2":{"rich_text":[{"text":{"content":"text"}}]}}`
- See reference.md for all block types

### Avoid
- Don't use `notion page find` unless you need fuzzy search across all pages
- Don't attempt filters on `db show` without checking syntax first
- Query by known titles directly to `page view` — it's fastest

