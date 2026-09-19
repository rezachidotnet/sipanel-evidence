Run sipanel_scope_production_implementation_20260919T164530Z · Status: INSTALLED ON sipanel AND RUNTIME-TESTED (49/49 tagged tests green in run #5, C9 pilot smoke green, upgrade green) — see SIPANEL_TEST_RESULTS_PT01_PT32.md and evidence/. Carried forward from run 20260919T145639Z where unchanged; status lines updated.

# SIPANEL — Test Data Inventory

## Records created in database `sipanel`: **0** (no database write occurred).

## Records the written tests would create (all inside the test transaction, rolled back by Odoo's test runner; batch identifier `SIPANEL-PT-CORE`, every name prefixed `SIPANEL-PT`)

| Kind | Names / pattern | Created by |
|---|---|---|
| Users | sipanel_pt_steward, sipanel_pt_estimator, sipanel_pt_plain, sipanel_pt_sales, sipanel_pt_sales_mgr, sipanel_pt_finance, sipanel_pt_exec, sipanel_pt_fin_rec, sipanel_pt_portal, sipanel_pt_stranger, sipanel_pt_other_co | tests/common.py of each module |
| Partners | SIPANEL-PT Synthetic Customer, SIPANEL-PT Synthetic Vendor (no e-mail, no phone) | sale_scope / execution common |
| Products | SIPANEL-PT Gutter run (anchor), Gutter, Bracket, Screw, Sealant cartridge, Installation labour, Base crane service, Coil, Dozen product, free item | core / sale / execution tests |
| Analytic plans / accounts | SIPANEL-PT System, SIPANEL-PT Activity, System A, MFG, INS, EQP, GEN | core common |
| UoM | SIPANEL-PT Dozen; family tags for m, cm, unit, hour | tests |
| Scope masters | SIPANEL-PT-GUTTER (V1/V2), SIPANEL-PT-OTHER, SIPANEL-PT-EMPTY, SIPANEL-PT-GUTTER-2 | tests |
| Quotations / orders | origin SIPANEL-PT-CORE / SIPANEL-PT-ORDINARY / SIPANEL-PT-PILOT | tests |
| Stock | picking type "SIPANEL-PT Site issue", location "SIPANEL-PT Site", quants for 4 products, draft pickings/moves | execution / costing tests |
| Purchase / MRP / Project | draft RFQs to the synthetic vendor, BoM for Gutter, MO, project "SIPANEL-PT Project", employee "SIPANEL-PT Installer" | execution / costing tests |
| Accounting | vendor bill / refund on synthetic RFQ lines, customer invoice on the synthetic order — posted inside the rolled-back test transaction only; never transmitted | costing tests |
| Company | SIPANEL-PT Other Co (isolation test) | security test |

The demo module `sipanel_scope_demo` (test only) would create persistent fixture records prefixed SIPANEL-PT (products, plans, partner, project, master V1) — install it only on a test run and archive/remove afterwards; it must never be installed as a Production dependency.

Outbound integrations: tests send no mail/SMS/portal invitation (test runner mail is queued and rolled back); nothing is submitted to the Iranian taxpayer system; no external supplier order is sent (RFQs stay draft).

## Addendum — what actually persisted in `sipanel` after this run

| Kind | Persisted | Note |
|---|---|---|
| Test-transaction records (users, partners, products, orders, pickings, POs, MOs, invoices, timesheets…) | **0** | Odoo test runner rolled every test transaction back (`--test-enable`) |
| Demo fixture (`sipanel_scope_demo`) | removed by uninstall, except: product 1083 "SIPANEL-PT Gutter run (anchor)" (archived) and scope master 91 "SIPANEL-PT-GUTTER" with released version 1 (archived) — both protected by restrict FKs and the module's own immutability rule | archived, inactive; 1 audit event of the fixture release retained (append-only) |
| Configuration records (approved) | analytic plans 80/81, picking type 91 + location "SIPANEL Site", project 55, 14 `sipanel.uom.family` rows, 9 approved policies, 6 `ir.config_parameter` keys, 8 group memberships for user 2 | intended operational configuration |
| Audit events from configuration | 9 `policy_approve` events | append-only |
| Attachments | none added (test artifacts rolled back) | — |
