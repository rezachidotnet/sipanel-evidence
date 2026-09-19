Run sipanel_scope_production_implementation_20260919T164530Z · Target: database `sipanel` on container `odoo-sipanel` (Odoo 19.0-20260528) · Build: source commit 99dd874 (fixes on top of 931f949) · Runner: Claude Code (claude-fable-5-1) · Date: 2026-09-19 UTC

# SIPANEL — Security Test Results (EXECUTED, run #5: all green)

| # | Required test | Test method(s) | Measured | Status |
|---|---|---|---|---|
| S-01 | ACL and record rules | test_s01_acl_matrix_subset; core test_acl_plain_user_read_only | plain user: read OK, write/create AccessError; steward cannot edit quotes; sales edits own working note; waiver approver fields protected; audit append-only even as admin/sudo | PASS |
| S-02 | Company isolation | test_s02_company_isolation | other-company user: empty search on scopes/masters, usage_count 0, AccessError on read | PASS |
| S-03 | Direct ORM/RPC/import bypass | test_s03_import_and_rpc_bypass_on_sealed; core test_released_version_is_immutable | `load()` on sealed component refused (message), estimator/admin write refused, state write refused; released version immutable incl. sudo and import | PASS |
| S-04 | Portal access | test_s04_portal_denied_on_internal_models | AccessError on all 6 internal models; no artifact before send; own sealed artifacts only after send; revision read refused; stranger sees nothing | PASS |
| S-05 | Stale-link / replay | test_pt10_optional_scope_transitions | wrong hash / missing revision refused; repeated accept idempotent (one audit row) | PASS |
| S-06 | PDF/attachment/export leakage | test_s07 (export_data without cost group refused), test_pt32 (artifact contains none of standard_price/unit_cost/cost_amount/margin/allowance/contingency) | no leakage | PASS |
| S-07 | Unauthorized cost/margin access | test_s07_cost_fields_hidden_without_group | read/search_read/export of cost fields AccessError for Sales; cost viewer OK | PASS |
| S-08 | Sealed revision mutation | test_seal_accept_flow_and_mismatch, test_s03 | UserError for estimator, admin, sudo; qty/price/unlink/artifact delete refused | PASS |
| S-09 | Cross-project / cross-company actual cost | test_s02; costing ACL (events/allocations readable by cost viewer/finance only; write refused even for finance — test_pt16_pt21) | denied | PASS |
| S-10 | Privileged override audit | test_s10_privileged_actions_audited | override_qty, manual_cost, seal events with actor/reason/correlation; immutable; payload hidden without cost group | PASS |
| S-11 (added) | Spoofed internal context flag | test_pt16_pt21_reconciliation (CD-12) | `with_context(sipanel_projection=True)` write by a normal user refused | PASS |

PII: synthetic partners without e-mail/phone; the runner's signup-mail lines in the logs are Odoo test-mode notifications for the synthetic users (no mail server matched; nothing sent). Real contacts were not read or modified by any test.
