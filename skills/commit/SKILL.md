---
name: commit
description: Create atomic commits with strict formatting rules. Use when user asks to commit changes with /commit or explicitly requests creating a git commit. Enforces 50-char max commit message, conventional commit format (feat/fix/refactor/docs/test/chore), and explicit file paths only (never git add . or commit -a).
---

# Commit

Create atomic commits following strict formatting and atomicity rules.

## Rules

### Message Length Limits (IRON RULE)

- Main message: 50 chars max
- Body (if included): max 2 lines, each 72 chars max
- Footer (if included): max 1 line, 72 chars max

### Atomic Commits

Keep commits atomic:
- Commit only files actually touched
- Always list paths explicitly in commit command

**For tracked files:**
```bash
git commit -m "<message>" -- path/to/file1 path/to/file2
```

**For brand-new files:**
```bash
git restore --staged :/
git add "path/to/file1" "path/to/file2"
git commit -m "<message>" -- path/to/file1 path/to/file2
```

Never run `git add .` or `git commit -a` - breaks atomicity.

### Conventional Commits Format

Use: `<type>[(scope)][!]: <summary>`

Types: `feat|fix|refactor|docs|test|chore`

Example:
```git
feat(auth): add TOTP

[optional body, max two lines, each under 72 chars]

[optional footer, max one line under 72 chars]
```
