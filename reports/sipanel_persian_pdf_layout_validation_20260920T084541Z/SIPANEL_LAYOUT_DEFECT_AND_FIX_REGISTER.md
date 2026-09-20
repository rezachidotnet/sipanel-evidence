# SIPANEL Layout Defect and Fix Register (STEP 1C, run 20260920T084541Z)

## L-01 — Cover-page date spills onto page 2 and overlaps the document-information block

| | |
|---|---|
| Severity | Medium — visible on every multi-page quotation PDF produced with the `sale_shamsi_report` cover (all customers, all states) |
| Reported by | owner, from Poppler rendering of `reports/sipanel_pdf_portal_live_fix_20260920T080013Z/SIPANEL_LIVE_QUOTATION_SI-26_312_REDACTED.pdf` |
| Reproduced | yes, from the real PDFs with pdfminer bounding boxes: live `SI-26/312` (cancelled) and fresh draft `SI-26/368` both show the 16.6 pt `1405/06/29 :` / `تاریخ` line at 161.6 pt from the top of page 2 intersecting the `فروشنده` / `انقضا` labels (`evidence/page_maps/live_before.page2.map.png`, `fresh_before.page2.map.png`) |
| Affects | all multi-page Persian (and non-Persian) quotations — state-independent; not limited to cancelled orders or the legacy record |
| Module / file | `sale_shamsi_report` (separate repo `/opt/odoo/addons/sale_shamsi_report`, branch `develop/shamsi-date-core`), `views/sale_report_templates.xml`, template `report_saleorder_document_shamsi`, xpath `//div[hasclass('page')]` position before |
| Root cause | fixed-height (20 cm) flex cover box with `page-break-after: always`; its content (spacers 50+100+50+50+300 px, 50 px title with line-height 2.2, three 26 px lines ≈ 924 px) exceeds the box; with `justify-content: center` the overflow spills below the box, i.e. past the forced page break, so the 26 px date line lands at the top of page 2 over the native `informations` block. The absolute white "footer cover" layer does not cover the spill |
| Fix (commit `b17fbb5`, local) | `overflow: hidden` on the cover box; spacers `100px → 60px` and `300px → 80px` (content ≈ 664 px inside 756 px). No other visual change |
| Regression test | `tests/test_sale_order_shamsi.py::TestShamsiTemplateStructure::test_sale_report_cover_page_is_bounded` — fails on the previous template (`overflow_hidden`, `max_spacer_le_100`, `sum_spacers_le_320`), passes on the corrected one (`evidence/structural_test_before_after.txt`); full suite 73/73 green after `-u sale_shamsi_report` |
| After-fix evidence | `evidence/pdf_after_fix/SI-26_368_fresh_after_fix_orm.pdf`, `…_http_fa_route.pdf`; page maps `fresh_after.page*.map.png`, `fresh_after_http.page*.map.png`: no ≥12 pt text at the top of page 2, zero real overlaps on pages 1, 2, 4, 5 |
| Residual | the cover keeps its original hacks (`margin-top: -150px` to hide the header, absolute white layer to hide the footer on page 1); they are now confined to the bounded box. A customer name longer than two lines would be clipped inside the cover instead of spilling — acceptable and safer than the overlap |
| Deployment | source edited in the Shamsi git working tree (also the bind-mounted addons path), `-u sale_shamsi_report` on `sipanel`, no restart (view change only), HTTP health 200 |

## Explicitly not changed (per authorisation)

| Item | Status |
|---|---|
| `report.url` | unchanged `http://127.0.0.1:8072` (asserted before creating data and after cleanup) |
| website languages | unchanged `en_US`, `fa_IR` |
| D-02 / D-03 (`0e2d63e`) | untouched; D-02 confirmed on the fresh quotation |
| D-04 (working scope unlink) | not fixed; cleanup used the documented workaround (clear `current_revision_id` first) |
| F-02 anchor product naming, F-03 separately billable, Translation-field architecture | untouched; the separately billable component rendered as existing behaviour (`بست دیواری (صورت‌حساب جداگانه): 24 عدد` as a note bullet) |

## Observations

| Id | Observation | Action |
|---|---|---|
| O-1 | fake-bold double draw of bold Latin runs (section title) shows as two overlapping fragments in text extraction; identical before/after | none; manual viewer check listed |
| O-2 | cover prints `سفارش فروش` for cancelled orders (module logic: quotation title only for draft/sent) | none |
| O-3 | `sale_shamsi_report` has no `i18n/` directory; the cover labels `Document Number:`/`Customer:`/`Date:` render in Persian through Odoo's core `sale` translations of identical source strings | none |
