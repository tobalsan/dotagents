---
name: choose-llm-for-task
description: Instantly pick the top 3 best-suited models for a task across the user's five harnesses (Claude Code, Codex, Grok CLI, Pi, OpenCode Go), factoring in real subscription/quota limits. Use whenever deciding which LLM/model to route a task to, delegating work to another agent/CLI, picking a council member, comparing models, or the user asks which model to use for X.
---

# Choose LLM For Task

Find the task type in the routing table below. Take the top-3 picks **in order** — try 1st, degrade to 2nd/3rd only if that harness is capped, unavailable, or scarce (see budgets). Cross-check the per-model cheat sheet and rules of thumb before committing to a scarce or costly pick.

## Harness budgets (real limits, Sep 2026)

| Harness | Tier | Models |
|---|---|---|
| Claude Code | High-tier sub, comfortable | claude-fable-5-1, claude-opus-5, claude-sonnet-5, claude-haiku-4-5 |
| Codex | High-tier sub, comfortable | gpt-5.6-sol, gpt-5.6-terra, gpt-5.6-luna; gpt-5.5 (superseded — avoid); gpt-5.3-codex-spark (separate rate limit, Pro preview) |
| Grok CLI | FREE, promo "unlimited" — unreliable/temporary | grok-4.6, grok-build-0.1 — opportunistic only, never critical-path |
| Pi | GLM Coding Plan Pro (flat-rate, generous) + Gemini via PAID API (real $) | glm-5.3 = cheap workhorse; gemini-* = use deliberately, prefer flash tiers |
| OpenCode Go | $12/5hr, $30/wk, $60/mo ($-denominated) | cheap = near-unlimited (muse-spark-1.3-contributor ~45.3k req/5hr — frontier-strong, not a weak bulk model; limited regions; Meta trains on prompts — never sensitive data; mimo-v2.5 ~30.1k; omen-alpha ~11.6k; longcat-2.0 ~11.4k; deepseek-v4-flash ~7.6k; qwen3.8-flash ~5.4k; qwen3.7-plus/hy3 ~4.3k; minimax-m3 ~3.2k; glm-5.3-flash ~1.58k / 2x promo ~3.16k; gpt-5.6-luna ~2.05k); scarce/costly (hy4-preview 1.35k, glm-5.3 220, grok-4.6 169, qwen3.8-max 160, kimi-k3 110 — reach Grok/GLM/Kimi via their own harness instead) |

## Routing table

| Task type | 1st | 2nd | 3rd | Why/notes |
|---|---|---|---|---|
| Hardest problems: architecture, deep diagnosis, gnarly debugging | claude-fable-5-1 | gpt-5.6-sol (high/max effort) | claude-opus-5 | Fable 5.1 = SOTA ceiling (Terminal-Bench 4.0 55.8%, CursorBench 73.4%); Sol close 2nd; Opus 5 near-frontier at half Fable price |
| Everyday feature implementation (agentic default) | claude-sonnet-5 | gpt-5.6-terra | glm-5.3 (Pi) | Sonnet = fast/agentic default; Terra ≈Fable-class at 1/4 cost; GLM-5.3 cheap flat-rate fallback (open-weight coding SOTA vs 5.2) |
| Large repo-scale refactor / hard coding | claude-opus-5 | gpt-5.6-sol | glm-5.3 | Opus 5: SWE-bench 96%; Sol: SOTA Coding Agent Index; GLM-5.3: true 1M ctx, big jump over 5.2 on long-horizon |
| Code / PR review (cross-vendor second opinion valuable) | claude-opus-5 | gpt-5.6-sol | grok-4.6 (free extra lane) | Deliberately diversify vendor; Grok 4.6 matches Sol on AA Intelligence Index, free but unreliable |
| Security review | gpt-5.6-sol (cyber SOTA; Trusted Access gated) | claude-fable-5-1 | claude-opus-5 | Sol ExploitBench SOTA but gated; Fable 5.1: 60% fewer cyber false positives, vuln *discovery* OK, not exploit-dev. Mythos 5.1 / Gemini 3.8 Flash Cyber = gated twins |
| Quick scoped edits, boilerplate, test scaffolding | claude-haiku-4-5 | gpt-5.6-luna | grok-build-0.1 | All cheap/fast; Luna beats Opus 4.8 on Coding Agent Index at 1/4 cost |
| Ultra-fast interactive iteration (pair loop) | gpt-5.3-codex-spark | claude-haiku-4-5 | gemini-3.8-flash | Spark 1000+ tok/s, separate quota; text-only, no deep reasoning. 3.8 Flash ~300 tok/s + agentic |
| Bulk/mechanical fan-out (mass migration, many small tasks) | muse-spark-1.3-contributor (OpenCode; never sensitive data) | omen-alpha or deepseek-v4-flash (OpenCode) | mimo-v2.5 (OpenCode; short/medium context ONLY) | Muse is both bulk king (~45.3k/5hr) AND frontier-strong (AA Index 61, ties Sol max / Grok 4.6). Contributor = Meta trains on prompts/code — never use on secrets, private IP, or sensitive data. Limited regions. Else Omen ~11.6k or DeepSeek Flash ~7.6k. MiMo: long-session cutoff bug |
| Classification / extraction / summarization at volume | gemini-3.5-flash-lite | deepseek-v4-flash | claude-haiku-4-5 | Flash-Lite cheapest+fastest, unusually strong for lite tier; costs real $ via API though |
| Deep reasoning, math, science (non-coding) | gemini-3.1-pro-preview (costly API — sparingly) | claude-fable-5-1 | gpt-5.6-sol | Gemini 3.1 Pro: ARC-AGI-2 77.1%, GPQA 94.3%, but expensive and slow. Fable 5.1 HLE 60.9%/65.0% tools |
| Cheap deep reasoning at volume | deepseek-v4-pro (OpenCode) | glm-5.3 (Pi) | glm-5.3-flash (OpenCode) | DeepSeek Pro: ~$0.04/task deep reasoning, verbose but absurdly cheap |
| Long-context (huge docs / whole repos, up to 1M) | claude-fable-5-1 | glm-5.3 | gpt-5.6-sol | Fable 1M ctx best-in-class; GLM's 1M genuinely holds up in practice |
| Multimodal (screenshots, PDFs, video, audio) | gemini-3.8-flash | claude-fable-5-1 (vision SOTA, no audio/video) | glm-5.3-flash or muse-spark-1.3-contributor (cheap bulk vision, OpenCode) | 3.8 Flash: text/image/video/audio/PDF + computer-use preview. Qwen3.8-flash / MiniMax-M3 also cheap bulk |
| Real-time info / web + X research | grok-4.6 (built-in web/X search, free) | gpt-5.6-sol (BrowseComp SOTA 92.2%) | gemini-3.8-flash (search grounding) | Grok's X search is a unique differentiator |
| Computer use / browser automation | claude-fable-5-1 (OSWorld 2.0 77.9% partial) | claude-opus-5 | gemini-3.8-flash | Fable 5.1 best-in-class computer-use; 3.8 Flash has computer-use preview |
| Long-horizon agentic knowledge work (docs, office, workflows) | claude-fable-5-1 | kimi-k3 (OpenCode; ~110 req/5hr — single high-value shots only) | hy4-preview (OpenCode; 1M ctx, office/productivity) | Fable 5.1 AutomationBench 31.4%. Kimi #1 AutomationBench but scarce. Hy4 supersedes Hy3 |
| Writing, docs, PRDs | claude-sonnet-5 | claude-fable-5-1 (quality paramount) | gpt-5.6-terra | Sonnet default; escalate to Fable 5.1 only when quality matters most |

## Per-model cheat sheet

**Claude Code**
- `claude-fable-5-1` — SOTA ceiling (Sep 2026). Stronger long-horizon coding/research than Fable 5 at same $10/$50; cache reads 4× cheaper ($0.25). OSWorld 77.9%, AutomationBench 31.4%. Adaptive thinking always on. Vuln discovery OK, not exploit-dev. Safety classifiers still may refuse cyber/bio-adjacent work. `claude-mythos-5-1` = same model, Glasswing-only.
- `claude-opus-5` — Frontier at half Fable price. SWE-bench 96%, strong computer-use. Moderate speed, $5/$25. Anthropic's recommended start for most workloads.
- `claude-sonnet-5` — Fast, agentic default, near-Opus on knowledge work. $2/$10.
- `claude-haiku-4-5` — Fastest, near-frontier for scoped tasks. $1/$5, 200K ctx only.

**Codex**
- `gpt-5.6-sol` — Flagship, SOTA coding agent index + cyber. $5/$30. `ultra` effort = 4-16 parallel agents but 6-12x token blowup — avoid for orchestration.
- `gpt-5.6-terra` — Recommended default Codex tier; ≈Fable-5 quality at 1/4 cost/time. $2/$12.
- `gpt-5.6-luna` — Cheapest fully-agentic tier; beats Opus 4.8 on Coding Agent Index. $0.20/$1.20. Not for ambiguous/high-stakes work.
- `gpt-5.5` — Superseded by Terra — avoid.
- `gpt-5.3-codex-spark` — Cerebras 1000+ tok/s pair-coding niche. Separate rate limit, Pro preview, text-only, doesn't auto-run tests.

**Grok CLI**
- `grok-4.6` — Matches Sol on AA Intelligence Index (61). Long-running agents, visual/interactive work, built-in web+X search. $2/$6 API, 500K ctx. Free-promo on CLI (unreliable). Prefer CLI over OpenCode (169/5hr).
- `grok-build-0.1` — Fast/cheap agentic SWE, always-on reasoning, no effort dial. Notably behind frontier accuracy (SWE-bench Verified 70.8% vs 88.7%).

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
- `kimi-k3` — #3 Intelligence Index, #1 AutomationBench, native vision. Costly + slow on long runs. SCARCE (110/5hr) — high-value single shots only.
- `hy4-preview` — Hy3 successor: 1M ctx, office/productivity + stronger coding/front-end. Preview (~1.35k/5hr).
- `hy3` — Beats GLM-5.2 on everything except coding; strong office/productivity/finance. 256K ctx only. Prefer Hy4 when available.
- `omen-alpha` — Cheap stealth (~11.6k/5hr, $0.20/$0.66). Unproven lab; treat as no-data-sharing bulk alternative to Muse.
- `longcat-2.0` — Cheap 1M-ctx bulk (~11.4k/5hr).
- `minimax-m3` — Cheap ($0.30/$1.20), native image/video + computer use. Vendor benchmarks unverified.
- `deepseek-v4-pro` — Cheap deep-reasoning workhorse (~$0.04/task). Slow, very verbose. ~1.05k/5hr.
- `deepseek-v4-flash` — Cheap/fast bulk, AA Index 50. No vision; community reports inconsistent steering. Quota tightened (~7.6k/5hr, was ~31k).
- `mimo-v2.5` — Very cheap (~30.1k/5hr), native image+audio. CRITICAL: hybrid-window "1M ctx" causes mid-response cutoffs in long agentic sessions — short/medium context ONLY.

## Rules of thumb

- Prefer free/flat-rate lanes (Grok CLI, GLM-5.3 via Pi, OpenCode cheap models) before spending on metered API (Gemini) or scarce quota.
- Escalate exactly one tier after a cheaper pick fails twice — don't jump straight to the most expensive model on first friction.
- Cross-vendor deliberately for reviews and second opinions (different training data/blind spots catch different bugs).
- Never use MiMo-V2.5 for long agentic sessions — reproducible mid-response cutoff bug.
- Muse Spark 1.3 is frontier-strong (AA 61) *and* the cheapest OpenCode lane — use it for non-sensitive bulk and everyday coding when region allows. **Contributor means prompts/inputs will likely be used for training. Never send secrets, private IP, or sensitive data.** Limited regions. Fall back to Omen Alpha or DeepSeek V4 Flash when data-sharing is unacceptable.
- Gemini API costs real dollars — default to flash-lite unless the task needs multimodal, computer-use, or 3.1 Pro-level reasoning. Prefer 3.8 Flash over older 3.6/3.7 Flash.
- OpenCode's scarce models (Kimi K3, Qwen3.8 Max, Grok 4.6, GLM-5.3) are cheaper to reach through their native harness: GLM-5.3 via Pi, Grok 4.6 via Grok CLI — save the OpenCode allocation for models unique to it (Muse, Omen, Hy4, GLM-5.3-Flash, Qwen3.8 Flash).

---
Data: September 2026. Re-verify pricing/limits if months have passed.
