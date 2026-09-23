# SIPANEL STEP 2C-CLOSEOUT-HARDENING Test Results (run 20260923T051626Z)

| Run | Command | Result | Log |
|---|---|---|---|
| 0. sudo-seal tag on the **unfixed** installed source (test file deployed only) | `odoo -d sipanel … -u sipanel_sale_scope --test-enable --test-tags sipanel_sales_seal_sudo` | 11 methods, **7 failures** — every pre-sudoed path sealed ("AccessError not raised") | `evidence/logs/test_sales_seal_sudo_before_fix.log` |
| 1. sudo-seal tag after the fix (module upgraded to 19.0.1.2.4) | same | **11 / 0** | `evidence/logs/test_sales_seal_sudo_after_fix.log` |
| 2. all Sales-seal tests (`sipanel_sales_seal`: STEP 2C-CLOSEOUT 11 + this pass 11) | `… --test-tags sipanel_sales_seal` | **22 / 0** | `evidence/logs/test_sales_seal_all_after_fix.log` |
| 3. full SIPANEL suite | `scripts/sipanel_install_and_test.sh test` | **266 tests (52 + 167 + 5 + 42), 204 methods, 0 failures** | `evidence/logs/test_sipanel_full_final.log` |
| 4. `sale_shamsi_report` | `… -u sale_shamsi_report --test-tags shamsi_characterization` | **80 / 0** | `evidence/logs/test_shamsi_closeout_hardening.log` |
| 5. restore-instruction structural tests | `python3 scripts/test_restore_instructions.py <point>` | **21 / 21** | `evidence/logs/restore_instructions_structural_checks.txt` |
| 6. recovery-script concurrency/reservation tests (temporary directories, simulated backups) | `python3 scripts/test_recovery_point_concurrency.py` | **11 / 11** | `evidence/concurrency/recovery_point_concurrency_tests.txt` |
| 7. live Sales seal/send pilot + refused pre-sudo probes | `odoo shell` (`evidence/scripts/pilot_closeout_hardening.py`) | PASS | `evidence/pilot/pilot_closeout_hardening.json` |

Totals: SIPANEL 253 → **266** by module statistics (`sipanel_sale_scope` 154 → 167); methods 193 → 204 (+11); Shamsi 80. Grand total **346 / 0 failures**. No existing assertion removed or weakened; no test file other than the new one changed.
