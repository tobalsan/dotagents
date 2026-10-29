---
name: e2e-autonomy
description: Run E2E tests in Thinh's real logged-in Chrome (e2e-browser + playwright-cli), type passwords from 1Password without exposing them, and ask Thinh for input (missing password, 2FA code, captcha, human check, a decision) via ask-human, then wait, park and resume. Use for E2E tests, browser login, needing a password or 2FA, or being blocked on Thinh.
---

# E2E autonomy

## Browser
- Need Thinh's logins (Google, SaaS, real sessions)? → `e2e-browser`. Public pages / local dev with no login → plain `playwright-cli`.
- Always pair start/stop:
  ```
  S=$(e2e-browser start --name <agent> https://app.example.com)   # prints session name
  playwright-cli -s=$S snapshot | click e12 | type "text" | press Enter | goto <url>
  e2e-browser stop $S                                              # always, even on failure
  ```
- `e2e-browser list`, `e2e-browser gc` (clean dead copies), `e2e-browser refresh-template` (after Thinh logs in somewhere new).
- Human pace: slowMo 200 ms is set. Use `click`/`type`/`press` like a person, wait a few seconds between pages, one action at a time. Never use `eval`/`run-code` to fill forms or click. `eval` is for reading only.
- No writes on third-party sites unless the task says so.

## Secrets
- Only via `e2e-browser type-secret $S <ref> "op://Agents/<item>/<field>"`. It never prints the secret.
- Never `op read` into the transcript, never paste/echo/log secrets, never put them in Discord, Linear or files.
- After `type-secret`, the page snapshot can contain the value in clear: use `e2e-browser snapshot $S` (masked) instead of `playwright-cli snapshot`, submit the form right away, and never read `.playwright-cli/*.yml` files.
- Item missing from the `Agents` vault → ask-human `--kind password`; Thinh adds it and replies `added`.

## Ask Thinh
Ask when: secret missing in `Agents`, 2FA/OTP code, captcha/human check, decision only Thinh can make. Don't ask for things you can find, retry or decide yourself.
```
ask-human ask "<question>" --from <agent> [--ref ALG-123|url] --kind password|2fa|check|other
```
- First output line = thread id. Keep it.
- Exit codes: `0` answer printed · `75` PENDING → run `ask-human wait <id>` again · `76` TIMEOUT (4 h since asked) → park.
- Each call blocks ≤ 240 s (`--wait` to change) with a heartbeat line every 60 s. Per runner:
  - Claude Code: Bash timeout 2 min by default → pass `timeout: 300000` or use `--wait 100`.
  - Codex: commands up to 240 s run fine (verified); stall_timeout 10 min is not hit thanks to heartbeats/short chunks.
  - pi / Yoplai subagents: default is fine.
- Loop `ask-human wait <id>` on 75 until 0 or 76. Do other unblocked work between calls if any.

## Park (on 76, or if you must stop)
```
ask-human park <id> --note-file note.md --runner <codex|claude|pi|yoplai-pi|...> --session <session or run id>
```
note.md must have lines `Doing:` `Done:` `Next:` `Blocker:` (Where/Resume are added automatically). If there is a Linear issue, comment with the printed thread URL. Then stop.

## Resume
`ask-human resume <id>` prints a resume prompt (handoff + Thinh's replies) and, for Yoplai runs, the `yoplai subagents resume …` command to run.
`ask-human list [--status waiting|parked|answered]` shows open requests.
