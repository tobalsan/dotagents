---
name: e2e-autonomy
description: Run E2E tests in Thinh's real logged-in browser with buu, type passwords from 1Password without exposing them, hand a step to Thinh in the tab (login, 2FA, captcha) with handoff(), and ask Thinh for what only he can give (a missing vault item, a decision) via ask-human, then wait, park and resume. Use for E2E tests, browser login, needing a password or 2FA, or being blocked on Thinh.
---

# E2E autonomy

## Browser
- Use buu for all browser work. Read the `buu` skill first for the commands and rules.
- On the Mac Studio, buu drives the main Chrome of the `agents` user. Only agents use it. Thinh sees it through screen sharing.
- On Thinh's MacBook, buu drives his own browser. Do not claim his tabs unless he asks.
- One session for each task. Always end it, also after a failure:
  ```sh
  export BUU_SESSION=<agent>-<task>
  buu js "await page.goto('https://app.example.com'); return page.url()"
  buu js "print(await page.locator('body').ariaSnapshot())"   # read the page
  buu js "await page.getByRole('button', {name: 'Sign in'}).click()"
  buu js "await shot()"                                      # prints a PNG path
  buu end
  ```
- Act at human pace. Do one action for each call, and wait a few seconds between pages.
- If `buu status` says that no browser is connected, Chrome is closed. Ask Thinh to open it.
- No writes on third-party sites unless the task says so.

## Secrets
- Type a secret with the helper in this skill. Never put a secret in `buu js` code:
  ```sh
  <skill-dir>/scripts/type-secret.sh "op://Agents/<item-id>/password" "page.getByLabel('Password')"
  ```
  The value goes through a pipe only. It is not in argv, stdout, stderr, or a file.
- Submit right after you type. Do not read the field back, and do not snapshot the page between the type and the submit.
- buu does not redact output. A screenshot or snapshot shows what the page renders.
- Refer to items by id, not by title: `op://Agents/<item-id>/<field>`. List ids: `op item list --vault Agents --format json | jq -r '.[] | "\(.id)\t\(.title)"'`. A title with a character like `—` fails with "invalid character in secret reference". That is not a sign-in problem.
- Check sign-in with `op whoami` before you ask Thinh.
- Never `op read` into the transcript. Never paste, echo, or log a secret. Never put a secret in Mattermost, Linear, or a file.
- `op` is the wrapper `~/.local/bin/op`. It runs as the `Agents` service account (token in `~/.config/op-sa/token`).
- If an `op` call hangs with no output, the call used `/opt/homebrew/bin/op` without the token, for example from a login `bash -l`. 1Password then shows an "authorize <app>" modal. Call `op` by name in a non-login shell. Never ask Thinh to approve the modal, because it gives access to his personal vaults.
- Do not call `op` from inside `buu js`. On the Mac Studio, macOS then shows an "authorize node" prompt after each Node update, and the call hangs until Thinh accepts it. Use `type-secret.sh`.
- Google accounts: passkeys do not work. Click "Try another way", then use the password and the authenticator code: `type-secret.sh "op://Agents/<item>/one-time password?attribute=otp" "<locator>"`.

## Missing access: get it, never skip
The point of this routine is to finish checks that need Thinh's access. Lack of access is a blocker to solve, not a reason to skip, unless the task says to skip that check.
- The Google account in the agents Chrome is cloud@tobal.fr (vault item id `3sayrtetl6andnpgji6thaqtuy`). Use it for Google SSO.
- Signed out of a site → log in. Find the item in the `Agents` vault and type it with `type-secret.sh`. For "Continue with Google", log in to Google first.
- No item in the vault → `ask-human --kind password` with the site and the account. Thinh adds the item and replies `added`.
- 2FA code, captcha, human check, or a failed login → hand the step to Thinh (next section).
- Skip only when the task or Thinh says so. On a timeout, park. Do not skip.

## Hand a step to Thinh
Thinh does the step himself in the tab, through screen sharing. He does not send codes in chat.
1. Ping him: `ask-human ask "Mac Studio Chrome, <site>: <what to do>, then click Continue on the card" --from <agent> --kind 2fa|check`. Keep the request id from the first output line.
2. In the same tab, call `buu js "await handoff('<what to do>, then click Continue'); return page.url()"`. It waits up to 10 minutes. Do not pass `--timeout`.
3. When `handoff` returns, check the URL or a page element. Do not assume the step worked.
4. Run `ask-human close <id>`.
5. If `handoff` throws `handoff timed out`, run `ask-human wait <id>`. If Thinh replies `done`, check the page and continue. Otherwise park (see below).

Never click the card or its Continue button. Only Thinh does that.

## Ask Thinh
Use `ask-human` for what only Thinh can give: a missing vault item, or a decision. Do not ask for things you can find, retry, or decide yourself.
```
ask-human ask "<question>" --from <agent> [--ref ALG-123|url] --kind password|2fa|check|other
```
- The first output line is the request id (the Mattermost post id). Keep it.
- Exit codes: `0` answer printed. `75` pending: run `ask-human wait <id>` again. `76` timeout (4 hours after the ask): park.
- Each call blocks up to 240 s (`--wait` changes it) and prints a heartbeat line every 60 s. For each runner:
  - Claude Code: the Bash timeout is 2 minutes by default. Pass `timeout: 300000` or use `--wait 100`.
  - Codex: commands up to 240 s run correctly.
  - pi and Yoplai subagents: the default is correct.
- Loop `ask-human wait <id>` on 75 until 0 or 76. Do other unblocked work between calls.
- Never use ask-human to announce a skip or to post "no reply needed".

## Park (on 76, or if you must stop)
```
ask-human park <id> --note-file note.md --runner <codex|claude|pi|yoplai-pi|...> --session <session or run id>
```
note.md must have the lines `Doing:` `Done:` `Next:` `Blocker:`. The tool adds Where and Resume. Then run `buu end --keep <tabId>` (id from `buu status`) to keep the tab of the blocked step, and stop.
- No linked issue: the park note is the full handoff.
- Linked issue (Linear or other): the issue is the channel from now on. Put the open question and the full handoff on the issue. Keep note.md short, with the issue URL.
- Never ask the same question in two places. If you wait on an issue, ask there only, not with ask-human.

## Resume
`ask-human resume <id>` prints a resume prompt (handoff and Thinh's replies). For Yoplai runs, it also prints the `yoplai subagents resume …` command.
`ask-human list [--status waiting|parked|answered]` shows open requests.
