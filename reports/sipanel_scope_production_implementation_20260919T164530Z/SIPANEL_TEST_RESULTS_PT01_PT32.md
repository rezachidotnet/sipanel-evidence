Run sipanel_scope_production_implementation_20260919T164530Z · Target: database `sipanel` on container `odoo-sipanel` (Odoo 19.0-20260528) · Build: source commit 99dd874 (fixes on top of 931f949) · Runner: Claude Code (claude-fable-5-1) · Date: 2026-09-19 UTC

# SIPANEL — Test Results Register PT-01…PT-32 (EXECUTED)

Every row was executed by Odoo's test runner against the real registry of database `sipanel` (`--test-enable --test-tags sipanel`, post-install, inside rolled-back test transactions). Final run: **#5, `evidence/odoo-test-5.log`: 49 tests, 0 failures, 0 errors, 197 s**. Earlier runs (#1–#4) and their failures are documented in `SIPANEL_RUNTIME_DEFECT_AND_FIX_REGISTER.md`; no failing test was weakened to pass. The C9 pilot smoke (`evidence/odoo-smoke.log`) ran the 50th test after installing the test-only fixture module.

| PT | Slice | Test method (module · class · method) | Measured result / evidence | Status |
|---|---|---|---|---|
| PT-01 | B | sale_scope · TestQuoteEngine · test_pt01_add_scope_snapshot_and_cost | 8 snapshots; 85/170/340/10/8/1/17 qty; direct 10547, derived 187, total 10734; no demand; second anchor claim refused by `anchor_line_unique` (logged SQL error is the expected violation) | PASS |
| PT-02 | A/B | sale_scope · test_pt02_version_isolation; core · TestScopeLifecycle · test_release_and_supersede | V1 snapshot byte-equal after V2 release + product cost 999; V1 superseded, V2 current | PASS |
| PT-03 | A/B | sale_scope · test_pt03_dimensional_quantity; core · TestRecipeValidation · test_uom_family_contract | 8500 cm → 85 m, equal cost; hour and unit rejected (ValidationError) | PASS |
| PT-04 | B | sale_scope · test_pt04_override_retained_and_stale | 180 retained after qty 85→90; stale flagged; send blocked (OVERRIDE_STALE); confirm clears; audit rows | PASS |
| PT-05 | B | sale_scope · test_pt05_percent_validation; core · test_percent_rules | self / percent-on-percent / mixed-unit / cross-scope refused; derived line qty 0, qty_kind none | PASS |
| PT-06 | B | sale_scope · test_pt06_split_with_dependent | source 10377 + destination 357 = 10734; lineage `moved_from/to`; new occurrence uid; 6 active left | PASS (after CD-04, CD-08, CD-10) |
| PT-07 | B | sale_scope · test_pt07_split_alone_blocked | UserError naming the dependent; nothing saved | PASS |
| PT-08 | B | sale_scope · test_pt08_note_stale | manual note kept; stale after label change; send blocked; review clears; line-name write-back | PASS (after CD-06) |
| PT-09 | B | sale_scope · test_pt09_duplicate_independent | copy = WORKING r1, no artifacts/hash/acceptance, new uids, original sealed & unchanged | PASS |
| PT-10 | C | sale_scope · TestGovernance · test_pt10_optional_scope_transitions | OFFERED cost 10734 outside baseline; portal edit only after send; stale hash / missing revision refused; raw qty write refused; accept 85 & baseline 10734; idempotent (1 audit); section delete/reorder/retype refused; decline path | PASS |
| PT-11 | C | sale_scope · test_pt11_customer_scope_and_internal_only | customer scope cost N/A, preset customer_scope, mode no_action, total 10534; internal-only allowance costed but absent from payload/note | PASS |
| PT-12 | D | execution · TestRelease · test_pt12_estimate_only_blocks | preflight UserError "ESTIMATE_ONLY"; no demand | PASS |
| PT-13 | D | execution · test_pt13_native_owner_links_not_creates | registry resolves native owner; R4 blocks conflicting version; native task created once; bridge links only; no MO/picking created | PASS |
| PT-14 | D | execution · test_pt14_release_twice_and_concurrent | second click returns the same batch, 7 demands; LockError × 3 attempts → "retry exhausted"; release succeeds after lock release | PASS |
| PT-15 | D | execution · test_pt15_adapter_failure_rolls_back | vendor missing → batch FAILED with redacted summary; PO/MO/picking counts unchanged; no target; later release succeeds | PASS (after CD-03, CD-09) |
| PT-16 | E | costing · TestActuals · test_pt16_pt21_reconciliation | only done outgoing moves recognised; receipts/PO commitment stored as excluded | PASS |
| PT-17 | E | same | finished-product issue counted once; raw coil moves stored as WIP/excluded | PASS |
| PT-18 | E | same (bill route); landed cost policy = NONE (deferred) | posted bill 450 recognised; commitment excluded | PASS (landed cost DEFERRED by policy) |
| PT-19 | E | costing · test_pt19_return_and_credit_reverse_once; execution · test_pt22_qty_delta_and_pt19_cancel_lineage | refund event negative, `reversal_of` set, net 0, second refresh no duplicate; bill and credit retained; cancelled move retained (state cancel) | PASS |
| PT-20 | E | costing · test_pt16_pt21_reconciliation | 9 h timesheet at governed 30/h = 270; no synthetic timesheet created by the module; equipment bill 450 | PASS |
| PT-21 | E | same | baseline 10734 (sealed), material = gutter issue value + 850 + 340 + 17 + 220, equipment 450, labour 270, revenue 12000; variance = recognised − 10734; bridge = direct overrun − 187; contingency has no event | PASS (after TD-05, TD-07) |
| PT-22 | D | sale_scope · test_pt22_price_only_amendment_keeps_baseline; execution · test_pt22_qty_delta_and_pt19_cancel_lineage | price-only change order: no demand, quantities identical; +10 delta demand with 10-unit move; −10 delta reduces the latest positive delta (never the original); order cancel refused with a done target | PASS (after CD-07, CD-10) |
| PT-23 | B/C | sale_scope · TestSecurity · test_s07 / test_s02 / test_s04 | see security results | PASS |
| PT-24 | A/B | core · test_released_version_is_immutable; sale_scope · test_s03_import_and_rpc_bypass_on_sealed | write/unlink/create/import/sudo/admin refused; state write refused | PASS (after CD-05 fix of state guard, TD-02) |
| PT-25 | B | sale_scope · test_pt25_foreign_currency_blocked | add refused; pricelist change refused; fx_rate 1.0 company_currency | PASS |
| PT-26 | B | sale_scope · test_pt26_cost_unit_conversion | dozen→unit factor 1/12, cost 12.0 for 6 units; incompatible unit refused | PASS |
| PT-27 | B | sale_scope · test_pt27_pricing_and_margin | 12000 − 10 % → 10800, margin 66; N/A at zero revenue; Apply Price by margin; cost refresh leaves price; negative margin needs joint waiver (Sales then Finance) | PASS |
| PT-28 | B | sale_scope · test_pt28_known_zero_vs_missing | zero price = MISSING until a reason makes it KNOWN_ZERO; estimate-only always MISSING | PASS (after CD-05) |
| PT-29 | E | costing · test_policy_fail_closed_and_pt29_unallocated | no policy → POLICY_MISSING / UNPOLICIED, completeness policy_missing; re-approval; foreign-project timesheet → UNALLOCATED 30, completeness incomplete; manual Finance allocation closes it | PASS (after CD-11) |
| PT-30 | infra | restore rehearsal (evidence/EV-07) | dump restored into `sipanel_restore_rehearsal_20260919`: 196 modules, 14 orders, 88 partners, 1061 attachments = live pre-change state; filestore archive extracts 713 files; rehearsal DB dropped | PASS |
| PT-31 | B | sale_scope · test_pt31_ordinary_sales_untouched | ordinary quotation: edits, section reorder/delete, send, confirm, copy — native behaviour, no seal hash | PASS |
| PT-32 | B/C | sale_scope · test_pt32_snapshot_roundtrip_language | sealed text artifact immune to master relabel; hash verified; no cost/margin/internal token in the artifact | PASS |

## Additional groups

| Group | Evidence | Status |
|---|---|---|
| Clean install (4 modules) | evidence/odoo-install-3.log ("Modules loaded", registry 43 s) after CD-01 | PASS |
| Upgrade `-u sipanel_commercial_scope_core` (cascade) | evidence/odoo-upgrade.log, no warnings | PASS |
| Ordinary non-Scope Sales regression | test_pt31 | PASS |
| Purchase / Inventory / MRP / Project regression | execution + costing suites (draft RFQ, draft MO with project, draft picking, native task once, picking validation, MO done) | PASS |
| Tax / discount / pricelist | test_pt27 | PASS |
| Portal governed transition, stale link, section guard | test_pt10 | PASS |
| Portal/PDF/internal-data leakage | test_s07 (export), test_pt32 (artifact bytes), test_s04 (portal ACL) | PASS |
| Report hygiene (report id 848, external_layout_bubble, duplicate commitment_date xpath in sale_shamsi_report) | not exercised by automated tests; unchanged modules; PDF rendering of the quotation in test mode returned HTML (stored as portal_html artifact) | NOT_APPLICABLE to this module set — manual PDF check remains a pilot task |
| Concurrent Release / retry | test_pt14 | PASS |
| Duplicate-procurement | test_pt13 (native owner links only), demand_key unique, preflight open-target check, test_pt14 (one batch) | PASS |
| Cancellation / amendment | test_pt22 (sale + execution), order cancel guard | PASS |
| Security S-01…S-10 | SIPANEL_SECURITY_TEST_RESULTS.md | PASS |
| Double-counting reconciliation | SIPANEL_DOUBLE_COUNTING_RECONCILIATION.md | PASS |
| C9 vertical pilot (fixture module) | evidence/odoo-smoke.log: test_c9_oracle_from_fixture 1/1 | PASS |
| Backup / restore / rollback rehearsal | EV-07; rollback not needed (no failure) — procedure documented | PASS (restore) / NOT_RUN (rollback, not required) |

## Totals

PASS 32 / FAIL 0 / BLOCKED 0 / NOT_APPLICABLE 0 (PT rows). Automated tests: 49 + 1 pilot = 50 executed, 50 green in the final runs. Test records created and persisted in `sipanel`: 0 (all test transactions rolled back; the fixture module was uninstalled and its two restrict-protected leftovers archived — see SIPANEL_TEST_DATA_INVENTORY.md addendum).
