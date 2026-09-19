Run sipanel_scope_implementation_rc_20260919T140237Z · Verdict: BLOCKED_NOT_ISOLATED · Status: DESIGN-LEVEL — NOT RUNTIME VALIDATED — no module was written, installed or tested in this run.

# SIPANEL — Security Matrix (design-level)

Baseline: Master v0.12 §C10 security matrix, C4-D04, C7-D03, C1-D09; Readiness v1.0 §8 (roles) and B-08; installed-source anchors SV-02/SV-03 (portal endpoint in `sale_management`), SV-05 (sections deletable after confirm), SV-14 (sale.order hooks), SV-20 (Production addon path has no git identity). Provisional profile applied: BQ-02=B joint Finance+Sales waiver (later unsigned instruction; worksheet selection was A), BQ-09 company-currency-only. No user is hard-coded. No PASS is claimed; every test row below is BLOCKED in this run.

## A. Role groups to create

| XML id | Module | Display name | Category | Implies (native) | Purpose |
|---|---|---|---|---|---|
| `sipanel_commercial_scope_core.group_scope_steward` | core | SIPANEL / Scope Steward | `module_category_sipanel_scope` (new category) | `base.group_user` | create/version/release/archive Scope masters; owns Product mapping requests (C1-D09) |
| `sipanel_commercial_scope_core.group_scope_estimator` | core | SIPANEL / Estimator | same | `base.group_user`, `group_scope_cost_viewer` | edit draft snapshots, components, specs, quantity/cost overrides, resolve ESTIMATE_ONLY (C4-D04) |
| `sipanel_commercial_scope_core.group_scope_cost_viewer` | core | SIPANEL / Cost & Margin Viewer | same | `base.group_user` | read cost/margin fields (field-level groups); no structural rights by itself |
| `sipanel_commercial_scope_core.group_scope_auditor` | core | SIPANEL / Auditor (read-only) | same | `base.group_user` | read everything in scope of company incl. audit events; zero write |
| `sipanel_sale_scope.group_scope_sales` | sale | SIPANEL / Scope Sales | same | `sales_team.group_sale_salesman` | add released Scopes to quotes, edit commercial/notes, send/confirm through native Sales groups; no implicit cost access |
| `sipanel_sale_scope.group_scope_waiver_sales` | sale | SIPANEL / Waiver — Sales approver | same | `sales_team.group_sale_manager` | Sales half of the joint waiver (BQ-02=B) |
| `sipanel_sale_scope.group_scope_waiver_finance` | sale | SIPANEL / Waiver — Finance approver | same | `account.group_account_manager` | Finance half of the joint waiver (BQ-02=B) |
| `sipanel_scope_execution.group_scope_execution_owner` | execution | SIPANEL / Execution Owner | same | `base.group_user`; native `stock.group_stock_user`, `purchase.group_purchase_user`, `mrp.group_mrp_user`, `project.group_project_user` are **not** implied — they must be granted separately so native approvals stay native | run Release Execution, view demands/targets, minimal operational cost only if also cost viewer |
| `sipanel_scope_costing.group_scope_finance` | costing | SIPANEL / Finance (cost recognition) | same | `account.group_account_manager`, `group_scope_cost_viewer` | approve recognition policies, review allocations, reconcile |
| `base.group_system` | native | Administration | — | — | technical configuration only; must not be required for daily operation |

Category `module_category_sipanel_scope` is created by the core module so groups appear together in user settings. No group is auto-assigned by data files; the runbook assigns roles to existing users post-install.

## B. Role × object × operation matrix

Legend: C create, R read, W write, U unlink, X = denied. "(rule)" = subject to record rules in §C. All rows implicitly restricted to the user's allowed companies.

| Model | Steward | Estimator | Cost viewer | Sales | Waiver Sales / Finance | Execution owner | Finance | Auditor | Portal |
|---|---|---|---|---|---|---|---|---|---|
| sipanel.scope | CRWU(draft-only U) | R | R | R (released only, rule) | R | R | R | R | X |
| sipanel.scope.version | CRW (RELEASED content immutable) | R | R | R (state RELEASED, rule) | R | R | R | R | X |
| sipanel.scope.recipe.line | CRWU (DRAFT version only) | R | R | R (released) | R | R | R | R | X |
| sipanel.scope.audit.event | C (via actions) R | C R | R (cost payload) | C R (own actions) | C R | C R | C R | R | X |
| sipanel.scope.favorite | CRWU own | CRWU own | CRWU own | CRWU own | CRWU own | CRWU own | CRWU own | R own | X |
| sipanel.quote.scope | R | CRW (draft) | R | CRW (commercial fields only; anchor/structure via actions) | R | R | R | R | X |
| sipanel.quote.scope.revision | R | CRW (WORKING only) | R | RW (`final_note`, `note_reviewed`, language; WORKING only) | R | R | R | R | X |
| sipanel.quote.scope.component | R | CRW (WORKING only; U ⇒ TOMBSTONE) | R | R (non-cost fields) | R | R (specs of released demand) | R | R | X |
| sipanel.quote.scope.artifact | R | R | R | R (own orders, rule) | R | R | R | R | R (own sealed artifacts only, rule) |
| sipanel.quote.waiver | X | C R | R | C R | R W (own approver field only) | X | R W (finance approver field) | R | X |
| sipanel.execution.owner.rule | R | R | R | R | R | R | R | R | X |  (write: `base.group_system` + Execution owner jointly via settings) |
| sipanel.execution.batch | R | R | R (cost) | R | R | C R W (state via action) | R | R | X |
| sipanel.execution.demand | R | R | R | R | R | C R (via batch) | R | R | X |
| sipanel.execution.target | R | R | R | X | X | C R (via adapters) | R | R | X |
| sipanel.cost.recognition.policy | X | X | R | X | X | X | C R W (approve) | R | X |
| sipanel.actual.cost.event | X | X | R | X | X | R (own demands) | R (projection job creates) | R | X |
| sipanel.actual.allocation | X | X | R | X | X | R | C R W (MANUAL with reason) | R | X |
| sipanel.scope.variance (view) | X | R | R | X | X | X | R | R | X |
| sale.order / sale.order.line (native) | native | native | native | native Sales groups | native | native | native | native | native portal (guarded, §E) |

Notes:
- "Draft-only U" on masters: unlink refused by `@api.ondelete` once any version is RELEASED or any quote scope references the identity, regardless of group.
- Sales may **not** write `product_uom_qty` of an OFFERED anchor directly; the ORM guard routes it through the governed transition (§E). This applies equally to `base.group_system`.
- Nobody, including Administration, can write content of a sealed revision or a RELEASED version through ORM, import or RPC; amendments create a new revision/version (C1-D02, C3-D03, PT-24).

## C. Record rules

| Rule XML id | Model | Groups | Domain / effect |
|---|---|---|---|
| `rule_scope_company` … one per SIPANEL model (`*_company`) | every `sipanel.*` model | global | `[('company_id','in',company_ids)]` — server-side company isolation (C4-D04) |
| `rule_scope_version_released_for_non_steward` | sipanel.scope.version | all except Steward, Auditor | `[('state','!=','DRAFT')]` — drafts not offered for selection (C1-D02) |
| `rule_quote_scope_sales_own_orders` | sipanel.quote.scope / revision / component / artifact / waiver | Scope Sales (without Sales Manager) | `[('order_id.user_id','=',user.id)]` OR team membership, mirroring native `sale.order` personal rule so Scope visibility never exceeds order visibility |
| `rule_quote_scope_sales_manager` | same | `sales_team.group_sale_manager` | `[(1,'=',1)]` within company |
| `rule_execution_owner_company` | batch/demand/target | Execution owner | company only |
| `rule_audit_readonly_auditor` | all `sipanel.*` | Auditor | `perm_write=False`, `perm_create=False`, `perm_unlink=False` (rule-level, in addition to ACL zero write) |
| `rule_portal_artifact_own` | sipanel.quote.scope.artifact | `base.group_portal` | `[('revision_id.quote_scope_id.order_id.partner_id','child_of',user.partner_id.commercial_partner_id.id), ('revision_id.state','in',['SENT_SEALED','ACCEPTED_SEALED'])]` read only |
| `rule_portal_deny_all` | every other `sipanel.*` model | `base.group_portal`, `base.group_public` | no ACL line exists ⇒ denied by default; an explicit rule with `[(0,'=',1)]` is added as belt-and-braces |
| `rule_favorite_own` | sipanel.scope.favorite | global | `[('user_id','=',user.id)]` |
| `rule_attachment_artifact_portal` | ir.attachment | portal | native attachment rule already requires access to `res_model/res_id`; the artifact rule above therefore bounds attachment access; tested in PT-23 |

Cross-project access: a user of another company or another Odoo tenant has no row in `company_ids` ⇒ empty recordset; existence counts (`usage_count`, search_count) are computed without `sudo` so unauthorized documents are not revealed (C1-D08).

## D. Field-level groups

| Fields | Models | Read | Write |
|---|---|---|---|
| `unit_cost`, `cost_amount`, `cost_source*`, `manual_cost_*`, `product_value_id`, `stale_cost`, `direct_cost_total`, `derived_cost_total`, `eligible_cost_total`, `missing_cost_count`, `net_revenue_projection`, `margin_amount`, `margin_percent` | revision, component | `group_scope_cost_viewer` | `group_scope_estimator` (WORKING only) |
| `override_reason`, `known_zero_reason`, `manual_cost_reason` | component | Estimator, Auditor, Finance | Estimator |
| `before_json`, `after_json` (audit) | audit event | `group_scope_cost_viewer` (+ Auditor) | nobody |
| `sales_approver_id`, `finance_approver_id` (+ dates) | waiver | all readers | respective waiver group only (checked in `write`, not only via `groups=`) |
| `sealed_hash`, `content_hash`, `release_checksum` | revision, artifact, version | all readers | nobody (readonly + write guard) |
| `terminal_event_*`, `excluded_models_json` | policy | cost viewer | `group_scope_finance` |
| `sipanel_*` fields on `sale.order` / `sale.order.line` | native | inherit native model access | computed/guarded; `sipanel_current_seal_hash` write only by seal hook |

Because the groups are applied on the fields themselves, `read`, `search_read`, `export_data`, `web_read_group`, report rendering and `mail.message` tracking honour them without view tricks (C7-D03). Views additionally hide the columns for non-viewers.

## E. Controller, RPC and leakage guards

| Surface | Native behaviour (installed) | Guard |
|---|---|---|
| `/my/orders/<id>/update_line_dict` (`sale_management/controllers/portal.py:11-58`, jsonrpc, `auth="public"`, `sudo()` write of `product_uom_qty`, SV-03) | writes any optional line qty when `_can_be_edited_on_portal()`; combo item lines updated too | `sale.order.line._can_be_edited_on_portal` override: for anchor lines of a Scope, return True only if the Scope's `current_revision_id.state == SENT_SEALED` **and** the request carries the current `sipanel_current_seal_hash` (added to the portal template payload); the `write` guard then performs the governed transition: single transition, native pricelist/tax recompute, audit event, at most one accepted delta, idempotent on repeat. Stale link/hash ⇒ refused with generic message; no data revealed. |
| `/my/orders/<id>/accept` (`sale/controllers/portal.py:313-341`) | signs and renders PDF | `sale.order._has_to_be_signed`/`action_confirm` override: refuse if any sealed revision hash ≠ `sipanel_current_seal_hash`; bind `acceptance_reference` to the sealed revision; store artifact hash (C7-D04) |
| `/my/orders/<id>` page and PDF (`sale/report/…`, `sale_shamsi_report` overrides SV-18) | renders `order_line` names/amounts | customer payload builder (allowlist, dictionary §"Customer payload allowlist") feeds line `name`; no SIPANEL internal model is referenced by any QWeb template; `sale_pdf_quote_builder` form fields excluded from SIPANEL data |
| `/my/orders/<id>/document/<doc>` and `ir.attachment` download | native access-token check | artifact attachments carry `res_model='sipanel.quote.scope.artifact'`; portal rule §C limits to own sealed artifacts |
| RPC/XML-RPC/JSON-RPC `write`/`create`/`unlink` and `base_import` | ORM | all guards live in `write`/`create`/`unlink`/`@api.ondelete` of the SIPANEL models and of `sale.order.line`, so import and RPC bypass is impossible without `sudo`; `sudo` usage inside the modules is limited to reading native carriers for projection and is never exposed to a controller argument |
| `export_data` / spreadsheet dashboards | ORM field groups | cost fields carry `groups=` ⇒ excluded automatically for non-viewers; export of `sipanel.*` models denied to portal by absent ACL |
| Chatter / `mail.tracking.value` | tracks field changes | cost fields are **not** tracked (`tracking=False`) so message bodies cannot leak amounts to followers without cost access; audit events hold the payload under field groups |
| Section reorder/delete (`_check_line_unlink`: "Sections and Notes can always be deleted", SV-05) | native | `unlink`/`write(sequence, display_type)` guard on `sipanel_is_scoped_section` and anchor lines while sealed (dictionary §2.7) |
| Company-currency (SV-12 fallback 1.0) | native silently converts | `action_quotation_send`/`action_confirm` raise when `sipanel_has_scopes` and `currency_id != company_id.currency_id` (BQ-09, B-06) |
| Logging | Odoo logs | SIPANEL log lines never include amounts, partner names or phone numbers; only ids, uids and hashes |

## F. Security test plan (mapping to the prompt's ten required tests)

All rows: **BLOCKED** in this run — reason: BLOCKED_NOT_ISOLATED (no clone). Build/clone/timestamp/runner columns therefore empty; no evidence attachment exists.

| # | Required test | Method on clone | PT mapping | Expected | Status |
|---|---|---|---|---|---|
| S-01 | ACL and record rules | `TransactionCase` per group: CRUD attempts on every SIPANEL model with `with_user()`; `check_access` matrix asserts §B exactly | PT-23, PT-24 | matrix §B holds; auditor zero write | BLOCKED |
| S-02 | Company isolation | second company + user; search/read/write across companies; `usage_count` from other company = 0 | PT-23 | empty recordsets; no AccessError leak of existence | BLOCKED |
| S-03 | Direct ORM/RPC/import bypass | `write`/`create`/`unlink` via `env` and via `xmlrpc` on RELEASED version, sealed revision, anchor line, scoped section; `base_import` CSV against recipe lines of RELEASED version | PT-24 | `UserError`/`AccessError`; audit event written; no change | BLOCKED |
| S-04 | Portal access | portal user of order partner and of another partner: order page, artifact download, `update_line_dict` with/without hash, JSON-RPC `read` on `sipanel.*` | PT-23, PT-10 | own sealed artifact only; every internal model denied; qty transition only with current hash | BLOCKED |
| S-05 | Stale-link / replay | send v1, amend to v2, replay v1 `update_line_dict` and accept; repeat accepted transition twice | PT-10 | v1 refused; second transition idempotent, one delta | BLOCKED |
| S-06 | PDF, attachment, export leakage | render quotation PDF and portal HTML as portal user; `export_data` as Sales without cost viewer; download artifact attachment by id guessing | PT-23, PT-32 | no cost/margin/internal component/product code in any byte of output; attachment 404/403 | BLOCKED |
| S-07 | Unauthorized cost/margin access | Sales user without cost viewer: `read`, `search_read` with cost fields, `web_read_group`, chatter history | PT-23 | fields absent/AccessError; no tracking values with amounts | BLOCKED |
| S-08 | Sealed revision mutation | as Estimator, Sales Manager and admin: write component qty/cost/note on SENT_SEALED and ACCEPTED_SEALED revisions | PT-24 | refused; new revision required | BLOCKED |
| S-09 | Cross-project access | user with project-limited native rules; read allocations/events of other project | PT-23, PT-29 | denied; UNALLOCATED bucket shows amounts only within company for cost viewers | BLOCKED |
| S-10 | Privileged override audit | admin performs waiver, override, preset change, manual allocation | PT-24 | `sipanel.scope.audit.event` rows with actor, reason, correlation; audit rows immutable | BLOCKED |

Additional negative tests carried from Master §C9: PT-23 (portal/RPC/export/PDF/attachment as customer and other company), PT-24 (released/confirmed edit through import and RPC).

## G. Segregation-of-duties statement

- Roles are configurable groups; **no user id, login or e-mail is written in any data file, code or report** (C4-D04, B-08).
- The existing internal user Taleghani may be assigned the initial business roles only by an explicit post-install configuration step in the runbook, after verifying the account is active, internal (`share=False`) and in the SIPANEL company. Nothing in the modules refers to that user.
- If that single user holds Sales, Finance, Inventory, Purchase and Administration roles simultaneously — which the v0.10 evidence suggests is the current state — the joint waiver (BQ-02=B), the Finance policy approval (BQ-04), Release Execution and native Purchase/MRP approvals are all exercisable by one person. This is recorded here as an **acknowledged single-person governance limitation**, not simulated segregation. Compensating control: every privileged action writes an immutable audit event with reason (§F S-10); the Auditor role can be granted to a second person for review. Adding a second approver is a business decision (owner TBE).
- Administration (`base.group_system`) is required only for configuration (settings parameters, owner-rule table, analytic plan selection) and must not be used for daily estimation.

## H. PII and data-handling rules for outputs

- Reports, tests, logs and evidence in this bundle contain no contact names, phone numbers, e-mail addresses, credentials, access tokens or database dumps; the SIPANEL modules must keep that property in their own logs and test fixtures (synthetic partners only, clone-only).
- Real contact phone numbers in Production data are never modified and never used for outbound tests (Readiness §6.2); clone builds must neutralize mail/SMS/WhatsApp gateways (`sms_gateway`, `contact_whatsapp`, `odoo_sms_batch` are installed) before startup.
- Cost, margin, override reasons, analytic dimensions and INTERNAL_ONLY components never appear in customer artifacts (C0-D09); the allowlist builder is the only path to customer text.
- Portal-facing error messages are generic; stale links do not reveal whether a newer revision exists.

## Status

Design-level only. Nothing above has been installed or tested (BLOCKED_NOT_ISOLATED). All ten security tests and PT-23/PT-24 are BLOCKED pending an isolated clone.
