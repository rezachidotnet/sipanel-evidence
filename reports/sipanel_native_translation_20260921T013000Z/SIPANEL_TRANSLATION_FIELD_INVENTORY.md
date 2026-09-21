# SIPANEL Translation Field Inventory (STEP 2A, run 20260921T013000Z)

Taken read-only from the installed source and the live `sipanel` database
**before** any change (`evidence/scripts/inventory.py`, `migration_preview.py`).

## 1. Legacy fields found

| Model | Legacy fields | Kind | Verdict |
|---|---|---|---|
| `sipanel.scope.version` | `label_fa`, `label_en` (Char, `string='Customer label (FA)/(EN)'`, tracking) | **master** | replaced by one `customer_label` |
| `sipanel.scope.version` | `customer_description_fa`, `customer_description_en` (Text) | **master** | replaced by one `customer_description` |
| `sipanel.scope.recipe.line` | `customer_label_fa`, `customer_label_en` (Char) | **master** | replaced by one `customer_label` |
| `sipanel.quote.scope.revision` | `label_fa`, `label_en`, `customer_description_fa`, `customer_description_en` | **quotation snapshot** | **kept** — see §3 |
| `sipanel.quote.scope.component` | `customer_label_fa`, `customer_label_en` | **quotation snapshot** | **kept** — see §3 |

There is no SIPANEL QWeb report template: `sipanel_sale_scope` writes the customer
note into `sale.order.line.name` (`quote_scope_revision.py`), so the PDF and the
portal render the native Sale templates. Nothing in the report layer names a
language-specific field.

## 2. Populated records before migration

| Model | Field pair | Records | blank both | FA only | EN only | distinct per language | identical |
|---|---|---:|---:|---:|---:|---:|---:|
| `sipanel.scope.version` | `label_fa\|label_en` | 2 | 0 | 0 | 0 | **2** | 0 |
| `sipanel.scope.version` | `customer_description_fa\|_en` | 2 | **1** | 0 | 0 | **1** | 0 |
| `sipanel.scope.recipe.line` | `customer_label_fa\|_en` | 7 | 0 | 0 | 0 | **7** | 0 |
| | **total field-records** | **11** | 1 | 0 | 0 | **10** | 0 |

Both master versions are **RELEASED** (ids 111, 115); all 7 recipe lines belong to
a released version. There are no draft masters. That is why the migration has to
run under the release guard — see the migration report.

**On the word "conflicting".** A first pass classified all 10 populated records as
"conflicting" because FA ≠ EN. That is not a conflict, it is the normal case and
exactly what a translation is for. A true conflict would be a legacy value
disagreeing with a native translation that already exists, and there were **zero**
of those, because the native fields did not exist yet. The classification was
renamed `distinct_per_language` and reported that way throughout.

**On "malformed".** The first pass also flagged 2 values as malformed because they
read as the boolean `False`. That is simply how Odoo returns an empty Text column;
they are the `blank_both` record above, not corrupt data. No value had leading or
trailing whitespace, and no value had a non-string type other than empty.

## 3. Why the quotation snapshot fields stay

The brief separates master translations from quotation snapshots, and forbids
snapshot fields that read from the master. A snapshot is a frozen copy, so it must
not be a translatable field at all: a translatable field would follow later master
edits through the jsonb column and silently rewrite a sent quotation.

The snapshot columns are therefore kept as plain columns and are now filled by
resolving the master translations once, at the moment the scope is added. Three
fields were **added** next to them to satisfy "copy the resolved text into
immutable snapshot fields; record the resolved language and provenance":

| Model | New field | Purpose |
|---|---|---|
| `sipanel.quote.scope.revision` | `label_resolved`, `customer_description_resolved` | the text actually resolved for this quotation's language |
| `sipanel.quote.scope.revision` | `resolved_language` | which language that was |
| `sipanel.quote.scope.revision` | `source_version_checksum` | provenance of the master version |
| `sipanel.quote.scope.revision` | `translation_provenance` (Json) | per term: language used, whether it was a fallback, which languages exist |
| `sipanel.quote.scope.component` | `customer_label_resolved`, `label_provenance` | the same, per recipe occurrence |

Every reader prefers the resolved field and falls back to the historical
language-pair lookup when it is empty. Revisions created before STEP 2A have it
empty, so their rendered text, their note and their sealed hashes do not move.

## 4. Records that must not change

| Kind | Count | Status after migration |
|---|---:|---|
| Sealed revisions (`sent_sealed` / `accepted_sealed`) | 2 | untouched — `write_date` still 2026-09-20 06:21 |
| Quotation components | 14 | untouched — `write_date` still 2026-09-20 06:21 |
| Acceptance artifacts | 4 | untouched — `write_date` still 2026-09-20 06:12; stored text still hashes to its recorded hash |

## 5. Languages

`en_US`, `fa_IR`, `ru_RU` are installed. `en_US` is the source term of every
translatable field. `ru_RU` is active on this database but carries no SIPANEL
customer text; the design handles it without new fields — a Russian quotation
would resolve nothing, be flagged as missing, and be refused at seal.
