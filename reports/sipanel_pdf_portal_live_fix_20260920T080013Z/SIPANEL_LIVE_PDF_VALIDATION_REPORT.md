# SIPANEL Live PDF Validation Report — `SI-26/312` after D-01 (STEP 1B, run 20260920T080013Z)

Record used: retained, cancelled validation quotation `SI-26/312` (`sale.order` 312). It was **not** edited (`write_date` unchanged at 2026-09-20 06:44:42 UTC, `signed_by` empty, sealed revisions untouched). Rendering through the customer HTTP path posts native "Quotation viewed by customer" chatter notifications; those are Odoo's own portal-view log, not an edit of the sealed content.

Render path: `GET /my/orders/312?access_token=<redacted>&report_type=pdf` (HTTP worker → `ir.actions.report._render_qweb_pdf('sale.action_report_saleorder')` → wkhtmltopdf 0.12.6.1 with `report.url = http://127.0.0.1:8072`). Language `fa_IR` (partner language). Files: `SIPANEL_LIVE_QUOTATION_SI-26_312_REDACTED.pdf` (root of the report), `evidence/pdf/quotation_live_en_route_after_D01.pdf`, `evidence/pdf/quotation_live_fa_route_after_D01.pdf`, `evidence/pdf/text_extraction_live_after_D01.txt`, PNG slices in `evidence/png/`.

| # | Check | Result | Evidence |
|---|---|---|---|
| 1 | HTTP result successful | **PASS** | 200 `application/pdf`, 134,803 B in 7.06 s (English route); 200, 134,819 B in 5.37 s (Persian route `/fa/…`) |
| 2 | No new `HostNotFoundError` in the Odoo log | **PASS** | count since 08:08 UTC = 0 (baseline before: 2 entries, last 06:14:56; the `WorkerHTTP timeout` at 08:05:32 belongs to the rejected port-8069 attempt, see D-01 report) |
| 3 | Report assets load | **PASS** | gevent process log: `GET /web/assets/1/d12ac26/web.report_assets_pdf.rtl.autoprefixed.min.css 200`, `GET /web/assets/1/f3a065c/web.report_assets_common.rtl.autoprefixed.min.css 200`, `GET /web/assets/1/f7a4315/web.report_assets_common.autoprefixed.min.css 200`, `GET /web/assets/1/061706e/web.report_assets_pdf.autoprefixed.min.css 200`, `GET /web/image/1804-…/signature.png 200` (`evidence/logs/odoo-sipanel_report_and_portal_REDACTED.log`) |
| 4 | CSS and table styles appear | **PASS** | bordered RTL table with coloured header, totals block, cover page, company header/footer (`evidence/png/report_live_part01.png`, `_part02.png`) |
| 5 | IRANSans embedded/used | **PASS** | PDF font resources: `/IRANSans` only (before D-01: DejaVuSans, DejaVuSans-Bold, NimbusSans-*) |
| 6 | `ریال` symbol renders | **PASS** | text layer carries U+FDFC `﷼` next to every amount (`﷼﷼ 43,450,000`) and the rendered image shows `ریال` after 28,500,000 / 2,500,000 / 11,000,000 / 39,500,000 / 3,950,000 / 43,450,000 (`report_live_part02.png`); before D-01 the same code point printed as a missing-glyph box |
| 7 | Persian text shaped and readable | **PASS** | 388 Arabic-block code points, 1,050 presentation-form glyphs in the text layer (connected forms); image shows correctly joined words (`متعلقات آبرو`, `ناودان گالوانیزه`, `داربست و دسترسی به محل به عهده کارفرما است`) |
| 8 | Totals unchanged | **PASS** | untaxed 39,500,000 / tax 3,950,000 / total 43,450,000 IRR = ORM `amount_total 43450000.0` = STEP 1A post-acceptance state (base 12 m × 2,500,000 − 5 % = 28,500,000; accepted option 5 m × 2,200,000 = 11,000,000); no amount differs between the English-route and Persian-route PDFs |
| 9 | No Cost, Margin or internal-only information | **PASS** | `marker_hits: []`, `cost_hits: []` (18 figures), `internal_word_hits: {}`, no 40–64-hex identifiers, no `scope_uid`/`occurrence_uid`; internal-only component 1843 absent; embedded UBL XML (6,388 B) unchanged in nature from STEP 1A (parties, lines, prices, taxes, anchor product name/reference — F-02, out of scope here) |
| 10 | Page count and page breaks | **PASS (recorded)** | 3 pages: p1 cover (657 chars: document number, customer), p2 header + line table + notes (1,919 chars), p3 totals + signature block + terms + footer (753 chars, contains `43,450,000`). Page breaks fall between cover/document and before the totals block; no line is split mid-text in the per-page extraction |
| 11 | Materially consistent with the STEP 1A dry-run fixed PDF | **PASS** | same font set (`IRANSans`), same 3-page structure, same text length class (3,299 vs 3,319 chars), same structure of embedded file and links; sizes 134,803 / 134,819 B vs 134,885 B. Differences are expected: totals now include the accepted option (dry run was rendered before the portal acceptance) and the cover reads `سفارش فروش` instead of `پیش فاکتور` because the retained record is in state *cancel* (the `sale_shamsi_report` cover prints "quotation" only for draft/sent) |
| 12 | No token, cookie or internal path in saved evidence | **PASS** | PDF text: `token_like: []`, no `/opt/odoo`, `/mnt/extra-addons`, `access_token`; report directory grep for the live token, `session_id=`, `db_password`, `admin_passwd`, `PRIVATE KEY`: none |

## Rasterisation

PDF pages could not be rasterised on this host (no `pdftoppm`, `gs`, `mutool`; nothing installed). Instead the live report HTML (`/fa/my/orders/312?…&report_type=html`) was rendered with the container's wkhtmltoimage against the same asset base (`http://127.0.0.1:8072`) and sliced with Pillow: `evidence/png/report_live_part01.png` (cover, header, line table) and `_part02.png` (optional section, totals, signature, terms, footer). Same engine as the PDF; single tall image, so the cover-page date overlapping the table header is an artefact of the image render, not of the 3-page PDF.

## Manual visual checks remaining

* Open `SIPANEL_LIVE_QUOTATION_SI-26_312_REDACTED.pdf` in a viewer and confirm page-break placement and the cover page as printed (`سفارش فروش` on this cancelled record; a live *sent* quotation prints `پیش فاکتور`).
