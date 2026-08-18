---
name: hledger-accounting
description: Personal accounting assistant for Thinh's plain-text-accounting (PTA) repo at ~/code/finance/hledger — an hledger journal synced from Revolut and BoursoBank via the GoCardless Bank Account Data API. Covers the repo layout, the two sync scripts (bank_sync_setup.py for connections/token renewal, account_sync.py for fetching transactions), API rate limits and dedup behavior, and day-to-day hledger commands for checking balances, querying transactions, income statements, and expense breakdowns. Use when asked about account balances, spending, transaction history, syncing bank data, refreshing/renewing bank connections, scheduling recurring syncs, or maintaining the journal.
---

# hledger accounting (Thinh's PTA repo)

Repo: `~/code/finance/hledger`. Run all commands from the repo root — `hledger` picks up `main.journal` via the default `-f main.journal` convention used below. Python always via `uv run python` (never bare `python`/`pip`).

## Repo layout

| Path | What it is |
|---|---|
| `main.journal` | The single journal (current year, started 2025-07-17). All balances live here. |
| `account_sync.py` | Fetches new transactions from the GoCardless API and appends them to the journal. |
| `bank_sync_setup.py` | Interactive menu: add bank connections, view details, renew expiring agreements, remove connections. |
| `view_credentials.py` | Shows stored API credentials. |
| `accounts_map.json` | Maps GoCardless account IDs, IBANs, and counterparty names → hledger accounts. Sync prompts for unknown keys unless `--skip-prompts`. |
| `~/.hledger_bank_config.json` | Connection config: tokens, agreement expiry, selected accounts (Revolut: main, joint, and pockets pro expenses/rent/investing/tax/vacation; BoursoBank: main). Plain JSON, do not commit. |
| `exports-*/`, `statements/` | Raw bank CSV exports + `.csv.rules` files for manual imports (see `csv_import_guide.md`, `examples/csv.rules/`). |
| `README.md` | Has a "Journal" section documenting past reconciliations and known caveats — read it before diagnosing balance discrepancies. |

Key hledger accounts: `assets:revolut:{main,joint,tax,vacation,...}`, `assets:boursobank:main`, `assets:cash`, `assets:okx`, `assets:bitget`, broker accounts (`assets:ibkr:*`, `assets:saxo:*`), `liabilities:debt:bnp` (MacBook credit, ~143.70/month direct debit), `income:{freelancing,refunds,referrals}`, `transfers:{audrey,mum,...}` (money moving to/from people, not expenses), and `expenses:{groceries,eating out,rent,utilities,taxes,subscriptions,general admin,recreation,health,household,transportation,gas,insurance,errands,misc}`.

## Day-to-day queries

Always sanity-check first: `hledger check` (validates parsing and balance assertions).

```bash
hledger bal assets liabilities                 # current balances
hledger bal assets:revolut --tree              # one bank, tree view
hledger reg assets:revolut:main -b 2026-08-01  # register (transaction list) since a date
hledger reg expenses:groceries -p "last month" # postings for a category in a period
hledger reg desc:Auchan                        # search by payee/description
hledger is -b 2026-01-01 -e 2026-09-01         # income statement for a window
hledger is -M -b "3 months ago"                # month-by-month income statement
hledger bal expenses -b 2026-08-01 --tree -S   # expense breakdown, sorted
hledger bal expenses tag:holidays              # by tag
hledger print desc:BNP                         # full transactions as journal text
```

Money sent to family/friends sits in `transfers:*`, not expenses — include it explicitly if the user asks "where did my money go". `expenses:misc` is the intentional catch-all (~500 EUR of cash + unidentifiable rows); don't force-categorize it.

## Syncing transactions

```bash
uv run python account_sync.py --dry-run    # ALWAYS dry-run first, review what would be written
uv run python account_sync.py              # real sync (auto-backs-up journal to main.backup.<timestamp>)
```

Useful flags: `--days N` (fetch window, default 30; dedup lookback widens to match), `--bank NAME`, `--account NAME`, `--skip-prompts` (unattended mode: unknown counterparties get fallback accounts instead of interactive prompts — required for cron), `--verbose`, `--journal PATH`, `--config PATH`.

Behavior to know:
- **Token refresh is automatic** during sync. If it fails, the *agreement* (90-day consent) has likely expired → run `uv run python bank_sync_setup.py` and use "Renew expiring agreements".
- **Rate limit: 4 successful transaction fetches per account per rolling day** (GoCardless). Exhausted limits surface as a `'NoneType' object has no attribute 'status_code'` error — that means 429, not a bug. Wait (the reset is typically minutes to hours) and retry; don't burn attempts on repeated full syncs. Dry-runs consume the same quota.
- **Dedup** filters rows already in the journal by (date, amount, account) fingerprint, plus counter-leg fingerprints so a transfer fetched from both sides books only once. The joint account is deliberately synced last so transfers into it book from the true source account. Trust the "duplicates filtered" count; don't re-add rows by hand.
- Transactions are booked on the bank's booking date; card payments settle 1–2 days after purchase, so a day-level mismatch vs. a bank app is usually pending settlement, not an error.

### Scheduled/recurring sync

For a cron or agent-scheduled job, the non-interactive form is:

```bash
cd ~/code/finance/hledger && uv run python account_sync.py --skip-prompts --quiet
```

Daily or every-few-days is the right cadence (rate limits make more frequent runs pointless). After an unattended run, check for fallback-account postings (`hledger reg unknown` — fallbacks land in `assets:unknown:main` or `assets:transfers:unknown`) and re-map anything new in `accounts_map.json`, then fix the postings.

### Connection setup / renewal

`uv run python bank_sync_setup.py` — interactive (needs a human for the bank's OAuth consent in a browser; don't run it headless). The menu handles: new connection, view details, renewal (agreements expire after ~90 days; the script warns on startup), removal. `--sandbox` for GoCardless sandbox testing.

## Editing the journal safely

- Back up first (`cp main.journal main.backup.$(date +%Y%m%d-%H%M%S)`), edit, then `hledger check` must pass before you're done.
- The journal contains **balance assertions** (e.g. an Aug 2026 pocket true-up asserting Revolut pocket balances). Deleting or editing historical transactions on asserted accounts breaks them — rebalance the assertion transaction's amounts rather than removing assertions.
- Match the existing entry style: `YYYY-MM-DD * Payee`, 4-space indented postings, amount on the first posting only when the second is implied.
- To reconcile an account against a bank statement: compare day-by-day sums of journal postings vs. statement rows (statement "Completed Date" ≈ journal booking date, ±1–2 days for card settlements), then fix the specific days that disagree. Persistent step-changes in cumulative drift mark missing or duplicated transactions.
- Commit only when asked; plain descriptive commit messages on `main`.
