# SIPANEL STEP 2C — Test Results (run 20260922T065650Z)

Counts are Odoo's `odoo.tests.stats` module totals (the convention of the
previous reports); "methods" is the number of `Starting Test…` lines.

| Run | Command (inside `odoo-sipanel`, `-d sipanel --no-http --stop-after-init`) | Result | Log |
|---|---|---|---|
| 0. STEP 2C tag on the **unfixed** installed source (only the new test files deployed) | `-u sipanel_sale_scope,sipanel_scope_execution --test-enable --test-tags sipanel_step2c` | 8 methods, **6 failures** (expected: 3 ERROR CD-2C-03, 1 FAIL CD-2C-01, 1 FAIL CD-2C-02, 1 FAIL from a wrong assertion of mine) | `evidence/logs/test_step2c_before_fix.log` |
| 1. full SIPANEL suite after deploying the fixes (performs the module upgrade) | `scripts/sipanel_install_and_test.sh test` (= `-u` all four SIPANEL modules `--test-tags sipanel`) | 214 tests (52+141+5+16), 162 methods, **1 error** (my test cancelled the order with the estimator's environment → AccessError; assertion corrected) | `evidence/logs/test_sipanel_full_after_fix.log` |
| 2. STEP 2C tests alone | `-u sipanel_sale_scope,sipanel_scope_execution --test-enable --test-tags sipanel_step2c` | 8 methods, **0 failures** | `evidence/logs/test_step2c_only_after_fix.log` |
| 3. `sale_shamsi_report` regression suite | `-u sale_shamsi_report --test-enable --test-tags shamsi_characterization` | **80 tests, 0 failures** (repo `/opt/odoo/addons/sale_shamsi_report` HEAD `5680013`, clean) | `evidence/logs/test_shamsi_step2c.log` |
| 4. full SIPANEL suite, final | `scripts/sipanel_install_and_test.sh test` | **214 tests, 0 failures**, 162 methods (`162 post-tests in 423.82s`) | `evidence/logs/test_sipanel_full_final.log` |
| 5. controlled live pilot on `sipanel` | `odoo shell` stages 1–5 | see the execution-batch report | `evidence/pilot/*.json` |

Totals: SIPANEL 202 → **214** (+12 by module statistics: `sipanel_sale_scope`
137 → 141, `sipanel_scope_execution` 8 → 16); test methods 155 → 162 (+8: 6 in
`test_step2c.py`, 2 in `TestAmendmentAfterConfirmation`); Shamsi 80 → 80.
Grand total **294 / 0 failures**.

## Required coverage → test

| Requirement | Test | Module |
|---|---|---|
| bridge-owner generated line creates zero native stock demand | `test_bridge_owner_generated_line_yields_one_demand_and_zero_native_demand`; also `test_generated_line_does_not_add_a_second_procurement_owner`, `test_one_component_yields_one_execution_demand` (2B) | execution / sale_scope |
| bridge release creates one execution demand | same test (`len(demands) == 1`, key derivation, one picking + one move) | execution |
| native owner links and does not duplicate | `test_native_owner_own_line_links_its_own_native_demand_and_creates_none` | execution |
| repeat release is idempotent | both scenario tests (release ×3 + explicit action) and `test_pt14_release_twice_and_concurrent` | execution |
| concurrency is idempotent | `test_pt14_release_twice_and_concurrent` (LockError path, bounded retry, nothing created, later release succeeds once) + live two-transaction run | execution |
| partial failure leaves no untracked partial records | `test_retry_after_failure_creates_the_full_demand_set_exactly_once`, `test_pt15_adapter_failure_rolls_back` | execution |
| retry after failure succeeds once | `test_retry_after_failure_…` (retry without fix fails again; retry after fix creates 7 demands / 4 pickings / 1 PO line / 1 MO exactly once) | execution |
| cancellation lineage | `test_amendment_after_release_with_generated_lines_keeps_lineage_and_adds_one_delta` (cancel section), `test_pt22_qty_delta_and_pt19_cancel_lineage` | execution |
| amendment lineage | same test + `TestAmendmentAfterConfirmation` (2) + `test_amendment_does_not_double_bill_the_same_component` (2B) | execution / sale_scope |
| Project/System/Activity propagation | `test_project_system_activity_propagate_to_every_execution_record` | execution |
| source-key uniqueness | scenario tests (`len(keys) == len(set(keys))`, one live demand per key) | execution |
| no duplicate procurement | scenario tests (document counts unchanged on repeat release; native: no bridge documents) | execution |
| no duplicate project cost | `test_actual_cost_projection_is_idempotent_and_never_double_allocates` | execution |
| STEP 2B invoice provenance and pricing hardening remain green | `TestInvoiceProvenanceAuthorization` (9) and `TestPricelistFailsClosed` (5) — all pass in runs 1 and 4 | sale_scope |

## Assertion discipline

No existing assertion was removed, bypassed or weakened. Two assertions in the
**new** tests were corrected between run 0/1 and run 2/4:

1. `test_bridge_owner_…` asserted that writing `demand_key` raises; an ORM
   `readonly` field does not raise on write, so the assertion now checks the
   field is declared readonly and that `delta_uid` is the revision reference.
2. `test_amendment_after_release_…` cancelled the order through the estimator's
   environment (the fixture's `_make_order` returns a recordset bound to that
   user), which raises `AccessError` on demand write; the cancel now runs as the
   execution owner. The AccessError itself is recorded as OBS-2C-05.
