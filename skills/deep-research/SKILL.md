---
name: deep-research
description: Conduct thorough multi-source research on complex topics. Use when user asks to research, investigate, or deeply explore a subject. Triggers on queries like "research X", "what's the current state of Y", "help me understand Z", "find out about", or any request requiring synthesis from multiple sources. NOT for simple factual lookups or single-source queries.
---

# Deep Research

Systematic research workflow: clarify intent → generate subqueries → parallel search → synthesize → report.

## Workflow

### 1. Clarify Intent (if needed)

Skip if query is specific and doesn't raise questions. Otherwise, ask:
- What's the goal? (decision-making, learning, writing, comparison)
- Scope constraints? (time period, geography, domain)
- Depth preference? (overview vs comprehensive)

Keep clarification brief—1-2 questions max.

### 2. Generate Subqueries

Generate 3-10 subqueries based on complexity. Adapt query types to the research:

**Angle-based** (for conceptual/evaluative queries):
- "consensus on best weight loss strategy" → pros, cons, alternatives, history, scientific backing

**Phrasing-based** (for how-to/technical queries):
- "video generation website with LLM" → different phrasings targeting same info

**Optional adversarial** (for gray-area topics):
- "criticisms of X", "X failures", "alternatives to X"

**Optional "without" queries** (when relevant):
- Original: "generate long videos with AI"
- Without: "generate long videos without AI" OR "generate short videos with AI"
- Skip for framework-specific or factual queries

### 3. Parallel Search

Launch 3-10 subagents (one per subquery). Each subagent uses ALL tools:

```
For each subquery, use in order:
1. exa search "<query>" -n 5
2. exa code "<query>" -t 5000  (if technical)
3. WebSearch for broader coverage
4. firecrawl_scrape for promising URLs needing full content
```

Subagents report findings back to main agent. Main agent controls all drilling—subagents do NOT spawn sub-subagents.

Read PDFs and academic papers when encountered.

### 4. Deduplicate

Dedupe at content level (semantic similarity), not just URL. Same information from multiple sources = one finding with multiple citations.

### 5. Saturation Check

After each round, ask: "Did I learn anything substantially new?"

- If yes and under max rounds → generate new subqueries for gaps, run another round
- If no or at max rounds → proceed to synthesis

**Safety cap**: Maximum 3 rounds of searching.

### 6. Auto-Drill (if needed)

Automatically drill deeper when:
- Insufficient detail on a highly relevant subtopic
- Key claim needs verification
- Contradictions need resolution

Trigger drilling by generating targeted subqueries and running focused searches. Main agent controls all drilling decisions.

User can also request drilling: "tell me more about X from the report"

### 7. Synthesize

- Reconcile conflicting information: present all perspectives, then offer tentative reconciliation
- Mark confidence levels on findings:
  - "widely agreed" (multiple quality sources)
  - "likely" (few sources, consistent)
  - "disputed" (sources disagree)
  - "thin evidence" (single source only)
- Explicitly flag claims with weak evidence

### 8. Generate Report

Default structure (adapt based on user request):

```markdown
## Executive Summary
[2-3 sentences: key finding + confidence + main caveat]

## Key Findings
[Bulleted findings with confidence markers]
- **[High confidence]** Finding 1
- **[Disputed]** Finding 2 — Source A says X, Source B says Y

## Conflicting Perspectives
[If applicable: present disagreements + tentative reconciliation]

## Sources
[Numbered list with brief description of each source's contribution]

## Gaps & Limitations
[What wasn't found, what remains uncertain, potential biases in sources]

## Suggested Next Steps
[2-3 highly pertinent options for further exploration]
```

### 9. Offer Next Steps

After presenting report, proactively suggest:
- Drilling into specific findings
- Exploring adjacent topics surfaced during research
- Investigating unresolved contradictions

## Tool Priority

Use in this order, but run searches in parallel across tools:

1. `exa search` / `exa code` — optimized for technical/documentation
2. `firecrawl_search` — broader web search
3. `WebSearch` — fallback for coverage
4. `firecrawl_scrape` — extract full content from promising URLs

## Key Principles

- **No source weighting**: Don't favor results just because they rank higher
- **Confidence matters**: Always indicate evidence strength
- **Parallel first**: Maximize parallel searches, then synthesize
- **User control**: User can always override, customize report structure, or redirect research
- **Honest gaps**: Report what wasn't found, not just what was
