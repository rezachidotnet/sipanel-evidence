Run sipanel_scope_production_implementation_20260919T145639Z · Verdict: BLOCKED_BEFORE_DATABASE_WRITE · Status: SOURCE WRITTEN AND STATICALLY CHECKED — NOT INSTALLED, NOT RUNTIME VALIDATED (see evidence/EV-02).

# SIPANEL — Double-counting Reconciliation

## Mechanism (as built)

1. **Natural key per monetary source**: `sipanel.actual.cost.event.source_key = model:res_id:component_type:company` with SQL UNIQUE ⇒ a source record can be included once.
2. **Layer + inclusion**: every candidate carries `layer ∈ {commitment, operational, wip, recognized}` and `inclusion ∈ {included, excluded_duplicate, policy_missing}`; only `recognized + included` events are summed (variance view). Commitments (PO lines), receipts, internal transfers, raw consumption, workorder analytic lines and unvalidated timesheets are **stored as excluded** so the exclusion is visible, not silent.
3. **Route policy fail-closed**: without an APPROVED `sipanel.cost.recognition.policy` for the route, events are `policy_missing` / `unpolicied` and sum nothing (test_policy_fail_closed_and_pt29_unallocated).
4. **Reversals**: refunds and returned moves are negative events linked by `reversal_of_id` to the original; a second refresh never duplicates (test_pt19).
5. **Separate measures**: baseline (accepted sealed `eligible_cost_total`, immutable), forecast (working revision), commitment, recognised cost, recognised revenue, unallocated, completeness — columns of `sipanel.scope.variance`; never mixed.

## Route table (terminal vs excluded), as implemented in `sipanel_scope_costing/models/projection.py`

| Route | Terminal (recognized/included) | Excluded (stored, amount 0) |
|---|---|---|
| shared_stock | done outgoing `stock.move` linked by target, `value` field | receipts, internal transfers (operational), PO line (commitment) |
| direct_purchase / equipment_service | posted vendor bill line on the linked PO line (refund negative, reversal_of) | PO line commitment, receipt moves |
| mfg_material | done outgoing move of the MO product (issue to project) | raw moves (wip), workorder analytic lines (wip), finished move when the issue exists |
| site_labour | timesheet `amount` (SV-17) on the linked project/task; zero cost flagged `cost_source_zero` | unvalidated timesheets (when a validation field exists) |
| return_credit | linked negative event | — |
| freight_landed | none (deferred) | — |

## Reconciliation result

**NOT EXECUTED.** The written test `test_pt16_pt21_reconciliation` asserts: one key per source; raw MO moves absent from included; material = gutter issue value + 850 + 340 + 17 + 220; equipment 450; labour 270; revenue 12000; variance view equals the event sums; contingency has no event.
