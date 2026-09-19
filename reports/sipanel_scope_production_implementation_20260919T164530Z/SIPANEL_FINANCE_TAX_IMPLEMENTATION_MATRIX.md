Run sipanel_scope_production_implementation_20260919T164530Z · Status: INSTALLED ON sipanel AND RUNTIME-TESTED (49/49 tagged tests green in run #5, C9 pilot smoke green, upgrade green) — see SIPANEL_TEST_RESULTS_PT01_PT32.md and evidence/. Carried forward from run 20260919T145639Z where unchanged; status lines updated.

# SIPANEL — Finance / Tax Implementation Matrix

| Topic | Implementation | Validation status |
|---|---|---|
| Recognition routes (BQ-04, AM-03-R1) | nine `sipanel.cost.recognition.policy` rows shipped **DRAFT** (`data/recognition_policies.xml`); Finance approves with source "management authorization 2026-09-19"; approval user must hold `group_scope_finance`; approved rows immutable; new version supersedes | not approved (no DB) |
| Terminal event sources | `stock.move.value` (IF-01), posted `account.move.line` on PO line, timesheet `account.analytic.line.amount` (SV-17), `hr.expense.total_amount` | not executed |
| Freight / landed cost | DEFERRED, policy `terminal_event_model='none'`; `stock_landed_costs` not installed | — |
| Company-owned equipment | policy row present (allocation source); no automatic projection candidate in MVP (manual allocation by Finance with reason) | — |
| Returns / credits | negative events linked via `reversal_of_id`; historical records never deleted | not executed |
| Analytic attribution (C0-D11, SV-15) | BUY_DIRECT/EQUIPMENT_SERVICE PO lines get `analytic_distribution` = Project account + System + Activity; MO gets `project_id` (project_mrp); stock issue carries a `stock.reference` | not executed |
| Taxes / discount / pricelist (C0-D01) | untouched: extension writes only `product_uom_qty` (governed) and `price_unit` (explicit Apply Price); margin uses native `price_subtotal` (untaxed after discount) | test_pt27 written |
| Currency (BQ-09) | company currency only; `fx_rate=1.0`, `fx_source='company_currency'`; foreign currency blocked at add/send/confirm/pricelist change | test_pt25 written |
| Invoicing | native per anchor line policy; revenue events = posted customer invoice lines linked to the anchor minus credits | not executed |
| Fiscal invoices / Iranian taxpayer system | never touched by the modules; test discipline forbids posting externally transmitted fiscal invoices | — |
| Product Unit precision (B-01), `cm` inactive | not changed by data files; runbook regression item | — |
| Statutory tax / accounting validation | **REQUIRED before live commercial use**; this matrix is derived from a management authorization, not a professional tax opinion | outstanding |
