Run sipanel_scope_production_implementation_20260919T145639Z · Verdict: BLOCKED_BEFORE_DATABASE_WRITE · Status: SOURCE WRITTEN AND STATICALLY CHECKED — NOT INSTALLED, NOT RUNTIME VALIDATED (see evidence/EV-02).

# SIPANEL — Test Results Register PT-01…PT-32

Common values for every row: build commit = see `SIPANEL_RELEASE_MANIFEST.txt`; target = database `sipanel` (NOT touched); actual result = **NOT EXECUTED**; status = **BLOCKED** (harness permission, EV-02); runner = Claude Code (claude-fable-5-1), 2026-09-19 UTC. Every PT has an automated test written; the column "Test" names the method that implements it (tag `sipanel`).

| PT | Slice | Test (module · class · method) | Expected invariant | Status |
|---|---|---|---|---|
| PT-01 | B | sale_scope · TestQuoteEngine · test_pt01_add_scope_snapshot_and_cost | 8 snapshots, qty 85 m, cost 10734, no execution records, anchor unique | BLOCKED |
| PT-02 | A/B | sale_scope · test_pt02_version_isolation; core · TestScopeLifecycle · test_release_and_supersede | V1 snapshot byte-equal after V2 release + cost change | BLOCKED |
| PT-03 | A/B | sale_scope · test_pt03_dimensional_quantity; core · TestRecipeValidation · test_uom_family_contract | 8500 cm ≡ 85 m; hour/unit rejected | BLOCKED |
| PT-04 | B | sale_scope · test_pt04_override_retained_and_stale | 180 retained, stale flagged, send blocked, confirm clears | BLOCKED |
| PT-05 | B | sale_scope · test_pt05_percent_validation; core · test_percent_rules | self/cycle/cross-scope/mixed-unit refused; percent cost no demand qty | BLOCKED |
| PT-06 | B | sale_scope · test_pt06_split_with_dependent | 10377 + 357 = 10734; lineage; no duplicate occurrence | BLOCKED |
| PT-07 | B | sale_scope · test_pt07_split_alone_blocked | actionable dependency message, nothing saved | BLOCKED |
| PT-08 | B | sale_scope · test_pt08_note_stale | note stays, stale warning, send blocked until reviewed | BLOCKED |
| PT-09 | B | sale_scope · test_pt09_duplicate_independent | copy = WORKING r1, no artifacts/keys, original unaffected | BLOCKED |
| PT-10 | C | sale_scope · TestGovernance · test_pt10_optional_scope_transitions | operator/portal transition bound to sealed revision; stale link refused; section guard | BLOCKED |
| PT-11 | C | sale_scope · test_pt11_customer_scope_and_internal_only | customer scope no cost; internal-only cost included, not leaked | BLOCKED |
| PT-12 | D | execution · TestRelease · test_pt12_estimate_only_blocks | release blocked; allowance stays no-action | BLOCKED |
| PT-13 | D | execution · test_pt13_native_owner_links_not_creates | one owner, native task once, bridge links only | BLOCKED |
| PT-14 | D | execution · test_pt14_release_twice_and_concurrent | one batch on double click; LockError bounded retry | BLOCKED |
| PT-15 | D | execution · test_pt15_adapter_failure_rolls_back | no orphan PO/MO/picking; batch FAILED | BLOCKED |
| PT-16 | E | costing · TestActuals · test_pt16_pt21_reconciliation | only consumption recognised; receipt/transfer/bill excluded | BLOCKED |
| PT-17 | E | costing · test_pt16_pt21_reconciliation | finished issue once; raw/workorder excluded | BLOCKED |
| PT-18 | E | costing · test_pt16_pt21_reconciliation (bill route); landed cost DEFERRED | chosen route only | BLOCKED |
| PT-19 | E | costing · test_pt19_return_and_credit_reverse_once; execution · test_pt22_qty_delta_and_pt19_cancel_lineage | signed reversal once; nothing deleted | BLOCKED |
| PT-20 | E | costing · test_pt16_pt21_reconciliation (9 h timesheet, 450 bill) | no synthetic timesheets; approved source only | BLOCKED |
| PT-21 | E | costing · test_pt16_pt21_reconciliation | baseline 10734, revenue 12000, bridge = direct overrun − 187 | BLOCKED |
| PT-22 | D | sale_scope · test_pt22_price_only_amendment_keeps_baseline; execution · test_pt22_qty_delta_and_pt19_cancel_lineage | no price-only demand; ±deltas; no deletion | BLOCKED |
| PT-23 | B/C | sale_scope · TestSecurity · test_s07/test_s02/test_s04 | zero cost/internal/other-company/portal leakage | BLOCKED |
| PT-24 | A/B | core · test_released_version_is_immutable; sale_scope · test_s03_import_and_rpc_bypass_on_sealed | deny bypass incl. import/sudo; audit | BLOCKED |
| PT-25 | B | sale_scope · test_pt25_foreign_currency_blocked | foreign currency blocked (BQ-09) | BLOCKED |
| PT-26 | B | sale_scope · test_pt26_cost_unit_conversion | dozen→unit factor 1/12; wrong unit refused | BLOCKED |
| PT-27 | B | sale_scope · test_pt27_pricing_and_margin | 12000 −10 % ⇒ 10800, margin 66; N/A at zero revenue; waiver | BLOCKED |
| PT-28 | B | sale_scope · test_pt28_known_zero_vs_missing | missing ≠ known-zero; readiness differs | BLOCKED |
| PT-29 | E | costing · test_policy_fail_closed_and_pt29_unallocated | UNALLOCATED visible; completeness incomplete | BLOCKED |
| PT-30 | infra | — (operational: recovery-point script + restore rehearsal) | restore counts/hashes equal | NOT_RUN |
| PT-31 | B | sale_scope · test_pt31_ordinary_sales_untouched | native pricing/confirm/copy unchanged | BLOCKED |
| PT-32 | B/C | sale_scope · test_pt32_snapshot_roundtrip_language | sealed artifact immune to master translation change; no internal tokens | BLOCKED |

## Additional groups

| Group | Test(s) | Status |
|---|---|---|
| Clean-database install / upgrade from preceding build | `scripts/sipanel_install_and_test.sh install|upgrade` | NOT_RUN |
| Ordinary non-Scope Sales regression | test_pt31_ordinary_sales_untouched | BLOCKED |
| Purchase / Inventory / MRP / Project regression | execution + costing suites (draft PO/MO/picking, native task once) | BLOCKED |
| Tax / discount / fiscal position | test_pt27 (discount, taxes outside R) | BLOCKED |
| Portal and PDF rendering (report 848, external_layout_bubble, duplicate commitment_date xpath) | manual on installed DB; text artifact test in test_pt32 | NOT_RUN |
| Concurrent Release and retry | test_pt14 | BLOCKED |
| Duplicate-demand | test_pt13, demand_key unique, preflight open-target check | BLOCKED |
| Security denial S-01…S-10 | see SIPANEL_SECURITY_TEST_RESULTS.md | BLOCKED |
| Finance reconciliation | test_pt16_pt21_reconciliation, test_pt19 | BLOCKED |
| Backup/restore, rollback rehearsal | — | NOT_RUN |
| C9 vertical pilot | demo · TestFixture · test_c9_oracle_from_fixture (+ full suites) | BLOCKED |

## Totals

PASS 0 / FAIL 0 / BLOCKED 31 / NOT_RUN 1 (PT-30) / NOT_APPLICABLE 0. Automated test methods written: 50 across 9 test classes.

## Failure and correction history

No test executed. Static verification (compile, XML, manifest/ACL/xml-id cross-check, stubbed import) passed after three corrections (EV-03, implementation log step 9–10). Reviewer findings applied before commit are listed in the implementation log.
