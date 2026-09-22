# SIPANEL STEP 2C — Project / System / Activity Propagation Trace (run 20260922T065650Z)

Dimensions of the pilot: project 97 `SIPANEL-STEP2C-… Project` (its analytic
account 1320, plan "Project" id 1), System 1317 (plan 80 "SIPANEL System"),
Activity INS 1318 and MFG 1319 (plan 81 "SIPANEL Activity"). Scope-level
`project_id` = 97 and `system_id` = 1317 on every pilot Scope; component-level
`activity_id` = 1318 (bracket, crane, labour) or 1319 (gutter).

## 1. Execution records (order A3 `SI-26/1724`, batch 261; identical pattern on A, C, B2)

| Record | Project | System | Activity | Quotation Scope | Revision | Component | Batch | Source key |
|---|---|---|---|---|---|---|---|---|
| demand 1512 (bracket, stock_issue) | 97 | 1317 | 1318 | 1547 | 1676 | occurrence `d3740a61…` | 261 | `demand_key` sha256(occurrence, `rev:1676`, `stock_issue`, `component_bridge_owner`) |
| demand 1513 (crane, equipment_service) | 97 | 1317 | 1318 | 1547 | 1676 | `8f8ca552…` | 261 | as above with `equipment_service` |
| demand 1514 (gutter, manufacture) | 97 | 1317 | **1319** | 1547 | 1676 | `7705305f…` | 261 | as above with `manufacture` |
| demand 1515 (labour) | 97 | 1317 | 1318 | 1547 | 1676 | `22a71af6…` | 261 | as above with `labour` |
| picking 786 / move 1124 (from 1512) | via demand + `stock.reference` `SIPANEL/SI-26/1724/ce7391aa` (order-level) | — | — | via target link | via demand | via demand | 261 | target link (demand 1512) |
| PO P26200 line 200 (from 1513) | `analytic_distribution` `{"1320,1317,1318": 100}` = project account + System + Activity | ✔ | ✔ | via target link | via demand | via demand | 261 | target link |
| MO 171 (from 1514) | `project_id` = 97 | — (no analytic field on `mrp.production` in Odoo 19) | — | via target link | via demand | via demand | 261 | target link |
| project 97 (linked by 1515) | itself | — | — | via target link | via demand | via demand | 261 | target link (`linked_existing`) |
| native demand 1520 → move 1130 (B2) | 97 | 1317 | 1318 | 1549 | 1678 | `76bc7f64…` | 263 | native link; the move itself belongs to Sale line 3338 → Scope 1549 / revision 1678 / component 11221 |
| delta demand 1522 (+10, A after CO-A) | 97 | 1317 | 1318 | 1280 | **1679** | `c4d8b4e4…` (same occurrence as 1123) | 264 (`amend:1679`) | sha256(occurrence, `amend:1679`, …) |
| cost events (projection, rolled back) | 97 | 1317 | 1318 | via allocation only when included | — | — | — | `source_key` = make_key(model, res_id, type, company) |

## 2. Gaps in the installed analytic configuration (stated, not fabricated)

| Carrier | Project | System | Activity | Gap |
|---|---|---|---|---|
| `sipanel.execution.demand` | field | field | field | none |
| `purchase.order.line` | project analytic account inside `analytic_distribution` | in `analytic_distribution` | in `analytic_distribution` | none — but only because project 97 has an analytic account; a project without `account_id` would carry System/Activity only |
| `stock.move` / `stock.picking` | not carried (no analytic field in Odoo 19 `stock.move`); linked through the demand and the order-level `stock.reference` | not carried | not carried | **gap**: material moves carry the dimensions only through the SIPANEL target link; the actual-cost projection re-attaches them from the demand |
| `mrp.production` | `project_id` (field exists in this installation) | not carried | not carried | **gap** for System/Activity on the MO itself; re-attached from the demand by the projection |
| `project.task` (native anchor) | via `project_id` | not carried | not carried | **gap**: timesheets on the task inherit the project account only |
| production plans 80 / 81 | — | 0 accounts | 0 accounts | **blocker for a real pilot** (OBS-2C-07): synthetic accounts had to be created for this run and were archived afterwards |

No analytic plan or account was invented for production use; the pilot's four
accounts are archived synthetic records named with the pilot prefix.
