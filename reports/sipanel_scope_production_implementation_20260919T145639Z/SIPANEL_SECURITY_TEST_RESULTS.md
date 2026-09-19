Run sipanel_scope_production_implementation_20260919T145639Z · Verdict: BLOCKED_BEFORE_DATABASE_WRITE · Status: SOURCE WRITTEN AND STATICALLY CHECKED — NOT INSTALLED, NOT RUNTIME VALIDATED (see evidence/EV-02).

# SIPANEL — Security Test Results

All rows: **BLOCKED — NOT EXECUTED** (EV-02). Tests are written under `sipanel_sale_scope/tests/test_security.py`, `sipanel_commercial_scope_core/tests/test_scope_lifecycle.py` and the costing/execution suites.

| # | Required test | Test method(s) | Expected | Status |
|---|---|---|---|---|
| S-01 | ACL and record rules | test_s01_acl_matrix_subset, core test_acl_plain_user_read_only | plain user read-only; steward cannot edit quotes; sales edits own working note; auditor/append-only audit | BLOCKED |
| S-02 | Company isolation | test_s02_company_isolation | empty recordsets, usage_count 0, AccessError on read | BLOCKED |
| S-03 | Direct ORM/RPC/import bypass | test_s03_import_and_rpc_bypass_on_sealed, core test_released_version_is_immutable | load() refused, sudo refused, state write refused | BLOCKED |
| S-04 | Portal access | test_s04_portal_denied_on_internal_models | AccessError on every internal model; own sealed artifacts only; stranger sees nothing | BLOCKED |
| S-05 | Stale-link / replay | test_pt10_optional_scope_transitions | wrong hash / missing revision refused; repeat idempotent (one audit row) | BLOCKED |
| S-06 | PDF/attachment/export leakage | test_s07 (export_data), test_pt32 (artifact text has no cost tokens) | cost fields absent; no internal token in customer artifact | BLOCKED |
| S-07 | Unauthorized cost/margin access | test_s07_cost_fields_hidden_without_group | AccessError on read/search_read/export of cost fields | BLOCKED |
| S-08 | Sealed revision mutation | test_seal_accept_flow_and_mismatch, test_s03 | UserError for estimator, admin, sudo | BLOCKED |
| S-09 | Cross-project access | test_s02 + costing ACL (events/allocations only for cost viewer/finance) | denied | BLOCKED |
| S-10 | Privileged override audit | test_s10_privileged_actions_audited | audit rows with actor/reason/correlation; immutable; payload gated | BLOCKED |

PII: test fixtures use synthetic partners without e-mail or phone; no real contact is read or used.
