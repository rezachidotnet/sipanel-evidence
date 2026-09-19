Run sipanel_scope_implementation_rc_20260919T140237Z · Verdict: BLOCKED_NOT_ISOLATED · Status: no module was written, installed or tested in this run; nothing below is a PASS.

# SIPANEL — Known Limitations and Deferred Items

## (a) Run-level limitations

| Item | State |
|---|---|
| Isolation | BLOCKED_NOT_ISOLATED — execution environment is the Production host (EV-01); no clone reachable; clone creation here prohibited |
| Addon source, migrations, module tests | NOT WRITTEN |
| PT-01…PT-32 and all additional test groups | BLOCKED / NOT_RUN (0 PASS) |
| Production Release Candidate ZIP | NOT_PRODUCED — no reviewed, tested source exists to package |
| Backup/restore and rollback rehearsals | NOT_RUN |
| Design documents in this directory | design-level, derived from the v0.12 pack and read-only installed-source verification (EV-03); NOT RUNTIME VALIDATED |

## (b) Architecture-level deferred items (Master C10, Open Questions register) — outside MVP

- Vendor price automation and supplier-offer selection.
- BoM estimated-cost explosion (BoM snapshot estimate uses full product cost; actual MO is native).
- Free-form formulas, expression language, cross-Scope percentage graph, nested percentage costing.
- General workflow engine and universal BI/reporting framework.
- `stock.move` / `stock.move.line` custom analytic dimensions.
- Fourth analytic plan; independent Work Package entity.
- Rental-asset lifecycle management (crane rental is a service RFQ/expense, not a stock asset).
- Automatic provisional settlement (BQ-03 = accepted change order only).
- AM-05 / pre-contract actual cost (BQ-08 = B for MVP; Recipe never creates pre-sales actual).
- Landed cost capitalization (`stock_landed_costs` not installed — EV-04); freight/landed route deferred unless separately enabled.
- Foreign-currency quotations (BQ-09 = company-currency-only; native 1.0 fallback per SV-12 makes silent FX unsafe; block until governed rates exist).
- Scope anchors as combo children / inside combo or subsection structures (SV-06); ordinary native combos unchanged.
- Shared favorites (personal favorites only in MVP).
- Advanced custody of customer-owned goods.
- Numeric thresholds: minimum margin, stale-cost age, UI performance targets, monitoring duration — all TBE; none invented.

## (c) Open business decisions (inputs this run did not have)

| Decision | State | Effect |
|---|---|---|
| BQ-04 recognised-cost route matrix | BUSINESS_DECISION_PENDING — Finance answer column empty → **MISSING_INPUT** | Slice E recognition rows stay `POLICY_PENDING`; PT-16…PT-21 cannot be PASS; AM-03-R1 applied only "subject to Finance route tests" |
| BQ/AM batch approval (G0B exit) | unsigned; run brief supplies a provisional profile only → **MISSING_INPUT** | all design documents stay PROVISIONAL |
| BQ-02 | run brief says **B (joint Finance + Sales approval)**; worksheet v0.12 provisional selection was **A (Sales Manager waiver group)** | the run brief is the later explicit instruction and was applied as B; deviation recorded here, thresholds remain TBE |
| BQ-01 = B, BQ-03 = A, BQ-05 = A, BQ-06 = A (+UNALLOCATED), BQ-07 = A, BQ-08 = B, BQ-09 = A | applied as provisional profile | unchanged from worksheet |
| AM-01-R2, AM-02, AM-04 | applied | no FROZEN text altered |
| AM-03-R1 | applied subject to Finance route tests | see BQ-04 |
| AM-05 | deferred, excluded from MVP | — |
| Build authorization naming repo + clone (G1) | **MISSING_INPUT** | no clone identity exists |

## (d) Installed-fact corrections found this run (EV-03)

| ID | Correction | FROZEN impact |
|---|---|---|
| IF-01 | `stock.move.value` is the Monetary **field** `value` on `stock.move` (`stock_account/models/stock_move.py:24`, `_get_value` :340-500), not a model; `product.value` is a model; no `stock.valuation.layer` | none — wording clarified |
| IF-02 | `is_optional` and the portal endpoint `/my/orders/<id>/update_line_dict` are defined in `sale_management` (SV-02/SV-03), not `sale` | none — `sipanel_sale_scope` depends on `sale_management` |
| IF-03 | `_check_line_unlink`: sections and notes can always be deleted, even on confirmed orders (SV-05) | none — confirms AM-01-R2 / B-05 guard necessity |

## (e) Implementation blockers B-01…B-10 — state after this run

| ID | Blocker | State |
|---|---|---|
| B-01 | UoM precision / inactive `cm` / dimensional guard and line rounding | OPEN — design only; global precision test requires clone (SV-10/11) |
| B-02 | AM-01-R2 / AM-02 wording and legal combination table | OPEN — applied provisionally per run brief; unsigned |
| B-03 | System/Activity analytic plans, applicability, groups, operation types | OPEN — configuration steps in Runbook C.8; EVIDENCE-DATED only Project plan exists |
| B-04 | Finance-signed recognised-cost matrix (BQ-04) | OPEN — MISSING_INPUT |
| B-05 | seal / acceptance binding; portal `update_line_dict` guard; section mutation guard | OPEN — design only (SV-03/SV-05) |
| B-06 | company-currency-only enforcement; no silent 1.0 | OPEN — design only (SV-12) |
| B-07 | scheduled backup, restore PASS, separate clone capacity | OPEN — root cause of BLOCKED_NOT_ISOLATED |
| B-08 | dedicated roles/groups, no hard-coded administrator | OPEN — group design in Security Matrix; not configured |
| B-09 | report id 848, `external_layout_bubble` override, duplicate `commitment_date` xpath | OPEN — SV-18 confirms the custom-addon items; 848 EVIDENCE-DATED; regression requires clone |
| B-10 | close enabled-scope BQ/CF items; deferred map | OPEN — deferred map is section (b) of this file |

## (f) Segregation-of-duties limitation

The architecture defines Steward, Estimator, Sales, Execution owner, Finance, Auditor and Portal roles as separate configurable groups. At the start the business intends a single existing internal user (Taleghani, referenced by role only) to hold several of them. If one user holds Sales, Finance, Inventory, Purchase and Administration simultaneously, segregation of duties is **not** achieved: the reason-trail and audit events still record actions, but no second-person control exists for waivers (BQ-02), release, recognition policy or privileged overrides. This is an acknowledged governance limitation, not a simulated control (Master C10 "Security matrix").

## (g) Session permission note

Two read-only probes into the Production container/database (installed-source grep inside `odoo-sipanel`; aggregate configuration counts on `sipanel`) were refused by the session's permission classifier ("Production Reads"). They were not retried by other means. The affected facts (report id 848, decimal precisions, cron/mail/payment counts, analytic plan and account counts, hourly costs, currency-rate count, `cm` state) are carried forward from the 2026-09-19 v0.10 evidence bundle (checksums verified, EV-00) and are marked EVIDENCE-DATED wherever used. Installed-source facts were instead verified from files copied out of the Odoo image without starting a container (EV-03).
