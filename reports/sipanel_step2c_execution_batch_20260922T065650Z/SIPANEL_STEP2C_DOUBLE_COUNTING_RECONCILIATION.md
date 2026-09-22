# SIPANEL STEP 2C — Double-Counting Reconciliation (run 20260922T065650Z)

## 1. Global counters (whole database `sipanel`, `sudo`)

| Counter | Baseline (preflight, 07:00) | After stage 2 (3 releases) | After stage 4 (6 orders, 1 cancelled) | After cleanup |
|---|---:|---:|---:|---:|
| `purchase.order` | 7 | 8 | 10 | **7** |
| `mrp.production` | 0 | 1 | 3 | **0** |
| `stock.picking` | 13 | 15 | 19 | **13** |
| `stock.move` (done) | 10 | 10 | 10 | **10** |
| internal quant quantity | 0 | 0 | 0 | **0** |
| `sipanel.execution.batch` | 0 | 4 | 11 | 11 (8 cancelled, 3 failed) |
| `sipanel.execution.demand` | 0 | 10 | 30 | 30 (18 cancelled, 12 failed) |
| `sipanel.execution.target` | 0 | 7 | 22 | 22 |
| `mail.mail` | 36 | 36 | 36 | **36** |
| posted `account.move` | 0 | 0 | 0 | **0** |

The stage-4 partial-failure sequence on A3 (`global_counts_before` /
`…after_two_failures` / `…after_success`) shows the two failed releases adding
**0** PO / PO line / MO / picking / move / target, and the successful retry adding
exactly 1 PO, 1 PO line, 1 MO, 1 picking, 3 moves (the SIPANEL issue move plus the
MO's raw and finished moves) and 5 targets.

## 2. Per-component duplicate counts (post-fix orders)

| Order | Component | Purchase | Stock (SIPANEL) | Stock (native) | MRP | Project/Task | SIPANEL demand (live) | Cost events (source_key) | Duplicates |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A3 | bracket | 0 | 1 picking / 1 move | 0 | 0 | 0 | 1 | 1 | 0 |
| A3 | crane | 1 PO line | 0 | 0 | 0 | 0 | 1 | 1 | 0 |
| A3 | gutter | 0 | 0 | 0 | 1 MO | 0 | 1 | (MO not done → none) | 0 |
| A3 | labour | 0 | 0 | 0 | 0 | project link (no timesheet) | 1 | 0 | 0 |
| C | bracket / crane / gutter / labour | 1 / 0 / 0 / 0 | 1 / 0 / 0 / 0 | 0 | 0 / 0 / 1 / 0 | 0 / 0 / 0 / link | 1 each | — | 0 |
| B2 | bracket | 0 | 0 | 1 move | 0 | 0 | 1 (linked) | — | 0 |
| B2 | labour | 0 | 0 | 0 | 0 | 1 task (native, linked) | 1 (linked) | — | 0 |
| A (after CO-A) | bracket | 0 | 2 pickings / 2 moves (20 + 10 = accepted 30) | 0 | 0 | 0 | 2 (20 + 10) | 2 (one per move) | 0 |
| B2 (after CO-B2) | bracket | 0 | 0 | 1 live move (30; the 20-move cancelled) | 0 | 0 | 2 (20 + 10, both native links) | — | 0 |

## 3. Actual-cost projection (Estimate-to-Actual)

`sipanel.actual.projection.refresh_order` was executed inside a rolled-back
savepoint on A (before and after the amendment) and B:

* A before amendment: 2 events — `stock.move 848` (material, operational,
  excluded_duplicate, 0.0) and `purchase.order.line 164` (service, commitment,
  excluded_duplicate, 0.0); B: 0 events (task with no timesheet). No allocation
  is created for excluded events, so nothing is counted twice and nothing is
  recognised before execution.
* A after amendment: 3 events (`848`, `164`, `1131`), `idempotent = true`
  (second refresh returns the same ids), `unique_source_keys = true`.
* Each event carries project 97 / system 1317 / activity 1318, i.e. the
  dimensions of its demand.

The automated test `test_actual_cost_projection_is_idempotent_and_never_double_allocates`
covers the same properties in the suite.

## 4. Revenue side

The reconciliation of every accepted revision (`reconciliation_json.problems`)
was `[]` after each amendment (A → 1679, B2 → 1680): one live generated line per
separately-billable component on the new revision, superseded lines at
quantity 0, and a superseded line that is invoiced would be reported as a
problem instead of being rewritten (`test_invoiced_superseded_line_is_left_alone_and_flagged`).
