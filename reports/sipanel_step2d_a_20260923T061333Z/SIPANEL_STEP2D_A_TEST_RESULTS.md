# SIPANEL STEP 2D-A — Test results

Run: 20260923T061333Z — Status: **NOT_EXECUTED** (BLOCKED_DISK_CAPACITY before the first write).

| suite | planned | executed | result |
|---|---|---|---|
| focused STEP 2D-A tests (roles, analytic, change order, backoff) | yes | no | not written, not run |
| full SIPANEL suite (baseline 266 tests, 0 failures at 2C-CLOSEOUT-HARDENING) | yes | no | not rerun; no source changed, baseline stands |
| sale_shamsi_report regression (baseline 80 tests, 0 failures) | yes | no | not rerun; module untouched |
| recovery structural checks (scripts/test_recovery_point_concurrency.py, test_restore_instructions.py) | yes | no | not rerun; script unchanged since fce346b |
| live controlled smoke test | yes | no | no synthetic record created |

No assertion was added, removed or weakened. Running the test runner was also avoided deliberately: it creates a test database of roughly the size of `sipanel` (~150 MB) on the same filesystem that already fails the capacity gate.
