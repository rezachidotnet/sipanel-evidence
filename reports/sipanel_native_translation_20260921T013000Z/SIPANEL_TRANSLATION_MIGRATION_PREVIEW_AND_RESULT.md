# SIPANEL Translation Migration — Preview and Result (STEP 2A, run 20260921T013000Z)

## 1. Preview (produced BEFORE the upgrade)

`evidence/scripts/migration_preview.py` ran against the live database while the
legacy columns still existed and the native columns did not, so it could not
write anything even by accident. It classified every legacy value with the same
`plan_record()` the real migration uses.

| Model | Field pair → native field | Records | Plan |
|---|---|---:|---|
| `sipanel.scope.version` | `label_fa\|label_en` → `customer_label` | 2 | 2 × distinct per language |
| `sipanel.scope.version` | `customer_description_fa\|_en` → `customer_description` | 2 | 1 × distinct per language, 1 × blank (skip) |
| `sipanel.scope.recipe.line` | `customer_label_fa\|_en` → `customer_label` | 7 | 7 × distinct per language |

```
scanned 11 field-records, 10 to write
terms:  en_US 10, fa_IR 10  (20 terms)
blank and skipped: 1
checksum_algo → v1 on 2 released versions (ids 111, 115)
no record required a blank en_US, no record had a pre-existing native translation
```

Full preview: `evidence/migration/preview.json` (per-record, with value lengths
rather than values).

## 2. Result (post-migrate, during the upgrade)

`sipanel_commercial_scope_core` 19.0.1.0.0 → **19.0.1.1.0**, so
`migrations/19.0.1.1.0/post-migrate.py` ran. It logs a dry run first, then
applies, so the log itself carries the before/after comparison:

```
SIPANEL STEP 2A translation backfill preview: {'records_scanned': 11, 'records_written': 10,
    'terms_written': 20, 'terms_by_lang': {'en_US': 10, 'fa_IR': 10}, 'skipped': 1}
SIPANEL STEP 2A translation backfill applied:  {'records_scanned': 11, 'records_written': 10,
    'terms_written': 20, 'terms_by_lang': {'en_US': 10, 'fa_IR': 10}, 'skipped': 1}
SIPANEL STEP 2A checksum_algo v1 marked on 2 released version(s)
```

**The applied result equals the preview exactly.** Log:
`evidence/logs/upgrade_2a.log`. Verification: `evidence/migration/verify.json`.

### Migrated content

| Record | `customer_label` after migration |
|---|---|
| version 115 | `en_US`: "Gutter accessories (validation data)" · `fa_IR`: "متعلقات آبرو (داده آزمایشی)" |
| version 111 | `en_US`: "Gutter accessories" · `fa_IR`: "متعلقات آبرو" |
| 7 recipe lines | 14 terms, 2 languages each |
| version 115 `customer_description` | `en_US` + `fa_IR` |
| version 111 `customer_description` | none — it was blank before, and stays blank |

**Nothing was lost:** 11 field-records in, 10 written, 1 genuinely empty.
20 terms stored, which is exactly the 20 non-empty legacy values counted in the
inventory.

## 3. Migration rules and how each was met

| Rule | How |
|---|---|
| existing FA → `fa_IR`, existing EN → `en_US` | `plan_record()`; no other mapping exists |
| never overwrite a non-empty native translation with an empty legacy value | a term is dropped from the write when its value is empty and a stored term already exists; covered by `test_plan_never_overwrites_a_native_translation_with_a_blank_legacy_value` |
| preserve conflicting values as separate language translations | FA and EN are written to different language keys and never merged or compared for precedence |
| preserve audit / provenance | the migration runs under the release guard and is logged; released versions keep their recorded checksum and are marked `checksum_algo='v1'` |
| do not modify sealed snapshot content | the migration touches only `sipanel_scope_version` and `sipanel_scope_recipe_line`; see §5 |
| remove legacy FA/EN fields from operator views | done — see the UI report |
| legacy columns may remain dormant | they did not have to: see §4 |

## 4. What actually happened to the legacy columns

The plan assumed the columns would stay dormant, because Odoo historically only
warns about the column of a removed field. **On Odoo 19 they were dropped.** The
upgrade log shows it:

```
Deleting 16572@ir.model.fields (…field_sipanel_scope_version__label_fa)
Deleting 16611@ir.model.fields (…field_sipanel_scope_recipe_line__customer_label_fa)
```

and afterwards `information_schema` shows no `*_fa` / `*_en` column on either
table. The ordering is what makes this safe: post-migrate runs **before** the
field cleanup, so the data was read and rewritten as translations first. Verified
end state:

```
sipanel_scope_version     -> customer_label jsonb, customer_description jsonb, checksum_algo varchar
sipanel_scope_recipe_line -> customer_label jsonb
dormant *_fa / *_en columns remaining: none
```

This is a better outcome than the dormant-column fallback the brief allowed, but
it had one consequence that had to be fixed: the v1 checksum verifier was written
to read those columns and could no longer run. It now **reconstructs** the v1
payload from the migrated translation map (`fa_IR` → `label_fa`, `en_US` →
`label_en`, absent → `False`, which is what an empty column used to read as).
That reconstruction is exact because the migration is a pure relabelling — and it
is self-checking: version 115, which still has all its content, verifies `True`
under v1 (see §6).

## 5. Sealed snapshots were not modified

| Evidence | Result |
|---|---|
| `write_date` of every `sipanel_quote_scope_revision` row | max 2026-09-20 06:21:57 — **before** the migration (2026-09-21 01:28:50) |
| `write_date` of every `sipanel_quote_scope_component` row | max 2026-09-20 06:21:57 |
| `write_date` of every `sipanel_quote_scope_artifact` row | max 2026-09-20 06:12:20 |
| stored text artifacts re-hashed from their stored content | both match their recorded `content_hash` |
| models the migration writes to | only `sipanel.scope.version` and `sipanel.scope.recipe.line` |

`_current_seal_hash()` does **not** match the recorded `sealed_hash` for the two
sealed revisions of `SI-26/312`. That is pre-existing and unrelated: the seal
payload includes the live `order.amount_untaxed` / `amount_total`, and that order
was cancelled and edited during the 2026-09-20 validation runs (live untaxed
39,500,000 against a sealed projection of 28,500,000). The stored hash itself is
untouched, which is what immutability means here; the recomputation is a drift
detector and it is correctly reporting drift that predates this step.

## 6. Release checksums after migration

| Version | State | Lines | `checksum_algo` | Recorded checksum verifies |
|---|---|---:|---|---|
| 115 | released | 7 | v1 | **yes** |
| 111 | released | **0** | v1 | no |

Version 111 is the archived demo leftover `SIPANEL-PT-GUTTER`. Its recipe lines
were deleted when the demo module was uninstalled on 2026-09-19, long before this
step; a release checksum covers the recipe, so it could not have matched since
then. The translation part of its payload reconstructs correctly — its
`customer_label` migrated to both languages — so the mismatch is entirely the
missing lines. Version 115, which kept its 7 lines, verifies `True`, which is what
proves the reconstruction algorithm itself is exact.

No checksum was recomputed or rewritten for any released version. From now on new
releases use **v2**, which hashes the complete stored translation map in sorted
language order.

## 7. Rollback

Not needed; no acceptance check failed. If it had been:

```
# restore the pre-STEP-2A database
docker exec -i odoo-db pg_restore -U odoo -d <target> \
  < /opt/odoo/backups/sipanel-pre-translation-20260921T013000Z/sipanel.dump
sudo tar -C /opt/odoo/data/filestore -xzf \
  /opt/odoo/backups/sipanel-pre-translation-20260921T013000Z/filestore-sipanel.tar.gz
git revert <commit>   # then -u sipanel_commercial_scope_core,sipanel_sale_scope
```

Because Odoo dropped the legacy columns, a source-only revert is **not** enough
after this migration: the database restore is the rollback path.
