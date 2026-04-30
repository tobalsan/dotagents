# FRP Quality Gates

Before declaring FRP done, every gate below must pass. If any fails, loop back to the relevant probing step.

## Goal Gates (Step 1)

- [ ] Feature stated in 2–3 sentences: what it does, for whom, success measure
- [ ] In-scope and out-of-scope explicitly listed
- [ ] No vague verbs left ("manage", "handle", "support") — all replaced with concrete behavior
- [ ] Success definition is observable, not aspirational

## Scale Gates (Step 2)

- [ ] Profile labeled (solo dev / internal MVP / prod-low / prod-HA / ...)
- [ ] User count / load named
- [ ] Failure tolerance named (what breaks if it breaks)
- [ ] Quality-bar implications drawn (e.g. "no E2E at this scale" or "feature flag required")

## Validation Gates (Step 3 — CRITICAL)

- [ ] Exact workspace path / branch / worktree specified
- [ ] Setup commands listed verbatim
- [ ] Service/server/preview command listed verbatim with port/URL/socket (if feature exposes a runtime surface)
- [ ] Test commands listed verbatim with file paths or patterns
- [ ] Lint + typecheck + build commands listed
- [ ] Testing modality named (unit / CLI / HTTP / server-RPC / library / browser-UI)
- [ ] If CLI: exact command + fixtures/inputs + expected stdout + expected exit code
- [ ] If HTTP: exact request (method/URL/headers/body) + expected status + response shape + auth setup
- [ ] If server / socket / RPC: bring-up command + client used + messages sent + expected responses
- [ ] If library/SDK: minimal driver script + asserted return values or side effects
- [ ] If browser/UI: URL + step-by-step interaction sequence (clicks, inputs, waits) + element selectors or visual checks + named browser-automation skill
- [ ] An end-to-end protocol against the running thing is specified — not just static checks
- [ ] Skills/tools to use named explicitly
- [ ] Acceptance criteria each tie to a runnable check
- [ ] Success and failure signals distinguishable from output alone

## "Fresh Agent" Test

Imagine an agent with zero prior context picks up the FRP. Can they:
- Find the workspace? ✅ / ❌
- Run setup without guessing? ✅ / ❌
- Execute every validation step? ✅ / ❌
- Tell pass from fail without asking? ✅ / ❌

If any ❌, FRP is not done.

## Information Density

- [ ] No generic references — all paths/URLs/commands are specific
- [ ] URLs include section anchors where applicable
- [ ] File references point at exact patterns to follow
- [ ] No "etc.", "and so on", "make sure it works" placeholders
