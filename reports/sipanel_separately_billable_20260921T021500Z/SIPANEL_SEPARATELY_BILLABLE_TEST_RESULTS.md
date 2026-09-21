# SIPANEL Separately-Billable Test Results (STEP 2B, run 20260921T021500Z)

## 1. Totals

| Suite | Before STEP 2B | After STEP 2B |
|---|---|---|
| `sipanel_commercial_scope_core` | 51 | **52** (+1, the P1 accessor test) |
| `sipanel_sale_scope` | 58 | **119** (+61) |
| `sipanel_scope_costing` | 5 | **5** |
| `sipanel_scope_execution` | 8 | **8** |
| **SIPANEL total** | **122, 0 failures** | **184, 0 failures** |
| `sale_shamsi_report` | 80, 0 failures | **80, 0 failures** |
| **Grand total** | **202** | **264, 0 failures** |

Logs: `evidence/logs/test_sipanel_final_2b.log`, `evidence/logs/test_shamsi_final_2b.log`.
`sale_shamsi_report` was not modified in this step (`git status` clean, HEAD `5680013`).

## 2. Coverage of the 30 required tests

| # | Required | Test |
|---|---|---|
| 1 | one eligible own-line component → exactly one Sale Line | `test_eligible_own_line_component_creates_exactly_one_sale_line` |
| 2 | repeated synchronisation creates no duplicate | `test_repeated_synchronisation_creates_no_duplicate` (+ `test_database_constraint_refuses_a_second_line_for_one_component`) |
| 3 | included component creates no separate line | `test_included_component_creates_no_separate_line` |
| 4 | internal-only creates no separate line | `test_internal_only_creates_no_separate_line` |
| 5 | customer-scope creates no separate line | `test_customer_scope_creates_no_separate_line` |
| 6 | inactive/removed component excluded | `test_deactivated_component_line_is_retired` |
| 7 | product-backed mapping | `test_product_backed_mapping_uses_the_component_product` |
| 8 | estimate-only without product blocks readiness | `test_estimate_only_without_product_blocks_readiness` |
| 9 | missing selling price blocks seal | `test_missing_selling_price_blocks_seal` |
| 10 | known-zero selling price distinguishable | `test_known_zero_selling_price_is_distinguishable_and_allowed` (+ `test_price_status_is_not_applicable_for_an_included_component`) |
| 11 | native taxes / fiscal position apply | `test_native_taxes_apply_to_the_generated_line` |
| 12 | anchor total excludes the separate line amount | `test_anchor_total_excludes_the_separate_line_amount` |
| 13 | quotation reconciliation has no double billing | `test_reconciliation_reports_no_double_billing`, `test_a_component_is_never_both_included_and_separate`, `test_included_component_stays_out_of_the_customer_note_bullets` |
| 14 | optional unaccepted line quantity zero, non-invoiceable | `test_optional_unaccepted_line_is_quantity_zero` |
| 15 | optional acceptance idempotent | `test_optional_acceptance_is_idempotent` (+ `test_optional_acceptance_gives_the_line_its_governed_quantity`) |
| 16 | provisional invoicing gate | `test_provisional_line_is_gated_from_invoicing`, `test_resolving_a_provisional_component_lifts_the_gate` |
| 17 | confirmed order produces the expected invoice line | `test_confirmed_order_produces_the_expected_invoice_line` |
| 18 | invoice description uses the frozen resolved translation | `test_invoice_description_uses_the_frozen_resolved_translation` |
| 19 | invoice line carries source provenance | `test_invoice_line_carries_source_provenance` |
| 20 | no duplicate procurement or execution demand | `test_generated_line_does_not_add_a_second_procurement_owner`, `test_one_component_yields_one_execution_demand` |
| 21 | no duplicate Project Cost | covered by 20 (a generated line creates no stock move, purchase line or analytic cost) + the unchanged recognition-policy suite |
| 22 | duplicate preserves snapshot, gets independent lines | `test_duplicate_quotation_gets_independent_projected_lines` |
| 23 | sealed line cannot be edited directly | `test_sealed_generated_line_cannot_be_edited_directly` |
| 24 | seal drift blocks acceptance | `test_seal_drift_blocks_acceptance` |
| 25 | seal drift blocks confirmation | `test_seal_drift_blocks_confirmation` |
| 26 | changed content requires new revision and reseal | `test_commercial_change_after_sealing_requires_a_new_revision_and_reseal` (+ `test_prior_artifacts_are_retained_after_amendment`) |
| 27 | RPC / import / context spoof attempts fail | `test_provenance_cannot_be_supplied_on_create`, `test_provenance_cannot_be_written_by_sudo_import_or_rpc_context`, `test_invoice_provenance_cannot_be_forged_on_a_manual_invoice` |
| 28 | Persian and English output | `test_invoice_description_uses_the_frozen_resolved_translation`, `test_english_quotation_invoices_in_english` |
| 29 | PDF/Portal show the separate line without internal leakage | `test_generated_line_appears_in_the_customer_pdf_without_internal_data`, `test_cost_and_margin_stay_restricted_on_the_generated_line` |
| 30 | existing SIPANEL and Shamsi suites green | 184 + 80, 0 failures |

Beyond the list: `test_seal_drift_blocks_invoice_creation` (the third gate),
`test_governed_manual_price_wins_over_the_pricelist`, and
`test_amendment_does_not_double_bill_the_same_component` — see §4.

## 3. Test design notes

* The fixture master carries one component of **every** treatment shape
  (included, separately billable, provisional, customer-scope, internal-only),
  so each test exercises the axes against a realistic recipe rather than a
  single-purpose stub.
* The master recipe line has no `provisional_basis` field, so PROVISIONAL is
  expressed on the component after the Scope is added — the same way STEP 1C
  and 1D did it. Mutating a component correctly marks the note stale, so the
  fixture regenerates the note; staleness is not what these tests are about.
* The spoof tests include `with_context(sipanel_projection=True)` — a **bare**
  context flag with no process-local token — to prove an RPC caller cannot unlock
  the projection path by guessing the key.

## 4. A real defect found by the live pilot, not by the first test pass

The first full test run was green, and the pilot then failed at confirmation
with a seal-drift refusal. The cause was not the drift gate but a genuine bug:

> `action_amend()` creates a new working revision and a fresh projection, while
> the superseded revision's Sale Lines were left in place — so the same
> component was billed twice on one order, and the order total moved.

Fixed by `_retire_superseded_projection()`, which deletes the prior revision's
projected lines (and leaves alone, while reporting, any that are already
invoiced or delivered). Now guarded by
`test_amendment_does_not_double_bill_the_same_component`, which asserts the line
count and the order total are unchanged by an amendment and that exactly one
line per component survives, owned by the new revision.

This is the single most valuable finding of the step, and it came from running
the thing for real.

## 5. Test-harness defects corrected during the run

None of these were product defects:

| Symptom | Cause | Fix |
|---|---|---|
| every test errored in the fixture | the master recipe line has no `provisional_basis`, so a provisional master line cannot be instantiated | set PROVISIONAL on the component instead |
| 18 tests blocked with "Customer note is stale" | the fixture mutates components after the note is generated, which correctly marks it stale | regenerate the note in the fixture |
| `'str' object has no attribute 'company_id'` | `_add_scope('fa_IR')` passed the language positionally into the `order` parameter | `_add_scope(order=self._order('fa_IR'))` |
| `'margin' unexpectedly found` in the PDF | the assertion searched raw HTML, where `margin` is a CSS property | compare against the visible text, and check concrete cost figures |
| artifact hash lists "differ" | the same two hashes in a different order | compare sorted |
