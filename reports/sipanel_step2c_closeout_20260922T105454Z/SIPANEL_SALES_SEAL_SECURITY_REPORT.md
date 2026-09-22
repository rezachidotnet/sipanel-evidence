# SIPANEL Sales Seal/Send Security Report — OBS-2CH-01 (run 20260922T105454Z)

## 1. Problem (measured on the unfixed source)

`evidence/logs/test_sales_seal_before_fix.log`: a plain Sales user (`sales_team.group_sale_salesman` + `sipanel_sale_scope.group_scope_sales`, no Cost & Margin Viewer) calling `action_quotation_sent` on their own quotation raised
`AccessError: You do not have enough rights to access the field "net_revenue_projection" on SIPANEL quote scope revision`, because `action_seal` wrote that `COST_GROUP` field as the calling user.

## 2. Boundary implemented (`sipanel_sale_scope/models/quote_scope_revision.py`, 19.0.1.2.3)

| Requirement | Implementation |
|---|---|
| no group granted to Sales | none; ACL and record rules unchanged (`evidence/acl/`) |
| field-level security kept | `net_revenue_projection`, cost and margin fields keep `groups=COST_GROUP` (`protected_fields_groups.txt`) |
| narrow process-local guard | `SEAL_SERVICE_GUARD = 'sipanel_seal_projection_service'`, checked by the existing `guard(env, name)` (flag + in-process token); opened by `guard_ctx()` only inside `action_seal` |
| native permission verified first | `_check_seal_permission()`: `self.check_access('write')` on the revision and `self.order_id.check_access('write')` on the exact `sale.order`, evaluated as the real user (ACL + record rules, e.g. "Personal Orders") before any elevation |
| elevated scope | one revision (`r.sudo()`), exactly the computed fields (`commercial_projection_json`, `net_revenue_projection`, `fx_source_currency_id`, `fx_rate`, `fx_date`, `fx_source`) plus the seal state fields, within the current Seal/Send transaction |
| initiating user preserved | `sudo()` keeps `env.uid`: `sealed_by_id = env.uid`, audit `seal` row `actor_user_id` = the Sales user |
| forgery refused | `write()` raises `AccessError` for any of `SEAL_PROJECTION_FIELDS` without the service token — sudo, `sipanel_seal_transaction`-only flag, raw context flags, guessed `sipanel_guard_token`, `import_file`, direct writes; same-value writes included |
| outputs | quotation PDF (rendered as the Sales user), portal-readable order/line fields, sealed artifact text and the draft invoice report carry no cost, margin or net-revenue data; the portal binding exposes only `revision_id` and `seal_hash` |

## 3. Tests (`tests/test_sales_seal.py`, tag `sipanel_sales_seal`)

| Requirement | Test | Before | After |
|---|---|---|---|
| plain Sales user seals/sends own permitted quotation | `test_plain_sales_user_seals_and_sends_own_quotation` | ERROR | PASS |
| cannot seal/send another salesperson's inaccessible order | `test_sales_user_cannot_seal_an_inaccessible_order` | PASS (guard) | PASS |
| cannot read `net_revenue_projection` (read, search_read, export, fields_get) | `test_sales_user_cannot_read_net_revenue_projection` | ERROR (fixture blocked by the defect) | PASS |
| cannot write `net_revenue_projection` / `commercial_projection_json` | `test_sales_user_cannot_write_net_revenue_projection` | FAIL | PASS |
| sudo without the genuine guard cannot forge (6 fields + transaction-flag-only) | `test_sudo_without_the_genuine_guard_cannot_forge_the_projection` | FAIL | PASS |
| raw context flag fails | `test_raw_context_flag_does_not_open_the_service` | FAIL | PASS |
| guessed token fails | `test_guessed_token_does_not_open_the_service` | FAIL | PASS |
| import context fails (sudo + `import_file`, and `load()` as Sales) | `test_import_context_does_not_open_the_service` | FAIL | PASS |
| audit actor is the initiating Sales user | `test_audit_actor_is_the_initiating_sales_user` | ERROR | PASS |
| Estimator and manager paths remain green; acceptance verifies the seal | `test_estimator_and_manager_paths_remain_green` | ERROR (fixture price → readiness; corrected) | PASS |
| PDF / portal / invoice output contain no cost, margin or net-revenue | `test_customer_outputs_contain_no_cost_margin_or_net_revenue` | ERROR | PASS |
| existing seal/checksum valid | asserted in the first test (`_current_seal_hash() == sealed_hash`) and by the manager confirmation | — | PASS |

10 of the 11 tests failed on the unfixed source. No existing assertion was removed or weakened; the existing security suite (`test_security.py`, `TestInvoiceProvenanceAuthorization`, `TestPricelistFailsClosed`, …) passes in the full run.

## 4. Live evidence (`evidence/pilot/pilot_closeout_sales_seal.json`)

Synthetic Sales user 2064 reduced to internal user + Salesperson (own documents) + Scope Sales (cost viewer / finance / execution owner / account manager / sale manager all False). Order `SI-26/2314` (its `user_id`): `action_quotation_sent` → order `sent`, revision `sent_sealed`, `sealed_by` = the Sales user, audit `seal` actor = the Sales user, `net_revenue_projection` (read via sudo) = anchor subtotal 25,000,000, checksum valid, artifacts pdf + text. Probes: 17 refused (reads, search_read, export, writes, sudo without guard, transaction-flag-only, raw flags, guessed token, import, six same-value sudo writes, sealing another salesperson's order `SI-26/2315`), stored values unchanged. Customer output: PDF rendered (43,632 bytes) with no cost/margin/net-revenue token or cost figure; portal binding keys `revision_id`, `seal_hash`; artifact text has no cost tokens.
