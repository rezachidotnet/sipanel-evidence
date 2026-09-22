# SIPANEL STEP 2C-CLOSEOUT Test Results (run 20260922T105454Z)

| Run | Command (`odoo -d sipanel --no-http --stop-after-init …` in `odoo-sipanel`) | Result | Log |
|---|---|---|---|
| 0. focused tag on the **unfixed** installed source (test file deployed only) | `-u sipanel_sale_scope --test-enable --test-tags sipanel_sales_seal` | 11 methods, **10 failures** (5 ERROR on the defect's `AccessError`, 5 FAIL "AccessError not raised" on the missing service guard; 1 fixture ERROR corrected afterwards) | `evidence/logs/test_sales_seal_before_fix.log` |
| 1. focused tag after deploying the fix (performs the upgrade to 19.0.1.2.3) | same | **11 methods, 0 failures** (two intermediate runs corrected the portal check to portal-readable fields; logs overwritten by the final one) | `evidence/logs/test_sales_seal_after_fix.log` |
| 2. full SIPANEL suite | `scripts/sipanel_install_and_test.sh test` | **253 tests (52 + 154 + 5 + 42), 193 methods, 0 failures** | `evidence/logs/test_sipanel_full_final.log` |
| 3. `sale_shamsi_report` | `-u sale_shamsi_report --test-enable --test-tags shamsi_characterization` | **80 tests, 0 failures** (repo HEAD `5680013`, clean) | `evidence/logs/test_shamsi_closeout.log` |
| 4. restore-instruction structural tests | `python3 scripts/test_restore_instructions.py <point>` | **21 / 21 PASS** | `evidence/logs/restore_instructions_structural_checks.txt` |
| 5. minimal live Sales seal/send pilot | `odoo shell` (`evidence/scripts/pilot_closeout_sales_seal.py`) | PASS (see the security report §4) | `evidence/pilot/pilot_closeout_sales_seal.json` |

Totals: SIPANEL 240 → **253** by module statistics (`sipanel_sale_scope` 141 → 154); methods 182 → 193 (+11); Shamsi 80. Grand total **333 / 0 failures**.

Assertion discipline: no existing assertion was removed, bypassed or weakened. Corrections made only to the **new** test file between run 0 and run 1: the estimator-path fixture used a price that failed readiness (margin), and the portal check first tried to render the portal template outside an HTTP request, then read every field as the portal user (blocked on `stock_reference_ids`); it now reads exactly the portal-visible order/line fields, the sealed artifacts, and asserts no cost/margin field is even visible to the portal user.
