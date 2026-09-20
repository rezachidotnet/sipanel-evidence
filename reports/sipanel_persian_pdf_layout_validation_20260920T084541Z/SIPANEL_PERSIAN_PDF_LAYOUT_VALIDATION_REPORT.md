# SIPANEL Persian PDF Layout Validation (STEP 1C, run 20260920T084541Z)

| Item | Value |
|---|---|
| Final verdict | **PASS_WITH_FINDINGS** (overlap reproduced, corrected, re-validated; D-02 confirmed on a fresh quotation; two observations recorded) |
| Target | database `sipanel`, container `odoo-sipanel` only; `odoo-db` used for the `sipanel` dump only; other tenants untouched |
| SIPANEL repo | `/home/ubuntu/sipanel_odoo_addons` HEAD `484b884` at start; this run adds only the report directory (commit below); D-02/D-03 (`0e2d63e`) untouched |
| Shamsi repo | `/opt/odoo/addons/sale_shamsi_report` (git `develop/shamsi-date-core`, was `b70e2cf`, clean) → **local commit `b17fbb5`**, not pushed |
| Configuration | `report.url` = `http://127.0.0.1:8072` before and after (verified in the creation and cleanup scripts); website languages `en_US, fa_IR` unchanged |
| Recovery point | `/opt/odoo/backups/sipanel-pre-layout-fix-20260920T084541Z` created and verified before the change (`evidence/recovery_point.log`) |
| Module upgrade | `-u sale_shamsi_report` only (template lives in `ir.ui.view`) |
| Restart | **none** — no Python change; the upgraded view is served immediately (HTTP `/web/login` 200, live PDF 200 after the upgrade) |

## 1. Page-2 overlap: reproduced from the real PDF

Method: pdfminer.six layout analysis of the actual PDF pages (text-line bounding boxes, font sizes, pairwise intersections) — no rasteriser is available on host or container and none was installed. Page maps drawn from the boxes are in `evidence/page_maps/` (red = ≥18 pt, blue = ≥12 pt, gray = body text).

| PDF | Page 2 finding |
|---|---|
| live `SI-26/312` (STEP 1B, cancelled legacy record) | 16.6 pt line `1405/06/29 :` at 161.6 pt from the page top intersects the informations-box label `فروشنده` (ix 33 pt, iy 6.6 pt) |
| fresh draft `SI-26/368` (created in this run, before the fix) | same: `1405/06/29 :` and `تاریخ` at 16.6 pt intersect `فروشنده` and `انقضا` at 161.6 pt (`evidence/page_maps/fresh_before.page2.map.png`, blue box crossing the info rows) |

The defect is therefore **not** specific to the cancelled record or the legacy snapshot: it affects **every multi-page quotation** rendered with the `sale_shamsi_report` cover page (state-independent; only the cover title differs).

## 2. Root cause

`sale_shamsi_report/views/sale_report_templates.xml`, template `report_saleorder_document_shamsi`, the `custom-full-page-cover` block inserted before the report page: a `position: relative; height: 20cm; display: flex; justify-content: center; page-break-after: always` box whose content — spacers 50 + 100 + 50 + 50 + **300** px, the 50 px bold title (line-height 2.2), three 26 px lines — adds up to ≈ 924 px, more than the 20 cm (≈ 756 px) box. Flex centering lets the overflow spill above and below the box; the bottom overflow (the 26 px "Date" line) is rendered **after** the forced page break, i.e. at the top of page 2, on top of the native `informations` block. The absolute white layer meant to hide the footer sits at the box bottom and does not cover the spill.

## 3. Correction (minimal, in the authoritative source)

| Change | Before | After |
|---|---|---|
| cover box style | no overflow rule | `overflow: hidden;` — nothing inside the cover can cross the page break |
| spacer before the text block | `100px` | `60px` |
| spacer before the date line | `300px` | `80px` (content ≈ 664 px, ≈ 90 px headroom for a two-line customer name) |
| regression test | — | `TestShamsiTemplateStructure.test_sale_report_cover_page_is_bounded` (cover must be one bounded 20 cm box with `overflow: hidden` and `page-break-after`, single spacer ≤ 100 px, total spacers ≤ 320 px, date rendered exactly once on the cover) |

Files changed (Shamsi repo, commit `b17fbb5`): `views/sale_report_templates.xml` (+3/−2), `tests/test_sale_order_shamsi.py` (+20). Diffs in `evidence/source_diff/`. Nothing else was redesigned: cover, Shamsi dates, IRANSans, signature block, footer, portal customisation unchanged. The date still appears once on the cover (module behaviour) and once in the native metadata block on page 2 — no stray copy anywhere else.

## 4. Fresh post-D-02 quotation `SI-26/368` — page-by-page result (after fix)

Rendered twice: ORM report path and the customer HTTP path `/fa/my/orders/368?…&report_type=pdf` (200, 161,830 B). Both 5 pages, `IRANSans` only.

| Page | Content | Overlaps (real, ix > 5 pt) | Header/footer |
|---|---|---|---|
| 1 | cover: `پیش فاکتور`, `شماره سند: SI-26/368`, customer, date | none | company header present; footer hidden by the cover layer (as designed) |
| 2 | informations block, line table start (base scope note with `24 عدد`, `6 عدد`, `8 ساعت`, `1 عدد`), long note lines | none — no ≥12 pt text at the top of the page any more | header + `Page 2 / 5` footer |
| 3 | note lines, optional section, optional scope note | only the fake-bold double draw of the section title (two fragments of the same Latin run at the same baseline, see Observation O-1) | header + `Page 3 / 5` |
| 4 | remaining notes, totals `28,500,000 / 2,850,000 / 31,350,000` with `ریال` | none | header + `Page 4 / 5` |
| 5 | signature block, terms note, footer | none | header + `Page 5 / 5` |

Before the fix the same quotation had the 16.6 pt date/label pair on page 2 (see §1). Everything else on pages 3–5 is identical before/after (page count 5 → 5, text length 12,117 → 12,118 chars).

## 5. Validation checklist (fresh PDF)

| # | Check | Result |
|---|---|---|
| 1 | Persian/RTL layout | PASS — RTL report bundles, right-aligned table, Persian labels |
| 2 | IRANSans only | PASS — font resources `['/IRANSans']` on all pages |
| 3 | `ریال` glyph | PASS — 10 rial signs (U+FDFC) in the text layer; rendered by the embedded IRANSans (verified in STEP 1B) |
| 4 | `عدد` / `ساعت`, no `Units` / `Hours` | **PASS** — `عدد` ×6, `ساعت` ×2, `Units` 0, `Hours` 0 (details in `SIPANEL_POST_D02_UOM_LANGUAGE_VALIDATION.md`) |
| 5 | No overlap on any page | PASS (see §4; O-1 is a text-extraction artefact) |
| 6 | No clipped table rows | PASS — every note line and scope bullet present in the per-page text; totals block intact |
| 7 | No duplicated date/metadata block | PASS — date once on the cover, once in the informations block; no stray copy |
| 8 | Header/footer on every page | PASS — company header lines at 62 pt from the top and `Page n / 5` on all 5 pages |
| 9 | Page breaks for long scope notes | PASS — 8 long note lines flow across pages 2–4 without split words; cover and totals on their own regions |
| 10 | Totals | PASS — 12 m × 2,500,000 − 5 % = 28,500,000; tax 10 % 2,850,000; total 31,350,000 = ORM values |
| 11 | No Cost/Margin/internal-only/supplier/analytic/audit leakage | PASS — back-office cost 18,144,382 and margin 10,355,618 present; 0 hits for markers, cost figures, internal words, 64-hex ids; internal-only component 1848 absent |
| 12 | No token/cookie/secret/path | PASS — PDF text `token_like: []`, no paths; evidence redacted |

## 6. Tests

| Run | Result |
|---|---|
| `sale_shamsi_report` suite before change (`--test-tags shamsi_characterization`) | 72 tests, 0 errors, 0 failures |
| `-u sale_shamsi_report` + suite after change | 73 tests (new test included), 0 errors, 0 failures |
| structural assertions against the previous template (`git show HEAD:…`) | FAIL (`overflow_hidden`, `max_spacer_le_100`, `sum_spacers_le_320`) — passes on the corrected template (`evidence/structural_test_before_after.txt`) |
| SIPANEL `TestCustomerOutput` + `TestSecurity` after change | 9 tests, 0 errors, 0 failures |

## 7. Observations (no change made)

| Id | Observation |
|---|---|
| O-1 | pdfminer reports two overlapping fragments for the bold optional-section title (`(Optional – validation)`) on page 3, both at the same baseline and offset 4 pt: wkhtmltopdf synthesises bold for IRANSans (single weight) by drawing the run twice; present before and after the fix and on the STEP 1B PDF — not a layout defect. Manual check of the section title in a viewer is listed as a visual item |
| O-2 | Cover title reads `پیش فاکتور` on the fresh draft; the STEP 1B PDF of the cancelled record read `سفارش فروش` because the cover prints "quotation" only for draft/sent (module behaviour) |

## 8. Manual visual checks remaining

Open `SIPANEL_FRESH_POST_D02_QUOTATION_SI-26_368_REDACTED.pdf` with Poppler/Preview and confirm: page 2 top area (informations block) clean; section title on page 3 renders as one bold line; page breaks between pages 2–4 acceptable.
