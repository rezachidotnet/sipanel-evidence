# SIPANEL Translation Regression Test Results (STEP 2A, run 20260921T013000Z)

## 1. Totals

| Suite | Before STEP 2A | After STEP 2A |
|---|---|---|
| `sipanel_commercial_scope_core` | 20 | **51** |
| `sipanel_sale_scope` | 37 | **58** |
| `sipanel_scope_costing` | 5 | **5** |
| `sipanel_scope_execution` | 8 | **8** |
| **SIPANEL total** | **70, 0 failures** | **122, 0 failures** |
| `sale_shamsi_report` | 80, 0 failures | **80, 0 failures** |
| **Grand total** | 150 | **202, 0 failures** |

52 tests added. Logs: `evidence/logs/test_sipanel_after_2a.log`,
`evidence/logs/test_shamsi_after_2a.log`.

## 2. Coverage of the 16 required areas

| # | Required test | Test | Suite |
|---|---|---|---|
| 1 | Persian master text stored and retrieved through `fa_IR` | `test_persian_master_text_round_trips_through_fa_IR` | core |
| 2 | English translation stored and retrieved through `en_US` | `test_english_master_text_round_trips_through_en_US` | core |
| 3 | translation editor / native field behaviour | `test_one_field_holds_every_language_and_the_dialog_sees_them` (adds `ru_RU` through the dialog's own API) | core |
| 4 | migration of existing FA/EN values | `TestLegacyTranslationMigration` — 7 tests incl. idempotency and dry run | core |
| 5 | missing translation warns in draft | `test_draft_warns_when_the_requested_translation_is_missing` | sale |
| 6 | missing translation blocks seal/send | `test_seal_fails_closed_when_the_requested_translation_is_missing`, `test_readiness_blocks_on_a_missing_translation` | sale |
| 7 | internal-only component exemption | `test_internal_only_component_needs_no_customer_translation` | sale |
| 8 | Persian quotation snapshot resolution | `test_persian_quotation_snapshots_the_persian_master_text`, `test_component_labels_are_resolved_in_the_quotation_language` | sale |
| 9 | English quotation snapshot resolution | `test_english_quotation_snapshots_the_english_master_text` | sale |
| 10 | master change does not alter a sealed snapshot | `test_master_translation_change_does_not_alter_an_existing_snapshot`, `test_sealed_snapshot_and_artifact_survive_a_master_translation_change` | sale |
| 11 | released master translation not editable by a normal write | `test_released_translation_cannot_be_edited_by_a_normal_write` | core |
| 12 | not editable via language context, RPC, import or `sudo` | `test_released_translation_cannot_be_edited_through_a_language_context`, `…_through_sudo`, `…_through_the_translation_dialog`, `test_released_recipe_line_translation_is_immutable_too`, `test_translation_stays_unchanged_after_a_rejected_edit` | core |
| 13 | duplicate quotation preserves snapshot/provenance | `test_duplicate_quotation_keeps_the_original_snapshot_and_provenance` | sale |
| 14 | PDF and portal display the resolved snapshot language | `test_customer_note_uses_the_resolved_snapshot_language`, `test_english_quotation_note_is_english`, `test_sealed_text_artifact_carries_the_resolved_language` + the live PDF check in the UI report §7 | sale |
| 15 | no cost / margin / internal leakage | `test_no_cost_margin_or_internal_text_reaches_the_customer_payload`, `test_master_internal_description_is_not_translatable_and_stays_internal` | sale |
| 16 | existing SIPANEL and Shamsi suites green | 122 + 80, 0 failures | both |

Fallback and missing-translation cases are tested explicitly, as required:
`test_missing_translation_is_distinguished_from_a_fallback` (a fallback is
detected as a fallback even though the value is non-empty),
`test_persian_only_master_does_not_leak_into_the_english_source`,
`test_snapshot_columns_hold_only_really_stored_terms`,
`test_plan_always_writes_en_US_explicitly`.

Additional tests beyond the list: the release-checksum group
(`TestReleaseChecksumCoversTranslations`, 5 tests) proving a translation edit
cannot slip past released-version immutability.

## 3. Pre-existing tests that had to change

| File | Change | Why |
|---|---|---|
| `core/tests/common.py` | fixture creates `customer_label` / `customer_description` and adds Persian terms via a new `set_translation()` helper | the legacy fields no longer exist |
| `core/tests/test_scope_lifecycle.py` | 3 immutability assertions retargeted to `customer_label` | same |
| `sale/tests/test_governance.py`, `test_quote_engine.py` | master writes retargeted to `customer_label` | same |
| `sale/tests/test_quote_engine.py::test_pt08_note_stale` | writes `customer_label_resolved` on the **snapshot component** | the note is built from the resolved snapshot term |

No assertion was weakened. The immutability tests still assert the same refusals,
now on the native field, and they gained the four new bypass routes.

## 4. Two failures found on the first full run, both mine

| Failure | Cause | Fix |
|---|---|---|
| `TestQuoteEngine.test_pt08_note_stale` — `ValueError: Invalid field 'customer_label' in 'sipanel.quote.scope.component'` | my bulk rename hit a **snapshot** component, which correctly has no `customer_label` | retargeted to `customer_label_resolved`, which is what the note builder reads |
| `TestTranslationSnapshot.test_sealed_snapshot_and_artifact_survive_a_master_translation_change` | compared two artifact hash **lists** whose order is not guaranteed | compare sorted |

Both were defects in the new tests, not in the product; the second one in
particular was not a real immutability failure — the same two hashes were
present, in the other order.

## 5. Compatibility re-verified

| Invariant | Status |
|---|---|
| Product ≠ Commercial Scope ≠ Recipe ≠ Manufacturing BoM | unchanged — no model relationship touched |
| Estimate ≠ Actual | unchanged — costing suite green |
| all six Billing Treatments | unchanged — `treatment_transition` only re-commented |
| D-02 Persian UoMs (`عدد` / `ساعت`) | intact — customer-output tests green, live PDF confirms |
| D-03 acceptance binding | intact — governance and customer-output tests green |
| L-01 and L-02 layout corrections | intact — 80 Shamsi tests green, live PDF is 2 pages with IRANSans |
| quotation duplication | intact — `test_pt09_duplicate_independent` plus the new provenance test |
| sealed revision immutability | intact — see the snapshot report |
| cost / margin leakage protections | intact — security suite green plus the new leakage test |
| `report.url`, website languages, paperformat | unchanged, re-asserted after cleanup |
