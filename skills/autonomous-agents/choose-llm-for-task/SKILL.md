---
name: choose-llm-for-task
description: Instantly pick the top 3 best-suited models for a task across the user's five harnesses (Claude Code, Codex, Grok CLI, Pi, OpenCode Go), factoring in real subscription/quota limits. Use whenever deciding which LLM/model to route a task to, delegating work to another agent/CLI, picking a council member, comparing models, or the user asks which model to use for X.
---

# Choose LLM For Task

Find the task type in the routing table below. Take the top-3 picks **in order** — try 1st, degrade to 2nd/3rd only if that harness is capped, unavailable, or scarce (see budgets). Cross-check the per-model cheat sheet and rules of thumb before committing to a scarce or costly pick.

## Harness budgets (real limits, Aug 2026)

| Harness | Tier | Models |
|---|---|---|
| Claude Code | High-tier sub, comfortable | claude-fable-5, claude-opus-5, claude-sonnet-5, claude-haiku-4-5 |
| Codex | High-tier sub, comfortable | gpt-5.6-sol, gpt-5.6-terra, gpt-5.6-luna; gpt-5.5 (superseded — avoid); gpt-5.3-codex-spark (separate rate limit, Pro preview) |
| Grok CLI | FREE, promo "unlimited" — unreliable/temporary | grok-4.5, grok-build-0.1 — opportunistic only, never critical-path |
| Pi | GLM Coding Plan Pro (flat-rate, generous) + Gemini via PAID API (real $) | glm-5.2 = cheap workhorse; gemini-* = use deliberately, prefer flash tiers |
| OpenCode Go | $12/5hr, $30/wk, $60/mo ($-denominated) | cheap = near-unlimited (deepseek-v4-flash ~31.6k req/5hr, mimo-v2.5 ~30.1k, qwen3.7-plus/hy3 ~4.3k, deepseek-v4-pro ~3.45k, minimax-m3 ~3.2k, gpt-5.6-luna ~4.1k); scarce/costly (glm-5.2 880, qwen3.8-max 160, grok-4.5 120, kimi-k3 110 — reach these via their own harness instead) |

## Routing table

| Task type | 1st | 2nd | 3rd | Why/notes |
|---|---|---|---|---|
| Hardest problems: architecture, deep diagnosis, gnarly debugging | claude-fable-5 | gpt-5.6-sol (high/max effort) | claude-opus-5 | Fable = SOTA ceiling; Sol close 2nd at lower cost; Opus 5 near-frontier at half Fable price |
| Everyday feature implementation (agentic default) | claude-sonnet-5 | gpt-5.6-terra | glm-5.2 (Pi) | Sonnet = fast/agentic default; Terra matches Fable-class at 1/4 cost; GLM cheap flat-rate fallback |
| Large repo-scale refactor / hard coding | claude-opus-5 | gpt-5.6-sol | glm-5.2 | Opus 5: SWE-bench 96%; Sol: SOTA Coding Agent Index; GLM: true 1M ctx holds up |
| Code / PR review (cross-vendor second opinion valuable) | claude-opus-5 | gpt-5.6-sol | grok-4.5 (free extra lane) | Deliberately diversify vendor for review; Grok free but unreliable, use opportunistically |
| Security review | gpt-5.6-sol (cyber SOTA; Trusted Access gated) | claude-opus-5 | claude-fable-5 (safety classifiers may refuse) | Sol ExploitBench SOTA but gated; Claude models can over-refuse benign-adjacent security work |
| Quick scoped edits, boilerplate, test scaffolding | claude-haiku-4-5 | gpt-5.6-luna | grok-build-0.1 | All cheap/fast; Luna beats Opus 4.8 on Coding Agent Index at 1/4 cost |
| Ultra-fast interactive iteration (pair loop) | gpt-5.3-codex-spark | claude-haiku-4-5 | gemini-3.6-flash | Spark 1000+ tok/s, separate quota; text-only, no deep reasoning |
| Bulk/mechanical fan-out (mass migration, many small tasks) | deepseek-v4-flash (OpenCode) | gpt-5.6-luna | mimo-v2.5 (OpenCode; short/medium context ONLY) | DeepSeek Flash = bulk king, ~31.6k req/5hr; MiMo has long-session cutoff bug — avoid long agentic runs |
| Classification / extraction / summarization at volume | gemini-3.5-flash-lite | deepseek-v4-flash | claude-haiku-4-5 | Flash-Lite cheapest+fastest, unusually strong for lite tier; costs real $ via API though |
| Deep reasoning, math, science (non-coding) | gemini-3.1-pro-preview (costly API — sparingly) | claude-fable-5 | gpt-5.6-sol | Gemini 3.1 Pro: ARC-AGI-2 77.1%, GPQA 94.3%, but expensive and slow |
| Cheap deep reasoning at volume | deepseek-v4-pro (OpenCode) | glm-5.2 (Pi) | deepseek-v4-flash | DeepSeek Pro: ~$0.04/task deep reasoning, verbose but absurdly cheap |
| Long-context (huge docs / whole repos, up to 1M) | claude-fable-5 | glm-5.2 | gpt-5.6-sol | Fable 1M ctx best-in-class; GLM's 1M genuinely holds up in practice |
| Multimodal (screenshots, PDFs, video, audio) | gemini-3.6-flash | claude-fable-5 (vision SOTA, no audio/video) | qwen3.7-plus or minimax-m3 (cheap bulk vision/video, OpenCode) | Gemini handles audio/video Claude can't; Qwen/MiniMax cheap bulk alternative |
| Real-time info / web + X research | grok-4.5 (built-in web/X search, free) | gpt-5.6-sol (BrowseComp SOTA 92.2%) | gemini-3.6-flash (search grounding) | Grok's X search is a unique differentiator |
| Computer use / browser automation | claude-opus-5 (OSWorld 70.6) | gemini-3.6-flash | minimax-m3 (cheap) | Opus 5 best-in-class computer-use at ~1/3 Fable cost |
| Long-horizon agentic knowledge work (docs, office, workflows) | claude-fable-5 | kimi-k3 (OpenCode; ~110 req/5hr — single high-value shots only) | hy3 (cheap office/productivity) | Kimi #1 AutomationBench but scarce — reserve for high-value shots |
| Writing, docs, PRDs | claude-sonnet-5 | claude-fable-5 (quality paramount) | gpt-5.6-terra | Sonnet default; escalate to Fable only when quality matters most |

## Per-model cheat sheet

**Claude Code**
- `claude-fable-5` — SOTA ceiling, best long-horizon/vision/1M ctx. Slow, $10/$50. Safety classifiers may refuse cyber/bio-adjacent work.
- `claude-opus-5` — Frontier at half Fable price. SWE-bench 96%, best computer-use. Moderate speed, $5/$25.
- `claude-sonnet-5` — Fast, agentic default, near-Opus on knowledge work. $3/$15 (intro $2/$10 thru 2026-08-31).
- `claude-haiku-4-5` — Fastest, near-frontier for scoped tasks. $1/$5, 200K ctx only.

**Codex**
- `gpt-5.6-sol` — Flagship, SOTA coding agent index + cyber. $5/$30. `ultra` effort = 4-16 parallel agents but 6-12x token blowup — avoid for orchestration.
- `gpt-5.6-terra` — Recommended default Codex tier; ≈Fable-5 quality at 1/4 cost/time. $2/$12.
- `gpt-5.6-luna` — Cheapest fully-agentic tier; beats Opus 4.8 on Coding Agent Index. $0.20/$1.20. Not for ambiguous/high-stakes work.
- `gpt-5.5` — Superseded by Terra — avoid.
- `gpt-5.3-codex-spark` — Cerebras 1000+ tok/s pair-coding niche. Separate rate limit, Pro preview, text-only, doesn't auto-run tests.

**Grok CLI**
- `grok-4.5` — Strong tier-two coding/agentic, built-in web+X search, token-efficient. $2/$6 API, free-promo on CLI (unreliable).
- `grok-build-0.1` — Fast/cheap agentic SWE, always-on reasoning, no effort dial. Notably behind frontier accuracy (SWE-bench Verified 70.8% vs 88.7%).

**Pi**
- `glm-5.2` — Best open-weight coding model, true 1M ctx, flat-rate generous quota. No vision; verbose; behind frontier on hardest reasoning.
- `gemini-3.1-pro-preview` — Deep-reasoning monster (ARC-AGI-2, GPQA). Costly API, slow (>90s at high thinking), preview rough edges — use sparingly.
- `gemini-3.6-flash` — Fast frontier-ish, strong agentic + built-in computer-use preview. $1.50/$7.50, real API cost.
- `gemini-3.5-flash-lite` — Fastest/cheapest Gemini, unusually strong for lite tier. $0.30/$2.50. Not for multi-step reasoning/agentic coding.

**OpenCode Go** — CLI needs provider-qualified IDs: `opencode run -m opencode-go/<model>` (bare `<model>` fails with a generic "Unexpected server error").
- `kimi-k3` — #3 Intelligence Index, #1 AutomationBench, native vision. Costly + slow on long runs. SCARCE (110/5hr) — high-value single shots only.
- `qwen3.8-max` — #1 reasoning/instruction-following, GPQA 90%. Strong reasoning but slow (~46 tok/s) and scarce on Go (160/5hr).
- `qwen3.7-plus` — Cheap multimodal GUI/agent workhorse, screen reading, ~4.3k req/5hr.
- `minimax-m3` — Cheap ($0.30/$1.20), native image/video + computer use. Vendor benchmarks unverified — treat as cheap multimodal option, not proven frontier.
- `deepseek-v4-pro` — Cheap deep-reasoning workhorse (~$0.04/task). Slow, very verbose.
- `deepseek-v4-flash` — Bulk king: cheap, fast, AA Index 50. No vision; community reports inconsistent steering.
- `hy3` — Beats GLM-5.2 on everything except coding; strong office/productivity/finance. 256K ctx only.
- `mimo-v2.5` — Cheapest, native image+audio. CRITICAL: hybrid-window "1M ctx" causes mid-response cutoffs in long agentic sessions — short/medium context ONLY.

## Rules of thumb

- Prefer free/flat-rate lanes (Grok CLI, GLM via Pi, OpenCode cheap models) before spending on metered API (Gemini) or scarce quota.
- Escalate exactly one tier after a cheaper pick fails twice — don't jump straight to the most expensive model on first friction.
- Cross-vendor deliberately for reviews and second opinions (different training data/blind spots catch different bugs).
- Never use MiMo-V2.5 for long agentic sessions — reproducible mid-response cutoff bug.
- Gemini API costs real dollars — default to flash-lite unless the task genuinely needs multimodal input or 3.1 Pro-level reasoning.
- OpenCode's scarce models (Kimi K3, Qwen3.8 Max, Grok 4.5, GLM-5.2) are cheaper to reach through their native harness: GLM-5.2 via Pi, Grok 4.5 via Grok CLI — save the OpenCode allocation for models unique to it.

---
Data: August 2026. Re-verify pricing/limits if months have passed.
