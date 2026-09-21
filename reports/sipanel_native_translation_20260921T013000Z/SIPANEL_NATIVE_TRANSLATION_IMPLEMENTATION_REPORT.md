# SIPANEL — Native Odoo translation-field implementation (STEP 2A)

| | |
|---|---|
| Run | `20260921T013000Z` (2026-09-21 01:25–02:10 UTC) |
| Scope | database `sipanel`, container `odoo-sipanel` only |
| Verdict | **PASS** — masters use native translatable fields, 20 legacy terms migrated with nothing lost, sealed snapshots unchanged, 202 tests green |
| Modules changed | `sipanel_commercial_scope_core` 19.0.1.0.0 → **19.0.1.1.0**, `sipanel_sale_scope` 19.0.1.0.0 → **19.0.1.1.0**, `sipanel_scope_demo` (test fixture) |
| Not changed | `sale_shamsi_report`, `sipanel_scope_costing`, `sipanel_scope_execution`, Product Master, `report.url`, website languages, paperformat |
| Recovery point | `/opt/odoo/backups/sipanel-pre-translation-20260921T013000Z` (created and verified before the first write) |
| Restart | **none** — `odoo-sipanel` `RestartCount=0`, `StartedAt=2026-09-20T06:40:08Z` |
| Other tenants | untouched — no command addressed `odoo-avizsazeh`, `odoo-shahbazi`, `odoo-ahantorob`, or any database but `sipanel` |

---

## 1. What changed

### Masters — one native field per customer text

| Model | Before | After |
|---|---|---|
| `sipanel.scope.version` | `label_fa`, `label_en` | **`customer_label`** — Char, `translate=True`, tracking |
| `sipanel.scope.version` | `customer_description_fa`, `customer_description_en` | **`customer_description`** — Text, `translate=True` |
| `sipanel.scope.recipe.line` | `customer_label_fa`, `customer_label_en` | **`customer_label`** — Char, `translate=True` |

Six language-specific columns became three translatable ones. The operator sees
one field and Odoo's standard translation control; `fa_IR`, `en_US` and any
future active language are maintained there, with no new field. `ru_RU` is
already installed and works without any change.

### Quotation snapshots — resolved once, then frozen

The snapshot columns stay plain columns, because a translatable snapshot would
follow later master edits and silently rewrite a sent quotation. They are now
filled by resolving the master's **stored** terms at add-scope time, and four
fields were added to record what was resolved:
`label_resolved`, `customer_description_resolved`, `resolved_language`,
`source_version_checksum`, `translation_provenance`, plus
`customer_label_resolved` and `label_provenance` per component.

Every reader prefers the resolved field and falls back to the historical
language-pair lookup when it is empty, so the two revisions sealed before this
step render exactly as before.

### Language readiness — fail closed

A draft may fall back, but the gap is posted on the Scope's chatter and recorded;
`action_seal()` refuses to send a quotation whose customer text has no
translation in that quotation's language. Internal-only components are exempt.

### Release checksum — v2 covers the whole translation map

`_content_checksum_payload()` now hashes the complete stored translation map in
sorted language order for the version and every recipe line. Releases made before
this step keep `checksum_algo='v1'` and their recorded checksum, so nothing was
rewritten. `update_field_translations` is overridden on both master models, so a
released version cannot be edited through the translation dialog either.

## 2. Verifying the Odoo 19 translation API

The brief asked for the technically correct way to detect a real stored
translation. Both facts below were checked against the installed source and then
measured, because getting this wrong silently sends the wrong language to a
customer.

1. **`get_field_translations()` cannot answer it.** It reads each language under
   `prefetch_langs`, and `Text._insert_cache` fills every installed language with
   `val['en_US']` when that flag is set. A language with no stored term is
   indistinguishable from one translated identically to English. Measured: a
   product with only an English name reports the English string for `fa_IR`.
2. **`Text._get_stored_translations(record)` is the only accessor that returns
   the raw jsonb map** with no fallback. `stored_translations()` wraps it in one
   place, with a conservative per-language comparison if a future version removes
   it. It is an ORM accessor, not hand-written translation SQL — no `UPDATE` of a
   translation is issued anywhere outside `update_field_translations`.

A third measurement changed the design. On a NULL jsonb column,
`update_field_translations(f, {'fa_IR': 'x'})` **copies the Persian term into the
`en_US` source**. Every write here therefore passes `en_US` explicitly, blank when
the record has no English text — which is also the correct representation of a
Persian-only master, since an English quotation then finds nothing and fails
closed.

## 3. Migration

11 field-records scanned, **10 written, 20 terms (10 `en_US` + 10 `fa_IR`), 1
genuinely blank and skipped, 0 lost**. The applied result equals the preview
exactly. Full detail, including the per-rule mapping and the rollback path, is in
`SIPANEL_TRANSLATION_MIGRATION_PREVIEW_AND_RESULT.md`.

**One assumption was wrong and is worth flagging:** the plan expected the legacy
columns to remain dormant. Odoo 19 **dropped** them once the fields were removed
(the upgrade log shows the `ir.model.fields` deletions). That is a better outcome
than the dormant-column fallback the brief permitted, and it was safe because
post-migrate runs before the field cleanup — but it means a source-only revert is
no longer sufficient after this migration, and the v1 checksum verifier had to be
rewritten to reconstruct its payload from the migrated translation map instead of
reading those columns. Version 115 verifying `True` under v1 is the evidence that
the reconstruction is exact.

## 4. Results

| Area | Result |
|---|---|
| Migrated records / terms | 10 records, 20 terms — `en_US` 10, `fa_IR` 10 |
| Conflicts | **0** true conflicts. All 10 populated records had FA ≠ EN, which is the normal case, not a conflict — kept as separate language terms |
| Blanks | 1 (`customer_description` on version 111) — skipped, not overwritten, still blank |
| Sealed snapshots changed | **none** — snapshot tables' `write_date` all predate the migration; stored artifact text still hashes to its recorded hash |
| UI | one customer label, one customer description, no `(FA)`/`(EN)` label, translation control available, no legacy field in any view |
| Tests | **202 green** (SIPANEL 122, Shamsi 80); 70 → 122 in SIPANEL, 52 added |
| Live end-to-end | Persian quotation resolved to `متعلقات آبرو (داده آزمایشی)`, PDF 2 pages, IRANSans embedded, `ریال`/`عدد`/`ساعت` present, no English leakage, no cost or margin leakage |

## 5. FACT / INFERENCE / RECOMMENDATION

### FACT
- Six language-specific master columns were replaced by three `translate=True`
  fields; the legacy columns no longer exist in the database.
- 20 terms migrated; preview and applied result identical; nothing lost.
- Both master versions on this database are RELEASED, so the migration ran under
  the release guard — the same guard that now refuses ordinary translation edits.
- `update_field_translations` bypasses `write`; without the override added here,
  a released Persian label could have been rewritten while its English term and
  release checksum stood still.
- Sealed revisions, components and artifacts were not written to.

### INFERENCE
- The v1/v2 checksum split is the only way to satisfy both "include the complete
  translation map" and "previously sealed content unchanged" without rewriting a
  recorded checksum. Rewriting them would have destroyed the evidence value of
  the field.
- Keeping the snapshot columns rather than replacing them with translatable
  fields is what makes the two pre-existing sealed revisions render unchanged.
  A translatable snapshot would have been a live read of the master by another
  name.
- Version 111's checksum mismatch is caused by its recipe lines having been
  deleted with the demo module on 2026-09-19, not by this migration: its text
  reconstructs correctly, and version 115 — which kept its lines — verifies.

### RECOMMENDATION
| Id | Recommendation | Priority |
|---|---|---|
| R-1 | Complete the `ru_RU` terms, or deactivate `ru_RU` if it is not a customer language. Today a Russian-language customer would be refused at seal — correct, but better decided deliberately. | medium |
| R-2 | Decide what to do about version 111, the archived demo leftover whose release checksum can no longer verify. Cleanest is to archive it out of the master list entirely. | medium |
| R-3 | Prune old recovery points — six now, ~110 MB each, on a filesystem at 90 %. Carried over from STEP 1D and now more pressing. | medium |
| R-4 | When the next module adds a customer-facing text field, use `translate=True` from the start and reuse `snapshot_customer_text()`; the FA/EN pair pattern is now retired. | low |
| R-5 | The separately-billable Sale/Invoice-line work (next step) will add customer text of its own — it should take its labels from the same resolved snapshot, not re-resolve the master. | low |

## 6. Evidence index

| Path | Contents |
|---|---|
| `evidence/migration/preview.json` | pre-upgrade migration preview, per record |
| `evidence/migration/verify.json` | post-migration verification |
| `evidence/ui_e2e.json` | rendered-view UI validation + live end-to-end result |
| `evidence/SIPANEL_TRANSLATION_E2E_QUOTATION.pdf` | the live Persian quotation |
| `evidence/logs/upgrade_2a.log` | upgrade incl. the migration preview/applied lines |
| `evidence/logs/test_sipanel_after_2a.log`, `test_shamsi_after_2a.log` | test runs |
| `evidence/source_diff/sipanel_step2a.diff` | the complete source diff |
| `evidence/scripts/` | every script used |
