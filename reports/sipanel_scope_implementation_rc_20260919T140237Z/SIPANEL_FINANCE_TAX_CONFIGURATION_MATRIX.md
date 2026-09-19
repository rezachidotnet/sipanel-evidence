Run sipanel_scope_implementation_rc_20260919T140237Z · Verdict: BLOCKED_NOT_ISOLATED · Status: DESIGN-LEVEL — NOT RUNTIME VALIDATED — no module was written, installed or tested in this run.

# SIPANEL — Finance / Tax Configuration Matrix (design-level)

Baseline: Master v0.12 §C5, §C8 (Actual Cost recognition matrix), `SIPANEL_FINANCE_BQ04_RECOGNIZED_COST_DECISION_PACK_v0.12.md`, Readiness v1.0 §5 and §7, FROZEN C0-D08, C0-D11, C0-D12. Provisional profile: BQ-02=B joint Finance+Sales (later unsigned instruction; worksheet selected A), BQ-03=A, BQ-04 one terminal recognised event per economic cost (Finance answers MISSING_INPUT), BQ-06=A with visible UNALLOCATED, BQ-08=B, BQ-09=A company-currency-only; AM-03-R1 applied subject to Finance route tests; AM-05 excluded. This is not accounting advice; nothing here changes Production configuration.

## A. Verified installed finance facts

Facts marked EVIDENCE-DATED come from the checksum-verified v0.10 read-only bundle (2026-09-19) because this run's own refresh probes were refused by the permission classifier; facts marked SV-xx were verified from installed source in this run (`evidence/EV-03_INSTALLED_SOURCE_VERIFICATION.md`).

| # | Fact | Source | Design consequence |
|---|---|---|---|
| F-01 | Company: periodic inventory valuation, standard cost, Anglo-Saxon accounting | EVIDENCE-DATED | PO is commitment; COGS/analytic at consumption/invoice differ from receipt; AM-03-R1 |
| F-02 | `analytic_costs` disabled on all 13 inspected stock operation types | EVIDENCE-DATED | no consumption analytic events exist today; selection of carriers is configuration (B-03) |
| F-03 | Only the Project analytic plan exists (3 accounts); no applicability rows; no users in Analytic Accounting group | EVIDENCE-DATED; SV-16 (plan `default_applicability`, `applicability_ids`) | System/Activity plans must be created and made applicable before any actual-cost pilot |
| F-04 | `res_currency_rate` is empty; conversion falls back to 1.0 via `COALESCE(rate, fallback, 1.0)` | EVIDENCE-DATED; SV-12 (`res_currency.py:120-155`) | foreign-currency quotations must fail closed (BQ-09, B-06) |
| F-05 | Inspected employee hourly costs are zero; timesheet cost = `-unit_amount × hourly_cost` | EVIDENCE-DATED; SV-17 | labour actual would be zero; governed hourly cost is a prerequisite for site/MFG labour routes |
| F-06 | `stock_landed_costs` not installed | EVIDENCE-DATED; EV-04 | landed cost route DEFERRED |
| F-07 | Decimal precision `Product Unit` = 0 and `Product Price` = 0; `cm` UoM inactive; `uom.rounding` is computed globally from `Product Unit` | EVIDENCE-DATED; SV-10, SV-11 | UoM precision change is Production-wide; Price precision (IRR) unchanged without Finance |
| F-08 | `sale_margin` not installed; `purchase_price` absent on sale lines | EVIDENCE-DATED; EV-04 | estimated margin stays custom/internal (C5-D04); no install |
| F-09 | Analytic carriers: `analytic.mixin` on `purchase.order.line`, `hr.expense`, `sale.order.line`, `mrp.workcenter`; `stock.move` writes analytic lines only when distribution non-empty; `mrp.workorder` MO/WC analytic lines; `mrp.production.project_id`; `project.project.account_id` | SV-15 | recognised-cost projection reads these; no custom `stock.move` field |
| F-10 | Valuation data: field `stock.move.value` (waterfall `_get_value`) and model `product.value`; no `stock.valuation.layer` | SV-09 (IF-01) | material cost events read `stock.move.value`; manual cost history from `product.value` |
| F-11 | `stock.reference` links sale orders (`stock_reference_ids`) and MOs (`reference_ids`) | SV-08 | commitment/operational trace through references |

## B. Configuration matrix

"Production change?" is **NEVER in this run** for every row; the column states whether the item would eventually be a Production configuration change requiring its own approval.

| # | Item | Current (evidence-dated) | Required for MVP | Approver | Clone test | Production change? |
|---|---|---|---|---|---|---|
| CF-A1 | Analytic plan **System** | absent | create plan; `default_applicability` = optional company-wide, mandatory on MO/consumption carriers where selected; accounts = the frozen System reference list (C1-D03) | Finance + Operations | PT-16, PT-17, PT-21 | yes, later |
| CF-A2 | Analytic plan **Activity** | absent | create plan; accounts incl. MFG, INS, EQP, GEN, PRO; PRO not applied to shared-stock purchases (C0-D11) | Finance | PT-16…PT-21 | yes, later |
| CF-A3 | `sipanel_scope.system_plan_id` / `activity_plan_id` settings | n/a | point to CF-A1/CF-A2 plans before first release | Administration (config) | install test | yes, later |
| CF-A4 | Operation types `analytic_costs` | disabled on all 13 | enable only on the operation type(s) chosen as the shared-stock consumption carrier (e.g. site consumption/internal issue); receipts and central→site transfers stay disabled | Finance (BQ-04 shared-stock route) | PT-16 | yes, later |
| CF-A5 | Analytic Accounting group membership | no users | grant to Finance role holder(s) only | Finance | PT-23 | yes, later |
| CF-B1 | Employee `hourly_cost` | zero | governed non-zero values for employees whose timesheets feed site/MFG labour; owner and effective date recorded; values TBE | Finance/HR | PT-20 | yes, later |
| CF-B2 | Workcenter cost per hour / `analytic_distribution` | not evidenced | set only if Finance selects workorder cost as MFG labour source; otherwise leave | Finance | PT-17 | yes, later |
| CF-C1 | Decimal precision `Product Unit` | 0 | evaluate 2 (shipped default) or value TBE; **global** effect on all quantities, pickings, MOs, invoices | Operations + Finance | full regression: existing pickings/MO/invoices on clone (B-01) | yes, later, Production-wide |
| CF-C2 | Decimal precision `Product Price` | 0 | **unchanged** unless Finance explicitly approves (IRR presentation) | Finance | PT-27 | not without Finance |
| CF-C3 | UoM `cm` | inactive | activate with reference to `m` (factor per installed `relative_factor` model) if quotes need cm; Recipe engine enforces family/rounding | Steward + Operations | PT-03 | yes, later |
| CF-C4 | Per-line rounding increment/mode | n/a (native has none per UoM) | recipe-line fields per dictionary §1.3 | Steward | PT-03, PT-26 | no (module data) |
| CF-D1 | Quotation currency | company currency; no rates | `sipanel_scope.company_currency_only = True`; Send/Confirm blocked for scoped quotes in other currency; no rate rows created | Finance | PT-25 (negative: block) | none for MVP |
| CF-D2 | Governed FX (post-MVP) | n/a | before enabling: rate source, date policy, missing-rate block, no silent 1.0 | Finance | PT-25 (positive) | yes, later |
| CF-E1 | Taxes, fiscal positions, tax-included flags | native, unchanged | untouched; estimate uses untaxed subtotal after discount (R) | none | PT-27 regression | none |
| CF-E2 | Pricelists / discounts | native | untouched; Apply Price writes `price_unit` only after preview; native recompute preserved | none | PT-27, PT-31 | none |
| CF-F1 | Anchor product invoice policy / type | per product | mapping reviewed at version release: NATIVE_LINE_OWNER products keep native policy; COMPONENT_BRIDGE_OWNER service anchors: `service_tracking` in {no, project_only}, invoice policy per Finance (order vs delivered) | Steward + Finance | PT-13, PT-31 | product data change, later |
| CF-F2 | Provisional settlement | n/a | BQ-03=A: adjustment only through accepted change order/new revision; no automatic invoice of actual; provisional marker and basis in customer text | Sales + Finance + legal | PT-22 | none |
| CF-F3 | Commercial waiver | n/a | BQ-02=B: joint Sales-manager + Finance approval with reason before Send when negative/below-threshold margin or missing estimate; thresholds TBE | Business owner | PT-27 (negative margin path) | none |
| CF-G1 | Landed cost / freight capitalization | module absent | DEFERRED from MVP; freight bills recognised only as EQUIPMENT_SERVICE-type direct cost if Finance selects, else excluded | Finance | PT-18 (partial) | none in MVP |
| CF-G2 | Returns / credits reversal mapping | native reversals | policy row `RETURN_CREDIT`: linked reversal of the original selected event, exactly once; never a second positive event, never deletion | Finance | PT-19 | none |
| CF-G3 | Recognition policy approval | n/a | `sipanel.cost.recognition.policy` rows APPROVED by `group_scope_finance` for every enabled route before Slice E is enabled | Finance | PT-16…PT-21 | none (module data) |
| CF-H1 | Pre-contract actual cost | n/a | BQ-08=B: overhead; AM-05 excluded; Recipe never creates pre-sales actuals | Management/Finance | none | none |
| CF-H2 | Mail/SMS/payment on clone | live on Production | neutralized before clone startup (sink mail server, crons off, payment providers disabled, SMS/WhatsApp gateways disabled) | Infrastructure | clone preflight | none |

## C. BQ-04 route matrix (AM-03-R1) — Finance answer MISSING_INPUT

Governing rule: for each economic cost exactly one terminal recognised event; commitments and operational quantities are separate columns and excluded from the recognised sum; returns/credits reverse the selected original event once. Model/field names cite installed anchors; none is a runtime attestation.

| Route | Commitment evidence (column only) | Operational qty (column only) | Candidate terminal recognised event (model / field, anchor) | Must exclude | Finance answer | PT tests |
|---|---|---|---|---|---|---|
| Shared-stock material | `purchase.order.line` (price_subtotal, state) via `stock.reference` (SV-08) | receipts and internal transfers: `stock.move.quantity` (qty_kind RECEIVED) | `account.analytic.line` created by `stock.move._prepare_analytic_lines` at `_action_done` on the selected consumption operation type with `analytic_costs` enabled (SV-15); amount from `stock.move.value` (SV-09) | PO amount; replenishment receipt value; central→site transfer; vendor bill for the same consumed value | **PENDING (MISSING_INPUT)** | PT-16, PT-19, PT-21 |
| Direct project purchase / dropship | `purchase.order.line` with `analytic_distribution` (SV-15) | direct delivery `stock.move` (dropship) qty | one of: posted vendor bill `account.move.line` (analytic distribution → `account.analytic.line`) **or** delivered `stock.move.value` — Finance selects exactly one | PO + bill + stock value summed | **PENDING** | PT-18, PT-19 |
| Manufacturing material | MO planned components (`mrp.production.move_raw_ids`) | raw consumed qty / finished produced qty (distinct kinds) | either raw-consumption analytic lines (`move_raw_ids.analytic_account_line_ids`, `mrp_account/models/mrp_production.py:31`, project via `mrp.production.project_id`) **or** finished-goods issue value (`stock.move.value` of the delivery/site issue) — mutually exclusive | raw AAL + finished issue full value together | **PENDING** | PT-17, PT-21 |
| Manufacturing labour | workorder planned hours | actual hours (`mrp.workorder`) | either `mrp.workorder.wc_analytic_account_line_ids` (SV-15) **or** `account.analytic.line` from timesheet (`hr_timesheet.py:468-469`) — one source | workorder + timesheet + payroll | **PENDING** | PT-17, PT-20 |
| Site labour | task assignment (no cost) | approved timesheet hours | `account.analytic.line` (timesheet) amount = `-unit_amount × employee.hourly_cost` (SV-17) after CF-B1 | estimated hours; payroll duplicate | **PENDING** | PT-20, PT-21 |
| Equipment / service | `purchase.order.line` service commitment | service completion units | posted vendor bill line (`account.move.line` with analytic) **or** approved `hr.expense` (analytic.mixin, SV-15) — selected per process | PO estimate + bill + expense | **PENDING** | PT-18, PT-20 |
| Freight / landed cost | PO commitment | optional logistic qty | NONE in MVP (module absent, F-06); if later capitalized it flows through material consumption | fee expensed and later material value duplicated | DEFERRED | PT-18 (partial) |
| Returns / credits | reduces commitment | returned qty (qty_kind RETURNED) | linked reversal event `reversal_of_id` of the original selected event; credit note `account.move.line` reversal when the terminal event was a bill | deleting old event; two reversals | **PENDING** | PT-19 |
| Revenue (for margin only) | quotation total (not revenue) | invoiced qty | posted customer invoice lines linked to anchor lines minus credit notes | quote subtotal; gross tax totals | **PENDING** | PT-21, PT-27 |

Required Finance choices (BQ-04 pack §"Required Finance choices"): (1) one event per enabled route; (2) `wip_reporting` TERMINAL_ONLY or WIP_SEPARATE; (3) overhead inclusion categories (thresholds TBE); (4) return/credit mapping approval; (5) BQ-09 company-currency-only confirmation. Until signed, `sipanel_scope_costing` computes no recognised events; all native cost sources are shown as UNPOLICIED alongside UNALLOCATED (BQ-06).

## D. Estimated-side tax and posting rules

- Estimated cost is built from `standard_price` snapshots (company-dependent, per product UoM, company currency — v0.10 evidence) or manual estimates; **recoverable tax is excluded from estimated cost**; non-recoverable or capitalized tax treatment follows Finance instruction, never operator guess (Master §C5).
- Estimated margin uses R = native untaxed subtotal after discount converted with the saved estimate FX (1.0 in MVP because quote currency equals company currency by construction, not by fallback); customer taxes are outside R (C5-D02, PT-27).
- **Nothing is posted from an estimate**: no journal entry, no analytic line, no valuation adjustment, no timesheet, no expense (C0-D11, C0-D12). `sipanel_scope_costing` only reads native events and writes its own sidecar projection/allocation records.
- Refreshing product cost never rewrites a sealed baseline; a new forecast revision is separate data (C5-D01).
- Actual recognised revenue = posted customer revenue events minus credits; never the quotation subtotal.

## E. Regression domains required before any Production enablement (from Readiness §9/§10)

taxes/discounts/fiscal positions on ordinary and scoped quotes (PT-27, PT-31); invoicing policies of anchor products; Product UoM precision impact on existing pickings/MOs/invoices (CF-C1); currency block (CF-D1); route procurement and kit explosion (PT-13); recognised-cost reconciliation against ledger (PT-21); returns/credits (PT-19). All BLOCKED in this run.

## Status

Design-level configuration specification. No configuration was changed on any database; BQ-04 Finance signature is MISSING_INPUT; every clone test is BLOCKED (BLOCKED_NOT_ISOLATED).
