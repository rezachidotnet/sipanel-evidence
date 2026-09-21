# SIPANEL Translation UI Validation Report (STEP 2A, run 20260921T013000Z)

Checked against the **rendered view architecture** (`Model.get_view()`), not the
XML source, so what is recorded here is what the operator's browser receives.
Script: `evidence/scripts/ui_and_e2e.py`; raw result: `evidence/ui_e2e.json`.

## 1. Scope Version form (`view_sipanel_scope_version_form`)

| Requirement | Result |
|---|---|
| view renders | yes |
| only one customer label visible | `customer_label` — 1 occurrence in the Customer text group (the second occurrence is the recipe-line column in the embedded list, which is the line's own label) |
| only one customer description visible | `customer_description`, 1 occurrence |
| no legacy `*_fa` / `*_en` field anywhere in the view | **none** |
| no `(FA)` / `(EN)` in any field label | **none** — the label is now `Customer label` |
| standard translation control available | yes — `customer_label.translate = True` and 3 languages are active, which is when Odoo renders the control beside the field |
| group heading | `Customer labels` → **`Customer text`** |

## 2. Recipe line form (`view_sipanel_recipe_line_form`)

| Requirement | Result |
|---|---|
| view renders | yes |
| one customer label | `customer_label`, 1 occurrence |
| legacy fields present | **none** |
| `(FA)` / `(EN)` in labels | **none** |
| translatable | yes |

## 3. Other master views

| View | Change |
|---|---|
| Scope Version list | `label_fa` → `customer_label`; no legacy field remains |
| Scope form, Versions tab | `label_fa` → `customer_label` |
| Scope Version form, recipe line list column | `customer_label_fa` → `customer_label` |

## 4. Quotation views (snapshot side)

The brief scopes the UI change to Scope Version and Recipe. The quotation views
keep their snapshot fields, but they now lead with the resolved value and its
provenance so an operator can see which language a quotation actually carries:

| View | Change |
|---|---|
| Quote Scope Revision form | group renamed to **Customer text (frozen snapshot)**; shows `resolved_language`, `label_resolved`, `customer_description_resolved`, `source_version_checksum`; `translation_provenance` and the `label_fa`/`label_en` pair are `optional="hide"` |
| Quote Scope Component form | shows `customer_label_resolved`; the language pair is `optional="hide"` |

## 5. How the operator maintains languages now

1. open the Scope Version (must be **Draft** — a released version refuses edits in
   every language, see the immutability report);
2. type the English text in **Customer label** / **Customer description** — that is
   the `en_US` source term;
3. click Odoo's translation control beside the field and fill `fa_IR`, `ru_RU` or
   any future active language;
4. release the version. From then on the text is frozen in every language, and a
   quotation created from it freezes its own copy.

No new language-specific field is ever needed: a newly activated language appears
in the translation dialog by itself. `test_one_field_holds_every_language_and_the_dialog_sees_them`
adds `ru_RU` through the same API the dialog uses and reads it back.

## 6. Permissions and boundaries unchanged

| Item | Result |
|---|---|
| `group_scope_cost_viewer` still guards `manual_cost_default` | yes, unchanged in the view |
| Steward / Estimator group definitions | untouched — no security file changed in this step |
| Released-version write guard | unchanged for content fields, **extended** to translations |
| Product Master | not touched |

## 7. Live end-to-end check

A Persian quotation was created from released version 115, rendered, then deleted:

| Check | Result |
|---|---|
| `resolved_language` | `fa_IR` |
| `label_resolved` | `متعلقات آبرو (داده آزمایشی)` |
| component labels resolved | `ناودان گالوانیزه`, `بست دیواری (صورت‌حساب جداگانه)`, `درزگیر سیلیکونی` |
| missing translations | none; no fallback used |
| customer note head | `متعلقات آبرو (داده آزمایشی)` |
| PDF | 2 pages, IRANSans embedded |
| Persian terms in the PDF | `متعلقات آبرو`, `ناودان`, `ریال`, `عدد`, `ساعت` all present |
| English leakage into the Persian PDF | `Gutter accessories` **absent** |
| `Units` / `Hours` | absent (D-02 intact) |
| `margin` / `unit_cost` in the PDF | absent |

Evidence PDF: `evidence/SIPANEL_TRANSLATION_E2E_QUOTATION.pdf`.
