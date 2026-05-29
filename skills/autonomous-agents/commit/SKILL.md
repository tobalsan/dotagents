---
name: commit
description: Create atomic commits with strict formatting rules. Use when user asks to commit changes with /commit or explicitly requests creating a git commit. Enforces 50-char max commit message, why-focused commit message/body, conventional commit format (feat/fix/refactor/docs/test/chore), and explicit file paths only (never git add . or commit -a).
---

# Commit

Create atomic commits following strict formatting and atomicity rules.

## Rules

### Message Length Limits (IRON RULE)

- Main message: 50 chars max
- Body: max 3 lines, each 72 chars max
- Footer (if included): max 1 line, 72 chars max

### Atomic Commits

Keep commits atomic:
- Commit only files actually touched
- Always list paths explicitly in commit command
- **One purpose per commit.** If changes implement several features, fixes, or
  unrelated purposes, split them into multiple separate commits — never bundle
  distinct purposes into a single commit, even if they touch overlapping files.

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

### Explain WHY, Not Just WHAT

Commit summary and body must explain why the change exists: user need,
bug impact, invariant being protected, or operational reason. Avoid summaries
that only name changed files or say what code was added.

A body is required unless the summary is truly explicit by itself. When changes
are medium or large, touch many files, or include multiple coordinated parts,
always include a body listing the important reasons/behavior. A large commit
like `2a1b7646bc3e` must have a body.

Use up to 3 body lines. Each line should add decision context or grouped impact,
not repeat the summary.

Example:
```git
feat(auth): require TOTP for admins

Protects privileged routes after password compromise.
Keeps user sessions valid while enforcing admin step-up.
```
