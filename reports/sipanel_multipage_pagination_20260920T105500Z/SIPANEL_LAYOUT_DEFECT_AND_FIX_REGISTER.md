# SIPANEL Layout Defect and Fix Register (STEP 1D, run 20260920T105500Z)

Carries forward L-01 from run `20260920T084541Z`; adds L-02 with three sub-defects.

---

## L-01 — Cover-page date spills onto page 2 (carried forward)

| | |
|---|---|
| Status | **Fixed in STEP 1C** (`sale_shamsi_report` commit `b17fbb5`), **not touched** by this run |
| Re-verified here | yes — on all 10 shapes, no body ink or text sits above the 147.4 pt band top; page 2 begins at 166.0 pt with the native information box |
| Regression guard | `TestShamsiTemplateStructure::test_sale_report_cover_page_is_bounded` still green |

---

## L-02 — Multi-page body clipping and orphan-page defect

| | |
|---|---|
| Severity | Medium — visible on any quotation whose line table breaks across a page, i.e. every SIPANEL quotation with a long customer note; customer-facing |
| Reported by | owner, from Poppler rendering of `SIPANEL_FRESH_POST_D02_QUOTATION_SI-26_368_REDACTED.pdf` |
| Reproduced | **yes** — 7 of 10 synthetic shapes fail the geometry acceptance before the change, 0 of 10 after |
| Affects | state-independent, language-independent, customer-independent |
| Fix | `sale_shamsi_report` local commit `5680013` (branch `develop/shamsi-date-core`, **not pushed**) |
| Deployment | `-u sale_shamsi_report` on `sipanel`; view + asset change only; **no restart** |

### L-02a — the table's outer box is not paginated with its rows

| | |
|---|---|
| Symptom | On a page where the line table breaks, the box keeps being painted over the empty tail left by the row that moved on — 44.7 to 105.7 pt of border below the last text line — and reaches 753.1 pt, 1.8 pt past the 751.3 pt printable bottom, stopping ~12 pt above the footer rule. Read by a human as "the table runs into the footer". |
| Owner of the faulty code | **Odoo core `web`** — `layout_assets/layout_boxed.scss`, compiled into `web.report_assets_common`: `.o_table_boxed-rounded table:not(.o_ignore_layout_styling){position:relative}` plus a `::before` with `position:absolute; top:0; left:0; bottom:0; right:0; border:1px solid #495057`. Neither `sipanel_sale_scope` nor `sale_shamsi_report` wrote it. |
| Root cause | wkhtmltopdf 0.12.6.1 (QtWebKit) does not paginate an absolutely positioned box with the rows it covers. It emits one rectangle carrying the full table height and relies on the page clip. pdfminer reads the unclipped geometry: D_SECTIONS before the fix has one rect at `y=265.0…1665.9` on page 2, `−339.8…1061.1` on page 3, `−990.7…506.9` on page 4 — the same box shifted by one page height each time, on an 841.9 pt page. |
| Proof | CSS variant matrix on the captured body HTML with identical wkhtmltopdf arguments: disabling the overlay (`::before{display:none}`) or removing the positioned containing block (`table{position:static}`) both drop the trailing frame from 105.7 pt to −2.8 pt; `tr{page-break-inside:avoid}` and signature-level `page-break-inside:avoid` change nothing. `evidence/probes/`, report §4. |
| Fix | Disable the overlay and draw a **real** border on the table, which WebKit paginates correctly. Scoped to `.o_sipanel_so_print`, a class this module now adds to `div.page`, so no other report is affected. The rounded header corners come from `thead th` rules and are unchanged. |
| Files | `static/src/css/report_fonts.css` (new rules), `views/sale_report_templates.xml` (`o_sipanel_so_print` on `div.page`) |
| After | trailing frame 4.3–6.9 pt on every shape (the table's own bottom border); no ink outside the band on any page |

### L-02b — the signature block is torn across a page break

| | |
|---|---|
| Symptom | When the space left on the page is smaller than the signature block, the caption and salesperson name stay behind and the **signature image lands alone on a page carrying no text at all** (E2, E3 before: page 3 has 0 characters). E4 before: caption on page 2, name + image on page 3. |
| Owner | **`sale_shamsi_report`** — it appends this block after `div[name='so_total_summary']` with no break protection |
| Rejected remedy | `page-break-inside: avoid` on the signature row. Measured on E2: WebKit keeps the block on page 2 and **overflows** it, pushing 12 words to y=771.5 pt — 20 pt inside the footer band. It creates the exact failure this work is meant to remove. |
| Rejected remedy | `orphans` / `widows`. QtWebKit ignores them; byte-identical output measured. |
| Fix | Lay the block out as `display: table` (`.o_sipanel_signature_block`, cells `display: table-cell`). WebKit then moves it as one unit, with no overflow. |
| Files | `views/sale_report_templates.xml` (class on the row), `static/src/css/report_fonts.css` |
| After | E2/E3/E4 page 3 carries caption + name + image together; no page has marks without text |

### L-02c — the line-table header never repeats

| | |
|---|---|
| Symptom | A price table spanning pages 2–4 shows its column headings (`توصیف`, `تعداد`, `قیمت واحد`, `تخفیف %`, `مالیات‌ها`, `مبلغ`) only on the first page |
| Owner | **Odoo core `sale`** — `sale/report/ir_actions_report_templates.xml:89` pins it with an inline `style="display: table-row-group"`, directly under Odoo's own comment *"In case we want to repeat the header, remove `display: table-row-group`"* |
| Fix | Clear that inline style from the SIPANEL sale report and re-apply it only through Odoo's own guard — `account.report_invoice_document` suppresses repetition when a line description exceeds 30 newlines, because one row taller than a page plus a repeating header misbehaves in wkhtmltopdf. Same guard, same threshold. |
| Files | `views/sale_report_templates.xml` |
| Cost | D_SECTIONS 4 → 5 pages; the other nine shapes unchanged |
| After | the header appears on every page the table runs onto (visually confirmed on C_LONGNOTES p3–p4 and D_SECTIONS p3–p4; asserted by the regression test on a Latin fixture) |

### Regression test

`sale_shamsi_report/tests/test_sale_order_shamsi.py::TestSaleOrderPdfPagination` —
five checks that read the rendered PDF, never the template source. Each renders the
report body with the exact wkhtmltopdf arguments Odoo uses but with an empty header
and footer, so everything left on the page is body content by construction, and takes
the printable band from the *effective* paperformat rather than a literal.

| Rule | Assertion | Before | After |
|---|---|---|---|
| R1 | no glyph inside the header/footer exclusion areas | pass | pass |
| R2 | no text line straddles a page boundary | pass | pass |
| R3 | no table frame painted outside the page box | **FAIL** | pass |
| R4 | no page carries marks (graphics or images) but no text | pass¹ | pass |
| R5 | the column header repeats on every continuation page | **FAIL** | pass |

¹ The in-Odoo fixture does not land the signature on a boundary; R4 is demonstrated
against the E2/E3 captures by `evidence/scripts/rule_replay.py`, which applies the
same five rules offline: 5 of 10 shapes fail before, 0 of 10 after.

### Explicitly not changed

| Item | Status |
|---|---|
| `report.url` | unchanged `http://127.0.0.1:8072` (asserted before creating data and after cleanup) |
| website languages | unchanged `[en_US, fa_IR]` |
| L-01 cover fix (`b17fbb5`) | untouched, re-verified |
| D-02 / D-03 (`0e2d63e`) | untouched, re-verified (Persian UoMs, portal signature binding) |
| paperformat A4 (margins 52/32 mm) | unchanged — the fix works within the configured boundaries, it does not move them |
| D-04 (working-scope unlink) | not fixed; cleanup used the documented workaround |
| font sizes, customer content, `overflow` suppression | none used — the brief excluded all three |
| other reports (invoice, picking, purchase) | untouched; the CSS is scoped to `.o_sipanel_so_print` |

### Observations

| Id | Observation | Action |
|---|---|---|
| O-1 | The Odoo core overlay bug affects every `o_table_boxed*` report on this database, not just the sale order. Only the sale order was corrected, per the minimum-change instruction. | R-1 / R-2 in the main report |
| O-2 | A final page carrying a few lines of running prose (C_LONGNOTES p5, D_SECTIONS p5) is retained as correct behaviour, not an orphan defect. Removing it would require overflowing the footer or truncating customer text. | none |
| O-3 | STEP 1C could not have caught L-02: it had no rasteriser, and its overlap check compared text boxes to each other, never to the printable band, and never looked at graphics. | closed by the new tooling |
