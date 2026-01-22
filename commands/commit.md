---
description: Create an atomic commit 
---

Commit the changes by following these rules:

## IRON RULE: BE CONCISE

Main commit message must be 50 chars max.

If including a body, only two lines / bullet points allowed, each 72 chars max.
If including a footer, only one line, 72 chars max.

## Atomic commits

Keep commits atomic:
- Commit only the files you actually touched.
- Always list paths explicitly in the commit command.

You MUST use the following commands to commit:

- For tracked files:
  git commit -m "<scoped message>" -- path/to/file1 path/to/file2

- For brand-new files:
  git restore --staged :/
  git add "path/to/file1" "path/to/file2"
  git commit -m "<scoped message>" -- path/to/file1 path/to/file2

Never run `git add .` or `git commit -a`. Those break atomicity.

## Conventional commits

The commit message must follow the Conventional commit format:

Use: <type>[(scope)][!]: <summary>"
Types: feat|fix|refactor|docs|test|chore"
Example: 

```git
feat(auth): add TOTP"

[optional body, max two lines, each under 72 chars]

[optional footer, max one line under 72 chars]
```
