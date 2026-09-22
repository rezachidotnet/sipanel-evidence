# SIPANEL Execution-Demand Immutability Report (run 20260922T083014Z)

## 1. Installed provenance/ownership fields of `sipanel.execution.demand` (inspected)

| Concept | Installed field | Treatment after this pass |
|---|---|---|
| demand key | `demand_key` (Char, readonly, indexed; partial unique index over live demands) | immutable |
| batch | `batch_id` (M2O `sipanel.execution.batch`, restrict) | immutable |
| order | `order_id` (related `batch_id.order_id`, stored) | follows the immutable batch; not writable through `write` vals |
| quotation Scope | `quote_scope_id` | immutable |
| revision | via `component_id.revision_id` (no direct field) | immutable through `component_id` |
| component / occurrence | `component_id` (occurrence uid on the component) | immutable |
| delta UID | `delta_uid` | immutable |
| execution mode | `execution_mode` | immutable |
| execution owner | `owner` | immutable |
| Project / System / Activity | `project_id`, `system_id`, `activity_id` | immutable |
| source quantities | `normalized_qty`, `signed_qty`, `uom_id`, `product_id` | immutable |
| reversal lineage | `reversal_of_id`, `cancelled_by_delta_uid` | immutable (now supplied at creation by the amendment engine) |
| governed state | `state`, `reversal_required`, `requested_date` | writable only with the engine token |
| identity | `name` (stored compute), `company_id` (related) | ORM-computed, not user-writable |

## 2. Boundary implemented (`execution_demand.py`, `execution_batch.py`, `sale_order.py`)

* `DEMAND_ENGINE_GUARD = 'sipanel_demand_engine'`, checked with the existing process-local `guard(env, name)` (flag **and** the in-process `sipanel_guard_token`). Opened only by `guard_ctx()` inside `_release_locked` (release + failure marking + adapters), `action_sipanel_release_amendment_delta` (delta creation, linking, reduction) and `action_cancel_planned` (governed cancellation).
* `create()` without the token → `AccessError` (also with sudo, `import_file`, a raw `sipanel_demand_engine=True` flag or a guessed token).
* `write()` with any of the 16 immutable fields → `AccessError` unconditionally (even the same value, even with the token: the fields are closed, not validated). Any other field without the token → `AccessError`.
* `unlink()` → `AccessError` always (lineage evidence).
* The real initiating user is preserved: the services use `sudo()` only where the native permission was established first (`sale.order._action_cancel`), and `sudo()` keeps `env.uid`, so `sipanel.scope.audit.event.actor_user_id` is the initiator (`execution_cancel` rows show the Sales user in the pilot).

## 3. Behavioural tests (`test_step2c_hardening.py::TestDemandImmutability`, all fail on `e01da19`, pass on `53268ef`)

| Requirement | Test | Before | After |
|---|---|---|---|
| direct `demand_key` modification refused, value unchanged | `test_direct_demand_key_modification_is_refused_and_value_unchanged` | FAIL | PASS |
| every immutable provenance field refused (same-value writes, with and without token) | `test_every_provenance_field_is_immutable` | FAIL | PASS |
| raw context flag does not bypass | `test_raw_context_flag_does_not_open_the_engine` | FAIL | PASS |
| guessed token does not bypass | `test_guessed_token_does_not_open_the_engine` | FAIL | PASS |
| sudo does not bypass | `test_sudo_does_not_open_the_engine` | FAIL | PASS |
| import does not bypass | `test_import_context_does_not_open_the_engine` | FAIL | PASS |
| forged demand creation refused (5 variants) | `test_forged_demand_creation_is_refused` | FAIL | PASS |
| never deleted | `test_demands_are_never_deleted` | ERROR | PASS |
| genuine release creates, failure marks failed, retry creates one live demand per key, cancellation transitions through the governed action with the initiator as actor; partial unique index intact | `test_genuine_release_failure_retry_and_cancellation_still_work` | FAIL | PASS |

No metadata assertion replaces a behavioural one.

## 4. Live probes (`evidence/pilot/pilot_2ch_run.json` → `provenance_probes`)

32 probes on demand 2504 of `SI-26/2094`: every one `refused AccessError`; `stored_values_unchanged = true`; `demand_count_unchanged = true`; batch 416 of the other order stayed `released` after the Sales user's forged attempts.
