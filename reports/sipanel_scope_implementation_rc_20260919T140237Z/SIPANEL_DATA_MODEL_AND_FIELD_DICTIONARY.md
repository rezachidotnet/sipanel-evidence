Run sipanel_scope_implementation_rc_20260919T140237Z · Verdict: BLOCKED_NOT_ISOLATED · Status: DESIGN-LEVEL — NOT RUNTIME VALIDATED — no module was written, installed or tested in this run.

# SIPANEL — Data Model and Field Dictionary (design-level)

Baseline: Architecture Master PROVISIONAL v0.12 §C10 "Field dictionary — candidate logical records"; FROZEN decisions v0.2 (15, unchanged); installed-source anchors SV-01…SV-20 in `evidence/EV-03_INSTALLED_SOURCE_VERIFICATION.md`; installed-fact clarifications IF-01 (`stock.move.value` is a **field** on `stock.move`, `product.value` is a **model**), IF-02 (`is_optional` and `/my/orders/<id>/update_line_dict` live in `sale_management`), IF-03 (sections/notes deletable after confirmation).

Applied provisional profile: BQ-01=B, BQ-02=B joint Finance+Sales (deviation from worksheet selection A recorded as a later unsigned instruction), BQ-03=A, BQ-04 one terminal recognised event per route (Finance answer MISSING_INPUT), BQ-05=A, BQ-06=A with visible UNALLOCATED, BQ-07=A, BQ-08=B, BQ-09=A company-currency-only; AM-01-R2, AM-02, AM-04 applied; AM-03-R1 applied subject to Finance route tests; AM-05 excluded from MVP.

Conventions used in every table:

- `company_id` is present on every SIPANEL model (`res.company`, required, default current company, indexed) unless the row says otherwise; company isolation is enforced by record rules (see `SIPANEL_SECURITY_MATRIX.md` §C) and by `_check_company_auto = True`.
- Every relational field that points at a record that may already be referenced by history (sealed revisions, released versions, allocations) uses `ondelete='restrict'`. `cascade` is used only from a child to its owning aggregate when the aggregate itself is deletable (draft-only).
- "Source of truth" states which record is authoritative for the value. Native Odoo fields are never duplicated as live `related` fields for historical data (C3-D01).
- Monetary values are `fields.Monetary` with an explicit `currency_id` = company currency (BQ-09). Quantities use `digits='Product Unit'` for display only; the stored value is not rounded by the global precision — the Recipe engine rounds per line (SV-10, C1-D04).
- Decision IDs reference the v0.12 Decision Register. Numeric thresholds are TBE.
- Nothing below is installed. Field names are the proposed technical names for the next authorized build; they may be adjusted during code review but not in ways that break the invariants stated in the constraint column.

---

## Module 1 — `sipanel_commercial_scope_core`

Depends on: `base`, `mail`, `product`, `uom`, `analytic`. No dependency on `sale`.

### 1.1 `sipanel.scope` — Scope identity

Purpose: the immutable commercial Scope identity, independent of Product (C1-D01). Inherits `mail.thread`, `mail.activity.mixin`.

| Field | Type | Required | Readonly / compute | Constraints / index | Source of truth | Decision |
|---|---|---|---|---|---|---|
| `code` | Char | yes | readonly after create | unique (`company_id`,`code`) SQL constraint; non-semantic; not equal to any product default_code by convention | this record | C1-D01, C1-D06 |
| `name` | Char (translate=False) | yes | — | internal name; never customer-facing fallback | this record | C1-D06 |
| `company_id` | Many2one res.company | yes | — | index; restrict | this record | C4-D04 |
| `owner_user_id` | Many2one res.users | no | — | Steward responsible | this record | C1-D08 |
| `current_version_id` | Many2one sipanel.scope.version | no | readonly; written only by `action_release` inside the release transaction | restrict; must belong to same scope and be RELEASED | release action | C1-D02, C1-D09 |
| `version_ids` | One2many sipanel.scope.version | — | — | — | children | C1-D02 |
| `archived` | Boolean | — | default False | archive blocks new selection; never unlink used identity | this record | C1-D08 |
| `active` | Boolean | — | default True | mirrors `archived` for native archive UX; both never delete | this record | C1-D08 |
| `duplicated_from_id` | Many2one sipanel.scope | no | readonly | restrict; set only by "Duplicate as New Scope" | duplicate action | C1-D07 |
| `usage_count` | Integer | — | compute non-stored, ACL-filtered count of `sipanel.quote.scope` by `source_scope_id` | count uses `sudo=False` so unauthorized documents are not revealed | quote scopes | C1-D08 |
| `favorite_user_ids` | Many2many res.users via sipanel.scope.favorite | — | — | personal favorites resolve to `current_version_id` | favorites | C4-D03 |

Constraints: `unlink` is refused when any version is RELEASED/SUPERSEDED or any `sipanel.quote.scope` references the identity (ondelete restrict + `@api.ondelete`). Archive is the only exit.

### 1.2 `sipanel.scope.version` — Scope version (Master Recipe container)

Purpose: versioned content of a Scope: labels, unit, applicability, anchor mapping and the single logical Recipe (C1-D02, C2-D01). Inherits `mail.thread`.

| Field | Type | Required | Readonly / compute | Constraints / index | Source of truth | Decision |
|---|---|---|---|---|---|---|
| `scope_id` | Many2one sipanel.scope | yes | readonly | restrict; index | this record | C1-D02 |
| `company_id` | Many2one res.company | yes | related stored from scope | must equal scope company | scope | C4-D04 |
| `revision` | Integer | yes | readonly; assigned at create = max+1 | unique (`scope_id`,`revision`); > 0 | create | C1-D02 |
| `parent_version_id` | Many2one sipanel.scope.version | no | readonly | restrict; same scope | New Version action | C1-D07 |
| `state` | Selection DRAFT/RELEASED/SUPERSEDED | yes | readonly; only `action_release` and the release transaction change it | no transition RELEASED→DRAFT; write on RELEASED/SUPERSEDED content fields raises (also via import/RPC) | release action | C1-D02, C1-D09 |
| `label_fa` | Char | release-required | — | approved customer label (Persian primary) | this record | C1-D06, BQ-01 |
| `label_en` | Char | no (Draft may be empty; missing target language blocks Send at quote level) | — | — | this record | BQ-01 |
| `customer_description_fa` / `customer_description_en` | Text | no | — | versioned; translations never live-translated | this record | C1-D06 |
| `internal_description` | Text | no | — | never in customer payload | this record | C0-D09 |
| `base_uom_id` | Many2one uom.uom | yes | readonly when RELEASED | restrict; must be active | this record | C1-D04 |
| `dimension_family` | Selection COUNT/LENGTH/AREA/VOLUME/MASS/TIME/OTHER | yes | — | engine-owned family (no `uom.category` in build, SV-10) | this record | C1-D04 |
| `anchor_product_id` | Many2one product.product | release-required | — | restrict; must be saleable, active, not combo type (SV-06) | this record | C1-D05 |
| `anchor_owner_mode` | Selection NATIVE_LINE_OWNER/COMPONENT_BRIDGE_OWNER | release-required | — | if COMPONENT_BRIDGE_OWNER: anchor product must be service with `service_tracking` in {no, project_only} (SV-13); `task_*` tracking refused | this record | C1-D05, BQ-07 |
| `all_systems` | Boolean | yes | default False | explicit ALL; empty `system_ids` with `all_systems=False` blocks release | this record | C1-D03 |
| `system_ids` | Many2many account.analytic.account | no | — | domain: plan = configured System plan (`sipanel_scope.system_plan_id`) | this record | C1-D03, B-03 |
| `note_template` | Text | no | — | deterministic generated-note skeleton; approved labels only | this record | C0-D09 |
| `default_responsibility` / `default_placement` / `default_certainty` / `default_disclosure` | Selection (AM-02 axes) | yes | defaults SIPANEL/INCLUDED_PARENT/FIRM/CUSTOMER_ELIGIBLE | preset label derived, see 2.3 | this record | C0-D10, AM-02 |
| `recipe_line_ids` | One2many sipanel.scope.recipe.line | — | — | — | children | C2-D01 |
| `released_by_id` / `released_date` | Many2one res.users / Datetime | — | readonly | set in release transaction | release action | C1-D09 |
| `release_checksum` | Char | — | readonly | SHA-256 of canonical JSON of version+lines at release; immutable evidence | release action | C1-D02 |
| `superseded_by_id` | Many2one sipanel.scope.version | — | readonly | restrict | release of successor | C1-D02 |

Release transaction (`action_release`): `scope_id.lock_for_update()` (SV-07, catch `LockError` → retry bounded, TBE count) → run release gates (unit, anchor mapping, applicability, recipe integrity, percent bases acyclic, labels) → set previous current to SUPERSEDED → set this to RELEASED → write `scope_id.current_version_id` — all in one DB transaction; failure rolls back entirely (C1-D09).

### 1.3 `sipanel.scope.recipe.line` — Recipe line (Master occurrence)

Purpose: one estimated requirement occurrence in a version (C0-D03, C2-D02). No mail.thread (child of version, audited through version chatter).

| Field | Type | Required | Readonly / compute | Constraints / index | Source of truth | Decision |
|---|---|---|---|---|---|---|
| `version_id` | Many2one sipanel.scope.version | yes | readonly | cascade only while version DRAFT (enforced in `_unlink_except_released`); index | this record | C2-D01 |
| `company_id` | Many2one res.company | yes | related stored | equals version company | version | C4-D04 |
| `occurrence_key` | Char (UUID4) | yes | readonly default uuid | unique SQL; carried into snapshots as `source_occurrence_key` | create | C2-D02 |
| `sequence` | Integer | yes | default 10 | — | this record | C7-D01 |
| `kind` | Selection PRODUCT/ESTIMATE_ONLY | yes | — | PRODUCT ⇒ `product_id` required; ESTIMATE_ONLY ⇒ `resolution_owner_id`, `resolution_note` required | this record | C0-D06 |
| `product_id` | Many2one product.product | conditional | — | restrict; canonical variant, not template; must be active | this record | C0-D06 |
| `internal_description` | Text | ESTIMATE_ONLY required | — | never customer-facing | this record | C0-D09 |
| `customer_label_fa` / `customer_label_en` | Char | no | — | only source of customer wording; empty ⇒ skipped in generated note with warning | this record | C0-D09, C7-D01 |
| `customer_eligible` | Boolean | — | default False | INTERNAL_ONLY disclosure forces False | this record | C0-D09 |
| `spec_json` | Json | no | — | structured key/value with unit, drawing revision; no executable expression; validated schema | this record | C2-D02 |
| `uom_id` | Many2one uom.uom | yes | — | restrict; active; `dimension_family` compatible with basis | this record | C1-D04 |
| `dimension_family` | Selection (as 1.2) | yes | — | engine check | this record | C1-D04 |
| `basis` | Selection PER_SCOPE_QTY/FIXED/MANUAL/PERCENT_OF_QUANTITY/PERCENT_OF_COST | yes | — | the five frozen bases only | this record | C0-D07 |
| `rate` | Float (digits 0 stored) | PER_SCOPE_QTY required | — | ≥ 0 | this record | C0-D07 |
| `fixed_qty` | Float | FIXED required | — | ≥ 0 | this record | C0-D07 |
| `percent` | Float | PERCENT_* required | — | 0 < percent; percent-of-percent forbidden | this record | C2-D03, AM-04 |
| `base_line_ids` | Many2many sipanel.scope.recipe.line (rel `sipanel_recipe_percent_base_rel`) | PERCENT_* required | — | same version; no self; no PERCENT_* member; acyclic (checked at write and release); PERCENT_OF_QUANTITY members share `dimension_family` | this record | C2-D03, AM-04 |
| `rounding_increment` | Float | yes | default 0 (= no rounding) | ≥ 0 | this record | C1-D04 |
| `rounding_mode` | Selection NONE/UP/NEAREST/DOWN | yes | default NONE | — | this record | C1-D04 |
| `activity_id` | Many2one account.analytic.account | release-required for executable kinds | — | domain: plan = `sipanel_scope.activity_plan_id` | this record | C0-D11, C2-D04 |
| `execution_mode` | Selection STOCK_ISSUE/BUY_DIRECT/MANUFACTURE/LABOUR/EQUIPMENT_SERVICE/NATIVE_ANCHOR_COVERED/NO_ACTION | yes | — | NO_ACTION requires `no_action_reason` | this record | C2-D04 |
| `no_action_reason` | Selection CUSTOMER_RESPONSIBILITY/ALLOWANCE/DECLINED_OPTION/COVERED_COST | conditional | — | — | this record | C2-D04 |
| `cost_policy` | Selection PRODUCT_COST/MANUAL_ESTIMATE/DERIVED | yes | DERIVED forced when basis = PERCENT_OF_COST | direct vs derived exclusive | this record | C0-D08, AM-04 |
| `manual_cost_default` | Monetary | MANUAL_ESTIMATE optional | — | company currency; copied to snapshot as MANUAL_ESTIMATE with provenance | this record | C0-D08 |
| `responsibility` / `placement` / `certainty` / `disclosure` | Selection (AM-02 axes) | yes | default from version | preset label computed | this record | AM-02 |
| `resolution_owner_id` | Many2one res.users | ESTIMATE_ONLY required | — | — | this record | C0-D06 |
| `resolution_note` | Text | ESTIMATE_ONLY required | — | — | this record | C0-D06 |

Write guard: any write to a line whose version is RELEASED/SUPERSEDED raises `UserError` regardless of channel (UI, import, RPC) — implemented in `write`/`create`/`unlink`, not in views only (C1-D02, PT-24).

### 1.4 `sipanel.scope.audit.event` — Audit event

Purpose: append-only application audit for privileged/structural actions (C4-D04). No mail.thread.

| Field | Type | Required | Readonly / compute | Constraints / index | Source of truth | Decision |
|---|---|---|---|---|---|---|
| `company_id` | Many2one res.company | yes | readonly | index | actor context | C4-D04 |
| `res_model` / `res_id` | Char / Integer | yes | readonly | index (`res_model`,`res_id`) | action | C4-D04 |
| `action` | Char | yes | readonly | e.g. `release`, `seal`, `portal_qty_transition`, `override`, `waiver`, `split`, `release_execution` | action | C4-D04 |
| `actor_user_id` | Many2one res.users | yes | readonly default uid | — | action | C4-D04 |
| `event_date` | Datetime | yes | readonly default now | — | action | C4-D04 |
| `before_json` / `after_json` | Json | no | readonly | cost payload only readable by cost viewer group (field group) | action | C4-D04 |
| `reason` | Text | conditional | readonly | required for override/waiver/preset change | action | C4-D02, BQ-02 |
| `revision_ref` | Char | no | readonly | quote revision or version identifier | action | C3-D03 |
| `correlation_uid` | Char | yes | readonly | groups events of one action/batch | action | C8-D02 |

`write` and `unlink` raise for every user (append-only application policy; explicitly not tamper-proof against a DB administrator — Master C10).

### 1.5 `sipanel.scope.favorite` — Personal favorite

| Field | Type | Required | Readonly / compute | Constraints / index | Source of truth | Decision |
|---|---|---|---|---|---|---|
| `user_id` | Many2one res.users | yes | default uid | unique (`user_id`,`scope_id`); record rule user own only | user | C4-D03 |
| `scope_id` | Many2one sipanel.scope | yes | — | cascade (favorite is disposable) | user | C4-D03 |
| `company_id` | Many2one res.company | yes | related from scope | — | scope | — |

### 1.6 Settings parameters (`ir.config_parameter`, company-scoped via `res.config.settings`)

| Key | Meaning | Constraint |
|---|---|---|
| `sipanel_scope.system_plan_id` | `account.analytic.plan` used as System dimension | must exist before any version release with `all_systems=False`; B-03 |
| `sipanel_scope.activity_plan_id` | `account.analytic.plan` used as Activity dimension | as above |
| `sipanel_scope.release_retry_count` | bounded retry count for `LockError` | integer TBE, default 3 |
| `sipanel_scope.company_currency_only` | BQ-09 switch | default True; may not be set False in MVP without Finance change record |

---

## Module 2 — `sipanel_sale_scope`

Depends on: `sipanel_commercial_scope_core`, `sale_management` (IF-02, SV-02/SV-03), `portal`.

### 2.1 `sipanel.quote.scope` — Quote Scope (aggregate identity on a quotation)

Purpose: stable identity of one Commercial Scope instance on a `sale.order`, bound to exactly one non-display anchor line (C0-D02, AM-01-R2). Inherits `mail.thread`.

| Field | Type | Required | Readonly / compute | Constraints / index | Source of truth | Decision |
|---|---|---|---|---|---|---|
| `order_id` | Many2one sale.order | yes | readonly | restrict; index | this record | C0-D01 |
| `company_id` | Many2one res.company | yes | related stored from order | equals order company | order | C4-D04 |
| `scope_uid` | Char (UUID4) | yes | readonly default | unique SQL | create | C3-D01 |
| `source_scope_id` | Many2one sipanel.scope | no (ad-hoc allowed) | readonly | restrict | Add Scope action | C1-D08 |
| `source_version_id` | Many2one sipanel.scope.version | no | readonly | restrict; must have been RELEASED at add time (checked, not enforced later) | Add Scope action | C0-D04 |
| `anchor_line_id` | Many2one sale.order.line | **yes** | readonly after create | restrict; unique SQL (`anchor_line_id`); line must belong to `order_id`, have `display_type` False, `combo_item_id` False, `linked_line_id` False (SV-06); independent of computed `parent_id` (SV-04) | Add Scope action | C0-D02, AM-01-R2 |
| `optional_section_line_id` | Many2one sale.order.line | no | — | restrict; section with `is_optional` (SV-02); presentation only | operator | C6-D02 |
| `current_revision_id` | Many2one sipanel.quote.scope.revision | yes after first revision | readonly | restrict; exactly one WORKING or the latest sealed | revision actions | C3-D01 |
| `accepted_revision_id` | Many2one sipanel.quote.scope.revision | no | readonly | restrict; state ACCEPTED_SEALED | confirm/accept hook | C3-D03 |
| `acceptance_state` | Selection BASE/OFFERED/ACCEPTED/DECLINED | yes | compute stored from anchor `product_uom_qty` and optional section (qty 0 + optional ⇒ OFFERED; qty > 0 ⇒ ACCEPTED; non-optional ⇒ BASE) | transitions only through governed action (operator or guarded portal endpoint) | anchor line qty via guard | AM-01-R2 |
| `acceptance_reference` | Char | no | readonly | portal token hash or operator event id; idempotent repeated acceptance | transition | C6-D04 |
| `state` | Selection DRAFT/SENT/ACCEPTED/AMENDING/CANCELLED | yes | compute stored from revisions | — | revisions | C3-D03 |
| `revision_ids` | One2many | — | — | — | children | C3-D01 |
| `readiness_json` | Json | — | compute non-stored | grouped validation issues per stage | engine | C4-D02 |
| `system_id` | Many2one account.analytic.account | no (Draft) release-required | — | must be compatible with `source_version_id` applicability | this record | C1-D03 |

Constraints: `unlink` only while no revision is sealed and no execution batch references the scope; otherwise archive/tombstone (`active=False`) (C3-D02). Deleting or re-sequencing the anchor line or its scoped section is refused by the `sale.order.line` guard (2.7).

### 2.2 `sipanel.quote.scope.revision` — Scope revision (snapshot)

Purpose: immutable-after-seal snapshot of the Scope on the quotation (C0-D04, C3-D01). Inherits `mail.thread`.

| Field | Type | Required | Readonly / compute | Constraints / index | Source of truth | Decision |
|---|---|---|---|---|---|---|
| `quote_scope_id` | Many2one sipanel.quote.scope | yes | readonly | restrict; index | this record | C3-D01 |
| `company_id` | Many2one res.company | yes | related stored | — | quote scope | — |
| `revision` | Integer | yes | readonly | unique (`quote_scope_id`,`revision`) | create | C3-D01 |
| `state` | Selection WORKING/SENT_SEALED/ACCEPTED_SEALED | yes | readonly | forward only; sealed revisions reject content writes from any channel | seal hooks | C3-D03 |
| `prior_revision_id` | Many2one self | no | readonly | restrict | amendment action | C3-D03 |
| `language` | Selection (res.lang codes) | yes | — | must be one language; mixed-language send blocked | order partner lang at create | BQ-01, C7-D04 |
| `project_id` | Many2one project.project | no | — | restrict | order context | C0-D11 |
| `system_id` | Many2one account.analytic.account | no | — | copied from quote scope at seal | quote scope | C1-D03 |
| `scope_qty` | Float | yes | WORKING: compute from `anchor_line_id.product_uom_qty` normalized to `base_uom_id`; sealed: stored frozen | ≥ 0; qty 0 only for OFFERED or Draft | anchor line (Draft) / this record (sealed) | C3-D01 |
| `quote_uom_id` / `base_uom_id` / `uom_factor` | Many2one / Many2one / Float | yes | readonly | factor snapshot; incompatible family refused at add time | Add Scope | C1-D04 |
| `label_fa` / `label_en` / `customer_description_*` | Char / Text | — | readonly copies | version-independent copies | source version at add | C0-D04 |
| `spec_json` | Json | no | — | scope-level specs | operator | C2-D02 |
| `commercial_projection_json` | Json | — | WORKING: compute non-stored from anchor line (price_unit, discount, tax_ids, price_subtotal, currency); sealed: stored | native line remains authoritative in Draft (C3-D01) | anchor line / seal | C3-D01 |
| `direct_cost_total` | Monetary | — | compute stored | sum of eligible direct component `cost_amount` | components | C0-D08 |
| `derived_cost_total` | Monetary | — | compute stored | sum of derived amounts | components | AM-04 |
| `eligible_cost_total` | Monetary | — | compute stored | direct + derived, excluding NOT_APPLICABLE/removed/transferred | components | C0-D08 |
| `missing_cost_count` | Integer | — | compute stored | components with `cost_status=MISSING` and executable | components | C0-D08 |
| `net_revenue_projection` | Monetary | — | compute (Draft) / stored (sealed) | untaxed subtotal after discount; company currency | anchor line | C5-D02 |
| `margin_amount` | Monetary | — | compute | R − C | — | C5-D02 |
| `margin_percent` | Float | — | compute | (R − C)/R×100; R = 0 ⇒ null shown "N/A" | — | C5-D02 |
| `fx_source_currency_id` / `fx_rate` / `fx_date` / `fx_source` | Many2one / Float / Date / Char | yes | readonly | MVP: rate = 1.0 only because quote currency == company currency (checked, not assumed — SV-12 fallback must never be the reason) | seal / add | BQ-09, C5-D02 |
| `generated_note` | Text | — | compute stored on demand (`action_regenerate_note`) | derived only from customer-eligible components + approved labels | engine | C0-D09 |
| `final_note` | Text | — | — | authoritative customer text | operator | C0-D09 |
| `note_manually_edited` | Boolean | — | set when `final_note` written by user | independent flag | operator | C0-D09 |
| `note_stale` | Boolean | — | compute stored: `note_fingerprint` ≠ current eligible-component fingerprint | independent flag | engine | C0-D09 |
| `note_reviewed` | Boolean | — | reset to False when stale becomes True | independent flag | operator | C7-D01 |
| `note_fingerprint` | Char | — | readonly | SHA-256 of eligible component payload at last generation/review | engine | C7-D01 |
| `review_user_id` / `review_date` | Many2one / Datetime | — | readonly | — | operator | C7-D01 |
| `sealed_hash` | Char | sealed-required | readonly | SHA-256 of canonical revision payload (header, commercial projection, components, notes, language) | seal hook (`action_quotation_send`/`portal_quote_accept`/`action_confirm`, SV-14) | C3-D03, C7-D04 |
| `sealed_date` / `sealed_by_id` | Datetime / Many2one | — | readonly | — | seal | C3-D03 |
| `artifact_ids` | One2many sipanel.quote.scope.artifact | — | — | — | children | C7-D04 |
| `component_ids` | One2many sipanel.quote.scope.component | — | — | — | children | C3-D01 |

Constraints: writes to any field except `note_reviewed`, `review_*`, `state` (forward) and `artifact_ids` on a sealed revision raise from `write` (PT-24). `unlink` refused when sealed.

### 2.3 `sipanel.quote.scope.component` — Component snapshot (occurrence)

Purpose: snapshot of one recipe occurrence in a revision, with quantity engine results, cost snapshot, treatment axes and execution intent (C0-D03, C2-D03, C5-D01, C6-D01).

| Field | Type | Required | Readonly / compute | Constraints / index | Source of truth | Decision |
|---|---|---|---|---|---|---|
| `revision_id` | Many2one sipanel.quote.scope.revision | yes | readonly | restrict; index | this record | C3-D01 |
| `company_id` | Many2one res.company | yes | related stored | — | revision | — |
| `occurrence_uid` | Char (UUID4) | yes | readonly default | unique SQL; stable across revisions of the same scope (copied), new UUID on split destination | create | C2-D02, C3-D04 |
| `source_occurrence_key` | Char | no | readonly | recipe line `occurrence_key` at add time | Add Scope | C0-D04 |
| `source_line_id` | Many2one sipanel.scope.recipe.line | no | readonly | restrict; trace only, never live-related | Add Scope | C0-D04 |
| `copy_from_id` | Many2one self | no | readonly | restrict; previous-revision component | amendment/duplicate | C3-D02 |
| `moved_from_id` / `moved_to_id` | Many2one self | no | readonly | restrict; split lineage; `remainder + moved = original final_qty` checked | split action | C3-D04 |
| `origin` | Selection MASTER/ADDED/OVERRIDDEN/REMOVED/TRANSFERRED/SPLIT_REMAINDER/SPLIT_DESTINATION | yes | readonly | — | actions | C2-D02 |
| `active_state` | Selection ACTIVE/TOMBSTONE | yes | default ACTIVE | tombstone keeps trace and invalidates note | actions | C2-D02 |
| `sequence` | Integer | yes | — | — | operator | C7-D01 |
| `kind` | Selection PRODUCT/ESTIMATE_ONLY | yes | — | as 1.3 | snapshot | C0-D06 |
| `product_id` | Many2one product.product | conditional | — | restrict | snapshot / resolve action | C0-D06 |
| `description` | Text | — | — | snapshot copy | snapshot | C0-D04 |
| `customer_label_fa` / `customer_label_en` | Char | — | — | snapshot copy; only eligible in note | snapshot | C0-D09 |
| `spec_json` | Json | — | — | order-specific specification | operator | C2-D02 |
| `uom_id` | Many2one uom.uom | yes | — | restrict | snapshot | C1-D04 |
| `uom_name_snapshot` | Char | yes | readonly | label frozen for history | snapshot | C3-D01 |
| `dimension_family` | Selection | yes | — | — | snapshot | C1-D04 |
| `basis` | Selection (five) | yes | — | — | snapshot | C0-D07 |
| `rate` / `fixed_qty` / `percent` | Float | conditional | — | as 1.3 | snapshot / operator | C0-D07 |
| `base_component_ids` | Many2many self (rel `sipanel_component_percent_base_rel`) | PERCENT_* required | — | same revision; no self; no PERCENT_*; no TOMBSTONE; no TRANSFERRED; acyclic; family-compatible for quantity percent — a dangling base is a save error, not a warning | operator | C2-D03, C3-D04 |
| `rounding_increment` / `rounding_mode` | Float / Selection | yes | — | — | snapshot | C1-D04 |
| `calc_raw_qty` | Float | — | compute stored by engine | before rounding | engine | C0-D07 |
| `calc_rounded_qty` | Float | — | compute stored | after per-line rounding | engine | C1-D04 |
| `final_qty` | Float | yes | = `calc_rounded_qty` unless `qty_override` | ≥ 0; MANUAL basis writes here directly | engine / operator | C0-D07 |
| `qty_override` | Boolean | — | — | — | operator | C0-D07 |
| `override_reason` | Text | required when `qty_override` | — | field group cost viewer? no — operator group; audited | operator | C0-D07 |
| `override_stale` | Boolean | — | compute stored: driver changed since override | never auto-reset; reviewer action clears | engine | C0-D07 |
| `override_before_qty` / `override_after_qty` | Float | — | readonly | — | override action | C0-D07 |
| `cost_source` | Selection PRODUCT_COST/MANUAL_ESTIMATE/DERIVED/NOT_APPLICABLE | yes | DERIVED iff basis PERCENT_OF_COST; NOT_APPLICABLE iff responsibility=CUSTOMER | exclusive | engine | C0-D08, AM-04 |
| `unit_cost` | Monetary | — | readonly for PRODUCT_COST | company currency; per `cost_uom_id` | snapshot / operator | C5-D01 |
| `cost_uom_id` / `cost_uom_factor` | Many2one / Float | PRODUCT_COST required | readonly | source product UoM and conversion factor to `uom_id` (PT-26) | snapshot | C5-D01 |
| `cost_source_date` | Datetime | — | readonly | — | snapshot | C0-D08 |
| `cost_source_company_id` | Many2one res.company | — | readonly | company used to read `standard_price` (company_dependent, v0.10 evidence) | snapshot | C5-D01 |
| `product_value_id` | Many2one product.value | no | readonly | restrict; latest manual cost history row at snapshot time when present (IF-01: model) | snapshot | C5-D01 |
| `manual_cost_user_id` / `manual_cost_date` / `manual_cost_reason` | Many2one / Datetime / Text | MANUAL_ESTIMATE required | — | never overwritten by refresh | operator | C0-D08 |
| `cost_status` | Selection KNOWN/KNOWN_ZERO/MISSING/NOT_APPLICABLE | yes | compute stored | KNOWN_ZERO requires `known_zero_reason` | engine / operator | C0-D08 |
| `known_zero_reason` | Text | conditional | — | — | operator | C0-D08 |
| `cost_amount` | Monetary | — | compute stored: `final_qty × unit_cost × cost_uom_factor` for direct; `Σ base cost_amount × percent/100` for derived | company currency | engine | C0-D08, AM-04 |
| `eligible_for_rollup` | Boolean | — | compute stored | False for CUSTOMER responsibility, TOMBSTONE, TRANSFERRED, OFFERED-not-accepted parent | engine | C0-D08 |
| `responsibility` | Selection SIPANEL/CUSTOMER | yes | — | AM-02 axis | operator | C6-D01 |
| `placement` | Selection INCLUDED_PARENT/OWN_LINE/NO_CUSTOMER_LINE | yes | — | OWN_LINE ⇒ must be split into its own quote scope (SEPARATELY_BILLABLE) | operator | C6-D01 |
| `acceptance` | Selection BASE/OFFERED/ACCEPTED/DECLINED | yes | related stored from parent quote scope unless OWN_LINE | — | quote scope | AM-01-R2 |
| `certainty` | Selection FIRM/PROVISIONAL | yes | — | PROVISIONAL ⇒ `provisional_basis` required | operator | C6-D03, BQ-03 |
| `provisional_basis` | Text | conditional | — | customer-visible basis/assumption | operator | C6-D03 |
| `disclosure` | Selection CUSTOMER_ELIGIBLE/INTERNAL_ONLY | yes | — | INTERNAL_ONLY ⇒ excluded from every customer payload | operator | C0-D10 |
| `treatment_preset` | Selection INCLUDED/SEPARATELY_BILLABLE/OPTIONAL/PROVISIONAL/CUSTOMER_SCOPE/INTERNAL_ONLY/CUSTOM | — | compute stored from axes; preset change audited | six frozen labels as presets | engine | C0-D10, AM-02 |
| `activity_id` / `system_id` | Many2one account.analytic.account | release-required | — | system override must be compatible with scope system + reason | operator | C0-D11 |
| `execution_mode` | Selection (as 1.3) | yes | — | — | snapshot / operator | C2-D04 |
| `execution_owner` | Selection NATIVE_LINE_OWNER/COMPONENT_BRIDGE_OWNER/NONE | yes | compute stored from version `anchor_owner_mode` and mode | — | engine | C8-D01 |
| `no_action_reason` | Selection | conditional | — | — | operator | C2-D04 |
| `resolution_owner_id` / `resolution_note` / `resolution_state` | Many2one / Text / Selection OPEN/RESOLVED_PRODUCT/APPROVED_NEW_PRODUCT/ALLOWANCE/CUSTOMER/DEFERRED | ESTIMATE_ONLY required | — | Release Execution refuses OPEN | operator | C0-D06 |
| `stale_cost` | Boolean | — | compute non-stored: `cost_source_date` older than TBE threshold — displayed only, never a gate in MVP | TBE | engine | C5-D04 |

Constraints: sealed revision ⇒ all component writes refused (inherits 2.2 guard). `unlink` refused; use TOMBSTONE.

### 2.4 `sipanel.quote.scope.artifact` — Sealed customer artifact

| Field | Type | Required | Readonly / compute | Constraints / index | Source of truth | Decision |
|---|---|---|---|---|---|---|
| `revision_id` | Many2one revision | yes | readonly | restrict; index | seal | C7-D04 |
| `company_id` | Many2one | yes | related stored | — | revision | — |
| `kind` | Selection PDF/PORTAL_HTML/TEXT | yes | readonly | — | seal | C7-D04 |
| `language` | Selection | yes | readonly | one language per artifact | seal | BQ-01 |
| `attachment_id` | Many2one ir.attachment | PDF required | readonly | restrict; `res_model` = this model; portal access via `sipanel_sale_scope` rule on own sealed artifacts only | seal | C7-D03 |
| `content_hash` | Char | yes | readonly | SHA-256 of bytes | seal | C7-D04 |
| `amount_untaxed` / `amount_total` / `currency_id` | Monetary / Many2one | yes | readonly | frozen values at send | seal | C7-D04 |
| `sent_date` / `sent_by_id` | Datetime / Many2one | yes | readonly | — | seal | C3-D03 |
| `acceptance_reference` | Char | no | readonly | links portal accept event | accept | C7-D04 |

Append-only (`write`/`unlink` raise).

### 2.5 `sipanel.quote.waiver` — Commercial waiver (BQ-02)

| Field | Type | Required | Readonly / compute | Constraints / index | Source of truth | Decision |
|---|---|---|---|---|---|---|
| `revision_id` | Many2one revision | yes | readonly | restrict | operator | BQ-02 |
| `company_id` | Many2one | yes | related stored | — | — | — |
| `waiver_type` | Selection NEGATIVE_MARGIN/MISSING_ESTIMATE/BELOW_MIN_MARGIN | yes | — | thresholds TBE; waiver never bypasses ACL, duplicate keys, wrong company or arithmetic errors | operator | C4-D02 |
| `reason` | Text | yes | — | mandatory | operator | BQ-02 |
| `sales_approver_id` / `sales_approved_date` | Many2one / Datetime | yes | readonly; only `group_scope_waiver_sales` may set | — | approver | BQ-02=B |
| `finance_approver_id` / `finance_approved_date` | Many2one / Datetime | yes | readonly; only `group_scope_waiver_finance` may set | joint approval required before Send (BQ-02=B, later unsigned instruction; worksheet selection was A) | approver | BQ-02 |
| `state` | Selection PENDING/APPROVED/REJECTED | yes | compute stored: APPROVED only when both approvers set | — | engine | BQ-02 |

### 2.6 Inherited fields on `sale.order`

| Field | Type | Readonly / compute | Constraints | Source of truth | Decision |
|---|---|---|---|---|---|
| `sipanel_quote_scope_ids` | One2many sipanel.quote.scope | — | — | children | C0-D02 |
| `sipanel_scope_count` | Integer | compute | — | — | C4-D01 |
| `sipanel_has_scopes` | Boolean | compute stored | used by guards and views; ordinary orders untouched when False (PT-31) | — | C0-D01 |
| `sipanel_current_seal_hash` | Char | readonly | hash of all current sealed revisions at last send; mismatch on accept/confirm ⇒ block with diff | seal hook | C3-D03 |
| `sipanel_company_currency_only_check` | Boolean | compute: `currency_id == company_id.currency_id` | when False and `sipanel_has_scopes`: `action_quotation_send`/`action_confirm` raise (BQ-09, B-06); native fallback to 1.0 (SV-12) never reached | — | BQ-09 |
| `sipanel_readiness_state` | Selection OK/WARNINGS/BLOCKED | compute | Send/Confirm gates | engine | C4-D02 |
| `sipanel_execution_batch_ids` | One2many (added by module 3) | — | — | — | C8-D01 |

Hook overrides (no core patch, SV-14): `action_quotation_send` (seal + artifact), `action_quotation_sent`, `action_confirm` (revision match, accepted revision set, owner registry snapshot), `_action_cancel` (no deletion; amendment delta), `copy_data` (copy latest revision as independent WORKING; drop acceptances/artifacts/idempotency keys/execution links), `write` (company-currency guard when scoped).

### 2.7 Inherited fields on `sale.order.line`

| Field | Type | Readonly / compute | Constraints | Source of truth | Decision |
|---|---|---|---|---|---|
| `sipanel_quote_scope_id` | One2many→Many2one-like (One2many with limit 1 semantics, inverse of `anchor_line_id`) | — | one scope per line (unique on scope side) | quote scope | C0-D02 |
| `sipanel_is_anchor` | Boolean | compute stored | — | — | AM-01-R2 |
| `sipanel_is_scoped_section` | Boolean | compute stored: section/subsection referenced by `optional_section_line_id` or containing an anchor by current `parent_id` at seal time (frozen list stored on revision) | guard input | — | AM-01-R2 |
| `sipanel_guard_state` | Selection FREE/SEALED/ACCEPTED | compute stored from linked scope revision | — | — | C3-D03 |

Guards implemented in `write`/`unlink`/`_can_be_edited_on_portal` (SV-03, SV-05, IF-03):

- `unlink` of an anchor line, or of a section/subsection flagged `sipanel_is_scoped_section`, is refused while any linked revision is sealed — this closes the native "Sections and Notes can always be deleted" path (SV-05).
- `write` of `sequence`/`display_type` on scoped sections and of `product_id`/`product_uom_id`/`display_type`/`linked_line_id` on anchor lines is refused while sealed.
- `write` of `product_uom_qty` on an anchor line of an OFFERED scope (operator UI or portal `update_line_dict`, SV-03) is routed through `sipanel.quote.scope.action_transition_acceptance()`: requires `current_revision_id.state == SENT_SEALED`, requires hash match with `sipanel_current_seal_hash`, applies exactly one transition, triggers native tax/pricelist recompute, writes an audit event and creates at most one accepted delta. Stale link ⇒ refuse.
- Combo item lines and lines with `linked_line_id` can never become anchors (SV-06).

---

## Module 3 — `sipanel_scope_execution`

Depends on: `sipanel_sale_scope`, `sale_stock`, `sale_project`, `sale_purchase`, `sale_mrp`, `sale_timesheet`, `purchase`, `stock`, `mrp`, `project`, `hr_timesheet`.

### 3.1 `sipanel.execution.owner.rule` — Owner registry

Purpose: declares, per anchor product / service tracking / route, which owner creates demand (C8-D01, BQ-05, BQ-07, SV-13).

| Field | Type | Required | Readonly / compute | Constraints / index | Source of truth | Decision |
|---|---|---|---|---|---|---|
| `company_id` | Many2one | yes | — | — | config | — |
| `product_id` | Many2one product.product | no | — | restrict; blank = default rule | config | C1-D05 |
| `service_tracking` | Selection no/task_global_project/task_in_project/project_only | no | — | matches `product.template.service_tracking` (SV-13) | config | BQ-07 |
| `route_kind` | Selection STOCK_RULE/KIT_EXPLOSION/PURCHASE_SERVICE/PROJECT_TASK/NONE | yes | — | maps to native hooks `_action_launch_stock_rule`, `sale_mrp` phantom explosion, `_purchase_service_generation`, `_timesheet_service_generation` | config | C8-D01 |
| `owner` | Selection NATIVE_LINE_OWNER/COMPONENT_BRIDGE_OWNER | yes | — | COMPONENT_BRIDGE_OWNER requires `route_kind` in {NONE, PROJECT_TASK(project_only)} | config | C8-D01 |
| `active` / `sequence` | Boolean / Integer | — | — | first match wins | config | — |

Release of a version with `anchor_owner_mode = COMPONENT_BRIDGE_OWNER` requires a matching rule or the default rule to resolve to COMPONENT_BRIDGE_OWNER; otherwise release is blocked (C1-D05).

### 3.2 `sipanel.execution.batch` — Release Execution batch

Inherits `mail.thread`.

| Field | Type | Required | Readonly / compute | Constraints / index | Source of truth | Decision |
|---|---|---|---|---|---|---|
| `order_id` | Many2one sale.order | yes | readonly | restrict | release action | C8-D01 |
| `company_id` | Many2one | yes | related stored | — | order | — |
| `accepted_revision_ids` | Many2many revision | yes | readonly | all ACCEPTED_SEALED | release action | C8-D01 |
| `action_uid` | Char (UUID4) | yes | readonly | **unique SQL (`order_id`,`revision_set_hash`,`action_uid`)** — batch key | release action | C8-D02 |
| `revision_set_hash` | Char | yes | readonly | hash of sorted accepted revision ids | release action | C8-D02 |
| `state` | Selection PLANNED/VALIDATED/RELEASED/FAILED | yes | readonly | FAILED ⇒ no partially committed targets (single transaction) | engine | C8-D02 |
| `requested_by_id` / `requested_date` / `released_by_id` / `released_date` | Many2one / Datetime | — | readonly | — | engine | C8-D01 |
| `error_summary` | Text | — | readonly | redacted (no vendor/contact data) | engine | C8-D02 |
| `retry_count` | Integer | — | readonly | bounded by `sipanel_scope.release_retry_count` | engine | C8-D02, SV-07 |
| `demand_ids` | One2many | — | — | — | children | C8-D02 |

`action_release_execution`: `order_id.lock_for_update()` (SV-07); on `LockError` retry up to bound then return existing batch/links; preflight all demands; create/link in one transaction; no vendor email/RFQ submission inside the transaction.

### 3.3 `sipanel.execution.demand` — Execution demand

| Field | Type | Required | Readonly / compute | Constraints / index | Source of truth | Decision |
|---|---|---|---|---|---|---|
| `batch_id` | Many2one batch | yes | readonly | restrict | batch | C8-D02 |
| `company_id` | Many2one | yes | related stored | — | batch | — |
| `component_id` | Many2one sipanel.quote.scope.component | yes | readonly | restrict; component must be in an ACCEPTED_SEALED revision, `eligible_for_rollup`, executable mode, `resolution_state ≠ OPEN` | batch | C8-D01 |
| `delta_uid` | Char | yes | readonly | authorized delta identity (initial release or accepted amendment) | batch | C8-D04 |
| `execution_mode` | Selection | yes | readonly | copied | component | C2-D04 |
| `owner` | Selection NATIVE_LINE_OWNER/COMPONENT_BRIDGE_OWNER | yes | readonly | NATIVE_LINE_OWNER demands are LINKED only, never CREATED | owner registry | C8-D01 |
| `demand_key` | Char | yes | readonly | **unique SQL** = hash(`component_id.occurrence_uid`,`delta_uid`,`execution_mode`,`owner`) | engine | C8-D02 |
| `normalized_qty` / `uom_id` | Float / Many2one | yes | readonly | qty in component UoM; never re-rounded by procurement pack/MOQ | component | C0-D07 |
| `product_id` | Many2one product.product | yes for executable | readonly | restrict | component | C0-D06 |
| `project_id` / `system_id` / `activity_id` | Many2one | release-required | readonly | dimensions passed to native carriers where supported | component/revision | C0-D11 |
| `requested_date` | Date | no | — | — | operator | C8-D03 |
| `state` | Selection PLANNED/LINKED/CREATED/IN_PROGRESS/FULFILLED/CANCELLED | yes | compute stored from targets | — | targets | C8-D04 |
| `cancelled_by_delta_uid` / `reversal_of_id` | Char / Many2one self | no | readonly | explicit lineage; no deletion of done docs | amendment | C8-D04 |
| `target_ids` | One2many | — | — | — | children | C8-D03 |

### 3.4 `sipanel.execution.target` — Target link / allocation

| Field | Type | Required | Readonly / compute | Constraints / index | Source of truth | Decision |
|---|---|---|---|---|---|---|
| `demand_id` | Many2one demand | yes | readonly | restrict | adapter | C8-D03 |
| `company_id` | Many2one | yes | related stored | must equal target record company (checked) | demand | — |
| `target_model` | Selection purchase.order.line / stock.move / stock.picking / mrp.production / project.task / project.project / stock.reference / account.analytic.line | yes | readonly | whitelist only (SV-08: `stock.reference` exists; no `procurement.group`) | adapter | C8-D03 |
| `target_res_id` | Many2oneReference | yes | readonly | existence + company validated at create | adapter | C8-D03 |
| `link_kind` | Selection CREATED/LINKED_EXISTING/NATIVE_ANCHOR_COVERED | yes | readonly | — | adapter | C8-D01 |
| `allocated_qty` / `uom_id` | Float / Many2one | yes | readonly | Σ allocated per demand ≤ normalized_qty (+ accepted deltas) | adapter | C8-D03 |
| `stock_reference_id` | Many2one stock.reference | no | readonly | restrict; grouping trace (SV-08) | adapter | C8-D03 |
| `reversal_of_id` | Many2one self | no | readonly | return/cancel lineage | adapter | C8-D04 |
| `origin_label` | Char | no | readonly | label only, never a key | adapter | C8-D02 |

Unique SQL (`demand_id`,`target_model`,`target_res_id`,`link_kind`). Portal: DENY.

---

## Module 4 — `sipanel_scope_costing`

Depends on: `sipanel_scope_execution`, `stock_account`, `mrp_account`, `purchase_stock`, `account`, `hr_timesheet`, `hr_expense`, `project_account`.

### 4.1 `sipanel.cost.recognition.policy` — Route policy (BQ-04 / AM-03-R1)

| Field | Type | Required | Readonly / compute | Constraints / index | Source of truth | Decision |
|---|---|---|---|---|---|---|
| `company_id` | Many2one | yes | — | unique (`company_id`,`route`,`version`) | Finance config | BQ-04 |
| `route` | Selection SHARED_STOCK/DIRECT_PURCHASE/MFG_MATERIAL/MFG_LABOUR/SITE_LABOUR/EQUIPMENT_SERVICE/FREIGHT_LANDED/RETURN_CREDIT | yes | — | — | Finance | BQ-04 |
| `terminal_event_model` | Selection account.analytic.line / stock.move / account.move.line / hr.expense / mrp.workorder / NONE | yes | — | exactly one per route; FREIGHT_LANDED = NONE (deferred) | Finance | AM-03-R1 |
| `terminal_event_filter_json` | Json | yes | — | declarative domain fragment (e.g. analytic category, picking type ids with `analytic_costs`, journal) | Finance | BQ-04 |
| `commitment_model` | Selection purchase.order.line / NONE | — | — | shown separately, never summed | Finance | AM-03-R1 |
| `operational_qty_model` | Selection stock.move / mrp.production / account.analytic.line / NONE | — | — | quantity columns only | Finance | AM-03-R1 |
| `excluded_models_json` | Json | yes | — | explicit exclusions (duplicates) | Finance | BQ-04 |
| `wip_reporting` | Selection TERMINAL_ONLY/WIP_SEPARATE | yes | — | Finance choice 2 (MISSING_INPUT) | Finance | BQ-04 |
| `version` / `approved_by_id` / `approved_date` / `state` DRAFT/APPROVED/SUPERSEDED | Integer / Many2one / Date / Selection | — | readonly after approval | only APPROVED policies feed events; approval user must be in `group_scope_finance` | Finance | BQ-04 |

No event may be computed without an APPROVED policy; until Finance signs, module 4 stays installable but produces zero recognised events (all actual shown as UNALLOCATED/UNPOLICIED).

### 4.2 `sipanel.actual.cost.event` — Selected recognised event (read-only projection record)

| Field | Type | Required | Readonly / compute | Constraints / index | Source of truth | Decision |
|---|---|---|---|---|---|---|
| `company_id` | Many2one | yes | readonly | — | source | — |
| `policy_id` | Many2one policy | yes | readonly | restrict | projection | BQ-04 |
| `source_model` | Selection (as policy) | yes | readonly | — | native | C8-D04 |
| `source_res_id` | Integer | yes | readonly | — | native | C8-D04 |
| `component_type` | Selection MATERIAL/LABOUR/SERVICE/EQUIPMENT/ADJUSTMENT/REVENUE | yes | readonly | — | policy | C8-D04 |
| `source_key` | Char | yes | readonly | **unique SQL** (`source_model`,`source_res_id`,`component_type`,`company_id`) — one inclusion per monetary source | projection | C8-D04 |
| `amount` | Monetary (signed) | yes | readonly | company currency; from `stock.move.value` (IF-01 field, SV-09), `account.analytic.line.amount` (SV-15/SV-17), `account.move.line.balance`, `hr.expense.total_amount` | native | C8-D04 |
| `event_date` | Date | yes | readonly | — | native | C8-D04 |
| `project_id` / `system_id` / `activity_id` | Many2one | no | readonly | from native carriers (`project.project.account_id`, plan columns, `mrp.production.project_id` — SV-15) | native | C0-D11 |
| `qty` / `uom_id` / `qty_kind` | Float / Many2one / Selection CONSUMED/PRODUCED/RECEIVED/RETURNED/HOURS/NONE | — | readonly | never mixed across kinds | native | C8-D03 |
| `reversal_of_id` | Many2one self | no | readonly | credits/returns reverse the original once | projection | C8-D04 |
| `allocation_state` | Selection ALLOCATED/PARTIAL/UNALLOCATED/UNPOLICIED | yes | compute stored | visible, never hidden | allocations | BQ-06 |
| `inclusion_policy_version` | Integer | yes | readonly | — | policy | BQ-04 |

Events are created by a projection job that only **reads** native records; no journal, analytic or valuation record is ever written by this module.

### 4.3 `sipanel.actual.allocation` — Allocation of an event to demand/occurrence

| Field | Type | Required | Readonly / compute | Constraints / index | Source of truth | Decision |
|---|---|---|---|---|---|---|
| `event_id` | Many2one event | yes | readonly | restrict | projection | C8-D04 |
| `company_id` | Many2one | yes | related stored | — | event | — |
| `demand_id` | Many2one sipanel.execution.demand | no | readonly | restrict; via `sipanel.execution.target` link | projection | C8-D04 |
| `component_id` | Many2one component | no | readonly | restrict; occurrence attribution | projection | BQ-06 |
| `quote_scope_id` | Many2one quote scope | no | readonly | restrict | projection | BQ-06 |
| `allocation_basis` | Selection TARGET_LINK/DIMENSION_MATCH/MANUAL/UNALLOCATED | yes | readonly | MANUAL requires reviewer and reason | projection/reviewer | C8-D04 |
| `amount` | Monetary (signed) | yes | readonly | Σ allocations per event = event amount (SQL check on flush) | projection | C8-D04 |
| `reviewer_id` / `reason` | Many2one / Text | MANUAL required | — | audited | reviewer | C8-D04 |

### 4.4 `sipanel.scope.variance` — SQL view (read-only)

Columns: `quote_scope_id`, `accepted_revision_id`, `project_id`, `system_id`, `activity_id`, `baseline_cost` (accepted sealed `eligible_cost_total`), `forecast_cost` (latest WORKING revision, if any), `committed_amount` (open `purchase.order.line` commitments linked by targets), `recognised_cost` (Σ allocated events), `unallocated_cost` (Σ UNALLOCATED events for the project), `recognised_revenue` (posted customer invoice lines minus credits linked to anchor lines), `variance_amount` = recognised − baseline (null when baseline absent, never 0), `completeness_flag` (INCOMPLETE while any UNALLOCATED/UNPOLICIED event exists for the project). `_auto = False`; groups: `group_scope_cost_viewer`.

---

## Module 5 — `sipanel_scope_demo` (clone/test only)

No models. Data files create the synthetic C9 "متعلقات آبرو" fixture (clone-only partner/project/system, synthetic products with artificial CU costs, master V1/V2, quote qty 85 m) exactly as in Master §C9. `installable: True`, `application: False`, never listed in any Production addon set; the Production release manifest must not contain it.

---

## Cross-module SQL constraints summary

| Model | Constraint | Purpose |
|---|---|---|
| sipanel.scope | unique (`company_id`,`code`) | identity |
| sipanel.scope.version | unique (`scope_id`,`revision`); partial unique index `scope_id WHERE state='RELEASED'` | one current released version |
| sipanel.scope.recipe.line | unique (`occurrence_key`) | occurrence identity |
| sipanel.quote.scope | unique (`scope_uid`); unique (`anchor_line_id`) | one scope per anchor (C0-D02) |
| sipanel.quote.scope.revision | unique (`quote_scope_id`,`revision`); partial unique `quote_scope_id WHERE state='WORKING'` | single working revision |
| sipanel.quote.scope.component | unique (`occurrence_uid`) | occurrence identity across split/lineage |
| sipanel.execution.batch | unique (`order_id`,`revision_set_hash`,`action_uid`) | batch key (C8-D02) |
| sipanel.execution.demand | unique (`demand_key`) | one demand per (occurrence, delta, mode, owner) |
| sipanel.execution.target | unique (`demand_id`,`target_model`,`target_res_id`,`link_kind`) | no duplicate link |
| sipanel.actual.cost.event | unique (`source_model`,`source_res_id`,`component_type`,`company_id`) | one inclusion per monetary source (C8-D04) |
| sipanel.cost.recognition.policy | unique (`company_id`,`route`,`version`) | policy versioning |
| all | `company_id` NOT NULL | isolation |

`ondelete` rules: every FK from history-bearing records (versions, revisions, components, artifacts, batches, demands, targets, events, allocations) to masters (`sipanel.scope`, `sipanel.scope.version`, `product.product`, `uom.uom`, `sale.order`, `sale.order.line`, `account.analytic.account`, `project.project`, `stock.reference`, `product.value`) is `restrict`. The only `cascade` is `sipanel.scope.favorite.scope_id` and DRAFT-only recipe lines under a DRAFT version (enforced additionally by `@api.ondelete`).

## Field-level access groups

| Field family | Models | `groups=` | Rationale |
|---|---|---|---|
| `unit_cost`, `cost_amount`, `direct_cost_total`, `derived_cost_total`, `eligible_cost_total`, `margin_amount`, `margin_percent`, `net_revenue_projection`, `manual_cost_*`, `product_value_id`, `cost_source_company_id`, `stale_cost` | revision, component | `sipanel_commercial_scope_core.group_scope_cost_viewer` | cost/margin invisible to Sales without explicit grant; enforced at ORM level so RPC/export/report honour it (C4-D04, C7-D03) |
| `before_json`, `after_json` on audit events whose action touches cost | audit event | `group_scope_cost_viewer` | audit payload may embed cost |
| `override_reason`, `manual_cost_reason`, `known_zero_reason`, `waiver.reason` | component, waiver | `group_scope_estimator` (write), `group_scope_auditor` (read) | internal reasoning not customer-facing |
| all `sipanel.actual.*`, `sipanel.scope.variance`, `sipanel.cost.recognition.policy` | module 4 | `group_scope_cost_viewer` read; `group_scope_finance` write policy | actual cost is Finance-scoped |
| every SIPANEL model | all | portal users: no ACL line ⇒ DENY; only `sipanel.quote.scope.artifact` read via record rule on own sealed artifacts | C7-D03 |

Details and the role matrix: `SIPANEL_SECURITY_MATRIX.md`.

## Customer payload allowlist (what may leave the internal boundary)

Only: revision `label_*`, `customer_description_*`, `final_note` (never `generated_note` directly), component `customer_label_*` for `disclosure=CUSTOMER_ELIGIBLE` and `active_state=ACTIVE`, `final_qty`/`uom_name_snapshot` only when placement ≠ NO_CUSTOMER_LINE, `provisional_basis` for PROVISIONAL, native anchor amounts. Everything else (product codes, costs, margins, override reasons, analytic dimensions, execution modes, INTERNAL_ONLY components, resolution notes) is stripped from the payload builder, not merely hidden by QWeb/CSS (C7-D01, C0-D09).

## Migration and upgrade rules

- Initial version of all modules: `19.0.1.0.0`; no `pre-`/`post-migrate` scripts; schema creation is additive only (new tables and new nullable columns on `sale.order`/`sale.order.line`).
- No field is added to `product.template`, `product.product`, `product.category`, `uom.uom`, `stock.move`, `stock.move.line` (C0-D06, C0-D11, Master C10 deferred list). Product Master is never remapped, recategorized or cleaned (C10-D03).
- No backfill: existing quotations get no snapshot; `sipanel_has_scopes=False` by default; ordinary sale lines keep native behaviour (PT-31).
- Later upgrades must be deterministic: every schema or data change ships as a numbered migration under `<module>/migrations/<version>/` with an idempotency check; tested by "upgrade from preceding build" before Production (Readiness §9).
- Uninstall is not rollback (C10-D03): uninstalling removes SIPANEL tables and history; the rollback runbook governs.

## Status

All of the above is a design specification derived from the v0.12 pack and read-only installed-source verification. It was not implemented, installed or tested in this run (BLOCKED_NOT_ISOLATED).
