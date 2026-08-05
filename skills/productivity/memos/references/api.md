# Memos REST API reference

Derived from the `usememos/memos` v0.30.0 protos (`proto/api/v1/*.proto`) and matching https://usememos.com/docs/api/latest. Base path `<base-url>/api/v1`. Auth: `Authorization: Bearer <PAT or accessToken>` on everything except `auth/signin` and `shares/{token}/memo`.

JSON is lowerCamelCase. `body: "*"` below means the JSON body is the request minus path params; `body: "<field>"` means the body *is* that message.

## Auth Service

| Method | Path | Body / params |
|---|---|---|
| GetCurrentUser | `GET /auth/me` | → `{"user":{"name":"users/1",...}}` |
| SignIn | `POST /auth/signin` | `{"passwordCredentials":{"username","password"}}` or `{"ssoCredentials":{"idpName","code","redirectUri","codeVerifier"}}` → `{user, accessToken, accessTokenExpiresAt}` |
| SignOut | `POST /auth/signout` | revokes the refresh cookie |
| RefreshToken | `POST /auth/refresh` | refresh token read from HttpOnly cookie → `{accessToken, expiresAt}` |

`accessToken` is short-lived and cookie-coupled — for agents use a PAT instead.

## Memo Service

| Method | Path | Notes |
|---|---|---|
| CreateMemo | `POST /memos` | body = Memo. `?memoId=` to choose the id (`^[a-zA-Z0-9]([a-zA-Z0-9-]{0,34}[a-zA-Z0-9])?$`) |
| ListMemos | `GET /memos` | `pageSize` `pageToken` `state` `orderBy` `filter` `showDeleted` |
| GetMemo | `GET /memos/{memo}` | |
| UpdateMemo | `PATCH /memos/{memo}?updateMask=…` | body = Memo (partial) |
| DeleteMemo | `DELETE /memos/{memo}` | `?force=true` to delete despite associated data. Permanent |
| SetMemoAttachments | `PATCH /memos/{memo}/attachments` | `{"attachments":[{"name":"attachments/x"}]}` — **replaces** the set; `[]` clears |
| ListMemoAttachments | `GET /memos/{memo}/attachments` | `pageSize` `pageToken` |
| SetMemoRelations | `PATCH /memos/{memo}/relations` | `{"relations":[…]}` — **replaces** the set |
| ListMemoRelations | `GET /memos/{memo}/relations` | |
| CreateMemoComment | `POST /memos/{memo}/comments` | body = Memo (the comment). `?commentId=` |
| ListMemoComments | `GET /memos/{memo}/comments` | `pageSize` `pageToken` `orderBy` |
| ListMemoReactions | `GET /memos/{memo}/reactions` | |
| UpsertMemoReaction | `POST /memos/{memo}/reactions` | `{"reaction":{"contentId":"memos/{memo}","reactionType":"👍"}}` |
| DeleteMemoReaction | `DELETE /memos/{memo}/reactions/{reaction}` | |
| CreateMemoShare | `POST /memos/{memo}/shares` | body = MemoShare, e.g. `{"expireTime":"2026-01-01T00:00:00Z"}`; omit for never-expires |
| ListMemoShares | `GET /memos/{memo}/shares` | |
| DeleteMemoShare | `DELETE /memos/{memo}/shares/{share}` | revokes the link |
| GetSharedMemo | `GET /shares/{shareToken}/memo` | **no auth**; 404 if invalid/expired |
| GetLinkMetadata | `GET /memos/-/linkMetadata?url=…` | → `{url,title,description,image}` |
| BatchGetLinkMetadata | `POST /memos/-/linkMetadata:batchGet` | `{"urls":[…]}`, results in input order |

### Memo resource

```json
{
  "name": "memos/abc123",          // identifier, memos/{uid}
  "state": "NORMAL",               // NORMAL | ARCHIVED
  "creator": "users/1",            // output only
  "createTime": "…", "updateTime": "…",   // settable on create, else server-set
  "content": "Markdown body #tag", // required
  "visibility": "PRIVATE",         // PRIVATE | PROTECTED | PUBLIC; default PRIVATE
  "tags": ["tag"],                 // output only, parsed from content
  "pinned": false,
  "attachments": [ /* Attachment */ ],
  "relations": [ /* MemoRelation */ ],
  "reactions": [ /* Reaction */ ],           // output only
  "property": {"hasLink":false,"hasTaskList":false,"hasCode":false,
               "hasIncompleteTasks":false,"title":"from first H1"},  // output only
  "parent": "memos/parent",        // output only, set on comments
  "snippet": "plain text …",       // output only
  "location": {"placeholder":"","latitude":0,"longitude":0}
}
```

Visibility: `PRIVATE` creator only · `PROTECTED` any signed-in user · `PUBLIC` anyone including anonymous.

`MemoRelation`: `{"memo":{"name":"memos/a"},"relatedMemo":{"name":"memos/b"},"type":"REFERENCE"}` — type is `REFERENCE` or `COMMENT`.

### ListMemos filter (CEL)

Combine with `&&` / `||`. Fields:

| Field | Type | Example |
|---|---|---|
| `content` | string | `content.contains("roadmap")` |
| `creator` | string | `creator == "users/1"` |
| `created_ts`, `updated_ts` | timestamp | `created_ts > now - duration("168h")` |
| `pinned` | bool | `pinned == true` |
| `visibility` | string | `visibility == "PUBLIC"` |
| `tags` | list\<string\> | `"work" in tags` or `tags.exists(t, t == "urgent")` |
| `has_task_list`, `has_link`, `has_code`, `has_incomplete_tasks` | bool | `has_incomplete_tasks == true` |

Gotcha: the filter uses `created_ts` / `updated_ts`, while `orderBy` uses `create_time` / `update_time`.

`orderBy` (AIP-132, comma-separated): `pinned`, `create_time`, `update_time`, `name`; default `create_time desc`. Example: `pinned desc, create_time desc`.

## Attachment Service

| Method | Path | Notes |
|---|---|---|
| CreateAttachment | `POST /attachments` | body = Attachment. `?attachmentId=` |
| ListAttachments | `GET /attachments` | `pageSize` `pageToken` `filter` `orderBy` |
| GetAttachment | `GET /attachments/{attachment}` | metadata only |
| UpdateAttachment | `PATCH /attachments/{attachment}?updateMask=…` | body = Attachment |
| DeleteAttachment | `DELETE /attachments/{attachment}` | |
| BatchDeleteAttachments | `POST /attachments:batchDelete` | `{"names":["attachments/a","attachments/b"]}` |

```json
{
  "name": "attachments/xyz",
  "filename": "chart.png",       // required
  "type": "image/png",           // required, MIME
  "content": "<base64>",         // input only
  "externalLink": "",            // optional; use instead of uploading bytes
  "size": 12345,                 // output only
  "createTime": "…",             // output only
  "memo": "memos/abc123"         // optional binding
}
```

Upload buffer limit is 32 MiB (instance setting may be lower). Raw bytes are served outside `/api/v1` at `<base-url>/file/attachments/{id}/{filename}`; add `?thumbnail=true` for images.

ListAttachments `filter` fields: `filename`, `mime_type`, `create_time`, `memo`; operators `=`, `!=`, `<`, `<=`, `>`, `>=`, `:` (contains), `in`. Example: `mime_type=="image/png"`, `filename.contains("report")`.

## User Service (the parts agents need)

| Method | Path | Notes |
|---|---|---|
| GetUser | `GET /users/{user}` | |
| ListUsers | `GET /users` | |
| GetUserStats | `GET /users/{user}:getStats` | tag inventory, pinned memos, totals |
| ListAllUserStats | `GET /users:stats` | |
| UpdateUser | `PATCH /users/{user}?updateMask=…` | |
| ListUserSettings / GetUserSetting / UpdateUserSetting | `GET|PATCH /users/{user}/settings…` | |
| ListPersonalAccessTokens | `GET /users/{user}/personalAccessTokens` | |
| CreatePersonalAccessToken | `POST /users/{user}/personalAccessTokens` | `{"description":"…","expiresInDays":0}` — 0 = never; value returned **once** |
| DeletePersonalAccessToken | `DELETE /users/{user}/personalAccessTokens/{pat}` | irreversible |

`UserStats`: `{"tagCount":{"work":42},"totalMemoCount":381,"pinnedMemos":["memos/x"],"memoTypeStats":{"linkCount","codeCount","todoCount","undoCount"},"memoCreatedTimestamps":[…],"memoUpdatedTimestamps":[…]}`.

## Other services

- **AI Service** — `Transcribe` audio via the configured provider.
- **Instance Service** — `GET /instance/profile`, plus instance settings/stats (admin).
- **Shortcut Service** — saved filters under `users/{user}/shortcuts`.
- **Identity Provider Service** — SSO config (admin).

## Errors

Standard JSON error object: `{"code":…, "message":…, "details":[…]}`. Common causes: missing `updateMask` on PATCH (400), PAT lacking the target user's ownership (403), wrong resource-name format (404).
