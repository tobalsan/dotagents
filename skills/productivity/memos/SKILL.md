---
name: memos
description: Read and manage a Memos instance over its REST API — list, search, create, edit, archive, delete memos; manage tags, attachments, comments, reactions, share links; plus account and personal access token (PAT) setup. Use when a user asks to capture a note to Memos, find or edit their memos, upload/attach files, or manage a Memos account, token, or settings.
---

# Memos

Memos is a self-hosted note/memo service. Everything an agent needs is in the REST API at `<base-url>/api/v1`. Prefer the API; use the browser only for account/PAT bootstrap, which has no unauthenticated API path.

Full endpoint listing, request bodies, and filter grammar: `references/api.md`. Read it before composing anything beyond the recipes below.

## Setup

Expect these in the agent's `.env` (mode `600`, never echoed):

```sh
MEMOS_URL=https://memos.example.com
MEMOS_PERSONAL_ACCESS_TOKEN=<token>
```

Every request: `-H "Authorization: Bearer $MEMOS_PERSONAL_ACCESS_TOKEN"`. Verify the token and learn your own user id with:

```sh
curl -fsS "$MEMOS_URL/api/v1/auth/me" -H "Authorization: Bearer $MEMOS_PERSONAL_ACCESS_TOKEN"
# -> {"user":{"name":"users/1", ...}}
```

If no token exists, see "Bootstrap an account or PAT" below.

## Conventions

- Resources are addressed by **name**: `memos/{id}`, `attachments/{id}`, `users/{id}`. Paths use the full name — `GET /api/v1/memos/abc123`.
- JSON fields are **lowerCamelCase** (`pageSize`, `updateMask`, `createTime`); fields *inside* a filter expression are snake_case (`created_ts`).
- Lists page with `pageSize` (default 50, max 1000) and `pageToken`; follow `nextPageToken` until absent.
- Updates are PATCH + `updateMask` naming exactly the fields to change. Omitting the mask is an error; a wrong mask silently drops edits.
- `tags` on a memo are **output-only**, parsed from `#tag` in the Markdown content. Change tags by editing content.

## Recipes

**List / search.** `filter` is a CEL expression (see `references/api.md` for fields and operators).

```sh
curl -fsS -G "$MEMOS_URL/api/v1/memos" -H "Authorization: Bearer $T" \
  --data-urlencode 'filter=content.contains("roadmap") && "work" in tags' \
  --data-urlencode 'orderBy=pinned desc, create_time desc' \
  --data-urlencode 'pageSize=20'
```

Archived memos need `state=ARCHIVED`; the default only returns `NORMAL`.

**Create.** Always set `visibility` explicitly — the server default is `PRIVATE`, which hides the memo from everyone but the agent's own account. Use `PROTECTED` (readable by signed-in users of the instance) so what the agent writes is visible to the user. Only use `PRIVATE` when asked to keep something to yourself, and `PUBLIC` only on explicit request.

```sh
curl -fsS -X POST "$MEMOS_URL/api/v1/memos" -H "Authorization: Bearer $T" \
  -H 'Content-Type: application/json' \
  -d '{"content":"Shipped the parser rewrite #work #eng","visibility":"PROTECTED"}'
```

**Edit.** Send only the masked fields.

```sh
curl -fsS -X PATCH "$MEMOS_URL/api/v1/memos/abc123?updateMask=content,pinned" \
  -H "Authorization: Bearer $T" -H 'Content-Type: application/json' \
  -d '{"content":"Updated body #work","pinned":true}'
```

**Archive vs delete.** Archiving is reversible and is the right default; `DELETE /api/v1/memos/{id}` is permanent. Confirm with the user before deleting.

```sh
curl -fsS -X PATCH "$MEMOS_URL/api/v1/memos/abc123?updateMask=state" \
  -H "Authorization: Bearer $T" -H 'Content-Type: application/json' -d '{"state":"ARCHIVED"}'
```

**Attach a file.** Upload, then bind. Content is base64 in JSON; cap ~32 MB.

```sh
curl -fsS -X POST "$MEMOS_URL/api/v1/attachments" -H "Authorization: Bearer $T" \
  -H 'Content-Type: application/json' \
  -d "{\"filename\":\"chart.png\",\"type\":\"image/png\",\"content\":\"$(base64 < chart.png)\"}"
# -> {"name":"attachments/xyz", ...}

curl -fsS -X PATCH "$MEMOS_URL/api/v1/memos/abc123/attachments" -H "Authorization: Bearer $T" \
  -H 'Content-Type: application/json' -d '{"attachments":[{"name":"attachments/xyz"}]}'
```

`SetMemoAttachments` **replaces** the whole set — include existing attachments or they are unbound. Download the raw bytes at `<base-url>/file/attachments/{id}/{filename}`.

**Tag inventory.** There is no tag endpoint; get counts from user stats:

```sh
curl -fsS "$MEMOS_URL/api/v1/users/1:getStats" -H "Authorization: Bearer $T"
# -> {"tagCount":{"work":42,"eng":17}, "totalMemoCount":381, "pinnedMemos":[...], ...}
```

Renaming a tag means rewriting `#old` → `#new` in the content of every memo matching `"old" in tags`.

## Safety

- Deleting memos, attachments, share links, or PATs is irreversible — inspect the target and get explicit confirmation first.
- `visibility: PUBLIC` and share links expose content to anonymous visitors. Never set `PUBLIC` or mint a share link without being asked.
- Batch operations (`attachments:batchDelete`) hit many resources at once; list and show what will be removed before running one.
- Never print tokens, passwords, or `.env` contents to chat, logs, or snapshots.

## Bootstrap an account or PAT

Only with explicit authorization — both are external mutations, and a PAT acts as the user.

Use `playwright-cli` directly, not through a Node script: `playwright-cli -s=memos open <base-url>`, `snapshot` after every state change, act on returned element refs (never guessed selectors), `playwright-cli -s=memos close` when done.

**playwright-cli command quick reference:** `open <url>`, `goto <url>` (NOT `navigate`), `fill <ref> <text>` (NOT `fill <ref> --text <text>`), `click <ref>`, `snapshot`, `run-code '<JS>'`, `close`. The session flag is `-s=memos`.

1. **Account** — generate a password locally (`openssl rand -base64 32`), sign up at `<base-url>/auth/signup`, confirm the authenticated home page loads, then write `MEMOS_URL` / `MEMOS_USERNAME` / `MEMOS_PASSWORD` to `.env` under `umask 077` + `chmod 600`. Verify without printing via `POST /api/v1/auth/signin` with `{"passwordCredentials":{"username":"…","password":"…"}}` — success returns `accessToken`. If signup is disabled or setup is already done, stop and report the exact UI state rather than trying an unverified alternate path.

   **PITFALL — base64 passwords and `cut -d=`:** `openssl rand -base64 32` produces strings that can end in `=` or `==` (base64 padding). `cut -d= -f2` silently truncates at the first `=`. Always use `cut -d= -f2-` (note the trailing dash) when extracting `KEY=value` pairs from `.env`, or use `sed`/`awk` instead. This cost a failed signin attempt with a misleading "unmatched username and password" error.

2. **PAT** — signed in, open `<base-url>/setting#access-token`, create a token with a purpose-specific description, and confirm the expiry the UI has selected before submitting unless the user named one. Copy the one-time value straight into `.env` as `MEMOS_PERSONAL_ACCESS_TOKEN`, then verify with `GET /api/v1/auth/me`.

   **PAT via API (preferred over UI):** Once you have a session `accessToken` from signin, create a PAT directly — no need to navigate the web UI:

   ```sh
   curl -fsS -X POST "$MEMOS_URL/api/v1/users/{user}/personalAccessTokens" \
     -H "Authorization: Bearer $SESSION_TOKEN" \
     -H 'Content-Type: application/json' \
     -d '{"description":"Cloud Agent API access","expiresInDays":0}'
   ```

   **The token value is in the `token` field, NOT `accessToken`.** Response shape:

   ```json
   {"personalAccessToken": {"name": "users/cloud/personalAccessTokens/…", "description": "…", "createdAt": "…", "expiresAt": null}, "token": "memos_pat_…"}
   ```

   Extract with `jq -r .token` or `python3 -c "import sys,json; print(json.load(sys.stdin)['token'])"`. Do not look for `accessToken` — that key only exists on the signin response, not on the PAT creation endpoint.

   Write the extracted token to `.env` as `MEMOS_PERSONAL_ACCESS_TOKEN`, then verify with `GET /api/v1/auth/me`.

Once authenticated, PATs are also manageable via the API (`users/{user}/personalAccessTokens`, see `references/api.md`). Revocation is destructive: identify the exact token and confirm first.

## Avatar upload

Avatar changes require the authenticated web UI. Use `playwright-cli` directly:

1. Open Memos, sign in if needed, then navigate to **Settings → My Account → Edit**. Snapshot after every navigation or click and use the returned refs.
2. **Use the agent's own avatar from the workspace** (`~/cloud/cloud.png` for Cloud). Do NOT web-search for stock images — the user expects you to use your workspace identity file. In the edit dialog, the avatar control is an invisible `input[type=file]`; `playwright-cli upload` will fail with "can only be used when there is related modal state present." Use `run-code` instead:

   ```sh
   playwright-cli -s=memos run-code 'async (page) => {
     await page.locator("input[type=file]").setInputFiles("/absolute/path/avatar.png");
   }'
   ```

3. After `setInputFiles`, verify the avatar preview loaded by checking the dialog's inner HTML for a `data:image` src. Click **Save**, then snapshot and confirm the dialog closed without error (the settings page should re-render cleanly). Close the browser session.
