# SIPANEL STEP 2C-HARDENING Test Results (run 20260922T083014Z)

| Run | Command (`odoo -d sipanel --no-http --stop-after-init …` in `odoo-sipanel`) | Result | Log |
|---|---|---|---|
| 0. hardening tag on the **unfixed** installed source (tests deployed only) | `-u sipanel_scope_execution --test-enable --test-tags sipanel_step2c_hardening` | 20 methods, **17 failures** (9 immutability, 4 boundary, 4 Sales) | `evidence/logs/test_hardening_before_fix.log` |
| 1. full suite after deploying the fix (performs the upgrade to 19.0.1.0.2) | `scripts/sipanel_install_and_test.sh test` | 240 tests / 182 methods, 5 failures — all in the new tests: Sales fixture sealed as the Sales user (`net_revenue_projection` cost-group field, OBS-2CH-01) and a too-broad `_action_cancel` spy that counted Odoo's own picking cancellation | `evidence/logs/test_sipanel_full_after_fix.log` |
| 2. hardening tag alone (final tests) | as run 0 | **20 methods, 0 failures** (`odoo.tests.stats`: 26) | `evidence/logs/test_hardening_only_after_fix.log` |
| 3. `sale_shamsi_report` | `-u sale_shamsi_report --test-enable --test-tags shamsi_characterization` | **80 tests, 0 failures**; repo HEAD `5680013`, clean | `evidence/logs/test_shamsi_2ch.log` |
| 4. full suite, final | `scripts/sipanel_install_and_test.sh test` | **240 tests (52 + 141 + 5 + 42), 182 methods, 0 failures** (`182 post-tests in 634.83s`) | `evidence/logs/test_sipanel_full_final.log` |
| 5. live pilot | `odoo shell` (`pilot_2ch_1_run.py`, `pilot_2ch_2_cleanup.py`) | see the hardening report | `evidence/pilot/*.json` |

Totals: SIPANEL 214 → **240** by module statistics (`sipanel_scope_execution` 16 → 42); methods 162 → 182 (+20 in `test_step2c_hardening.py`); Shamsi 80. Grand total **320 / 0 failures**.

Assertion discipline: no existing assertion was removed, bypassed or weakened. Two corrections to the **new** tests between run 1 and run 2: (a) the Sales order is prepared by the estimator and then assigned to the Sales user (`user_id`), because sealing writes a cost-group field a plain Sales user cannot write (recorded as OBS-2CH-01, not silenced); (b) the idempotency spy counts only `stock.move._action_cancel` calls originating in `adapters.py`, since Odoo's own order cancellation legitimately re-visits its pickings. The STEP 2C fixtures were moved from `test_step2c.py` to `tests/common.py` unchanged so both test files share them.

Coverage map: immutability 9 tests, native-owner boundary 6 tests, Sales cancellation 5 tests — see the three topic reports for the requirement → test mapping.
