Run sipanel_scope_production_implementation_20260919T164530Z · Status: INSTALLED ON sipanel AND RUNTIME-TESTED (49/49 tagged tests green in run #5, C9 pilot smoke green, upgrade green) · runtime source commit 99dd874 · reports/evidence commit 13676e4 · bundle commit cbc246f · reconciled 2026-09-19 (documentation only)

# SIPANEL — Test Data Inventory (reconciled with the final runtime state)

## A. Transactional test records: **0 persisted**

All automated tests (runs #1–#5, targeted runs 3b/4b, pilot smoke) executed under Odoo's test runner; every test transaction was rolled back. The records below were therefore created and discarded inside each run and do **not** exist in `sipanel` (batch identifier `SIPANEL-PT-CORE`, every name prefixed `SIPANEL-PT`):

| Kind | Names / pattern | Created by |
|---|---|---|
| Users | sipanel_pt_steward, _estimator, _plain, _sales, _sales_mgr, _finance, _exec, _fin_rec, _portal, _stranger, _other_co | tests/common.py of each module |
| Partners | SIPANEL-PT Synthetic Customer, SIPANEL-PT Synthetic Vendor (no e-mail, no phone) | sale_scope / execution common |
| Products | anchor, Gutter, Bracket, Screw, Sealant cartridge, Installation labour, Base crane service, Coil, Dozen product, free item | core / sale / execution tests |
| Analytic plans / accounts | SIPANEL-PT System / Activity, System A, MFG, INS, EQP, GEN | core common |
| UoM / families | SIPANEL-PT Dozen; family tags for m, cm, unit, hour | tests |
| Scope masters | SIPANEL-PT-GUTTER (V1/V2), -OTHER, -EMPTY, -GUTTER-2 | tests |
| Quotations / orders / pickings / RFQs / MO / invoices / timesheets / expenses | origin SIPANEL-PT-CORE / -ORDINARY / -PILOT; posted inside the rolled-back transaction only, never transmitted | sale / execution / costing tests |
| Company | SIPANEL-PT Other Co | security test |

Outbound integrations: no mail/SMS/portal invitation was sent (test-mode notifications for synthetic users appear in the logs as "no mail server matches … fallback"; nothing left the host); nothing was submitted to the Iranian taxpayer system; no external supplier order was sent (RFQs stayed draft and were rolled back). Real contacts and telephone numbers were neither read for test data nor modified.

## B. Synthetic fixture (`sipanel_scope_demo`, installed for the smoke run only, then uninstalled)

| Record | State now |
|---|---|
| partner "SIPANEL-PT Synthetic Customer", project "SIPANEL-PT Gutter site", plans "SIPANEL-PT System/Activity" + 5 accounts, 6 component products, recipe lines, version V1 xml records | deleted by the uninstall |
| product 1083 "SIPANEL-PT Gutter run (anchor)" | **archived** (active=False) — protected by a restrict FK from the released version |
| scope master 91 "SIPANEL-PT-GUTTER" with released version 1 | **archived** (active=False) — the module's own immutability rule forbids deleting a released master; it cannot be selected for new quotations |
| 1 audit event (`release` of the fixture version) | **retained** — audit events are append-only by design |

## C. Persistent operational configuration (intended, management-approved)

| Record | Value |
|---|---|
| `account.analytic.plan` | 80 "SIPANEL System", 81 "SIPANEL Activity" |
| `stock.picking.type` / `stock.location` | 91 "SIPANEL Site Issue" (internal, WH/Stock → "SIPANEL Site", usage customer) |
| `project.project` | 55 "SIPANEL Execution (default)" |
| `sipanel.uom.family` | 14 rows (length, count, time, mass, volume, area) |
| `sipanel.cost.recognition.policy` | 9 rows, state APPROVED (source recorded), 9 `policy_approve` audit events |
| `ir.config_parameter` | sipanel_scope.system_plan_id=80, activity_plan_id=81, stock_issue_picking_type_id=91, default_project_id=55, release_retry_count=3, company_currency_only=True |
| `res.users` 2 (Taleghani) | 8 SIPANEL groups added |
| `sipanel.execution.owner.rule` | 5 default rows (module data) |
| Modules | 4 installed (196 → 200); `sipanel_scope_demo` uninstalled |

No attachment, quotation, order, invoice or stock document created by tests persisted.
