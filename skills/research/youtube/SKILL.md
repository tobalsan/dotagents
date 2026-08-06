---
name: youtube
description: Extract transcripts and metadata from YouTube videos, playlists, and channels using yt-dlp, cheaply enough to use a video as a research source. Use whenever a YouTube URL needs to be read, cited, summarized, or searched — "what does this video say", "summarize this talk", "get the transcript", or any research lane that turns up youtube.com / youtu.be links. NOT for downloading video or audio files.
---

# YouTube

`yt-dlp` is the base tool. It reads a video's captions and metadata without downloading the video.

**The whole job is getting the content out at a fraction of its raw size.** A 19-minute talk is ~28k tokens as raw captions and ~3k after cleaning — the same words, minus the timestamps and YouTube's rolling-window repetition. Never read a raw `.vtt` into context.

Work in a scratch directory (`$DIR`), not the current one — these commands write files.

## 1. Metadata first

One call, ~500 bytes, 1–2s. Gives you the canonical video ID, which is the dedup key for anything tracking sources.

```bash
yt-dlp --skip-download --no-warnings \
  --print "%(title)s | %(channel)s | %(upload_date)s | %(duration_string)s" \
  --print "%(id)s | %(webpage_url)s" \
  --print "%(description).500s" "$URL"
```

Never use `-J` / `--dump-single-json` for this. It returns ~150 KB (~37k tokens) because it embeds every format variant, the engagement heatmap, and the full caption-language menu. Only reach for it with a `jq` filter already in hand.

## 2. See which captions exist

```bash
yt-dlp --extractor-args "youtube:skip=translated_subs" --list-subs --skip-download "$URL"
```

`skip=translated_subs` is what keeps this readable — without it YouTube returns the cross product of every source language times ~150 machine-translation targets (~956 lines).

## 3. Pull the track

```bash
yt-dlp --extractor-args "youtube:skip=translated_subs" \
  --write-sub --write-auto-sub --sub-langs "en" --sub-format vtt \
  --skip-download -o "$DIR/%(id)s.%(ext)s" "$URL"
```

- Both `--write-sub` and `--write-auto-sub`: yt-dlp takes the human-written track when one exists and falls back to auto-captions when it doesn't.
- **Use an exact language code.** `--sub-langs "en.*"` also matches translated-back junk (`en-de`, `en-ja`, `en-es-419`) and pulls dozens of files.
- **vtt, not json3.** json3 is ~2× larger for identical content — it carries a timing object per word.
- `-o -` does not stream subtitles; it writes a file literally named `-`. Write to a path, then read it.

`WARNING: ... no impersonate target is available` means yt-dlp can't mimic a browser's TLS fingerprint, so requests go out looking like a bot. Harmless once, but it's what trips the bot check under volume — see the failure table. Fix the install (`uv tool install "yt-dlp[default,curl-cffi]"`) rather than working around it; `yt-dlp --list-impersonate-targets` should list Chrome and Safari.

No English track → use the real spoken-language code from step 2 and translate while reading. yt-dlp's auto-translation buys nothing.

## 4. Clean before reading

Auto-captions repeat nearly every line — a rolling window carries the previous line forward. This is a YouTube artifact with no yt-dlp flag to fix it, so strip it yourself:

```bash
grep -vE '^([0-9]|WEBVTT|Kind:|Language:| *$)' "$DIR/$ID.en.vtt" \
  | sed -E 's/<[^>]+>//g' | awk '!seen[$0]++' > "$DIR/$ID.txt"
```

~89% smaller. Output is readable prose, lowercase and unpunctuated for auto-captions — fine to read, cheap to tidy further since it's already small.

## 5. Long videos: navigate, don't swallow

Over ~20 minutes, check for chapters before reading the whole thing:

```bash
yt-dlp --skip-download --print "%(chapters)j" "$URL"
```

~2 KB even for a 40-chapter course. Filter the cleaned transcript to the `start_time`/`end_time` windows that match what you're after. `--download-sections` and `--split-chapters` slice *media*, never subtitle text — the windowing is yours to do.

No chapters and still huge? `--print "%(heatmap)j"` gives YouTube's "most replayed" curve as a weak proxy for the substantive parts.

## Playlists and channels

Enumerate cheaply, then treat each video as its own source:

```bash
yt-dlp --flat-playlist -I 1:25 --print "%(id)s | %(title)s | %(url)s" "$URL"
```

`--flat-playlist` skips per-video metadata fetches; `-I` takes `START:STOP:STEP`. Never let a channel URL expand unbounded.

## Failure modes

| Symptom | What to do |
| --- | --- |
| `There are no subtitles for the requested languages` | Clean exit, not an error. Record the video with metadata only and move on; audio transcription is only worth it for a high-value source. |
| `Sign in to confirm you're not a bot` / `LOGIN_REQUIRED` | YouTube's PO-Token enforcement. Check `--list-impersonate-targets` isn't empty, retry once with `--sleep-requests 2`, then `--cookies-from-browser chrome`. If it still fails, skip the source and say so. |
| Age-gated, private, or members-only | Same cookie path, and members-only content is unreachable without that account's session. Skip and note it. |
| Many videos in one run | Guest limit is ~300 videos/hour, ~2000 signed in. Parallel researchers hitting YouTube at once is exactly what trips it — serialize or add `--sleep-requests 1`. |
| Live stream | `--live-from-start`, otherwise a mid-stream capture is partial. |

## Reporting a video as a source

Cite it by canonical URL (`https://www.youtube.com/watch?v=<id>`) — the video ID is stable across the URL variants (`youtu.be`, `&t=`, `/shorts/`, tracking params) that would otherwise look like distinct sources.

Carry the channel and upload date with the claim. A video is one person talking; date and speaker are what make it weighable evidence rather than an anonymous assertion.
