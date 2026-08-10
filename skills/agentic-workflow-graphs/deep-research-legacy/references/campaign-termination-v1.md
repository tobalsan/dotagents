# Campaign termination v1

Optional outer-campaign contract. Without a campaign target, deep-research remains one pass and callers use `manifest-verify`; `campaign-evaluate` always requires a config.

## Configuration

Config is JSON validated by [`campaign-termination-v1.schema.json`](campaign-termination-v1.schema.json). `target` is type-flexible through predicates:

- `count`: folded ledger count at least `at_least`, with explicit `statuses` and optional `source_types`. Rejected rows count only when `rejected` is named.
- `saturation`: `streak` consecutive verified terminal iteration manifests whose outcome is `saturated` and whose gap-report JSON contains `{"saturated":true}`.
- `deadline`: reached when `now >= at`.
- `budget`: reached when usage `cost_usd` or `tokens` is at least `limit`.
- `all`, `any`, and `not`: recursive composition. Targets can therefore be any supported predicate shape.

`limits` contains only direct hard operational deadline/budget predicates. Precedence is explicit: an exceeded limit produces `failed` unless an identical predicate occurs positively in a target that evaluates complete. A match beneath `not` never exempts a limit; a match beneath `all` or `any` exempts it only when the whole target is true and that positive matching branch is true. No inferred defaults, wall clock, paths, statuses, source types, or usage values exist.

## Inputs and result

```bash
python3 scripts/research_state.py campaign-evaluate \
  --config CAMPAIGN/termination.json \
  --ledger CAMPAIGN/source-ledger.jsonl \
  --manifest CAMPAIGN/passes/1/iteration-manifest.jsonl \
  --artifact-root CAMPAIGN \
  --usage CAMPAIGN/usage.json \
  --now 2026-01-31T00:00:00Z
```

Repeat `--manifest` in chronological iteration order. Evaluator verifies unique iteration IDs and strictly increasing terminal `observed_at` values; reordered, duplicate, or time-ambiguous histories fail. Saturation targets require at least one manifest. Supply `--usage` when any budget predicate needs it. Gap-report paths come only from verified terminal manifests, remain beneath explicit artifact root, and point to JSON boolean saturation evidence.

Stdout is one canonical JSON object conforming to [`campaign-evaluation-result-v1.schema.json`](campaign-evaluation-result-v1.schema.json). Exit `0` means `continue`, `10` means `complete`, and `20` means `failed`. Missing or malformed config/state, unsafe evidence, and unverifiable manifests are `failed` with `reason: state_error`; they never produce completion. `--now` is mandatory, making deadline results replayable.
