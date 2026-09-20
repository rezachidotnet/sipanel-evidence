# SIPANEL Post-D-02 Unit-of-Measure Language Validation (STEP 1C, run 20260920T084541Z)

Purpose: prove on a **newly created** quotation that the installed D-02 correction (`sipanel_sale_scope`, commit `0e2d63e`, upgraded on `sipanel` in STEP 1A) renders Persian unit names. The retained `SI-26/312` is an immutable pre-D-02 snapshot and cannot prove this.

## Validation quotation

| Item | Value |
|---|---|
| Order | `SI-26/368` (id 368), state **draft** throughout, client reference `SIPANEL-PDF-LAYOUT-CHECK-20260920T084541Z` |
| Customer | synthetic partner 509 `… مشتری آزمایشی پارسی (Synthetic Persian Customer)`, `lang = fa_IR`, no e-mail/phone |
| Master | released version 115 of the archived STEP 1A temporary master (7 recipe lines incl. `own_line` bracket, provisional-capable sealant, customer-responsibility scaffolding, `internal_only` screw) — reused, not modified |
| Scopes | 271 base (12 m, 2,500,000 IRR/m, 5 % discount, tax 10 %), 272 optional (5 m, 2,200,000) under an optional section; sealant set provisional at quote time; 8 long Persian note lines + long terms note to force ≥ 3 pages |
| Language of revisions | `fa_IR` (from the partner) |

## Result

| Evidence | Value |
|---|---|
| `uom_name_snapshot` values on the components of revision r1 | `{'m', 'ساعت', 'عدد'}` |
| Generated customer note (anchor line text) | `- ناودان گالوانیزه: 12 m` · `- بست دیواری (صورت‌حساب جداگانه): 24 عدد` · `- درزگیر سیلیکونی: 6 عدد (مقدار اولیه؛ …)` · `- نصب و راه‌اندازی: 8 ساعت` · `- داربست … (خارج از محدوده)` · `- جرثقیل: 1 عدد` |
| PDF text layer (after fix, 5 pages) | `عدد` ×6, `ساعت` ×2, **`Units` 0, `Hours` 0** |
| Portal page `/fa/my/orders/368` | contains `عدد` and `ساعت`, no `Units`/`Hours`, `lang="fa-IR"` |
| Untranslated unit | `m` (metre) has no Persian translation in `uom.uom` on this database, so it falls back to the source name — expected D-02 behaviour |

Comparison with the pre-D-02 snapshot `SI-26/312`: `24 Units`, `8 Hours`, `1 Units` (immutable sealed note, unchanged by design).

**D-02 verdict on a fresh quotation: PASS.**

## Test coverage

`sipanel_sale_scope/tests/test_customer_output.py::test_co01_unit_names_follow_quotation_language` re-run after the Shamsi template upgrade: pass (log `evidence/test_sipanel_customer_output_after_fix.log`, 9 tests green including the 6 security tests).

## Not changed

No Translation-field refactor, no data-level translation added or invented (`عدد`/`ساعت` are the pre-existing Odoo core `uom` translations), no separately-billable redesign.
