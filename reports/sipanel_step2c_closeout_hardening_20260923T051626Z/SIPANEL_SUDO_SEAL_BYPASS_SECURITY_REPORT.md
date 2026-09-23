# SIPANEL Sudo Seal Bypass Security Report (run 20260923T051626Z)

## 1. The bypass (reproduced on `84748b2`)

`_check_seal_permission()` called `self.check_access('write')` and `self.order_id.check_access('write')` on the recordset it was invoked on. Odoo's `check_access()` begins with `if not self.env.su and …` (`orm/models.py` 4114): under superuser mode it checks nothing. A pre-sudoed recordset therefore sealed without any permission. Reproduction (`evidence/logs/test_sales_seal_sudo_before_fix.log`, 7 failures "AccessError not raised"):

* `rev.with_user(plain_user).sudo().action_seal()` — a user with no sales rights sealed a quotation;
* `inaccessible_rev.with_user(sales).sudo().action_seal()` and `inaccessible_order.with_user(sales).sudo().action_quotation_sent()` — a Sales user sealed another salesperson's order;
* sudo + raw context flags, sudo + guessed token, sudo + `import_file`, sudo + genuine `sipanel_seal_transaction` flag without permission — all sealed.

## 2. Correction (`quote_scope_revision.py`, 19.0.1.2.4)

```python
initiating_uid = self.env.uid
plain_env = self.env(user=initiating_uid, su=False)
rev = self.with_env(plain_env)
rev.check_access('write'); rev.order_id.check_access('write'); rev.quote_scope_id.check_access('write')
```

* The initiating uid is captured before elevation; a non-sudo environment is rebuilt for it and all checks run on records browsed in that environment (ACL + record rules, e.g. "Personal Orders").
* Nothing trusts `self.env.su`, the pre-sudoed recordset, context flags (`sipanel_seal_projection_service`, `sipanel_seal_transaction`, `import_file`, `active_model/active_ids`) or tokens — the gate reads none of them.
* Root: Odoo's `Environment.__new__` (`orm/environments.py` 66: `if uid == SUPERUSER_ID: su = True`) forces superuser mode for uid 1, so uid 1 is the only uid that cannot be checked non-sudo. That is Odoo's design; no SIPANEL bypass exists (the previous explicit root shortcut was removed) and `test_root_uid_is_superuser_by_odoo_design` documents it.
* After the check, elevation is unchanged: `r.sudo().with_context(**guard_ctx('sipanel_seal_transaction', SEAL_SERVICE_GUARD)).write({…})` for the projection and seal fields of that one revision; `sealed_by_id = env.uid`; audit actor = `env.uid`; COST_GROUP field security untouched; no group or ACL added.

## 3. Tests (`tests/test_sales_seal_sudo.py`, tag `sipanel_sales_seal_sudo`; each refused path asserts state, hash, `sealed_by_id`, artifact count, projection and order state unchanged)

| Requirement | Test | Before | After |
|---|---|---|---|
| A. plain Sales user seals own quotation; audit actor & `sealed_by_id`; checksum verifies | `test_plain_sales_user_seals_own_quotation` | PASS | PASS |
| A. Estimator and Sales Manager paths; acceptance verifies the seal | `test_estimator_and_sales_manager_paths_succeed` | PASS | PASS |
| A. root uid documented (Odoo forces su) | `test_root_uid_is_superuser_by_odoo_design` | PASS | PASS |
| B. `unauthorized_user.sudo().action_seal()` refused (plain user, steward) | `test_unauthorized_user_sudo_action_seal_is_refused` | **FAIL** | PASS |
| B. `inaccessible_revision.with_user(sales).sudo().action_seal()` refused | `test_inaccessible_revision_with_sales_sudo_is_refused` | **FAIL** | PASS |
| B. `inaccessible_order.with_user(sales).sudo().action_quotation_sent()` / `_send()` refused | `test_inaccessible_order_with_sales_sudo_send_is_refused` | **FAIL** | PASS |
| B. sudo + raw context flags refused | `test_sudo_with_raw_context_flags_is_refused` | **FAIL** | PASS |
| B. sudo + guessed token refused | `test_sudo_with_guessed_token_is_refused` | **FAIL** | PASS |
| B. sudo + `import_file` refused | `test_sudo_with_import_context_is_refused` | **FAIL** | PASS |
| B. sudo + genuine seal-transaction flag without the service token refused; server-action context refused; direct projection write under that flag refused | `test_sudo_with_genuine_transaction_flag_but_no_service_token_is_refused` | **FAIL** | PASS |
| C. Sales still cannot read protected fields; PDF/portal binding/artifacts clean | `test_sales_still_cannot_read_protected_fields_and_outputs_stay_clean` | PASS | PASS |

The earlier Sales-seal suite (`test_sales_seal.py`, 11) passes unchanged (22/0 for the combined tag). No assertion removed or weakened.

## 4. Live evidence (`evidence/pilot/pilot_closeout_hardening.json`)

Order `SI-26/2545` (administrator's, inaccessible to the Sales user 2064 whose groups are internal user + Salesperson (own documents) + Scope Sales): eight probes — `rev.with_user(sales).sudo().action_seal()`, `order.with_user(sales).sudo().action_quotation_sent()`, `rev.with_user(plain).sudo().action_seal()` (plain internal user 1376), sudo + raw flags, sudo + guessed token, sudo + `import_file`, sudo + genuine transaction flag, and the plain non-sudo call — all `refused AccessError`, revision state `working` and stored values unchanged after each. Order `SI-26/2544` (the Sales user's own): sealed and sent by that user, `sealed_by` and audit actor = the Sales user, checksum valid, projection = anchor subtotal 25,000,000 (read via sudo only); field reads of `net_revenue_projection`, `margin_amount`, `eligible_cost_total` refused; PDF rendered as the Sales user has no cost/margin/net-revenue token; portal binding keys `revision_id`, `seal_hash`; artifact text clean.
