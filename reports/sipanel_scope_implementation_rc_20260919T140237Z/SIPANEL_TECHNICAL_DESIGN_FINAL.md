Run sipanel_scope_implementation_rc_20260919T140237Z · Verdict: BLOCKED_NOT_ISOLATED · Status: DESIGN-LEVEL — NOT RUNTIME VALIDATED — no module was written, installed or tested in this run.

# SIPANEL Commercial Scope / Recipe / Estimation — Technical Design (Odoo 19 Community)

## 0. Status and authority

| Item | Value |
|---|---|
| Baseline | Architecture Master PROVISIONAL v0.12, Decision Register v0.12, Frozen Decisions v0.2 (15 FROZEN, byte-verified hash `00b5d867…e22da`) |
| Installed target | Odoo 19.0-20260528 Community, Python 3.12.3, PostgreSQL 15.18 (SV-01) |
| Evidence used | `evidence/EV-03_INSTALLED_SOURCE_VERIFICATION.md` (SV-01…SV-20, read-only source extraction this run); v0.10 evidence bundle facts carried as EVIDENCE-DATED 2026-09-19 |
| Business profile applied | BQ-01=B; BQ-02=**B, joint Finance + Sales** (deviates from worksheet v0.12 which selected A — recorded as *later instruction, unsigned*); BQ-03=A; BQ-04 = one terminal recognised event per economic cost per route; BQ-05=A; BQ-06=A with visible UNALLOCATED; BQ-07=A; BQ-08=B; BQ-09=A |
| Amendments applied | AM-01-R2, AM-02, AM-04 applied; AM-03-R1 applied **subject to Finance route tests** (PT-16…PT-21); AM-05 **excluded** from MVP |
| Numeric thresholds | all `TBE` (margin floor, stale-cost age, retry count, performance targets) — stored as configuration parameters, never hard-coded |
| Runtime validation | NONE. PT-01…PT-32 = BLOCKED (see `SIPANEL_TEST_RESULTS_PT01_PT32.md`) |
| Authority order | FROZEN text > approved later decisions (recorded) > installed source/schema > this design > public documentation |

Nothing in this document alters a FROZEN paragraph. Where the installed build contradicts a design assumption the correction is recorded as IF-xx and the FROZEN text is left untouched.

Installed-fact corrections carried into this design:

| ID | Correction | Design consequence |
|---|---|---|
| IF-01 | `stock.move.value` is a Monetary **field** on `stock.move` (SV-09); `product.value` is a **model**; no `stock.valuation.layer`, no `stock.move.value` model | actual-cost projection reads field `stock.move.value` and model `product.value`; no layer model referenced anywhere |
| IF-02 | `is_optional` and `/my/orders/<id>/update_line_dict` are provided by `sale_management` (SV-02, SV-03) | `sipanel_sale_scope` depends on `sale_management`; controller override targets `sale_management.controllers.portal.CustomerPortal.portal_quote_option_update` |
| IF-03 | `_check_line_unlink` lets sections/notes be deleted even in state `sale` (SV-05) | scoped-section guard is implemented in `sale.order.line.unlink` / `write` (sequence, display_type), not left to native |

## 1. Architecture overview and preserved separations

```
Scope identity ──► Scope version (DRAFT→RELEASED→SUPERSEDED) ──► Recipe lines (occurrences)
                                                   │
Native sale.order ──► Quote Scope (anchor_line_id) ─┴─► Scope revision (WORKING→SENT_SEALED→ACCEPTED_SEALED)
                                                            ├─► Component snapshots (direct / derived)
                                                            ├─► Sealed customer artifact (hash)
                                                            └─► Execution batch ─► Demand ─► Target links (native docs)
                                                                                              └─► Actual cost events (read-only projection) ─► Allocation / UNALLOCATED
```

| Separation (prompt §Authority rule 7) | Enforced by |
|---|---|
| Product ≠ Commercial Scope | `sipanel.scope` has its own code/company/owner; product mapping is an explicit `anchor_product_id` on the version (C1-D01, C1-D05); no product is created by scope actions |
| Commercial Scope ≠ Recipe | recipe lines are children of the *version*, never of the sale line (C2-D01); customer sees the scope, never the recipe (C0-D03) |
| Recipe ≠ Manufacturing BoM | recipe line may reference a product that has a BoM; no BoM read/write from quote actions; MO created only by the MANUFACTURE adapter after Release (C0-D05) |
| Billing Treatment ≠ Product classification | treatment axes live on the version default and on the component snapshot (C0-D10, AM-02); never on `product.template` |
| Estimate ≠ Commitment ≠ Actual | three datasets: `sipanel.quote.scope.component` (estimate), `sipanel.execution.demand`/native PO (commitment), `sipanel.actual.cost.event` (recognised actual); no writes across them (C0-D08, C0-D11, AM-03-R1) |
| Project ≠ System ≠ Activity ≠ Product Category | Project = `project.project`; System and Activity = `account.analytic.account` under two **configured** plans (SV-16); product category untouched (C0-D11) |

## 2. Module boundaries (summary)

Full dependency validation against the 196 installed modules is in `SIPANEL_MODULE_AND_DEPENDENCY_MANIFEST.md`.

| Module | Version | Depends on (installed) | Owns |
|---|---|---|---|
| `sipanel_commercial_scope_core` | 19.0.1.0.0 | base, mail, product, uom, analytic | Slice A: identity, version, recipe lines, audit, favorites, groups, company rules |
| `sipanel_sale_scope` | 19.0.1.0.0 | sipanel_commercial_scope_core, sale_management, portal | Slices B + C: quote scope, revisions, components, artifacts, waivers, wizards, sale.order/line inherits, portal override |
| `sipanel_scope_execution` | 19.0.1.0.0 | sipanel_sale_scope, sale_stock, sale_project, sale_purchase, sale_mrp, sale_timesheet, purchase_stock, mrp, project, hr_timesheet | Slice D: owner registry, batch, demand, target links, adapters |
| `sipanel_scope_costing` | 19.0.1.0.0 | sipanel_scope_execution, stock_account, mrp_account, account, hr_expense, project_account | Slice E: recognition policy, actual event projection, allocations, variance view |
| `sipanel_scope_demo` | 19.0.1.0.0 | all four above | C9 synthetic fixture; **clone/test only, never Production** |

Constraints honoured by every module: no core patch; no edit of native addon source; ORM/ACL/record-rules/chatter/transactions only; additive schema; deterministic migrations (`migrations/19.0.1.0.0/` pre/post scripts with idempotent guards); no credentials or dumps; demo module is not a dependency of any Production module.

## 3. Slice A — Foundations (`sipanel_commercial_scope_core`)

### 3.1 Models

| Model | Purpose | Key fields |
|---|---|---|
| `sipanel.scope` | Scope identity (C1-D01) | `code` (Char, non-semantic, unique per company), `company_id`, `owner_id`, `current_version_id` (RELEASED only), `active` (archive), `uid_key` (UUID, readonly) |
| `sipanel.scope.version` | Versioned content (C1-D02) | `scope_id`, `revision` (Integer ≥1, unique per scope), `parent_version_id`, `state` (draft/released/superseded), `name_fa`, `name_en`, `customer_desc_fa`, `customer_desc_en`, `base_uom_id`, `anchor_product_id`, `owner_mode` (native_line_owner/component_bridge_owner), `all_systems` (Boolean), `system_ids` (M2M analytic accounts, plan-restricted), `note_template`, `default_treatment_*` axes, `released_by`, `released_at`, `content_hash` |
| `sipanel.scope.recipe.line` | Recipe occurrence (C2-D02) | `version_id`, `occurrence_key` (UUID), `sequence`, `kind` (product/estimate_only), `product_id` (variant), `internal_desc`, `customer_label_fa/en`, `label_customer_eligible`, `spec_json` (typed key/value, unit, drawing rev; no expressions), `uom_id`, `basis` (per_scope_qty/fixed/manual/percent_of_quantity/percent_of_cost), `rate`, `fixed_qty`, `percent`, `base_line_ids` (M2M same version), `rounding_increment`, `rounding_mode` (up/nearest/down), `activity_id`, `execution_mode`, `cost_policy` (product_cost/manual_estimate), `manual_cost`, `treatment_*` axes, `estimate_owner_id`, `resolution_state` |
| `sipanel.scope.audit.event` | Append-only application audit (C10 field dictionary) | `res_model`, `res_id`, `action`, `actor_id`, `ts`, `before_json`, `after_json`, `reason`, `revision_ref`, `correlation_uid`; cost payload gated by group |
| `sipanel.scope.favorite` | Personal favorite to identity (C4-D03) | `user_id`, `scope_id`; resolves to current released version at pick time |

System/Activity references are `account.analytic.account` records whose `plan_id` equals the plan configured in `ir.config_parameter` keys `sipanel_scope.system_plan_id` / `sipanel_scope.activity_plan_id`. Until Finance configures those plans (B-03) the fields are optional-with-warning in Draft and blocking at Release (C4-D02).

### 3.2 Lifecycle state machine

```
DRAFT ──release()──► RELEASED ──(new draft released)──► SUPERSEDED
  ▲                      │
  └── new_version() ◄────┘   (copies content into a new DRAFT with parent_version_id; never "unrelease")
Identity.active = False  (archive) is orthogonal; blocks new selection, keeps history readable.
```

`release()` algorithm (single transaction):
1. `scope_id.lock_for_update()` — SV-07: `FOR UPDATE SKIP LOCKED`; on `LockError` raise a UserError "release in progress" (no retry loop here; user re-clicks). Two concurrent releases cannot both become current.
2. Run release validations (3.3). Any failure ⇒ rollback, nothing partially released.
3. Set previous current version `state='superseded'`, new version `state='released'`, `released_by/at`, compute `content_hash` (sha256 over canonical JSON of version + lines).
4. `scope.current_version_id = version`. Chatter message + audit event.

### 3.3 Release validations (Master C1, C1-D09)

| # | Check | Block/Warn at Release |
|---|---|---|
| R1 | company matches all referenced products/analytic accounts | BLOCK |
| R2 | name_fa or name_en present per BQ-01 (target-language rule applies at quote Send, not here); at least one approved customer label | BLOCK |
| R3 | `base_uom_id` active and dimensional family of every line's `uom_id` compatible with `rate` semantics (3.5) | BLOCK |
| R4 | `anchor_product_id` set, sale_ok, and `owner_mode` consistent with `product.type`/`service_tracking` (SV-13): COMPONENT_BRIDGE_OWNER requires `service_tracking in ('no','project_only')`; task-creating tracking forbidden for that owner (C1-D05) | BLOCK |
| R5 | applicability explicit: `all_systems=True` XOR `system_ids` non-empty (C1-D03) | BLOCK |
| R6 | recipe integrity: no empty recipe, no duplicate occurrence_key, no removed base references | BLOCK |
| R7 | percent validity: base lines exist, same version, no self-reference, no percent-on-percent, no cycle; PERCENT_OF_QUANTITY bases share a UoM family; PERCENT_OF_COST bases are direct-cost lines (AM-04) | BLOCK |
| R8 | executable known lines (`kind=product`, mode ≠ NO_ACTION) have activity and execution mode | BLOCK |
| R9 | `kind=estimate_only` lines have owner, description, uom, and `resolution_state='needs_resolution'` ⇒ version flagged `requires_quote_resolution` (allowed, never "ready to execute") | WARN + flag |
| R10 | INTERNAL_ONLY lines have no customer-eligible label | BLOCK |
| R11 | rounding increment > 0 and mode set for every quantity-bearing line | BLOCK |
| R12 | anchor product is not a combo product and not a combo child candidate (SV-06) | BLOCK |

Current product cost is **not** a release condition (C1-D09): cost is read at quote time.

### 3.4 Permissions and company boundaries

Groups (all in `sipanel_commercial_scope_core`, configurable, no users assigned by data files):

| Group xml_id | Role |
|---|---|
| `group_sipanel_scope_steward` | create/version/release/archive master |
| `group_sipanel_estimator` | edit draft snapshots, cost overrides, read cost |
| `group_sipanel_sales` | commercial actions on quotes (with native `sales_team.group_sale_salesman`) |
| `group_sipanel_execution_owner` | Release Execution, track demands |
| `group_sipanel_finance` | recognition policy, reconciliation, waiver co-approval |
| `group_sipanel_auditor` | read-only everything permitted |
| `group_sipanel_cost_reader` | separate explicit permission to see cost/margin fields (RPC/export/report enforced via field `groups=`) |
| `group_sipanel_waiver_sales` / `group_sipanel_waiver_finance` | BQ-02 joint waiver |

Record rules: `company_id in company_ids` on every model; released versions readable by all internal groups; drafts readable by steward/estimator/auditor only. The existing internal user Taleghani may be assigned these groups only by explicit configuration during install (runbook), not by data XML. If one user holds Sales+Finance+Inventory+Purchase+Admin the segregation-of-duties limitation is recorded in the security matrix.

### 3.5 Dimensional UoM contract and explicit rounding

SV-10: the installed `uom.uom` has no category, and rounding is one global value derived from decimal precision `Product Unit` (`_compute_rounding`). Therefore the engine owns both:

| Element | Design |
|---|---|
| Dimensional family | `sipanel.uom.family` mapping (config data + settings): each `uom.uom` used by Scope/Recipe is tagged `length / area / volume / mass / count / time / service`. Family derived from `parent_path`/`relative_uom_id` chain where possible; otherwise explicit tag. Conversion allowed only inside one family via native `_compute_quantity(raise_if_failure=True)`. |
| Rate dimension | PER_SCOPE_QTY `rate` is "component uom per **base** uom"; quote quantity in another compatible unit is normalised to base first (example Master C1: 8500 cm → 85 m only if `cm` is active and convertible; `cm` is inactive — EVIDENCE-DATED — so Quote uses base until B-01 is closed). |
| Per-line rounding | `rounding_increment` (Float > 0) and `rounding_mode` on recipe line, copied into component snapshot. `raw_calculated_qty`, `rounded_calculated_qty`, `final_qty` stored separately (C2-D03). Rounding upward for indivisible demand is a line policy, not global. |
| Global precision | Product UoM precision change is Production-wide (SV-11); the module never changes `decimal.precision` in data files. Runbook records it as a Clone regression item (B-01). Product Price precision is not touched (Finance). |
| Procurement packaging / MOQ | never in recipe basis (C0-D07); adapters may group but never rewrite estimated demand |

### 3.6 Usage trace

`sipanel.scope.version.usage_count` computed via `search_count` on `sipanel.quote.scope` with `source_version_id` under the caller's ACL (C1-D08); the count is displayed as "≥ n (visible to you)" to avoid leaking existence of unauthorized documents. Usage detail view lists quote/revision/state.

### 3.7 Immutable released versions (incl. import/RPC)

- `write()` on `sipanel.scope.version` and `sipanel.scope.recipe.line` raises `UserError` when `state != 'draft'`, except an allow-list of non-content fields (`state`, `released_*`, `content_hash`, `message_*`, `active` on identity). This is model-level, so `base_import`, XML-RPC, `web_save`, and `sudo()` from other modules all hit it; `sudo()` bypasses ACL but not Python constraints.
- `unlink()` on a version with usage or state ≠ draft ⇒ blocked; identity uses archive.
- `copy()` on version ⇒ implemented as `new_version()` (same identity) or `duplicate_as_new_scope()` (new identity, new code) — both explicit actions (C1-D07).
- Test PT-24 covers import/RPC bypass.

## 4. Slice B — Quotation and estimation (`sipanel_sale_scope`)

### 4.1 Models

| Model | Purpose | Key fields |
|---|---|---|
| `sipanel.quote.scope` | Quote-level Scope identity (C3-D01) | `order_id`, `scope_uid` (UUID), `source_scope_id`, `source_version_id`, **`anchor_line_id`** (M2O `sale.order.line`, required, ondelete restrict, unique), `optional_section_line_id` (presentation only), `current_revision_id`, `accepted_revision_id`, `state`, `system_id`, `project_id`, `is_adhoc` |
| `sipanel.quote.scope.revision` | Snapshot revision | `quote_scope_id`, `revision`, `state` (working/sent_sealed/accepted_sealed), `prior_revision_id`, `language`, `scope_qty`, `scope_uom_id`, `uom_labels_json`, `commercial_projection_json` (qty, unit, price_unit, discount, taxes, subtotal — copied at seal), `direct_cost`, `derived_cost`, `total_cost`, `missing_cost_count`, `net_revenue`, `margin_amount`, `margin_pct` (N/A when R=0), `fx_rate`, `fx_date`, `fx_source` (company-currency-only ⇒ 1.0 with source `company_currency`), `generated_note`, `final_note`, `note_generated_fp`, `note_final_fp`, `note_manually_edited`, `note_stale`, `note_reviewed_by/at`, `sealed_hash`, `sealed_at`, `sealed_by`, `artifact_id` |
| `sipanel.quote.scope.component` | Component snapshot | `revision_id`, `occurrence_uid`, `source_line_id`, `copy_from_id`, `moved_from_id`, `origin` (master/added/overridden/removed/transferred), `product_id`, `desc`, `spec_json`, `customer_label`, `label_eligible`, `uom_id`, `uom_label`, `basis`, `rate/fixed_qty/percent`, `base_component_ids`, `raw_calculated_qty`, `rounded_calculated_qty`, `final_qty`, `override_flag`, `override_reason`, `override_stale`, `cost_source` (product_cost/manual_estimate/derived), `unit_cost`, `cost_uom_id`, `cost_conversion_factor`, `cost_currency_id`, `cost_date`, `cost_company_id`, `cost_product_value_id` (M2O `product.value`, provenance), `manual_cost_user_id/date/reason`, `cost_status` (known/known_zero/missing/not_applicable), `derived_base_amount`, `line_cost`, `activity_id`, `system_id`, treatment axes (`responsibility`, `placement`, `acceptance`, `certainty`, `disclosure`), `preset_label`, `execution_mode`, `owner_mode`, `active_state` (active/tombstone), `resolution_state`, `resolution_owner_id` |
| `sipanel.quote.scope.artifact` | Sealed customer artifact (C7-D04) | `revision_id`, `kind` (pdf/portal_html/text), `attachment_id`, `sha256`, `language`, `amount_untaxed`, `amount_total`, `sent_at`, `sent_by`, `acceptance_ref` |
| `sipanel.quote.waiver` | BQ-02 joint waiver | `order_id`, `revision_id`, `kind` (negative_margin/missing_estimate/below_floor), `reason`, `sales_approver_id`, `sales_approved_at`, `finance_approver_id`, `finance_approved_at`, `state` (pending/approved/rejected); Send blocked while pending |

Transient wizards: `sipanel.wizard.add.scope`, `.refresh.cost`, `.replace.recipe`, `.split.move`, `.apply.price`, `.regenerate.note`, `.treatment.transition`, `.release.check` (readiness drawer).

### 4.2 Explicit Scope anchor line (C0-D02, AM-01-R2)

- Add Scope creates, in one transaction: the `sale.order.line` (product = `anchor_product_id`, qty = scope qty, native price/tax/pricelist computation untouched), the `sipanel.quote.scope` with `anchor_line_id`, revision 1 (WORKING), components.
- `sale.order.line.sipanel_quote_scope_id` (O2M inverse, at most one) and `sipanel_is_scope_anchor` (stored Boolean).
- Anchor constraints: not `display_type`, not `combo_item_id`, not `linked_line_id` to a combo parent (SV-06), not `is_downpayment`. A line cannot become an anchor of two scopes (SQL unique on `anchor_line_id`).
- `parent_id`/`sequence` are presentation (SV-04); nothing in the extension reads `parent_id` for ownership.

### 4.3 Revision state machine

```
WORKING ──seal_on_send()──► SENT_SEALED ──accept()──► ACCEPTED_SEALED
   ▲                            │                          │
   └── new WORKING (amend) ◄────┴──────────────────────────┘   (never unseal; delta recorded)
```
- `seal_on_send()` hooked in `sale.order.action_quotation_send` (wizard path) and `action_quotation_sent` (manual mark) — SV-14: both call the same private `_sipanel_seal_current_revisions()`; idempotent if already sealed with identical hash.
- `sealed_hash` = sha256 over canonical JSON of (header commercial values, commercial projection of anchor, component customer-eligible rows, final note, language, amounts). Stored with the artifact.
- `accept()` hooked in `portal_quote_accept` (controller override) and in `action_confirm` (`_sipanel_check_accepted_revision`): if `current_revision_id.state != sent_sealed` or anchor projection hash ≠ sealed hash ⇒ block with diff (C3-D03). After ACCEPTED_SEALED the revision is the execution baseline.

### 4.4 Quantity engine (C0-D07, C2-D03)

| Basis | Inputs | `raw_calculated_qty` | Guards |
|---|---|---|---|
| PER_SCOPE_QTY | rate, scope qty normalised to base uom | `scope_qty_base × rate` | rate ≥ 0; family compatibility (3.5) |
| FIXED | fixed_qty | `fixed_qty` | unchanged by scope qty |
| MANUAL | operator input | value entered | `False`/None ≠ 0: missing blocks Send with warning; zero allowed with reason |
| PERCENT_OF_QUANTITY | base components (same revision, direct quantity lines, same uom family), percent | `Σ normalised base final_qty × percent / 100` | bases exist, active, not percent lines, same family |
| PERCENT_OF_COST | base components (direct-cost lines), percent | no physical qty (`final_qty = 0`, `qty_kind='none'`); `derived_base_amount = Σ base line_cost`; `line_cost = base × percent/100` | AM-04: derived, never a purchase source; no demand |

Then `rounded_calculated_qty = round_to_increment(raw, increment, mode)`; `final_qty = override_value if override_flag else rounded_calculated_qty`.

Prohibited: percent on percent, self-reference, cross-scope reference, reference to tombstoned line, cycles (DFS check at save), negative quantities in baseline. Scope qty 0 allowed only for WORKING or OFFERED acceptance state.

### 4.5 Cost sources (C0-D08, C5-D01, AM-04)

| Source | Snapshot content | Rule |
|---|---|---|
| PRODUCT_COST | `product_id.with_company(company).standard_price` (company-dependent, in company currency, per product uom — v0.10 evidence), converted to component uom via `uom._compute_price`, `cost_product_value_id` = latest `product.value` row for that product/company if one exists (provenance), `cost_date=now`, `cost_status` = known / known_zero(with reason required) / missing (no `standard_price` and no `product.value`) | later product cost changes never touch the snapshot |
| MANUAL_ESTIMATE | `unit_cost`, `manual_cost_user_id/date/reason` | never overwritten by Refresh; refresh only re-reads PRODUCT_COST lines selected in the wizard preview |
| derived (PERCENT_OF_COST) | base amount + percent | recomputed from bases on every direct change; never a third purchase source |

`line_cost = final_qty × unit_cost × cost_conversion_factor` in company currency (BQ-09 ⇒ no FX). Roll-up eligibility: `responsibility=SIPANEL`, `active_state=active`, acceptance ∈ {BASE, ACCEPTED}; CUSTOMER responsibility ⇒ `cost_status=not_applicable`; OFFERED options shown separately, excluded from baseline total.

### 4.6 Overrides and stale detection

- Setting `final_qty` manually ⇒ `override_flag=True`, `override_reason` required, before/after audit.
- Any driver change (scope qty, rate, basis, base set, uom) ⇒ `override_stale=True`; the override value is retained, never reset (C0-D07). The readiness drawer lists stale overrides; Send blocks until each is confirmed or cleared (C4-D02).
- `cost_stale` flag on PRODUCT_COST components when `cost_date` older than config `sipanel_scope.cost_stale_days` (TBE; blank = disabled).

### 4.7 Atomic split / move (C3-D04)

`sipanel.wizard.split.move` in one transaction:
1. lock source and destination `sipanel.quote.scope` (`lock_for_update`; `LockError` ⇒ UserError).
2. For each selected occurrence: partial qty ⇒ two components (source remainder + destination moved) with `moved_from_id`, `remainder + moved = original final_qty`; full move ⇒ source component `active_state=tombstone, origin=transferred`, destination `origin=transferred`.
3. Dependency gate: if any percent component references a moved line, the wizard requires an explicit relocation choice (move dependent too / rebase to remaining lines) — otherwise BLOCK (PT-07). Dangling bases are never saved.
4. Destination scope may be new (creates its own anchor line, revision 1) or an existing WORKING scope of the same order.
5. Cost conservation assertion: `Σ line_cost(source_after) + Σ line_cost(dest_after) == Σ line_cost(source_before)` within currency rounding — raises if violated (PT-06).
6. Both notes ⇒ `note_stale=True`; customer price of destination is an operator decision in Apply Price, never auto-allocated.

### 4.8 Pricing and internal margin (C5-D02, C5-D03, C5-D04)

- `C` = eligible cost (company currency); `R` = anchor `price_subtotal` (native untaxed, after discount) — BQ-09 ⇒ same currency, `fx_rate=1.0` recorded with `fx_source='company_currency'`.
- `margin_amount = R − C`; `margin_pct = (R − C)/R × 100` if `R ≠ 0` else `N/A` (displayed as `—`, stored NULL).
- Apply Price wizard: target margin `m` (m < 1) ⇒ suggested `R = C/(1−m)`; markup `k` ⇒ `R = C×(1+k)`; writes `price_unit = R / product_uom_qty` to the anchor **only on explicit Apply**, then native recompute of taxes/discount/pricelist runs untouched. Manual `price_unit` edits keep working; reason logged.
- Negative margin or below-floor (`sipanel_scope.min_margin_pct`, TBE) ⇒ waiver required (BQ-02 joint). Cost refresh never changes price.
- `sale_margin` is not installed and is not a dependency; no `purchase_price` write (C5-D04).

### 4.9 Customer note generation (C0-D09, C7-D01)

Independent flags on the revision: `has_generated`, `note_manually_edited`, `note_stale`, `note_reviewed`.

- `generate()` is deterministic: customer-eligible, active, non-INTERNAL_ONLY components in `sequence` order, using `customer_label` in revision language; missing label ⇒ skipped + review warning (never SKU/vendor fallback). Hidden fields (cost, waste, supplier, reason) are excluded from the payload, not just hidden in QWeb.
- `note_generated_fp` = sha256(eligible component tuple); `note_final_fp` = sha256(final_note). On component change: recompute `note_generated_fp`; if it differs from the fingerprint at last accept ⇒ `note_stale=True`. Final text is never replaced automatically; Regenerate wizard shows diff and requires explicit accept.
- Projection to `sale.order.line.name` of the anchor is one-way from the revision on explicit save; a direct edit of the anchor `name` (native form) writes back into the WORKING revision `final_note` through the line `write()` inherit with `note_manually_edited=True` — one source, no background sync.
- Send blocks when `note_stale and not note_reviewed` (C4 validation matrix).

### 4.10 Duplicate and replacement

- `sale.order.copy_data` inherit: for each quote scope copy the **latest revision** into a new WORKING revision 1 on the new order; copy `source_version_id`; do **not** copy artifacts, waivers, acceptances, execution links or idempotency keys; cost snapshots kept with `cost_stale` indicator; no master upgrade (C3-D02).
- Replace Recipe wizard: builds a draft replacement revision from a chosen released version; diff added/removed/spec/qty; manual overrides retained or dropped explicitly; never silent merge.
- Refresh Cost wizard: PRODUCT_COST lines only, before/after preview.

### 4.11 Sealed customer artifact

On seal: render the native `sale.action_report_saleorder` PDF (same call path as portal accept, SV-14) into `ir.attachment` (res_model = artifact), store sha256, language (`partner.lang` frozen into `revision.language`), amounts. Portal `document` route remains native; artifacts are accessible only via the order's own access token (portal rule) and internal groups. The hash is evidence, not a legal signature (C7-D04).

## 5. Slice C — Optional and provisional scope (`sipanel_sale_scope`)

### 5.1 Native quantity-state compatibility (IF-02)

Optional in Odoo 19 = ordinary `sale.order.line` under a section whose `is_optional=True` (SV-02). A Scope with placement `OWN_LINE` and acceptance `OFFERED` is created under an optional section with `product_uom_qty=0`; `ACCEPTED` = same line with qty > 0 (AM-01-R2). No option model is created; ordinary non-Scope optional lines keep native behaviour (PT-31).

### 5.2 Explicit `anchor_line_id`

Already stored (4.2). Optional section membership is recorded in `optional_section_line_id` for presentation only and recomputed after reorder; it never changes ownership.

### 5.3 Governed operator and Portal transition

| Path | Native point (SV-03) | Extension behaviour |
|---|---|---|
| Portal | `sale_management.controllers.portal.CustomerPortal.portal_quote_option_update` (`/my/orders/<id>/update_line_dict`, jsonrpc, auth public) | Overridden in `sipanel_sale_scope/controllers/portal.py`: if the line is a Scope anchor ⇒ (1) order must have a `sent_sealed` current revision for that scope and the request must carry `revision_id`/hash matching it (stale link ⇒ JSON error, no write); (2) transition `OFFERED→ACCEPTED` or `ACCEPTED→DECLINED` executed through `sipanel.quote.scope._transition_acceptance(new_state, actor='portal')`, which sets qty (scope qty for accept, 0 for decline), triggers native recompute, writes an audit event with actor/IP-less correlation; (3) idempotent: repeated accept returns current state; (4) at most one accepted state ⇒ at most one demand later. Non-Scope lines fall through to `super()`. |
| Operator | `sale.order.line.write({'product_uom_qty': …})` on an anchor | `write()` inherit: qty transitions on anchors of `sent_sealed` scopes are allowed only through the treatment-transition wizard (context key `sipanel_governed_transition=True`); raw edits raise. WORKING revisions accept edits normally (Draft). |
| Model guard | `sale.order.line._can_be_edited_on_portal()` (SV-02) | override returns `False` for anchors whose scope has no `sent_sealed` revision, and for anchors in `accepted_sealed` state |

### 5.4 Current sealed revision binding

Portal page rendering (inherit `sale.sale_order_portal_content`) injects `data-sipanel-revision` and the sealed hash for Scope anchors; the accept/decline JS payload is extended (asset bundle `web.assets_frontend`) to send them. Server ignores requests whose revision is not the current sealed one (stale/replay ⇒ reject, PT-10, PT-23).

### 5.5 Section reorder / delete protection (IF-03)

`sale.order.line` inherits:
- `unlink()`: a `line_section`/`line_subsection`/`line_note` that is the `optional_section_line_id` of a Scope with a sealed revision, or any anchor line with a sealed revision, cannot be deleted (raise before `_unlink_except_confirmed`, which would allow it — SV-05).
- `write()` on `sequence`/`display_type`/`is_optional` of such lines ⇒ blocked when the scope is sealed; allowed in WORKING with recomputation of `optional_section_line_id`. Moving an anchor out of/into an optional section in WORKING state is a treatment transition (preset change), audited.

### 5.6 Tax and pricelist recomputation

The extension writes only `product_uom_qty` and, on Apply Price, `price_unit`; native `_compute_price_unit`, `_compute_tax_id`, `_compute_amount` and fiscal position logic run unchanged (C0-D01). The controller's `env.protecting([discount, price_unit])` (SV-03) is preserved by calling `super()` for non-scope lines and by using the same protection in `_transition_acceptance`.

### 5.7 Accepted Change Order boundary (BQ-03=A, C6-D03)

PROVISIONAL certainty stores `provisional_amount`, `provisional_basis` and settlement text on the component/revision. Adjustment after acceptance is only through a new WORKING revision (amendment) that becomes `accepted_sealed` via native quote re-send/accept or an internal accepted change record (`sipanel.quote.scope.revision.change_order_ref`). No automatic invoice of actuals; invoicing stays native per anchor policy.

## 6. Slice D — Execution Bridge (`sipanel_scope_execution`)

### 6.1 Owner registry (C1-D05, C8-D01, BQ-05, BQ-07)

`sipanel.execution.owner.rule`: `product_id`/`product_tmpl_id`/`route_kind` → `owner` (NATIVE_LINE_OWNER | COMPONENT_BRIDGE_OWNER), `native_hook` (informational: `sale_stock._action_launch_stock_rule` / `sale_project._timesheet_service_generation` / `sale_purchase._purchase_service_generation` / `sale_mrp kit`), `tracking_expected` (`service_tracking` value), `active`. Resolution order: product → template → route default. Version `owner_mode` must match the resolved rule at Release validation R4.

| Owner | Who creates demand | Bridge behaviour |
|---|---|---|
| NATIVE_LINE_OWNER | native confirm hooks (SV-13) — stock rules, kit explosion, service→task/project, service→PO | components under that anchor get `execution_mode=NATIVE_ANCHOR_COVERED`; Bridge links the native docs (via `stock_reference_ids`, `task_id`, `purchase_line_ids`) as targets; never re-creates |
| COMPONENT_BRIDGE_OWNER | explicit Release action | anchor product must not trigger native demand (R4); if `service_tracking='project_only'` the native project is linked (BQ-07=A), tasks are never created in parallel |

### 6.2 Explicit Release action

`sale.order.action_sipanel_release_execution()` (button, group execution owner): preflight ⇒ creates `sipanel.execution.batch` ⇒ runs adapters ⇒ commits. Preflight (Master C8): order `state='sale'`, accepted revision sealed, roles, company, product/UoM/spec readiness, project/system/activity present, execution mode and owner resolved, recognition route known (costing module may add its own check), no NO_ACTION line without reason. Missing cost ⇒ commercial waiver may exist; invalid product/qty never executable.

### 6.3 Idempotency keys (Master C8, verbatim)

| Record | Key | Constraint |
|---|---|---|
| `sipanel.execution.batch` | `(order_id, accepted_revision_id, release_action_uid)` | SQL unique |
| `sipanel.execution.demand` | `(component_occurrence_uid, authorized_delta_uid, execution_mode, owner)` | SQL unique |
| `sipanel.execution.target` | `(demand_id, target_model, target_res_id)` | SQL unique |

`authorized_delta_uid` = UUID of the accepted revision (baseline) or of an accepted amendment delta.

### 6.4 LockError handling and bounded retries (SV-07)

```
for attempt in range(1, max_attempts+1):          # max_attempts = ir.config_parameter sipanel_scope.release_max_attempts (TBE; must be set at install, no invented default)
    try:
        with self.env.cr.savepoint():
            batch.lock_for_update(); demands.lock_for_update()
            ...create/link...
        break
    except (LockError, psycopg2.errors.UniqueViolation):
        self.env.cr.rollback_to_savepoint handled by context manager
        existing = self._find_existing_batch(keys)   # return same target links
        if existing: return existing
        sleep(backoff[attempt])                        # backoff table configurable
raise UserError("Release still in progress / retry exhausted")
```
Two concurrent clicks ⇒ one batch; the loser reads and returns the winner's links (PT-14).

### 6.5 Adapters (C8-D03)

Abstract `sipanel.execution.adapter` with `preflight(demand)`, `create_or_link(demand)`, `cancel_delta(demand)`. Implementations:

| Mode | Target (native) | Native approval boundary | Link fields |
|---|---|---|---|
| STOCK_ISSUE | `stock.picking` (internal/consumption type configured per company) + `stock.move` | reserve/validate by Inventory | `stock.move` ids; `stock.reference` created with name = order/scope key and linked via `sale.order.stock_reference_ids` (SV-08) |
| BUY_DIRECT | draft `purchase.order` / `purchase.order.line` grouped only by vendor/company/currency/uom-compatible/spec/date (Master C8) | vendor/PO approval by Purchase | `purchase.order.line` ids; `analytic_distribution` (SV-15) set to Project/System/Activity for direct-project purchases only (C0-D11) |
| MANUFACTURE | `mrp.production` for product/BoM, `project_id` (SV-15 project_mrp), one System per MO, Activity default MFG (overridable, audited) | confirm/consume/done by MRP | `mrp.production` id, `reference_ids` |
| LABOUR | link existing `project.project`/`project.task` (from native tracking or configured project); **no timesheet creation** | real hours by staff | `project.task` id |
| EQUIPMENT_SERVICE | service RFQ (`purchase.order.line`) or expense process handle | bill/expense approval | `purchase.order.line` or `hr.expense` id |
| NATIVE_ANCHOR_COVERED | link docs already created by native confirm (`stock_reference_ids`, `task_id`, `purchase_line_ids`) | native | as found |
| NO_ACTION | none; `reason` (customer_responsibility / allowance / declined / covered) | owner sign-off | — |

Kit/manufactured parent: exactly one owner explodes (native for NATIVE_LINE_OWNER; MANUFACTURE adapter never explodes BoM into separate demands).

### 6.6 Atomic failure handling

All creation of one batch runs inside one DB transaction (savepoint around the batch); any adapter exception ⇒ rollback of everything created by that batch, batch `state='failed'`, `error_summary` redacted (no vendor/contact data). No external side effect (mail, vendor submission) is triggered inside the transaction; RFQs are left in draft (PT-15).

### 6.7 Amendment, cancellation, return lineage

- Amendment (new ACCEPTED_SEALED revision): compute per-occurrence delta vs the last released quantities; only positive/negative deltas become new demands with a new `authorized_delta_uid`; price-only amendments produce no demand (PT-22).
- Negative delta: `cancel_delta()` reduces unreserved planned demand (draft PO line qty, unconfirmed MO, unreserved move); confirmed/done docs are never deleted — the demand records `reversal_required=True` and links the native return/credit created through native workflows (PT-19).
- Order cancel: native `action_cancel` inherit blocks when done targets exist, otherwise cancels planned demand and marks batch `cancelled`.

### 6.8 No duplicate demand

Guaranteed by: owner registry (one owner per line), unique demand key, NATIVE_ANCHOR_COVERED linking instead of creating, and the release preflight refusing components already linked to an open target (PT-13).

## 7. Slice E — Actual cost and reporting (`sipanel_scope_costing`)

### 7.1 Recognition policy (BQ-04, AM-03-R1)

`sipanel.cost.recognition.policy` rows = Finance-signed route matrix (versioned, `approved_by`, `approved_at`, `effective_from`). Until a signed row exists for a route, the projection for that route reports `POLICY_MISSING` and sums nothing (fail closed). Candidate rows shipped as **inactive** data, mirroring the BQ-04 pack:

| Route | Commitment evidence (shown, excluded) | Operational qty (shown, excluded) | Candidate terminal recognised event — source model/field (SV-09/15/17) | Excluded duplicates |
|---|---|---|---|---|
| Shared-stock material | `purchase.order.line` amount | receipt `stock.move.quantity` | `account.analytic.line` created by the consumption `stock.move` (`_prepare_analytic_lines`, only when analytic distribution present and operation type `analytic_costs` enabled — EVIDENCE-DATED disabled) valued from field `stock.move.value` | PO, receipt, internal transfer, vendor bill for same value |
| Direct project purchase / dropship | PO commitment | delivery move qty | posted `account.move.line` (vendor bill) with analytic distribution to Project, **or** analytic line — exactly one per Finance | PO + bill + stock value summed |
| Manufacturing material | MO planned | raw `stock.move.quantity` | raw-consumption analytic line (`mrp_account`) **or** finished-goods issue value (`stock.move.value`) — mutually exclusive per policy | raw AAL + finished issue together |
| Manufacturing labour | workorder planned | workorder hours | `mrp.workorder` `wc_analytic_account_line_ids` **or** timesheet cost — one | workorder + timesheet + payroll |
| Site labour | assignment | approved `account.analytic.line.unit_amount` | timesheet `amount` (= −hours × `hourly_cost`, SV-17; zero hourly cost ⇒ zero, flagged `COST_SOURCE_ZERO`) | payroll duplicate |
| Equipment / service | PO commitment | service units | posted vendor bill line **or** approved `hr.expense` | PO + bill + expense |
| Freight / landed cost | commitment | — | **DEFERRED** (`stock_landed_costs` not installed — EVIDENCE-DATED) | — |
| Returns / credits | reduce commitment | returned qty | signed reversal linked to original event (`reversal_of_id`) | double reversal |

### 7.2 Actual cost event projection

`sipanel.actual.cost.event` (stored, rebuilt by an explicit "Refresh actuals" action or an **opt-in** cron that is shipped inactive): `source_model`, `source_res_id`, `source_line_id`, `monetary_component` (material/labour/service/expense/adjustment), `company_id`, `date`, `amount_signed`, `currency_id`, `project_id`, `system_id`, `activity_id`, `qty`, `qty_kind` (consumed/received/returned/hours), `layer` (commitment/operational/wip/recognized), `policy_id`, `inclusion` (included/excluded_duplicate/policy_missing), `reversal_of_id`. Natural key `(source_model, source_res_id, monetary_component, company_id)` unique. Read-only: no journal, no analytic line, no `stock.move` field is written.

`sipanel.actual.allocation`: event → demand/occurrence, `allocated_amount`, `basis` (direct_link / proportional / manual with reviewer). Sum of allocations per event = event amount or the remainder is `UNALLOCATED`.

### 7.3 Separation of layers

| Layer | Column | Source |
|---|---|---|
| Baseline | accepted sealed revision `total_cost` (immutable) | Slice B |
| Forecast | current WORKING revision cost | Slice B |
| Commitment | open PO lines linked to demands | `purchase.order.line` |
| Operational qty | received / consumed / returned / hours | `stock.move`, timesheet |
| WIP | MO in progress (reported separately if Finance chooses "WIP separately") | `mrp.production` |
| Recognised | one terminal event per economic cost | 7.1 |

### 7.4 Reporting (BQ-06=A)

SQL view `sipanel.scope.variance`: per Project/System/Activity and per Scope occurrence: baseline, forecast, commitment, recognised, variance (`actual − baseline`; N/A when baseline absent), `unallocated_amount`, `completeness` (complete / incomplete / policy_missing). Revenue = posted customer invoice lines minus credits linked to the anchor (`sale_line_ids`), never quote totals. The Scope-level completeness indicator is shown on the order form and blocks any "profitability" label until `unallocated_amount = 0` and all routes have policy.

## 8. Report hygiene gate (B-09) — Clone regression, not Production cleanup

| Item | Evidence | Handling |
|---|---|---|
| `ir.actions.report` id 848 on `sale.order` | EVIDENCE-DATED (v0.10 audit); not re-read this run (probe refused) | Clone step: identify origin (xml_id/module), decide disable vs delete on Clone, document; no automatic Production change |
| `sale_shamsi_report` inherits global `web.external_layout_bubble` | SV-18 (`views/sale_report_templates.xml:156-157`) | render all customer PDFs (quote, invoice, picking) on Clone before/after module install; extension never overrides `web.external_layout*` |
| duplicate xpath on `span[@t-field='sale_order.commitment_date']` | SV-18 (`views/sale_portal_templates.xml:41` and `:59`) | portal regression PT-32; raise as a separate fix request to the owner of `sale_shamsi_report`; the extension does not touch that template |

## 9. FX fail-closed (BQ-09, SV-12)

`res.currency._get_rates` falls back to 1.0 when no rate row exists. The extension therefore: (a) `sale.order` constraint — an order containing any Scope must have `currency_id == company_id.currency_id`, else Add Scope / Send / Confirm raise; (b) every revision stores `fx_rate=1.0, fx_source='company_currency'`; (c) the full FX design (source/company/quote currency, date, rate source) remains in the field dictionary as inactive fields so enabling FX later does not require schema change, but no code path converts with a missing rate.

## 10. Conflicts and amendments applied

| Conflict | FROZEN text | Applied amendment | Where |
|---|---|---|---|
| CF-01 | C0-D02 / C0-D10 unchanged | AM-01-R2 | §4.2, §5.3–5.5 |
| CF-02 | C0-D10 unchanged | AM-02 (six presets over five axes) | §4.1 component axes, §5.7 |
| CF-03 | C0-D11 unchanged | AM-03-R1 subject to PT-16…PT-21 | §7 |
| CF-04 | C0-D07 / C0-D08 unchanged | AM-04 | §4.4, §4.5 |
| CF-05 | C0-D11 unchanged | AM-05 **excluded** (BQ-08=B) | no pre-contract actual path designed |

No new CONFLICT_FOUND against FROZEN text was discovered in this run.

## 11. Not designed / deferred

Supplier offers, BoM estimated-cost explosion, free formulas, workflow engine, `stock.move`/`stock.move.line` custom dimensions, fourth analytic plan, Work Package, generic BI, rental asset management, automated provisional settlement, landed cost, foreign-currency quotations, combo-child anchors, shared favorites, pre-contract actuals (AM-05). See `SIPANEL_KNOWN_LIMITATIONS_AND_DEFERRED_ITEMS.md`.
