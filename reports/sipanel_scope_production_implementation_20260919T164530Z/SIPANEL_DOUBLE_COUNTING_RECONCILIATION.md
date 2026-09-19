Run sipanel_scope_production_implementation_20260919T164530Z · Target: database `sipanel` on container `odoo-sipanel` (Odoo 19.0-20260528) · Build: source commit 99dd874 (fixes on top of 931f949) · Runner: Claude Code (claude-fable-5-1) · Date: 2026-09-19 UTC

# SIPANEL — Double-counting Reconciliation (EXECUTED)

Mechanism as built (unchanged): natural key per monetary source (SQL UNIQUE), `layer` + `inclusion` on every candidate (commitments, receipts, raw MO moves, workorder analytic lines stored as *excluded*, never silently dropped), fail-closed route policy, linked reversals, separate measures in `sipanel.scope.variance`.

## Measured in run #5 (`test_pt16_pt21_reconciliation`, `test_pt19_return_and_credit_reverse_once`, `test_policy_fail_closed_and_pt29_unallocated`)

| Check | Result |
|---|---|
| One recognised event per source key | assert len(keys) == len(set(keys)) ✔ |
| Raw coil consumption of the MO not in recognised set; stored as WIP/excluded | ✔ |
| PO line commitment stored as commitment/excluded; bill recognised once (450) | ✔ |
| Material recognised = gutter issue `stock.move.value` + 850 + 340 + 17 + 220 | ✔ |
| Labour = 9 h × 30 = 270 from the real timesheet; module created no timesheet | ✔ |
| Revenue = posted invoice lines on the anchor = 12000 | ✔ |
| Variance view = event sums; recognised margin = revenue − cost; variance = cost − 10734 | ✔ |
| Contingency (PERCENT_OF_COST) has no actual event | ✔ |
| Refund creates a negative event linked by `reversal_of_id`; net 0; second refresh does not duplicate; bill/credit retained | ✔ |
| Route without approved policy → events POLICY_MISSING, sums nothing, completeness policy_missing | ✔ |
| Timesheet on a project without target link → UNALLOCATED 30 visible; manual Finance allocation with reason closes it and is audited | ✔ |
| Idempotent refresh (same number of events) | ✔ |
| Projection writes no native record (analytic line count unchanged) | ✔ |

Finance policies are now APPROVED in the database with source "Management authorization 2026-09-19"; statutory tax/accounting validation remains required before live commercial use.
