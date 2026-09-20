# SIPANEL Temporary Data Cleanup Report (STEP 1C, run 20260920T084541Z)

Prefix: `SIPANEL-PDF-LAYOUT-CHECK-20260920T084541Z`. Scripts: `evidence/scripts/create_1c.py`, `render_after_1c.py`, `cleanup_1c.py`; ids in `evidence/validation_record_ids.json`.

## Created

| Model | Ids | Notes |
|---|---|---|
| res.partner | 509 | synthetic Persian customer, `lang=fa_IR`, internal-note marker |
| sale.order | 368 `SI-26/368` | draft only; client ref/origin = prefix; long terms note; portal access token generated for the HTTP render (never printed, staged file deleted) |
| sale.order.line | 11 | 2 scope anchors, 1 optional section, 8 note lines |
| sipanel.quote.scope / revision / component | 271, 272 / 2 working revisions / 14 components | from released version 115 (reused, unchanged) |
| mail.message | internal note marker + native "Quotation viewed" notifications | on order 368 |
| sipanel.scope.audit.event | 2 (`add_scope`) | audit trail |

Reused without change: version 115 (`released`), archived master scope 95, archived products 1113–1120 (referenced by the version), analytic accounts 249/250.

## Deleted (all safe: draft order, working revisions, no artifacts, no sealed data)

| Record | Result |
|---|---|
| quote scopes 271, 272 | deleted (D-04 workaround: `current_revision_id` cleared first, then components → revisions → scopes) |
| 14 components, 2 revisions | deleted |
| 11 order lines, order `SI-26/368` | deleted (chatter messages cascade-deleted with the order) |
| partner 509 | deleted (no remaining references) |

## Retained

| Record | Why |
|---|---|
| 2 `sipanel.scope.audit.event` rows (`add_scope` for scopes 271/272, now dangling `res_id`) | append-only audit trail; never deleted by policy |
| version 115 / master 95 / products / analytic accounts from STEP 1A | pre-existing archived validation master, restrict-protected; unchanged |

Nothing was archived in this run.

## Side-effect verification (after cleanup, committed state)

| Check | Value |
|---|---|
| `mail.mail` created since 08:45 UTC | 0 |
| stock.picking / mrp.production / purchase.order with origin `SI-26/368` | 0 / 0 / 0 |
| account.move (invoice origin `SI-26/368`) | 0 |
| project.task (sale order 368) | 0 |
| sipanel.execution.demand / batch (order 368) | 0 / 0 |
| users created since 08:45 UTC | 0 |
| records still carrying the prefix (`sale.order`, `sipanel.quote.scope`, `res.partner`, artifacts) | 0 / 0 / 0 / 0 |
| `report.url` | `http://127.0.0.1:8072` |
| website languages | `en_US`, `fa_IR` |

## Other state changes on `sipanel` in this run

| Change | Detail |
|---|---|
| module upgrade | `sale_shamsi_report` (view `sale_shamsi_report.report_saleorder_document_shamsi`, id 3372, now contains `overflow: hidden` and no 300 px spacer) |
| recovery point | `/opt/odoo/backups/sipanel-pre-layout-fix-20260920T084541Z` (verified) |
| container | no restart |
| Shamsi source | commit `b17fbb5` on `develop/shamsi-date-core` (local) |
