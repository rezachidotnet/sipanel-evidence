# SIPANEL Native Owner Cancellation Boundary Report (run 20260922T083014Z)

## 1. Rule implemented (`adapters.py`)

| Target link kind | Created by | On SIPANEL cancel / reduce | `reversal_required` |
|---|---|---|---|
| `created` (bridge) | SIPANEL | draft/planned documents withdrawn: PO line qty 0 (draft/sent PO), MO cancel, move cancel, picking cancel; executed documents untouched | True only if the document is executed (done move/picking, produced MO, confirmed/received/invoiced PO line, analytic line, approved expense) |
| `native_anchor_covered` / `linked_existing` (native line, existing project/task) | native Odoo / pre-existing | **never touched**: no cancel, no quantity change, no delete; only the demand lineage (state) is updated after observing the native state | True only if the observed native document is executed; a linked project/task never |

`cancel_delta` returns immediately for an already-cancelled demand; `action_cancel_planned` skips cancelled batches and cancelled/failed demands and writes one `execution_cancel` audit row per real cancellation — repeated cancellation performs no second document action. `reduce_planned` on a demand whose targets are all native links updates only the lineage (cancel when fully reduced, `reversal_required` from the executed classification). `sale.order._action_cancel` refuses only when an executed document **created by SIPANEL** exists; native executed documents are the native line's responsibility.

## 2. Tests (`TestNativeOwnerBoundary`)

| Requirement | Test | Before | After |
|---|---|---|---|
| bridge-owned cancel withdraws SIPANEL drafts, no reversal noise | `test_bridge_owned_cancel_withdraws_sipanel_documents_and_classifies_reversal` | FAIL | PASS |
| native-owned cancel leaves move/task untouched; repeated cancel idempotent; Odoo later cancels its own delivery | `test_native_owned_cancel_leaves_native_documents_untouched` (spies `stock.move._action_cancel` from `adapters.py`) | FAIL | PASS |
| native amendment reduction never cancels/reduces a native move; one live native move; no bridge document | `test_native_amendment_reduction_never_touches_native_documents` | PASS (guard) | PASS |
| repeated cancellation idempotent (documents, states, single audit row) | `test_repeated_cancellation_is_idempotent` | FAIL | PASS |
| completed bridge target refuses plain order cancel and is classified as requiring reversal | `test_completed_bridge_target_refuses_plain_cancel_and_requires_reversal` | FAIL | PASS |
| zero duplicate stock/procurement/cost records after cancel; cost projection keys unique | `test_zero_duplicate_records_after_cancel_and_recount` | PASS (guard) | PASS |

## 3. Live evidence (`pilot_2ch_run.json`)

* Native order `SI-26/2095`: delivery move 1893 (`confirmed`, 20) and task 3148 identical before and after two `action_cancel_planned` calls (`untouched_by_sipanel = true`); demands 2506/2507 `cancelled`, `reversal_required` False; the move became `cancel` only through Odoo's own order cancellation.
* Bridge order `SI-26/2094`: SIPANEL pickings 1295 and 1296 (+ moves 1894/1895) `cancel`; project link demand 2505 `reversal_required` False; repeated cancellation left the evidence identical (`after_repeats_identical = true`, 0 documents created by cancellation).
* Duplicates: purchase orders 0, MOs 0, native moves from bridge generated lines 0, live demand keys unique.
