---
name: docs-preparator
description: Process documentation URLs into concise, LLM-optimized knowledge for implementation. Use when user provides documentation links and needs to implement something based on those docs. E.g. "I need to implement auth using Supabase. Here are the docs https://supabase.com/docs/guides/auth", "Can you help me set up Inngest workflows? https://www.inngest.com/docs", "I want to add Redis caching using redis-py. The docs are at https://redis-py.readthedocs.io/"
---

# Docs Preparator

Transform verbose documentation into dense, actionable implementation knowledge.

## Workflow

1. **Fetch** - Retrieve content from URLs using web tools
2. **Extract** - Identify essential information:
   - Core concepts and architecture patterns
   - API signatures, parameters, return types
   - Setup/config steps
   - Common patterns and best practices
   - Import statements and dependencies
   - Error handling approaches
   - Auth patterns when relevant

3. **Condense** - Strip ruthlessly:
   - Remove verbose explanations, keep actionable facts
   - Remove marketing, tutorials, beginner content
   - Eliminate redundant examples
   - Use terse, technical language
   - Prefer bullets and code over prose
   - Omit obvious information

4. **Format** - Structure for LLM consumption:
   - Direct, imperative instructions
   - Minimal working examples with inline comments
   - Key constraints and gotchas flagged
   - Dependencies and version requirements
   - Quick-reference format for APIs

## Output Format

```markdown
# [Library/Service Name] - Implementation Guide

## Setup
[Minimal install/config steps]

## Core Concepts
[Terse explanations of key abstractions]

## Common Patterns
[Minimal working examples]

## API Quick Reference
[Key functions/methods with signatures]

## Gotchas
[Critical constraints, errors, edge cases]

## Dependencies
[Required packages, versions]
```

## Constraints

- Max 4000 tokens output
- No tutorials or learning paths
- No "why" unless critical to correctness
- Code must be copy-paste ready
- Assume reader has general programming knowledge

## Error Handling

- URL unreachable: report and suggest alternatives
- Docs too large: focus on most relevant sections
- Unclear priority: ask user for specific focus areas

## Quality Checks

- Verify code snippets are syntactically valid
- Ensure APIs match current docs
- Flag ambiguities or missing info
- Note if docs seem outdated
