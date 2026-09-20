# SIPANEL Temporary Data Cleanup Report (STEP 1D, run 20260920T105500Z)

## 1. What was created

All synthetic, all on database `sipanel`, all prefixed
`SIPANEL-PAGINATION-CHECK-20260920T105500Z` in `client_order_ref` / `origin` /
partner name. Every order stayed in **draft**; none was confirmed, sent or emailed.

| Model | Count | Detail |
|---|---|---|
| `sale.order` | 10 | SI-26/385 … SI-26/394 (shapes A, B, C, D, E1–E6) |
| `sale.order.line` | 37 | anchor lines, note lines, one optional section line |
| `sipanel.quote.scope` | 11 | 10 base + 1 optional (D_SECTIONS) |
| `sipanel.quote.scope.revision` | 11 | all left in `working` state, never sealed |
| `sipanel.quote.scope.component` | 77 | generated from released version 115 |
| `res.partner` | 1 | id 531, synthetic Persian customer |
| portal access tokens | 10 | generated on the above orders for the portal fetch |

Reused, never modified: released scope version **115** and its master scope, tax 287,
UoM `uom.product_uom_meter`, user 2.

## 2. What was removed

`evidence/scripts/cleanup_1d.py`, committed. Guards before deleting: every order must
be `draft`, every `client_order_ref` must carry the run prefix, every revision must be
`working`, and no revision may have artifacts.

```json
{"deleted": {"orders": 10, "order_lines": 37, "scopes": 11, "revisions": 11,
             "components": 77, "partner": 531,
             "order_names": ["SI-26/385", …, "SI-26/394"]},
 "archived": {}, "errors": {}}
```

Deletion order works around **D-04** (`sipanel.quote.scope.unlink()` on a working
scope raises `MissingError`): clear `current_revision_id`, flush, then components →
revisions → scopes → anchor lines → orders.

**Leftovers after cleanup — all zero:**

| Model | Remaining with the run prefix |
|---|---|
| `sale.order` | 0 |
| `sale.order.line` | 0 |
| `sipanel.quote.scope` | 0 |
| `sipanel.quote.scope.revision` | 0 |
| `sipanel.quote.scope.artifact` | 0 |
| `res.partner` (incl. archived) | 0 |

## 3. Side effects — none

Checked after cleanup for anything created since 2026-09-20 10:49 UTC or linked to
the ten order names:

| Model | Count |
|---|---|
| `mail.mail` created during the run | 0 |
| `stock.picking` | 0 |
| `mrp.production` | 0 |
| `purchase.order` | 0 |
| `account.move` | 0 |
| `project.task` | 0 |
| `sipanel.execution.demand` | 0 |
| `sipanel.execution.batch` | 0 |
| `res.users` created during the run | 0 |

No email was sent, and no procurement, invoice, picking, manufacturing, task or
execution demand was created — as required.

## 4. Configuration re-asserted after cleanup

| Setting | Value | Expected |
|---|---|---|
| `report.url` | `http://127.0.0.1:8072` | unchanged (never set to 8069) |
| website 1 languages | `['en_US', 'fa_IR']` | unchanged |
| report paperformat | `A4`, margin_top 52 mm, margin_bottom 32 mm | unchanged |
| scope version 115 | `released` | unchanged |

## 5. Retained audit evidence

**In the database: nothing from this run.** The rendered PDFs, the page PNGs, the
contact sheets, the geometry JSON and the logs in this report directory are the audit
evidence; no operational record needs to persist for them to be re-checked.

Records retained by **earlier** runs are untouched and were verified still present:

| Record | Run | State |
|---|---|---|
| `sale.order` 312 (SI-26/312, cancelled) and its archived scopes 217/218, sealed revisions 237/238, artifacts 255–258, archived master scope 95 / version 115, archived products 1113–1120, partner 426, analytic 249/250 | 20260920T060817Z | present, untouched |
| archived demo leftover scope 91 (`SIPANEL-PT-GUTTER`) | earlier | present, untouched |

## 6. Filesystem cleanup

| Location | Action |
|---|---|
| `odoo-sipanel:/tmp/sipanel_1d`, `/tmp/l02_*`, `/tmp/wk_*`, `/tmp/rule_replay.py`, `/tmp/contact_sheet.py` | removed |
| `odoo-sipanel:/tmp/report.tmp.*.pdf` (a stale wkhtmltopdf temp file) | removed |
| `odoo-sipanel:/tmp/sipanel_val` (temp directory left by STEP 1C; its contents are already copied into the 1C report directory) | removed |
| `odoo-sipanel:/tmp/tmpli5agw7c` (temp directory from the body-only render prototype) | removed |
| `odoo-sipanel:/tmp/custom-requirements.txt`, `cyan_phase2_*.py`, `sipanel_guard_test_data` | **left alone** — predate this run |
| host scratchpad `/tmp/claude-1000/.../scratchpad` | session-scoped, not part of the deliverable |
| host `/opt/odoo/backups/sipanel-pre-multipage-20260920T104900Z` | **retained** — this run's recovery point, 110 MB |

## 7. Note on disk

`/` is at **90 % (2.8 GB free)**. Five recovery points now exist under
`/opt/odoo/backups`, ~110 MB each. Nothing was deleted; pruning the older ones is an
owner decision (R-6 in the main report).
