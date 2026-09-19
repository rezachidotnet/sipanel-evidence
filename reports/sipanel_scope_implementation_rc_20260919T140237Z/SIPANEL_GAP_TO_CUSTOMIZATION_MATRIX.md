Run sipanel_scope_implementation_rc_20260919T140237Z · Verdict: BLOCKED_NOT_ISOLATED · Status: DESIGN-LEVEL — NOT RUNTIME VALIDATED — no module was written, installed or tested in this run.

# SIPANEL — GAP to Customization Matrix

Every customization below is mapped to a documented GAP and to decision IDs. Native anchors cite `evidence/EV-03_INSTALLED_SOURCE_VERIFICATION.md` (SV-xx) or the v0.12 technical verification items (TV-xx). Status: DESIGNED = specified in `SIPANEL_TECHNICAL_DESIGN_FINAL.md`; DEFERRED = out of MVP by decision; EXCLUDED = removed by the applied business profile. No row is a runtime PASS.

| GAP-ID | Requirement (slice) | Native Odoo 19 capability (installed) | Gap | Customization (module · model/field/hook) | Decision IDs | Test IDs | Status |
|---|---|---|---|---|---|---|---|
| GAP-A01 | Scope identity independent of Product (A) | `product.template/product` only (TV-01/10) | no non-product commercial scope entity | core · `sipanel.scope` (code, company, owner, current_version_id, active) | C1-D01, C0-D01 | PT-01, PT-31 | DESIGNED |
| GAP-A02 | Versioned scope content with DRAFT/RELEASED/SUPERSEDED (A) | no native versioning of custom masters (TV-09) | lifecycle absent | core · `sipanel.scope.version.state`, `release()` with `lock_for_update` (SV-07) | C1-D02, C1-D09 | PT-02, PT-24 | DESIGNED |
| GAP-A03 | Exactly one current released version under concurrency (A) | row locks via `lock_for_update` raise `LockError` (SV-07) | no application rule | core · identity lock in `release()`; `LockError` ⇒ UserError | C1-D02 | PT-02 | DESIGNED |
| GAP-A04 | Recipe occurrences separate from BoM (A) | `mrp.bom`/`mrp.bom.line` are manufacturing structures (TV-16) | no estimation recipe | core · `sipanel.scope.recipe.line` (occurrence_key, kind, basis, rounding) | C0-D03, C0-D05, C2-D01, C2-D02 | PT-01, PT-13 | DESIGNED |
| GAP-A05 | ESTIMATE_ONLY components with owner/resolution (A) | none | placeholder governance absent | core · `kind='estimate_only'`, `estimate_owner_id`, `resolution_state`; release rule R9 | C0-D06, C2-D02 | PT-12 | DESIGNED |
| GAP-A06 | System applicability ALL / list (A) | analytic accounts under plans (SV-16) | no applicability on custom master | core · `all_systems` XOR `system_ids`; plan configured by `ir.config_parameter` | C1-D03 | PT-01 | DESIGNED |
| GAP-A07 | Dimensional UoM compatibility (A) | `uom.uom` has no category; conversion by factor chain only (SV-10) | dimension not validated | core · `sipanel.uom.family` tag + engine check before `_compute_quantity` | C1-D04, C0-D07 | PT-03, PT-26 | DESIGNED |
| GAP-A08 | Per-line rounding increment/mode (A) | one global rounding from `Product Unit` precision (SV-10/11) | no per-line rounding | core · `rounding_increment`, `rounding_mode`; raw/rounded/final qty | C2-D03 | PT-03, PT-04 | DESIGNED |
| GAP-A09 | Immutable released versions incl. import/RPC (A) | native `write` is open; `base_import` and RPC write freely | no immutability | core · `write()/unlink()` guards on version & lines (Python-level, not ACL-only) | C1-D02, C10-D03 | PT-24 | DESIGNED |
| GAP-A10 | Usage trace without leaking unauthorized documents (A) | none | — | core · `usage_count` via ACL-scoped `search_count` | C1-D08 | PT-23 | DESIGNED |
| GAP-A11 | Configurable roles, no hard-coded users (A) | `res.groups`, record rules | no scope roles | core · 9 groups + company record rules; no user in data XML | C4-D04 | PT-23, PT-24 | DESIGNED |
| GAP-A12 | Personal favorites to identity (A) | none | — | core · `sipanel.scope.favorite` resolving to current released | C4-D03 | — | DESIGNED |
| GAP-A13 | Append-only audit with before/after and reason (A) | chatter tracking (values only, no reason, editable subtypes) | structured audit absent | core · `sipanel.scope.audit.event` + chatter message | C4-D04, C10 dictionary | PT-24 | DESIGNED |
| GAP-B01 | One explicit anchor `sale.order.line` per Scope (B) | `parent_id` computed from sequence (SV-04); combo relations (SV-06) | no durable ownership | sale_scope · `sipanel.quote.scope.anchor_line_id` (unique, restrict); anchor constraints | C0-D02, AM-01-R2 | PT-01, PT-10 | DESIGNED |
| GAP-B02 | Quote Scope revisions WORKING/SENT_SEALED/ACCEPTED_SEALED (B) | `sale.order.state` and `locked` only (SV-14) | no revision model | sale_scope · `sipanel.quote.scope.revision` | C3-D01, C3-D03 | PT-02, PT-09 | DESIGNED |
| GAP-B03 | Snapshot components copied, not linked live (B) | none | — | sale_scope · `sipanel.quote.scope.component` (all values copied; product id trace only) | C0-D04, C3-D01 | PT-02 | DESIGNED |
| GAP-B04 | Quantity engine with five bases (B) | none; `product_percentage_price` NO_REUSE (SV-19, TV-23) | — | sale_scope · engine on component (`_compute_quantities`), cycle/self/cross-scope validation | C0-D07, C2-D03 | PT-05 | DESIGNED |
| GAP-B05 | Direct cost sources PRODUCT_COST / MANUAL_ESTIMATE with provenance (B) | `standard_price` company-dependent; `product.value` history model (SV-09, TV-12) | no snapshot/provenance | sale_scope · `cost_source`, `cost_product_value_id`, `cost_status`, manual user/date/reason | C0-D08, C5-D01 | PT-26, PT-28 | DESIGNED |
| GAP-B06 | Derived PERCENT_OF_COST not a purchase source (B) | none | — | sale_scope · `derived_base_amount`, no qty demand | AM-04, C2-D03 | PT-05 | DESIGNED |
| GAP-B07 | Override retention + stale detection (B) | none | — | sale_scope · `override_flag/reason/stale`, readiness drawer | C0-D07 | PT-04 | DESIGNED |
| GAP-B08 | Atomic split/move with lineage & cost conservation (B) | none | — | sale_scope · `sipanel.wizard.split.move`, `moved_from_id`, conservation assertion | C3-D04, C0-D08 | PT-06, PT-07 | DESIGNED |
| GAP-B09 | Internal margin against untaxed net price (B) | `sale_margin` not installed; `purchase_price` absent (TV-12/23) | no margin field, must not install | sale_scope · `margin_amount`, `margin_pct` on revision; group-gated | C5-D02, C5-D04 | PT-27 | DESIGNED |
| GAP-B10 | Apply Price with target margin / markup (B) | native price/pricelist/tax recompute (TV-14) | no suggestion action | sale_scope · `sipanel.wizard.apply.price` writes `price_unit` only on explicit apply | C5-D03 | PT-27 | DESIGNED |
| GAP-B11 | Joint Finance+Sales waiver for negative margin / missing estimate (B) | none | — | sale_scope · `sipanel.quote.waiver` (two approvers, reason); thresholds TBE | BQ-02=B (later instruction, unsigned), C4-D02 | PT-27 | DESIGNED |
| GAP-B12 | Generated vs final customer note, independent flags (B) | `sale.order.line.name`, note lines (TV-07) | no state model | sale_scope · `generated_note`, `final_note`, fingerprints, `note_manually_edited/stale/reviewed` | C0-D09, C7-D01 | PT-08 | DESIGNED |
| GAP-B13 | Internal data excluded from customer payload (B) | QWeb can hide but data still reachable | payload-level filtering | sale_scope · projection builds only eligible labels; internal fields `groups=` gated | C0-D09, C7-D03 | PT-23, PT-32 | DESIGNED |
| GAP-B14 | Duplicate quote = independent copy, no upgrade (B) | `sale.order.copy_data` (SV-14) | scope records not copied natively | sale_scope · `copy_data` inherit (latest revision → WORKING 1; no artifacts/keys) | C0-D04, C3-D02 | PT-09 | DESIGNED |
| GAP-B15 | Explicit Refresh Cost / Replace Recipe with diff (B) | none | — | sale_scope · two wizards with before/after preview | C3-D02 | PT-02, PT-04 | DESIGNED |
| GAP-B16 | Sealed customer artifact with hash (B) | PDF rendered at portal accept only (SV-14) | no stored sealed artifact per revision | sale_scope · `sipanel.quote.scope.artifact` (attachment, sha256, language, amounts) | C7-D04, C3-D03 | PT-32 | DESIGNED |
| GAP-B17 | Seal at Send; mismatch check at Confirm/Accept (B) | `action_quotation_send/sent`, `action_confirm`, `portal_quote_accept` hooks (SV-14) | no seal | sale_scope · inherits + controller override | C3-D03 | PT-10, PT-24 | DESIGNED |
| GAP-B18 | Company-currency-only, fail closed (B) | `_get_rates` falls back to 1.0 (SV-12) | silent wrong conversion | sale_scope · order/scope currency constraint; `fx_source='company_currency'` | BQ-09, C5-D02, B-06 | PT-25 (BLOCKED by design until FX enabled) | DESIGNED |
| GAP-B19 | Ad-hoc quote Scope without new product (B) | none | — | sale_scope · `is_adhoc` with anchor-product mapping validation; promotion to master explicit | C10 field dictionary | PT-01 | DESIGNED |
| GAP-C01 | Optional Scope = native qty-state line (C) | `is_optional` on section; qty 0 line (SV-02) | acceptance state not modelled | sale_scope · acceptance axis OFFERED/ACCEPTED/DECLINED mapped to qty; no option model | AM-01-R2, C6-D02 | PT-10 | DESIGNED |
| GAP-C02 | Governed portal qty transition bound to sealed revision (C) | `portal_quote_option_update` writes qty directly with sudo (SV-03) | ungoverned | sale_scope · controller override; `_can_be_edited_on_portal` override; revision/hash in payload | AM-01-R2, B-05 | PT-10, PT-23 | DESIGNED |
| GAP-C03 | Governed operator transition (C) | free `write` on `product_uom_qty` | — | sale_scope · `sale.order.line.write` guard + treatment transition wizard | C6-D04 | PT-10 | DESIGNED |
| GAP-C04 | Section reorder/delete cannot detach sealed Scope (C) | sections/notes always deletable (SV-05); sequence editable | — | sale_scope · `unlink`/`write` guards on `sequence`, `display_type`, `is_optional` | AM-01-R2, B-05 | PT-10 | DESIGNED |
| GAP-C05 | Six presets over orthogonal axes (C) | none | — | sale_scope · five axis fields + `preset_label`; transition wizard with preview | AM-02, C6-D01 | PT-10, PT-11 | DESIGNED |
| GAP-C06 | Provisional amount/basis and change-order-only adjustment (C) | none | — | sale_scope · `certainty=PROVISIONAL`, `provisional_amount/basis`, `change_order_ref` | BQ-03=A, C6-D03 | PT-22 | DESIGNED |
| GAP-C07 | Customer-scope items: no cost, no demand (C) | none | — | sale_scope · `responsibility=CUSTOMER` ⇒ `cost_status=not_applicable`, mode NO_ACTION | C0-D10, C6-D04 | PT-11 | DESIGNED |
| GAP-C08 | Combo-child anchors (C) | combo relations exist (SV-06) | ownership collision risk | none — constraint forbids | C1-D05, Source audit §2 | PT-31 | EXCLUDED (MVP) |
| GAP-D01 | Owner registry NATIVE_LINE_OWNER vs COMPONENT_BRIDGE_OWNER (D) | native confirm hooks per route (SV-13) | ownership implicit | execution · `sipanel.execution.owner.rule` | C1-D05, C8-D01, BQ-05 | PT-13 | DESIGNED |
| GAP-D02 | Explicit Release Execution action (D) | native confirm creates demand immediately | no separate release for bridge components | execution · `action_sipanel_release_execution`, preflight | C0-D12, C8-D01, BQ-05=A | PT-12, PT-14 | DESIGNED |
| GAP-D03 | Idempotent batch/demand/target keys (D) | none | — | execution · SQL unique keys (Master C8) | C8-D02 | PT-14 | DESIGNED |
| GAP-D04 | LockError catch + bounded retry returning existing links (D) | `SKIP LOCKED` ⇒ `LockError` (SV-07) | no retry policy | execution · retry loop, attempts from config (TBE) | C8-D02 | PT-14 | DESIGNED |
| GAP-D05 | Adapters STOCK_ISSUE / BUY_DIRECT / MANUFACTURE / LABOUR / EQUIPMENT_SERVICE / NATIVE_ANCHOR_COVERED / NO_ACTION (D) | native pickings, POs, MOs, tasks; `stock.reference` (SV-08) | no component-level creation/link | execution · `sipanel.execution.adapter` implementations + `sipanel.execution.target` | C8-D03 | PT-13, PT-15, PT-16, PT-17 | DESIGNED |
| GAP-D06 | Atomic batch failure (D) | ORM transaction/savepoint | policy absent | execution · single transaction per batch; no external side effects inside | C8-D02 | PT-15 | DESIGNED |
| GAP-D07 | Amendment / cancellation / return lineage (D) | native returns, credits, cancel | no delta model | execution · `authorized_delta_uid`, `cancel_delta()`, `reversal_required` | C0-D12, C8-D04 | PT-19, PT-22 | DESIGNED |
| GAP-D08 | Project link, never duplicate task (D) | `service_tracking` creates project/task (SV-13) | duplication risk | execution · LABOUR adapter links only; R4 forbids task-creating tracking for bridge owner | BQ-07=A, C1-D05 | PT-13, PT-20 | DESIGNED |
| GAP-D09 | Direct-purchase analytic attribution at purchase time only (D) | `analytic_distribution` on PO line (SV-15) | rule absent | execution · BUY_DIRECT sets distribution only for direct-project route | C0-D11 | PT-16, PT-18 | DESIGNED |
| GAP-E01 | Finance-signed route matrix, fail closed (E) | none | — | costing · `sipanel.cost.recognition.policy` (inactive candidates shipped) | BQ-04, AM-03-R1, B-04 | PT-16…PT-21 | DESIGNED (Finance signature MISSING_INPUT) |
| GAP-E02 | One terminal recognised event per economic cost (E) | analytic lines from moves/workorders/timesheets/bills (SV-15/17); field `stock.move.value` (SV-09) | duplication across layers | costing · `sipanel.actual.cost.event` natural key + `inclusion` | C8-D04 | PT-16, PT-17, PT-18, PT-21 | DESIGNED |
| GAP-E03 | Commitment / operational / WIP / recognised separation (E) | native reports mix layers | — | costing · `layer` on event; separate columns in variance view | AM-03-R1 | PT-21 | DESIGNED |
| GAP-E04 | Shared-stock boundary: cost at consumption only (E) | analytic on moves requires operation-type `analytic_costs` (EVIDENCE-DATED disabled) | configuration + policy | costing policy row + runbook configuration (B-03) | C0-D11, BQ-04 | PT-16 | DESIGNED (config prerequisite) |
| GAP-E05 | MRP without raw/labour/finished duplication (E) | `mrp_account` analytic lines on raw moves and workorders (SV-15) | exclusivity rule absent | costing · mutually exclusive policy rows per Finance choice | BQ-04 | PT-17 | DESIGNED |
| GAP-E06 | Approved labour source with governed hourly cost (E) | timesheet amount = −hours × hourly_cost; hourly costs zero (SV-17, EVIDENCE-DATED) | zero actuals | costing · `COST_SOURCE_ZERO` flag; runbook prerequisite | BQ-04 | PT-20 | DESIGNED (config prerequisite) |
| GAP-E07 | Reversals and credits linked once (E) | native returns/credit notes | linkage absent | costing · `reversal_of_id` | C8-D04 | PT-19 | DESIGNED |
| GAP-E08 | Visible UNALLOCATED bucket and completeness indicator (E) | none | — | costing · `sipanel.actual.allocation`, `unallocated_amount`, `completeness` | BQ-06=A | PT-29 | DESIGNED |
| GAP-E09 | Baseline vs forecast vs actual, Project/System/Activity report (E) | project profitability panel (TV-22) lacks estimate baseline | — | costing · SQL view `sipanel.scope.variance` | C8-D04, C10-D01 | PT-21, PT-29 | DESIGNED |
| GAP-E10 | Pre-contract actual cost (E) | technically possible via native docs | policy | none | AM-05, BQ-08=B | — | EXCLUDED (MVP) |
| GAP-E11 | Landed cost capitalisation (E) | `stock_landed_costs` not installed (EVIDENCE-DATED) | — | none | BQ-04 pack | PT-18 (partial) | DEFERRED |
| GAP-S01 | Cost/margin fields hidden from RPC/export/report (Security) | field `groups=` enforces on read/export/report; views alone do not | — | all · `groups='sipanel_commercial_scope_core.group_sipanel_cost_reader'` on cost fields | C4-D04, C7-D03 | PT-23 | DESIGNED |
| GAP-S02 | Company isolation in server rules (Security) | record rules | — | all · `company_id` rules on every model | C4-D04 | PT-23 | DESIGNED |
| GAP-S03 | Portal: own sent artifacts only (Security) | portal access token on `sale.order` | new models need rules | sale_scope · portal rules for artifact via order token; deny on all internal models | C7-D03 | PT-23 | DESIGNED |
| GAP-S04 | Stale-link / replay rejection (Security) | none | — | sale_scope · revision id + hash in portal payload | AM-01-R2 | PT-10, PT-23 | DESIGNED |
| GAP-S05 | Privileged override audit (Security) | none | — | core · audit event with reason on every waiver/override/release | C4-D04 | PT-24 | DESIGNED |
| GAP-S06 | Segregation-of-duties limitation record (Security) | — | single-person governance | security matrix records it; no simulated separation | C4-D04 | — | DESIGNED (documentary) |
| GAP-R01 | Report id 848 on `sale.order` (Report hygiene) | EVIDENCE-DATED stray report action | unknown origin | none in module; Clone decision step in runbook | B-09 | PT-32 | DESIGNED (gate) |
| GAP-R02 | Global `web.external_layout_bubble` override by `sale_shamsi_report` (Report hygiene) | SV-18 | regression risk for all PDFs | none in module; rendered regression on Clone | B-09 | PT-32 | DESIGNED (gate) |
| GAP-R03 | Duplicate `commitment_date` xpath in `sale_shamsi_report` portal template (Report hygiene) | SV-18 | portal rendering risk | fix request to that module's owner; extension does not touch it | B-09 | PT-32 | DESIGNED (gate) |
| GAP-R04 | Product UoM precision global change, `cm` inactive (Config) | SV-10/11; EVIDENCE-DATED precision 0 | Production-wide config | runbook Clone regression; no data-file change | B-01, C1-D04 | PT-03 | DESIGNED (gate) |
| GAP-R05 | System/Activity analytic plans and applicability (Config) | plans configurable (SV-16); only Project plan exists (EVIDENCE-DATED) | configuration | runbook; `ir.config_parameter` keys | B-03, C0-D11 | PT-16 | DESIGNED (config) |

## Customizations with no GAP

None permitted. Every model, field, hook, controller override and wizard in the five modules maps to a GAP-ID above; a code review item in the next authorized run is to reject any addition without a GAP-ID and decision ID.

## Native features deliberately not used

| Feature | Reason | Decision |
|---|---|---|
| `sale_margin` / `purchase_price` | not installed; adding it introduces unapproved semantics (cost per selling unit) | C5-D04, TV-12/23 |
| `product_percentage_price` | historical custom module; NO_REUSE after audit (TV-23); depends only on `product` (SV-19) | C0-D07 |
| `stock_landed_costs` | not installed; freight route DEFERRED | BQ-04 pack |
| `sale.order.option` | model does not exist in this build; optional = qty-state line in `sale_management` (SV-02) | AM-01-R2 |
| `stock.valuation.layer`, `procurement.group` | absent in Odoo 19; replaced by field `stock.move.value` + model `product.value` and `stock.reference` (SV-08/09, IF-01) | C8-D03 |
| Custom fields on `stock.move` / `stock.move.line` | forbidden at this phase | C0-D11 |
| Automatic Product creation from Scope/Recipe | forbidden | C0-D06, C1-D01 |
| Core monkey patches / native addon edits | forbidden | C10-D01 |
