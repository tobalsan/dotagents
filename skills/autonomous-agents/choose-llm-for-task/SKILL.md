---
name: choose-llm-for-task
description: Instantly pick the top 3 best-suited models for a task across the user's five harnesses (Claude Code, Codex, Grok CLI, Pi, OpenCode Go), factoring in real subscription/quota limits. Use whenever deciding which LLM/model to route a task to, delegating work to another agent/CLI, picking a council member, comparing models, or the user asks which model to use for X.
---

# Choose LLM For Task

Find the task type in the routing table below. Take the top-3 picks **in order** — try 1st, degrade to 2nd/3rd only if that harness is capped, unavailable, or scarce (see budgets). Cross-check the per-model cheat sheet and rules of thumb before committing to a scarce or costly pick.

## Harness budgets (real limits, Sep 2026)

| Harness | Tier | Models |
|---|---|---|
| Claude Code | High-tier sub, comfortable | claude-opus-5-5 (default hard work), claude-fable-5-1, claude-opus-5 (superseded — avoid), claude-sonnet-5, claude-haiku-4-5 |
| Codex | High-tier sub, comfortable | gpt-6-astra (flagship — not the everyday default), gpt-6-sol (everyday default), gpt-6-luna (light scout / scaffolds); gpt-5.6-sol/terra/luna and gpt-5.5 (superseded — avoid); gpt-5.3-codex-spark (separate rate limit, Pro preview) |
| Grok CLI | PAID API, reliable | grok-4.7 ($2/$6, 500k ctx — live research; prefer high, not xhigh); grok-4.6 (superseded — avoid); grok-build-0.1 ($1/$2, $2/$4 at ≥200k). Web search + X search $5/1k calls each on top of tokens. Prefer CLI over OpenCode (grok scarce there) |
| Pi | GLM Coding Plan Pro (flat-rate, generous) + Gemini via PAID API (real $) | glm-5.3 = cheap workhorse; gemini-* = use deliberately, prefer flash tiers |
| OpenCode Go | $12/5hr, $30/wk, $60/mo ($-denominated) | cheap = near-unlimited (muse-spark-1.3-contributor ~45.3k req/5hr — frontier-strong, not a weak bulk model; limited regions; Meta trains on prompts — never sensitive data; mimo-v2.5 ~30.1k, mimo-v2.6 pro/flash if listed — short/medium context until cutoff rechecked; omen-alpha ~11.6k; longcat-2.0 ~11.4k; deepseek-flash = V4.1 Flash, replaces v4-pro and v4-flash, ~7.6k until remeasured; qwen3.8-flash ~5.4k; qwen3.7-plus/hy3 ~4.3k; minimax-m3 ~3.2k; glm-5.3-flash ~1.58k / 2x promo ~3.16k); scarce/costly (hy4-preview 1.35k, glm-5.3 220, grok 169, qwen3.8-max 160, kimi-k3 110 — reach Grok/GLM/Kimi via their own harness instead). Quotas above not remeasured 25 Sep. |

## Routing table

| Task type | 1st | 2nd | 3rd | Why/notes |
|---|---|---|---|---|
| Hardest problems: architecture, deep diagnosis, gnarly debugging | claude-opus-5-5 | gpt-6-astra (high/max) | claude-fable-5-1 | Opus 5.5 AA Intelligence 58 (new high), TB4.0 59.6% ties Astra, Briefcase Elo 1822. $4/$20, cache reads $0.20. Max effort burns ~119k out/task — drop effort before jumping to Fable. Fable still the cache-heavy long-coding fallback |
| Everyday feature implementation (agentic default) | claude-sonnet-5 | gpt-6-sol | glm-5.3 (Pi) | Sonnet = fast/agentic default; Sol replaces Terra at $2/$10 (same input price, better coding index). GLM-5.3 cheap flat-rate fallback |
| Large repo-scale refactor / hard coding | claude-opus-5-5 | gpt-6-astra | glm-5.3 | Opus 5.5 leads agentic knowledge work and ties Astra on TB4.0; watch output-token burn. Astra 1.05M + context notes. GLM cheap 1M |
| Code / PR review (cross-vendor second opinion valuable) | claude-opus-5-5 | gpt-6-astra | grok-4.7 (Grok CLI, high) | Cross-vendor. Astra stays the OpenAI review voice. Grok 4.7 for a third lab — prefer high, not xhigh |
| Security review | gpt-6-astra (ExploitBench 100%; Critical; prod=review/patch only, refuses PoC; Daybreak for exploit-dev) | claude-fable-5-1 | claude-opus-5-5 | Astra unchanged. Fable: vuln discovery OK, not exploit-dev. Opus 5.5 ships Fable-class cyber safeguards (verification program). Mythos 5.1 / Gemini 3.8 Flash Cyber = gated twins |
| Quick scoped edits, boilerplate, test scaffolding, code scout | gpt-6-luna | claude-haiku-4-5 | grok-build-0.1 | Luna is the light-scout favorite: $0.10/$0.50, ~$0.07/task, fully agentic, sensitive-code safe. Coding Agent Index 41 (−2 vs 5.6 Luna) — lookup/scaffold, not implementation. Same Codex budget as Sol. Haiku if Codex is capped |
| Ultra-fast interactive iteration (pair loop) | gpt-5.3-codex-spark | claude-haiku-4-5 | gemini-3.8-flash | Spark 1000+ tok/s, separate quota; text-only, no deep reasoning. 3.8 Flash ~300 tok/s + agentic |
| Bulk/mechanical fan-out (mass migration, many small tasks) | muse-spark-1.3-contributor (OpenCode; never sensitive data) | omen-alpha or deepseek-flash (OpenCode) | gpt-6-luna (sensitive code) or mimo-v2.6-flash if listed (short/medium context ONLY) | Muse is both bulk king (~45.3k/5hr) AND frontier-strong (AA Index 61). Contributor = Meta trains on prompts/code — never secrets, private IP, or sensitive data. Sensitive bulk: Luna, not Muse. MiMo V2.5 cutoff not confirmed fixed on V2.6 |
| Classification / extraction / summarization at volume | gpt-6-luna | deepseek-flash (OpenCode) | gemini-3.5-flash-lite | Luna $0.10/$0.50 undercuts Flash-Lite ($0.30/$2.50) and stays on Codex quota. Flash-Lite if you need Gemini speed and Luna is capped. DeepSeek if the payload must stay off Codex |
| Deep reasoning, math, science (non-coding) | gpt-6-astra | claude-opus-5-5 | gemini-3.1-pro-preview (costly API — sparingly) | Astra still leads science/math token-efficiency. Opus 5.5 leads HLE (61.4%) and SciCode (66.9%) on AA. Gemini 3.1 Pro only when both fail |
| Cheap deep reasoning at volume | deepseek-flash (OpenCode; V4.1) | glm-5.3 (Pi) | glm-5.3-flash (OpenCode) | `deepseek-v4-pro` routes to V4.1 Flash since 14 Sep at Flash rates. Peak $0.30/$1.20, off-peak half. Native vision. Verbose |
| Long-context (huge docs / whole repos, up to 1M) | claude-opus-5-5 | claude-fable-5-1 | glm-5.3 | Opus 5.5: 1M, cache reads $0.20, no 272k surcharge. Fable cache reads $0.25 if Opus token burn dominates. Astra/Sol/Luna whole-request 2× after 272k input — avoid for huge prefixes |
| Multimodal (screenshots, PDFs, video, audio) | gemini-3.8-flash | claude-fable-5-1 (vision SOTA, no audio/video) | glm-5.3-flash or muse-spark-1.3-contributor (cheap bulk vision, OpenCode) | 3.8 Flash: text/image/video/audio/PDF + computer-use preview. Qwen3.8-flash / MiniMax-M3 also cheap bulk |
| Real-time / near-real-time research, scoping, recent sources | grok-4.7 via Grok CLI (web + X search, effort high) | gemini-3.8-flash (search grounding) | gpt-6-luna (follow-up scout once sources are in hand) | **Default this lane to Grok CLI + grok-4.7.** Native web search *and* X search — unique for live/recent sources. Prefer high, not xhigh (xhigh ~81k out/task; real cost can exceed Astra). Do not route this through OpenCode Grok. Luna scouts code/docs after sources exist; it does not search X |
| Computer use / browser automation | gpt-6-astra | claude-fable-5-1 | gemini-3.8-flash | Astra claimed SOTA + faster (OSWorld 72.6% ~40 min); Fable OSWorld 77.9% partial on Anthropic protocol — different harness. 3.8 Flash still has computer-use preview |
| Long-horizon agentic knowledge work (docs, office, workflows) | claude-opus-5-5 | gpt-6-astra | kimi-k3 (OpenCode; ~110 req/5hr — single high-value shots only) | Opus 5.5 AA-Briefcase Elo 1822 (+143 vs Fable 5.1), first Anthropic presentation lead over Sol. Astra still strong on AutomationBench. Kimi K2.8 Preview sits behind `kimi-for-coding` and claims ~K3 with no public bench — do not spend scarce K3 quota to reach it |
| Writing, docs, PRDs | claude-opus-5-5 | claude-sonnet-5 | gpt-6-astra | Opus 5.5 leads presentation quality on AA-Briefcase. Sonnet for faster drafts. Astra for polished professional docs when Claude is capped |

## Per-model cheat sheet

**Claude Code**
- `claude-opus-5-5` — Default for hard work (22 Sep 2026). AA Intelligence 58 (new high), TB4.0 59.6% ties Astra, HLE 61.4%, SciCode 66.9%, AA-Briefcase Elo 1822. $4/$20, cache reads $0.20 (60% below Opus 5), 1M ctx, >30% faster than Opus 5. Max effort ~119k output tokens/task — drop effort before escalating. Fable-class cyber/bio safeguards. Best behavioral audit Anthropic has published.
- `claude-fable-5-1` — Prior SOTA; now the fallback when Opus 5.5 token burn dominates or Claude quota favors the $10/$50 lane you already pay for. Cache reads $0.25. OSWorld 77.9%, AutomationBench 31.4%. Vuln discovery OK, not exploit-dev. `claude-mythos-5-1` = same model, Glasswing-only.
- `claude-opus-5` — Superseded by Opus 5.5 — avoid. Was $5/$25.
- `claude-sonnet-5` — Fast, agentic default, near-Opus on knowledge work. $2/$10.
- `claude-haiku-4-5` — Fastest Claude for scoped tasks. $1/$5, 200K ctx only. Second choice behind GPT-6 Luna for light scouts.

**Codex**
- `gpt-6-astra` — Codex flagship. $10/$50, 1.05M ctx. TB4.0 ties Opus 5.5 at 59.6% (xhigh, AA). ExploitBench 100% (Critical; production refuses PoC). Most token-efficient frontier (~27k out/task). Not the everyday default; pin Sol. Fast mode 2× rates. Long-context surcharge after 272k input. `ultra` still 6–12× token blowup — avoid for orchestration. Experimental context notes (Plus/Pro, off by default).
- `gpt-6-sol` — Everyday Codex default (22 Sep). $2/$10, cache reads $0.20, 1.05M ctx. AA Coding Agent Index 57 (+2 vs 5.6 Sol) at ~$1.06/task, half the old Sol cost. Hallucination 92%→60%. Weaker GDPval presentation. Same 272k whole-request 2× cliff as Astra. Replaces Terra and 5.6 Sol.
- `gpt-6-luna` — Light-scout and scaffold favorite. $0.10/$0.50, cache reads $0.01, 1.05M ctx. ~$0.07/task. Fully agentic, sensitive-code safe (unlike Muse). Coding Agent Index 41 (−2 vs 5.6 Luna) — lookup, extraction, boilerplate, not implementation or ambiguous work. Same Codex budget as Sol. Same 272k cliff, still cheap after 2×.
- `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`, `gpt-5.5` — Superseded — avoid. Terra’s reason to exist ended when Sol landed at $2 input.
- `gpt-5.3-codex-spark` — Cerebras 1000+ tok/s pair-coding niche. Separate rate limit, Pro preview, text-only, doesn't auto-run tests.

**Grok CLI** — API-metered, reliable (no longer a free promo). Token rates below; web_search and x_search are extra at $5/1k calls each.
- `grok-4.7` — Live-research default (21 Sep). Same $2/$6 and 500k ctx as 4.6; cache hits $0.50. Text + image in. AA Coding Agent Index 56 with Grok Build (+9 vs 4.6 xhigh), Intelligence 46, Briefcase 1657 Elo. **Prefer effort high, not xhigh** — xhigh ~81k out/task, and real-world cost can exceed 2× Grok 4.6 (Theo, 22 Sep). Not the cheap coder. Web + X search is why this harness wins scoping. Set a prompt cache key. Prefer CLI over OpenCode.
- `grok-4.6` — Superseded by 4.7 — avoid.
- `grok-build-0.1` — Fast/cheap agentic SWE, always-on reasoning, no effort dial. $1/$2 (<200k). Notably behind frontier accuracy (SWE-bench Verified 70.8% vs 88.7%). Third choice for light scouts after Luna and Haiku.

**Pi**
- `glm-5.3` — Best open-weight coding model (post-train bump over 5.2: Terminal-Bench 3.0 28.3 vs 4.6, DeepSWE 66.9 vs 46.2). True 1M ctx, flat-rate generous quota. Text-only; verbose; behind closed frontier on hardest reasoning. Prefer Pi over OpenCode (220/5hr).
- `gemini-3.1-pro-preview` — Deep-reasoning monster (ARC-AGI-2, GPQA). Costly API, slow (>90s at high thinking), preview rough edges — use sparingly.
- `gemini-3.8-flash` — Best Flash: long-horizon SWE/agents, AA Index 59, ~300 tok/s, 1M ctx. Text/image/video/audio/PDF in. Computer-use + search grounding. $0.75/$3.75, real API cost. Uses more tokens at high effort. `gemini-3.8-flash-cyber` = Fairwind-gated.
- `gemini-3.5-flash-lite` — Fastest/cheapest Gemini, unusually strong for lite tier. $0.30/$2.50. Not for multi-step reasoning/agentic coding.

**OpenCode Go** — CLI needs provider-qualified IDs: `opencode run -m opencode-go/<model>` (bare `<model>` fails with a generic "Unexpected server error").
- `muse-spark-1.3-contributor` — **Very strong, not just cheap.** Same Muse Spark 1.3 checkpoint: AA Intelligence Index 61 (xhigh; independent), ties GPT-5.6 Sol (max) and Grok 4.6 (high); Terminal-Bench 2.1 85%. Also the bulk king (~45.3k/5hr), 1M ctx, multimodal. **Contributor = Meta can and likely will train on prompts/code. Never use for secrets, private IP, or any sensitive data.** Limited regions.
- `glm-5.3-flash` — Native multimodal GLM, beats 5.2 on coding/agents at ~1/10 the price. ~1.58k/5hr (2× promo ~3.16k). Good cheap vision+coding.
- `qwen3.8-flash` — Cheap fast Qwen (~5.4k/5hr), 1M ctx. Prefer over 3.7-plus for new work.
- `qwen3.8-max` — #1-tier reasoning/instruction-following. Slow and scarce (160/5hr).
- `kimi-k3` — #3 Intelligence Index, #1 AutomationBench, native vision. Costly + slow on long runs. SCARCE (110/5hr) — high-value single shots only. K2.8 Preview (11 Sep) claims ~K3 quality, 1M on every tier, image+video, fewer thinking tokens; no public bench. In Kimi Code it sits behind `kimi-for-coding` (silent swap). Do not burn K3 quota to reach the preview.
- `hy4-preview` — Hy3 successor: 1M ctx, office/productivity + stronger coding/front-end. Preview (~1.35k/5hr).
- `hy3` — Beats GLM-5.2 on everything except coding; strong office/productivity/finance. 256K ctx only. Prefer Hy4 when available.
- `omen-alpha` — Cheap stealth (~11.6k/5hr, $0.20/$0.66). Unproven lab; treat as no-data-sharing bulk alternative to Muse.
- `longcat-2.0` — Cheap 1M-ctx bulk (~11.4k/5hr).
- `minimax-m3` — Cheap ($0.30/$1.20), native image/video + computer use. Vendor benchmarks unverified.
- `deepseek-flash` (V4.1 Flash, 10 Sep) — Replaces both V4 Pro and V4 Flash. Since 14 Sep, `deepseek-v4-pro` routes here at Flash rates. Native vision, 1M ctx, 552B MoE, 8B active prefill / 16B decode, KV cache ~1/4 of prior Flash. Peak $0.30/$1.20, off-peak half, cache hit $0.003–$0.006. Vendor: ahead of V4-Pro on agent tasks, some reasoning evals still behind. OpenCode quota not remeasured (~7.6k was the old Flash figure).
- `mimo-v2.6-pro` / `mimo-v2.6-flash` (22 Sep, if listed) — Omni (text/image/video/audio), 1M, vendor AA index 46.3 on Pro. API $0.435/$0.87 (Pro) and $0.14/$0.28 (Flash). Candidates for cheap multimodal bulk. V2.5’s long-session cutoff is **not confirmed fixed** — short/medium context until rechecked.
- `mimo-v2.5` — Very cheap (~30.1k/5hr), native image+audio. CRITICAL: hybrid-window "1M ctx" causes mid-response cutoffs in long agentic sessions — short/medium context ONLY. Prefer V2.6 Flash once the cutoff is confirmed gone.

## Rules of thumb

- Prefer free/flat-rate lanes (GLM-5.3 via Pi, OpenCode cheap models) before spending on metered API (Grok CLI, Gemini) or scarce quota.
- Light scouts, lookups, scaffolds, extraction: **gpt-6-luna first** when the payload is code or sensitive. Non-sensitive mass scouts stay on Muse. Live-source scouting stays on Grok CLI.
- For live or recent-source work (what's new, who said it, which docs/posts to trust): **Grok CLI + grok-4.7, effort high.** Web + X search is the differentiator — scope there, then hand off. xhigh burns ~81k out/task and can cost more than Astra. Do not use Luna for this lane; it does not search X.
- Escalate exactly one tier after a cheaper pick fails twice — don't jump straight to the most expensive model on first friction. Luna fails twice → Sol, not Astra. Opus 5.5 max burns tokens → drop effort before jumping to Fable or Astra.
- Cross-vendor deliberately for reviews and second opinions (different training data/blind spots catch different bugs).
- Never use MiMo-V2.5 for long agentic sessions — reproducible mid-response cutoff bug. V2.6 Pro/Flash are candidates only; treat the cutoff as still open until rechecked.
- Muse Spark 1.3 is frontier-strong (AA 61) *and* the cheapest OpenCode lane — use it for non-sensitive bulk and everyday coding when region allows. **Contributor means prompts/inputs will likely be used for training. Never send secrets, private IP, or sensitive data.** Limited regions. Sensitive fallback is GPT-6 Luna. No-data-sharing OpenCode fallback is Omen Alpha or DeepSeek V4.1 Flash.
- Gemini API costs real dollars — default to Luna or DeepSeek Flash for text volume. Use 3.8 Flash when the task needs audio/video, computer-use, or search grounding. Prefer 3.8 Flash over older 3.6/3.7 Flash. Flash-Lite is no longer the cheapest extraction tier.
- OpenCode's scarce models (Kimi K3, Qwen3.8 Max, Grok, GLM-5.3) are cheaper to reach through their native harness: GLM-5.3 via Pi, Grok 4.7 via Grok CLI — save the OpenCode allocation for models unique to it (Muse, Omen, Hy4, GLM-5.3-Flash, Qwen3.8 Flash, DeepSeek V4.1 Flash, MiMo V2.6).
- Hard work: Opus 5.5 first, Astra when you need token-efficient science/computer-use or a second lab, Fable when Opus token burn dominates. Do not default Codex to Astra.
- Pin a Codex model (`gpt-6-sol` everyday, `gpt-6-luna` for scouts). Newer Codex builds may fall back to Astra if model is unset.
- Astra, Sol, and Luna input >272k doubles the whole request — prefer Opus 5.5 / Fable / GLM for huge-prefix agents.

---
Data: 25 Sep 2026. OpenCode req/5hr figures not remeasured. Re-verify pricing/limits if months have passed.
