# FRP: <feature name>

## 1. Goal

**Problem**: <concrete pain solved>

**End-user behavior**: <what user can do after ship that they couldn't before>

**Inputs → Outputs**: <data flow>

**In scope**:
- <bullet>

**Out of scope** (explicit):
- <bullet>

**Success definition**: <measurable, observable>

## 2. Scale & Quality Bar

**Profile**: <solo dev | internal MVP | production-low-criticality | production-HA | ...>

**Constraints**:
- Users / load: <e.g. 1 user, ~50 internal, public prod>
- Environment: <local | staging | prod | multi-region>
- Failure tolerance: <annoyance | lost data | page oncall>
- Performance budget: <latency, throughput, or N/A>
- Security / compliance: <auth, PII, audit, or none>
- Persistence: <ephemeral | single-user store | shared DB | ...>
- Migration / rollback: <plan or N/A>

**Quality bar implications**:
- <e.g. unit tests sufficient — no E2E needed at this scale>
- <e.g. needs feature flag + staged rollout>

## 3. Context

**Codebase pointers**:
- `<path/to/file.ext>` — <why relevant, pattern to follow>
- `<path/to/test.ext>` — <existing test pattern>

**External docs** (with section anchors):
- <https://...#section> — <what it covers>

**Conventions to follow**:
- <naming, style, error handling pattern observed in repo>

**Known gotchas**:
- <library quirks, version pins, prior incidents>

## 4. Implementation Tasks (dependency-ordered)

1. <task> — <files touched, key naming>
2. <task> — <...>
3. <task> — <...>

## 5. Validation Plan

> A fresh agent must be able to execute this top-to-bottom without asking questions.

### 5.1 Setup

**Workspace**: <exact path or worktree, e.g. `~/.worktrees/$project/feature-x`>
**Branch**: <branch name>
**Install**: `<command>`
**Env / secrets**: <vars needed, where to get them>
**Services to start**: `<command>` (e.g. `docker compose up db`)

### 5.2 Commands to run

- Lint: `<command>`
- Typecheck: `<command>`
- Unit tests: `<exact path/pattern>`
- Integration tests: `<exact path/pattern>`
- Build: `<command>`

### 5.3 Manual / interactive verification

**Modality**: <unit-only | CLI | browser | HTTP API | ...>

**Skills / tools to use**:
- <e.g. `webapp-testing` for Playwright browser flows>
- <e.g. `agent-browser` for visual confirmation>
- <e.g. `verification-before-completion` before marking done>

**Steps**:
1. <action> → <expected observable result>
2. <action> → <expected observable result>

**For browser flows**: URL = `<url>`, flow = `<click X → fill Y → assert Z>`
**For CLI flows**: command = `<exact>`, expected stdout/exit code = `<...>`
**For HTTP**: `curl ...` → expected status / response shape

### 5.4 Acceptance criteria

- [ ] <observable behavior 1, tied to command or check above>
- [ ] <observable behavior 2>
- [ ] <observable behavior 3>

### 5.5 Success vs failure signals

**Success**: <exact output / state>
**Failure / regression**: <what to watch for; existing tests that must still pass>

## 6. Open Questions / Risks

- <risk or unknown to flag>

## 7. Confidence

**One-pass implementation likelihood**: <1–10>
