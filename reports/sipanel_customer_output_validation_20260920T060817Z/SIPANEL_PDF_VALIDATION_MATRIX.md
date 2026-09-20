# SIPANEL PDF Validation Matrix — quotation `SI-26/312` (run 20260920T060817Z)

Report path exercised: `sale.action_report_saleorder` (qweb-pdf, paper A4, layout `web.external_layout_bubble` with the pre-existing `sale_shamsi_report` overrides: cover page, Shamsi dates, IRANSans font, "Sell Department" signature block, company footer). Language: `t-lang="doc.partner_id.lang"` = `fa_IR`.

Three renders were analysed (all identical in content):

| File | How produced | Pages | Fonts embedded |
|---|---|---|---|
| `evidence/pdf/SI-26_312_quotation_as_served_before_D01_fix.pdf` (= the redacted sample PDF) | HTTP portal download `/my/orders/312?access_token=…&report_type=pdf` (customer path, HTTP worker) | 2 | DejaVuSans, DejaVuSans-Bold, NimbusSans-* |
| ORM render `_render_qweb_pdf` as user 2 and the seal-time artifact (attachment 3955) | same engine, same result (67,373 bytes each) | 2 | same |
| `evidence/pdf/SI-26_312_quotation_dryrun_with_D01_fix.pdf` | ORM render inside a rolled-back transaction with `report.url=http://127.0.0.1:8069` | 3 | IRANSans only |

Analysis tooling (already in the container, nothing installed): PyPDF2 2.12.1 (structure, fonts, metadata, embedded files, annotations), pdfminer.six 20221105 (text per page), wkhtmltoimage 0.12.6.1 + Pillow (PNG evidence). Scripts: `evidence/scripts/pdf_analyze.py`, `pdf_embedded.py`, `png_evidence.py`.

| # | Check | Result | Evidence |
|---|---|---|---|
| 1 | PDF renders successfully through the installed report path | **PASS** | HTTP 200 `application/pdf`, 67,373 bytes; valid PDF 1.4, 2 pages; seal-time artifacts 3955/3956 also valid |
| 2 | Persian characters readable, not disconnected or corrupted | **PASS with D-01 caveat** | 320 Arabic-block code points + 810 presentation-form glyphs extracted → text is shaped (connected) in both renders. As served today (D-01) the fallback font is DejaVu Sans (readable, shaped) and the currency symbol `ریال` after each amount prints as a missing-glyph box (see `png/quotation_before_unstyled_part02.png`); with D-01 corrected the PDF embeds IRANSans and the symbol renders (`png/quotation_dryrun_fixed_part02.png`) |
| 3 | RTL ordering operationally acceptable | **PASS** | Persian title `پیش فاکتور`, right-aligned table headers (`توصیف / تعداد / قیمت واحد / تخفیف % / مالیات‌ها / مبلغ`), note bullets and totals read right-to-left in the styled render; unstyled render keeps correct glyph order but loses table borders/alignment (D-01) |
| 4 | Page breaks, tables, totals and notes readable | **PASS (page-level)** | Page 1 = cover (document number, customer, date), page 2 = header block, line table, totals block (`مبلغ بدون مالیات 28,500,000 / مالیات بر ارزش افزوده 2,850,000 / کل 31,350,000`), signature block, terms note, footer `Page 2 / 2`. With D-01 corrected the document needs 3 pages; per-page text extraction shows no truncated line. Visual page-break inspection remains a manual item (no PDF rasteriser on host) |
| 5 | Scope title and customer description appear correctly | **PASS** | anchor line text starts with `متعلقات آبرو (داده آزمایشی)` then `شرح مشتری: تأمین و نصب متعلقات آبرو مطابق نقشه — …` (both from the released version labels, language fa) |
| 6 | Included / optional / provisional / separately billable presented correctly | **PASS** | included: `- ناودان گالوانیزه: 12 m`, `- نصب و راه‌اندازی: 8 Hours`, `- جرثقیل: 1 Units`; separately billable (placement own_line): `- بست دیواری (صورت‌حساب جداگانه): 24 Units` (F-03: no separate priced line is generated); provisional: `- درزگیر سیلیکونی: 6 Units (مقدار اولیه؛ پس از بازدید محل نهایی می‌شود (داده آزمایشی))`; optional: separate section `گزینه‌های اختیاری (Optional – validation)` with its own anchor line `0 m × 2,200,000 = 0`, note lists the option content with 5 m / 10 Units |
| 7 | Inclusions, exclusions, assumptions, customer responsibilities distinguishable | **PASS** | customer responsibility rendered without quantity as `- داربست و دسترسی به محل به عهده کارفرما است (خارج از محدوده)`; provisional basis in parentheses; order-level customer note `یادداشت مشتری (داده آزمایشی): …` in the terms block; line note `یادداشت سطر (داده آزمایشی): …` as an italic note row |
| 8 | Qty, UoM, unit price, tax, total consistent with the quotation | **PASS** | line: `12 m`, `2,500,000`, discount `5`, tax `10%`, subtotal `28,500,000`; optional: `0 m`, `2,200,000`, `10%`, `0`; totals 28,500,000 / 2,850,000 / 31,350,000 = ORM `amount_untaxed/amount_tax/amount_total`. Unit names printed in English (`m`, `Units`, `Hours`) although Persian translations exist → **D-02, fixed for new quotations** (after-fix note on the helper order: `6 عدد`, `8 ساعت`) |
| 9 | Internal-only components absent | **PASS** | component 1843 (`disclosure=internal_only`, label `INTERNAL-MARKER-LABEL-FA-…`, 20 screws) absent from text, UBL XML and HTML report; `marker_hits: []` |
| 10 | Cost, cost source, margin, internal estimate, supplier, analytic, recognition policy, audit ids, internal notes absent | **PASS** | back-office values present at the same time: eligible cost 18,144,382, margin 10,355,618 (36.34 %), unit costs 731,000 / 9,876 / 55,555 / 4,321 / 8,765,000 / 123, manual-cost reason, analytic accounts `…INTERNAL-MARKER-ANALYTIC…`, version internal description, product descriptions, partner internal note, internal chatter note — none found in any PDF text (`cost_hits: []`, `internal_word_hits: {}`, no 40–64-hex ids, no `scope_uid`/`occurrence_uid`) |
| 11 | Hidden data not present in text extraction, metadata, attachments or HTML comments | **PASS with F-02** | metadata `{Producer: Odoo, Creator: Odoo}`, no XMP, no JavaScript/OpenAction; annotations = 2 links to `https://sipanelco.ir` (company footer); **one embedded file** `SI-26_312_ubl_bis3.xml` (6,381 bytes, native `sale_edi_ubl` Peppol order): contains buyer/seller names and addresses, order id, customer reference, line descriptions (= the customer notes), quantities, prices, taxes, totals and `SellersItemIdentification` = anchor product internal reference `VAL-ANCHOR-60817Z` and `Item/Name` = anchor product name — no cost/margin/internal-only data (`evidence/pdf/embedded_ubl_bis3_order.xml`). HTML report source has one `<![endif]` conditional comment only |
| 12 | No portal token, secret or internal filesystem path | **PASS** | `token_like: []`, no `/opt/odoo`, `/mnt/extra-addons`, `access_token` in PDF text or XML; the salesperson signature image is embedded as data, not as a tokenised URL |

## Visual evidence (PNG)

| File | What it shows |
|---|---|
| `evidence/png/quotation_before_unstyled_part01.png`, `_part02.png` | the report HTML rendered with the currently configured base URL (`http://odoo:8069`, unresolvable) — how customer PDFs look today (D-01): no layout, no logo, missing currency glyph |
| `evidence/png/quotation_dryrun_fixed_part01.png`, `_part02.png` | the same HTML with a resolvable base URL — IRANSans, RTL table, totals block, signature block, footer |

Both images are single tall renders (wkhtmltoimage); the cover-page date overlapping the table header in `quotation_dryrun_fixed_part01.png` is a single-image artefact (the cover is `page-break-after: always` in the PDF, which has 3 pages).
