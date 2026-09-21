# SIPANEL Translation Snapshot and Immutability Report (STEP 2A, run 20260921T013000Z)

## 1. The boundary

```
  MASTER  (sipanel_commercial_scope_core)        QUOTATION  (sipanel_sale_scope)
  ───────────────────────────────────────        ──────────────────────────────────
  sipanel.scope.version                          sipanel.quote.scope.revision
    customer_label        jsonb  translate=True    label_resolved        varchar  ← resolved once
    customer_description  jsonb  translate=True    customer_description_resolved
  sipanel.scope.recipe.line                        resolved_language
    customer_label        jsonb  translate=True    source_version_checksum
                                                   translation_provenance  jsonb
             │                                     label_fa / label_en   ← only real terms
             │  resolve once, at add-scope         sipanel.quote.scope.component
             └────────────────────────────────►      customer_label_resolved
                    copy, never reference             label_provenance
```

Master text is translatable. Snapshot text is **never** translatable — asserted
by `test_snapshot_is_not_a_live_read_of_the_master`, which walks
`rev._fields[...].translate` for every snapshot column.

## 2. What happens when a Scope is added to a quotation

1. the quotation language is taken from the customer (`partner.lang`);
2. `snapshot_customer_text()` reads the master's **stored** terms — not a
   fallback — and returns the term for that language, the terms worth freezing,
   and a provenance record;
3. the resolved term goes into `label_resolved` / `customer_label_resolved`, and
   the per-language terms into the existing `label_fa` / `label_en` columns.
   **Only terms that really exist are written**: an English term is never copied
   into the Persian column;
4. `resolved_language`, `source_version_checksum` and `translation_provenance`
   record where the text came from;
5. if anything had to fall back, the gap is posted on the Scope's chatter and
   stored in `translation_provenance['missing']`.

## 3. Immutability of an existing quotation

| Claim | Test |
|---|---|
| a later master translation change does not alter an existing snapshot | `test_master_translation_change_does_not_alter_an_existing_snapshot` |
| a sealed revision's hash and artifacts survive a master translation change | `test_sealed_snapshot_and_artifact_survive_a_master_translation_change` |
| a duplicate copies the quotation, it does not re-resolve today's master | `test_duplicate_quotation_keeps_the_original_snapshot_and_provenance` |
| snapshot fields are not translatable | `test_snapshot_is_not_a_live_read_of_the_master` |

Live evidence on the production data is in the migration report §5: the snapshot
tables' `write_date` all predate the migration, and both stored text artifacts
still hash to their recorded `content_hash`.

## 4. Immutability of a released master, in every language

`write` already covered a language context, an import, an RPC call and `sudo()`,
because the guard is a process-local token rather than a permission. It did
**not** cover `update_field_translations`, which is the method Odoo's own
translation dialog calls and which writes the jsonb column without going through
`write`. Without the override, a released Persian label could have been rewritten
while the English term and the release checksum stood still.

Both master models now override it:

| Route | Blocked by | Test |
|---|---|---|
| form write | `write` guard | `test_released_translation_cannot_be_edited_by_a_normal_write` |
| write under `lang=fa_IR` | `write` guard | `test_released_translation_cannot_be_edited_through_a_language_context` |
| `sudo()` | `write` guard (token, not permission) | `test_released_translation_cannot_be_edited_through_sudo` |
| translation dialog / RPC / import | `update_field_translations` override | `test_released_translation_cannot_be_edited_through_the_translation_dialog` |
| released recipe line | `_check_version_draft` in both methods | `test_released_recipe_line_translation_is_immutable_too` |
| — and nothing changed after a rejected attempt | | `test_translation_stays_unchanged_after_a_rejected_edit` |

## 5. Release checksum covers the whole translation map

`_content_checksum_payload()` (v2) hashes
`translation_map(record, 'customer_label')` — the complete stored map, in sorted
language order — for the version and for every recipe line, instead of two named
language columns. Adding a language, changing one language, or changing a recipe
line's translation all change the checksum:

| Test | Asserts |
|---|---|
| `test_checksum_payload_contains_the_full_translation_map` | the map is present and sorted |
| `test_adding_a_translation_changes_the_checksum` | a new `ru_RU` term changes it |
| `test_changing_one_language_changes_the_checksum` | a changed `fa_IR` term changes it |
| `test_recipe_line_translation_participates_in_the_checksum` | a line's term changes it |
| `test_existing_release_keeps_its_recorded_checksum_verifiable` | v1 releases still verify under v1 |

Existing releases keep the algorithm they were made with (`checksum_algo`), so no
recorded checksum was rewritten. See the migration report §6.

## 6. Language readiness — fail closed

| Situation | Behaviour |
|---|---|
| draft, requested translation missing | allowed, falls back, **warning posted on the Scope**, recorded in `translation_provenance['missing']`, and `LABEL_LANG` is a blocking readiness issue |
| sealing / sending, requested translation missing | `action_seal()` raises; the revision stays `working` and no artifact is created |
| internal-only component missing a customer translation | exempt — it never reaches the customer (`label_provenance['exempt']`) |
| customer-eligible component with no label in any language | warning only (`LABEL`), and release validation R2 blocks it at the master |

Tests: `test_draft_warns_when_the_requested_translation_is_missing`,
`test_seal_fails_closed_when_the_requested_translation_is_missing`,
`test_seal_succeeds_once_the_translation_exists`,
`test_readiness_blocks_on_a_missing_translation`,
`test_internal_only_component_needs_no_customer_translation`.

## 7. Detecting a real translation rather than a fallback

Verified against the installed Odoo 19 source and by measurement, not assumption:

* `Model.get_field_translations()` returns the `en_US` **fallback** for a language
  with no stored term — `Text._insert_cache` fills every installed language with
  `val['en_US']` under `prefetch_langs`, which is what that method uses. It cannot
  answer the question.
* `Text._get_stored_translations(record)` returns the raw jsonb map with no
  fallback. It is the only accessor in the installed ORM that can, so
  `stored_translations()` wraps it in one place, with a conservative
  per-language fallback if a future version removes it. This is an ORM accessor,
  not hand-written translation SQL; no `UPDATE` of a translation is ever issued
  outside `update_field_translations`.

A measured trap that shaped the design: on a NULL jsonb column,
`update_field_translations(f, {'fa_IR': 'x'})` **copies the Persian term into the
`en_US` source**. Every write in this implementation therefore passes `en_US`
explicitly — blank when the record has no English text. Covered by
`test_plan_always_writes_en_US_explicitly` and
`test_persian_only_master_does_not_leak_into_the_english_source`.
