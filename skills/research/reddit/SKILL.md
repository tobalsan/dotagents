---
name: reddit
description: Search Reddit, list a subreddit's threads, and read a thread's comments — routing around the fact that Reddit 403s almost every scraper. Use whenever a reddit.com URL needs to be read or cited, a research lane wants practitioner opinion ("what do people actually say about X"), or a subreddit needs enumerating. NOT for posting, voting, or anything requiring a logged-in account.
---

# Reddit

Reddit blocks nearly every automated fetch. **The whole job is knowing which three routes still work, so you don't burn a research lane rediscovering that the other seven are dead.**

Two routes carry all the weight:

| | Route | Cost | Use for |
| --- | --- | --- | --- |
| **Discovery** | `firecrawl search` with a `site:` operator | ~1 credit, instant | finding threads by topic |
| **Reading** | Reddit's own `.rss` endpoints | free, ~1 req/45s | listings and thread comments |
| *fallback* | arctic-shift archive API | free, unmetered | >48 comments, deleted content |

Work in a scratch directory (`$DIR`) — these commands write files.

## Dead routes — do not try

Every one of these was measured against `r/quant` and `r/algotrading`. They fail on *all* Reddit URLs, not just some.

| Route | Failure |
| --- | --- |
| `WebFetch` / `WebSearch` | Reddit's robots.txt blocks Anthropic's crawler. `WebSearch` returns zero reddit.com results even unfiltered; an `allowed_domains: ["reddit.com"]` filter is a hard 400. |
| `firecrawl scrape` / `crawl` | Explicit refusal: *"we do not support this site."* Search is fine — only scraping is blocked. |
| `exa search` / `exa crawl` | `includeDomains: ["reddit.com"]` returns 0 results; Reddit isn't in Exa's index. `exa crawl` → 403. |
| `markdown.new/<url>` | 500, "all conversion methods failed." |
| `r.jina.ai/<url>` | Returns 200 wrapping Reddit's *"You've been blocked by network security"* page. The 200 is a lie — check the body. |
| `<url>.json`, `old.reddit.com` | 403 on every User-Agent, including a full Chrome string. Reddit killed the free JSON API. |
| Playwright / headless browser | Works for ~2 requests, then silently dies. A cold headless Chromium really does render posts and `<shreddit-comment>` nodes with no login — then a burst of 8 URLs 20s later returned **8× HTTP 200 with zero content and no challenge marker**. That's the trap: it reads as "this thread has no comments," not as a block, so it poisons a research lane with false empties instead of failing loudly. RSS and arctic-shift survive the block, so it's session/fingerprint-scoped, not an IP ban. |
| `curl_cffi` TLS impersonation | Doesn't help — `chrome`, `safari`, and `chrome124` all return byte-identical 403s on `.json`. HTML pages *appear* to return 200, but the body is Reddit's **"Prove your humanity"** interstitial or a JS proof-of-work challenge: no posts, no `shreddit-comment` tags. Check the body, not the status. Don't try to solve the challenge — it's an anti-bot control, against Reddit's ToS, and the params rotate. |

## 1. Discovery — find threads by topic

`firecrawl search` reads Google's index, which still carries Reddit even though Firecrawl won't scrape it. Fast, no rate limit, `--limit` up to 100.

```bash
firecrawl search "site:reddit.com/r/algotrading backtesting overfitting" --limit 20
```

Returns title + canonical URL + a snippet per hit — often enough to triage which threads are worth a read.

- Drop the subreddit for a site-wide sweep: `site:reddit.com <query>`.
- `--tbs qdr:m` (or `qdr:y`) when recency matters — Reddit advice ages badly.
- No credits, or the query is broad? Reddit's own search RSS works, at the rate limit in §2:
  ```bash
  ./rget.sh "https://www.reddit.com/search.rss?q=subreddit%3Aquant+interview&sort=top&t=year" "$DIR/s.xml"
  uv run --no-project python rfeed.py "$DIR/s.xml"
  ```

## 2. Listings and threads — Reddit's RSS

`.rss` is the only Reddit-native endpoint still serving unauthenticated traffic. It needs a browser User-Agent and a retry loop; `rget.sh` is both.

```bash
./rget.sh "https://www.reddit.com/r/algotrading/top/.rss?t=month&limit=25" "$DIR/list.xml"   # listing
./rget.sh "https://www.reddit.com/r/quant/comments/1vh0old/.rss?limit=100" "$DIR/thread.xml" # thread
uv run --no-project python rfeed.py "$DIR/thread.xml"
```

**`rfeed.py` is not optional.** Raw RSS is ~2× its content — XML scaffolding, HTML-escaped bodies, and a `submitted by /u/x [link] [comments]` tail on every entry. It emits `## title / url / date | author / body`.

**Sort in the URL, because you cannot sort afterwards.** RSS carries no score. `top/.rss?t=month|year|all` is how you get Reddit's ranking; `/hot/`, `/new/`, and `?sort=top` on a thread work the same way. Fetching `/new/` and hoping to rank by upvotes later does not work — see §5.

### The rate limit is the real constraint

**~1 successful request per 45–60 seconds, per IP, across all of reddit.com.** Measured: three 15s-spaced attempts return 429 before one returns 200. Headers say it plainly — `x-ratelimit-remaining: 0.0`, `x-ratelimit-reset: 45`.

A 429 body is *empty with HTTP 200 sometimes* — always check size, not just status. `rget.sh` does.

Consequences worth planning around:
- **Parallel researchers share one bucket.** Five agents hitting RSS at once means five agents each waiting ~4 minutes. Serialize Reddit work through one lane, or use §3.
- Budget ~1 minute per URL. Twenty threads is twenty minutes — decide from `firecrawl search` snippets which ones you actually need.

### Thread RSS caps at 48 comments

49 entries: the post plus 48 comments. `limit=100`, `limit=500`, and `depth=10` all return the same 49 — verified on a 200-comment thread. It's flat, too: no nesting, no `parent_id`, so reply structure is lost.

For most research this is fine — the top 48 under `?sort=top` is the substance. When you need more, or the thread is old and gutted, go to arctic-shift.

## 3. arctic-shift — the archive fallback

A free, unauthenticated, unmetered mirror of Reddit's firehose. No rate limit worth mentioning, so this is the route when many agents need Reddit at once.

**It does not lag — it over-reports.** Measured against `r/quant`, arctic-shift's newest post was 15:06 UTC while Reddit's own `/new/.rss` topped out at 10:42, apparently 4.5 hours behind. It isn't: all four "extra" posts were `removed_by: automod_filtered`. arctic-shift ingests at *submission*, RSS shows only what survives moderation. On a heavily-automodded sub that's most of the recent queue — 4 of the last 5 posts here. So treat an arctic-shift listing as *submissions*, not *live threads*: filter on `removed_by_category` before citing anything from it, or you'll cite posts no reader can see. Cross-check against a `.rss` listing when it matters. (Post frequency also masquerades as lag — `r/AskReddit` shows 0 min, `r/algotrading` 16, purely because of how often each gets posts.)

```bash
B=https://arctic-shift.photon-reddit.com/api
curl -s "$B/comments/search?link_id=1q4gpu1&limit=100" | jq -r '.data[]|"[\(.author)] \(.body)"'
curl -s "$B/posts/search?subreddit=quant&limit=25&sort=desc" | jq -r '.data[]|"\(.title)\n  \(.id) \(.created_utc)"'
```

Use it for exactly three things:

- **Comments past the 48-cap.** Both endpoints return the full set — 55 comments on a thread where RSS gave 48. `/comments/tree?link_id=<id>&limit=25000` nests them Reddit-style (`replies` is `""` or a `{kind:"Listing"}` whose `data.children` you recurse); `/comments/search?link_id=<id>` returns the same comments flat, each carrying `parent_id` (`t3_` = top-level, `t1_` = reply). Use the tree when reply structure matters, search when it doesn't.
- **Deleted and removed content — sometimes.** Bodies are snapshotted at ingest, so a body sometimes survives removal. Don't count on it: sampling 100 `r/quant` posts per window, only **53% (2026), 15% (2025), 37% (2023)** had a recoverable body; the rest read `[removed]`/`[deleted]` *in the archive too*. It's the only route that recovers anything, but it's a coin flip, not a guarantee.
- **Bulk enumeration without the rate limit.** `/posts/search?subreddit=<sub>` with `after=`/`before=` walks a subreddit's history. Dates take ISO, epoch, or relative offsets (`3m`, `1year`).

**Its scores are worthless.** Every post and comment reads `score: 1` and `num_comments: 0`, including 2021 threads whose real scores settled years ago — the archive snapshots at ingest and never backfills. Never rank, filter, or cite by an arctic-shift score. Rank via Reddit's `top/.rss?t=` instead (§2).

**Keyword search is a trap.** `query=` on `/posts/search` requires `subreddit` or `author`, and even then times out unless the `after`/`before` window is ~1 month or narrower — a 2-month window on `r/quant` failed, and so did the current month. `/comments/search` doesn't take `query` at all (it's `body=`), and every `body=` search times out, including scoped to one thread. Do topic discovery with `firecrawl search` (§1) and treat arctic-shift as an ID-and-subreddit lookup.

`fields=` errors don't enumerate what's valid; `permalink` is *not* a field (build URLs from `id`). Valid: `author, author_fullname, author_flair_text, created_utc, distinguished, id, retrieved_on, subreddit, subreddit_id, score`, plus posts-only `title, selftext, url, num_comments, link_flair_text, over_18, spoiler, post_hint, crosspost_parent` and comments-only `body, link_id, parent_id`. Full docs: `github.com/ArthurHeitmann/arctic_shift/blob/master/api/README.md` — the live `/api-docs` path 404s.

## 4. Context discipline — never read a thread into your own context

A fetched thread averages **~4,900 tokens**; eleven of them came to ~54,000. A few subreddit lanes will exhaust an orchestrator before the research starts. The corpus is not the deliverable — the claims are.

**The rule: the agent that fetches must never read what it fetched.**

`rfetch.py` makes that enforceable rather than aspirational. It writes one file per thread and prints only a manifest:

```bash
uv run --no-project python rfetch.py "$DIR/threads" \
  https://www.reddit.com/r/algotrading/comments/1q4gpu1/ qjrj7b 1vh4fhb
```

```
id         status            cmts   bytes  path | title
1q4gpu1    ok                  49   19151  …/1q4gpu1.md | Is overfitting the #1 reason…
qjrj7b     no-body             69   26891  …/qjrj7b.md  | This is how I use walkforward…
1vh4fhb    automod_filtered     1     668  …/1vh4fhb.md | Best Device For Paper Analysis
```

Measured: **1,274 bytes of manifest against 60,350 bytes on disk**, 47× smaller. It accepts URLs or bare IDs, dedups by post ID, and `status` is your triage column — skip `automod_filtered` rows (invisible to any reader you'd cite them to), and note `no-body` rows still carry their comments, which is usually where the substance is.

**Do not `cat`, `Read`, `grep`, or `head` the thread files.** Hand the paths to a subagent instead.

### Delegating the digest

One subagent per **5–10 threads**, on a **mid-tier model** (Sonnet-class — GLM 5.2, gpt-5.6-terra, Minimax M3, Gemini Flash, and equivalents sit here too). This is judgment work — *is this consensus or one confident voice?* — not extraction, and the cheapest tier flattens exactly that distinction while the frontier tier is wasted on it. Digest agents are independent, so fan them out in parallel; nothing here is rate-limited. Give each the file paths, the research question, and a fixed output shape:

```
URL: <canonical url from line 2 of the file>
TITLE: <title>
CLAIMS:
- <claim> [consensus|contested|single-voice]     (max 6, one line each)
NOTABLE: <the single most actionable technique, or "none">
CAVEAT: <thread age, removed status, credibility signals, or "none">
```

Measured on two threads: 46 KB of source in, ~2.4 KB of digest out — roughly **60:1** at the orchestrator boundary.

Three constraints belong in that prompt, and each fixes an observed failure:

- **Cap the output explicitly** (character limit *and* max claims). Without it the digest agent writes an essay and you have moved the overflow, not removed it.
- **Force the consensus / contested / single-voice tag.** Reddit's whole value is knowing whether ten practitioners independently agree or one assertive person asserted. An ungraded claim is worse than no claim, because it reads as settled.
- **Forbid invented vote counts.** The source carries none (§5) and a digest agent will otherwise supply plausible-looking ones. Same for quote length — cap it, or you get wholesale reproduction.

Keep the files on disk after digesting. When a claim needs verification later, re-delegate a reader against the same path — cheaper than re-fetching, and the archive may have changed.

## 5. Scores, and what you can honestly claim

**No free route returns real vote counts.** RSS has no score field; arctic-shift's is frozen at 1; Firecrawl snippets carry none. So "this answer had 2k upvotes" is not a claim you can make.

What you *can* do is let Reddit rank for you: a thread pulled from `top/.rss?t=year` is by construction among the year's most-upvoted, and `?sort=top` on a thread puts the community's preferred comments first. Cite *position*, not number — "the top-voted reply" is supportable; "+412" is not.

**Don't go looking for the OAuth API as a way out.** Self-serve app creation is closed as of 2026-08: the form at `reddit.com/prefs/apps` passes its reCAPTCHA and then refuses with a pointer to the Responsible Builder Policy. Per `reddit.com/r/reddit.com/wiki/api/`, new legacy Data API apps now require **a valid moderation use case** submitted through a support request; general research and personal reading don't qualify, and the Developer Platform it steers you to is for apps that run *on* Reddit, not external retrieval. Unless you moderate the subreddit in question and hold real credentials, there is no OAuth route — use ordering, and say scores are unavailable rather than inventing figures.

## Failure modes

| Symptom | What to do |
| --- | --- |
| HTTP 429, or 200 with an empty body | The rate limit. `rget.sh` handles it; if it exhausts six tries, another agent is sharing the IP — serialize, or switch to arctic-shift. |
| `firecrawl search` returns nothing for `site:reddit.com/r/x` | Subreddit name is wrong or private. Confirm the sub exists before assuming Reddit has no coverage. |
| Body is `[removed]` / `[deleted]` | Live Reddit is gutted. arctic-shift recovers the text maybe half the time (§3) — if it doesn't, the comments usually still survive, so keep the thread. |
| Thread has far more comments than you got | The 48-cap. Go to `/comments/search`. |
| Everything 403s including RSS | Reddit is rate-limiting the IP hard, or the sub is quarantined/private. Record the URL as an uncrawled source and move on — don't spend a lane on it. |

## Reporting a thread as a source

Cite the canonical form: `https://www.reddit.com/r/<sub>/comments/<id>/`. The 7-char post ID is the dedup key — the trailing slug, `?utm_*`, `old.`, `np.`, and `redd.it` shortlinks all resolve to the same thread and would otherwise inflate a unique-source count.

Carry the subreddit and date with every claim. Reddit is anonymous strangers: a 2019 answer about broker APIs is probably wrong now, and `r/algotrading` and `r/quant` disagree about the same questions for structural reasons. Attribute to the thread and note it as practitioner opinion, never as established fact.
