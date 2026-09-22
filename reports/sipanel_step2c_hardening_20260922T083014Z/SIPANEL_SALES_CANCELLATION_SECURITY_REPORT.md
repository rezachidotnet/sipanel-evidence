# SIPANEL Sales Cancellation Security Report (run 20260922T083014Z)

## 1. Service boundary (`sipanel_scope_execution/models/sale_order.py::_action_cancel`)

1. `o.check_access('write')` — the caller's native ACL and record rules on `sale.order` decide whether they may cancel this order (Sales users: their own documents through the "Personal Orders" rule).
2. Executed documents created by SIPANEL block the cancel (`UserError`), as before.
3. Only then: `o.sipanel_execution_batch_ids` (this order's batches, live states only) `.sudo().action_cancel_planned()`. The batch action opens the engine token itself; `sudo()` is the narrow service that lets the demand writes pass the ACL. Scope is bounded by construction: the recordset is the order's own batches, nothing is searched by user-supplied ids.
4. `sudo()` keeps `env.uid`, so the audit row `execution_cancel` records the initiating Sales user (`actor_user_id`, plus `initiator_login` in `after_json`).

ACL rows were not changed (`evidence/acl/ir_model_access_live.txt`): Sales users keep read-only on batches and demands and no access to targets; a direct demand write, a batch action on another order (with or without a forged `sipanel_demand_engine` context or a guessed token), or `action_cancel` on an order they cannot write all raise `AccessError`.

## 2. Tests (`TestSalesCancellation`)

| Requirement | Test | Before | After |
|---|---|---|---|
| authorised Sales user cancels their permitted order with released execution; actor preserved; no general demand rights | `test_authorized_sales_user_cancels_own_order_with_released_execution` | ERROR | PASS |
| unauthorised user cannot cancel | `test_unauthorized_user_cannot_cancel_the_order` | ERROR | PASS |
| Sales user cannot write a demand (plain, raw flag, guessed token) | `test_sales_user_cannot_write_a_demand_directly` | ERROR | PASS |
| Sales user cannot cancel another order's demand by RPC-equivalent call or context manipulation | `test_sales_user_cannot_cancel_another_orders_demand` | ERROR | PASS |
| Execution Owner behaviour remains valid | `test_execution_owner_cancellation_remains_valid` | PASS (guard) | PASS |

("Before" errors were the Sales fixture failing on the unfixed source's `AccessError` in cancel.)

## 3. Live evidence

Order `SI-26/2094` (user_id = synthetic Sales user 2064, not an Execution Owner): `action_cancel` as that user → order `cancel`, batches 415/417 `cancelled`, all demands `cancelled`, audit rows `execution_cancel` with actor `SIPANEL-STEP2CH-20260922T083014Z-sales`; `has_access` on demands for that user: write False, create False, unlink False. Forged attempts on order `SI-26/2095` (not theirs): batch action, batch action with forged engine context, and order cancel — all `AccessError`, batch 416 stayed `released`.

Observation OBS-2CH-01: the Sales fixture had to be sealed by the estimator because a plain Sales user cannot write `net_revenue_projection` during the seal (pre-existing, outside this pass).
