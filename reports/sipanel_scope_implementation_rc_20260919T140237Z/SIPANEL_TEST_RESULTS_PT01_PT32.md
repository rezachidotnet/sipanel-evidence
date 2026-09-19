Run sipanel_scope_implementation_rc_20260919T140237Z · Verdict: BLOCKED_NOT_ISOLATED · Status: no module was written, installed or tested in this run; nothing below is a PASS.

# SIPANEL — Test Results Register PT-01…PT-32

Common values for every row (stated once, apply to all):

- Build commit: **NONE** — no source was written in this run.
- Clone identity: **NONE** — `BLOCKED_NOT_ISOLATED` (see BLOCKED_NOT_ISOLATED.md, EV-01, EV-02).
- Configuration: none applied; profile intended = provisional BQ/AM profile from the run brief.
- Actual result: **NOT EXECUTED**.
- Status: **BLOCKED**.
- Timestamp / runner: 2026-09-19 UTC / Claude Code (claude-fable-5-1).
- Evidence reference: `BLOCKED_NOT_ISOLATED.md`, `evidence/EV-01_HOST_ENVIRONMENT_IDENTITY.txt`, `evidence/EV-02_DATABASE_INVENTORY_AND_RECOVERY_POINT.txt`.
- Blocker reason: execution environment is the Production host; no isolated clone reachable; clone creation on this host prohibited (Readiness v1.0 §6.1).

## PT-01 … PT-32 (definitions from Master C9, verbatim expected invariants)

| Test ID | Slice | Input references (C9 synthetic fixture) | Expected result (invariant / evidence) | Status |
|---|---|---|---|---|
| PT-01 | B | released master V1, Scope qty 85 m, 8 occurrences | independent snapshot and compatible anchor; cost 10734; no execution records | BLOCKED |
| PT-02 | A/B | publish V2 (adds outlet), change product cost and labels | V1 snapshot unchanged byte/value comparisons | BLOCKED |
| PT-03 | A/B | qty entered as 8500 cm and as 85 m; m² attempt | same demand/cost if installed conversion valid; incompatible m² rejected | BLOCKED |
| PT-04 | B | override Bracket 170→180 then change scope qty | final 180 retained; stale override flagged; reviewer action required | BLOCKED |
| PT-05 | B | percentage self/cycle/cross-scope/mixed-unit bases | validation rejects; percent cost no physical demand | BLOCKED |
| PT-06 | B | split Screw + dependent 5 % allowance to new Scope | source 10377 + destination 357; lineage preserved, no duplicate occurrence counted | BLOCKED |
| PT-07 | B | split Screw alone (allowance base left behind) | block with actionable dependency message | BLOCKED |
| PT-08 | B | change components after manual final note | note stays, stale warning; cannot send unreviewed mismatch | BLOCKED |
| PT-09 | B | duplicate quote then modify | original unaffected; no acceptance/execution links copied; no master upgrade | BLOCKED |
| PT-10 | C | additional crane option, Optional+Provisional; operator and portal `update_line_dict` (SV-03) | operator and portal acceptance both bind current sealed revision; explicit anchor stays stable through section reorder/delete; tax/pricelist recompute; included/demand once only | BLOCKED |
| PT-11 | C | Customer Scope component / INTERNAL_ONLY component | customer scope no supply cost; internal cost included but not leaked | BLOCKED |
| PT-12 | D | ESTIMATE_ONLY without Product; missing dimensional context | release blocked; approved allowance remains no-action | BLOCKED |
| PT-13 | D | native anchor with kit/route (SV-13) + bridge | one owner, single demand/explosion; no hidden component sale lines | BLOCKED |
| PT-14 | D | Release twice; concurrent `SKIP LOCKED`/`LockError` (SV-07); timeout retry | one unique authorized demand per key; bounded retry returns same target links | BLOCKED |
| PT-15 | D | one adapter fails before commit | atomic rollback of batch-created docs; no orphan confirmed order claims | BLOCKED |
| PT-16 | E | buy shared stock, transfer to site, consume | only selected consumption cost recognized; receipt/transfer/bill excluded duplicate | BLOCKED |
| PT-17 | E | manufacture Gutter, consume raw/labour, finished issue | parent full value counted once; MO labour/timesheet not duplicated | BLOCKED |
| PT-18 | E | direct buy + bill + landed cost | chosen recognition route only; capitalization respected (landed cost module not installed — EV-04) | BLOCKED |
| PT-19 | E | partial receipt/backorder/return/credit | links and remaining demand preserved; signed reversal once | BLOCKED |
| PT-20 | E | real labour 8/9 hours; equipment bill | no synthetic timesheets; correct actual approved source only | BLOCKED |
| PT-21 | E | post fixture actual and revenue | cost 11150, baseline 10734, net variance 416, margin 850; variance bridge +603 direct overrun and −187 unused contingency; source-ledger reconciliation | BLOCKED |
| PT-22 | D | price-only amendment; qty increase/decrease; cancel/reconfirm | no price-only demand; deltas only; no deletion of actual | BLOCKED |
| PT-23 | B/C | portal/RPC/export/PDF/attachment as customer and as other company | zero access to cost, internal notes, unauthorized order, records or existence counts | BLOCKED |
| PT-24 | A/B | released/confirmed edit through import and RPC | deny bypass; new revision required; audit event | BLOCKED |
| PT-25 | B | FX source 100 at saved rate 2; later rate 3 | estimate 200 unchanged; actual 300 if valid event; FX difference 100 not history overwrite (MVP: foreign currency blocked, BQ-09 — test reduces to block assertion) | BLOCKED |
| PT-26 | B | source cost per dozen to unit | valid conversion before multiplication; wrong cost-unit not silently accepted | BLOCKED |
| PT-27 | B | 10 % discount on 12000 fixture | net 10800; margin 66; zero-revenue margin % = N/A; taxes outside R | BLOCKED |
| PT-28 | B | known-zero vs missing cost | different readiness/status; missing not silently treated as free | BLOCKED |
| PT-29 | E | unallocated actual cost | visible bucket and reconciliation gap; Scope profitability not claimed complete | BLOCKED |
| PT-30 | infra | backup/restore on separate clone host with attachments/revisions | restore counts/links/artifact hashes and ledger equality; no live mail/cron/payment/portal integration | BLOCKED |
| PT-31 | B | ordinary Sales line without Scope | native pricing/invoice/route regression unchanged | BLOCKED |
| PT-32 | B/C | snapshot roundtrip customer PDF/portal language | exact accepted version, no silent live master translation update | BLOCKED |

## Additional required test groups

| Group | Scope | Status | Reason |
|---|---|---|---|
| Clean-database install | four Production modules on a clean DB (Runbook B.3) | BLOCKED | no clone; no source |
| Upgrade from preceding build | `-u` of the four modules over a previous RC | BLOCKED | no preceding build exists |
| Ordinary non-Scope Sales regression | quotations/orders without Scope, templates, sections, combos/subsections (SV-06) | BLOCKED | no clone |
| Purchase / Inventory / MRP / Project regression | existing documents after Product Unit precision change (B-01), routes, kits, service tracking | BLOCKED | no clone |
| Tax / discount / fiscal position / invoice regression | native computation with Scope anchors present | BLOCKED | no clone |
| Portal and PDF rendering | report id 848 (EVIDENCE-DATED), `external_layout_bubble` override and duplicate `commitment_date` xpath (SV-18) | BLOCKED | no clone |
| Concurrent Release and retry | two simultaneous Release actions; `LockError` (SV-07) | BLOCKED | no clone; no source |
| Duplicate-demand tests | NATIVE_LINE_OWNER vs COMPONENT_BRIDGE_OWNER (SV-13) | BLOCKED | no clone; no source |
| Security denial 1 — ACL and record rules | | BLOCKED | no clone; no source |
| Security denial 2 — company isolation | | BLOCKED | |
| Security denial 3 — direct ORM/RPC/import bypass | | BLOCKED | |
| Security denial 4 — Portal access | | BLOCKED | |
| Security denial 5 — stale-link / replay | | BLOCKED | |
| Security denial 6 — PDF, attachment and export leakage | | BLOCKED | |
| Security denial 7 — unauthorized cost/margin access | | BLOCKED | |
| Security denial 8 — sealed revision mutation | | BLOCKED | |
| Security denial 9 — cross-project access | | BLOCKED | |
| Security denial 10 — privileged override audit | | BLOCKED | |
| Finance reconciliation | selected events vs ledger, PT-16…PT-21 | BLOCKED | BQ-04 unsigned (MISSING_INPUT); no clone |
| Backup / restore rehearsal | PT-30 | NOT_RUN | no isolated target (see rehearsal report) |
| Rollback rehearsal | | NOT_RUN | no isolated target (see rehearsal report) |
| C9 "متعلقات آبرو" vertical pilot | full fixture | BLOCKED | see SIPANEL_VERTICAL_PILOT_RESULTS.md |

## Totals

PASS 0 / FAIL 0 / BLOCKED 32 (+ 21 additional groups BLOCKED, 2 NOT_RUN) / NOT_APPLICABLE 0.

## Failure and correction history

None — no test was executed in this run. No diagnosis, fix or rerun occurred.
