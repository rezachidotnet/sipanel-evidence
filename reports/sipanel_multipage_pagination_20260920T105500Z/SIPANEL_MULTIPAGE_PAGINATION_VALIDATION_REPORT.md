# SIPANEL — Multi-page pagination validation (STEP 1D)

| | |
|---|---|
| Run | `20260920T105500Z` (2026-09-20 10:49–12:00 UTC) |
| Scope | database `sipanel`, container `odoo-sipanel` only |
| Defect | **L-02 — multi-page body clipping and orphan-page defect** |
| Verdict | **PASS** — L-02 reproduced, root cause identified and corrected; 10/10 document shapes clean after the fix (7/10 failed before) |
| Source change | `sale_shamsi_report` (separate repo `/opt/odoo/addons/sale_shamsi_report`, branch `develop/shamsi-date-core`), local commit `5680013`, **not pushed** |
| Recovery point | `/opt/odoo/backups/sipanel-pre-multipage-20260920T104900Z` (created and verified before the first write) |
| Restart | **none** — `odoo-sipanel` `RestartCount=0`, `StartedAt=2026-09-20T06:40:08Z` (before this run) |
| Other tenants | untouched — no command in this run addressed `odoo-avizsazeh`, `odoo-shahbazi`, `odoo-ahantorob` or any database other than `sipanel` |

---

## 1. FACT — the measured environment

Captured from the live render path by wrapping `subprocess.Popen` inside a throw-away
`odoo shell` process (the running server was not patched). This is the *effective*
invocation, not an assumption:

```
/usr/local/bin/wkhtmltopdf --disable-local-file-access --quiet --page-size A4
  --margin-top 52.0 --dpi 90 --zoom 1.0666666666666667 --header-spacing 52
  --margin-left 0.0 --margin-bottom 32.0 --margin-right 0.0 --orientation Portrait
  --javascript-delay 1000 --header-html <hdr> --footer-html <ftr> <body> <out>
```

| Item | Value |
|---|---|
| `wkhtmltopdf` | 0.12.6.1 (with patched qt) — QtWebKit |
| Report | `sale.action_report_saleorder` → `sale.report_saleorder_document` |
| Layout | `web.external_layout_bubble` (company 1), extended by `sale_shamsi_report.external_layout_bubble_custom` |
| Effective paperformat | `A4` (id 1) — `margin_top` 52 mm, `margin_bottom` 32 mm, `margin_left/right` 0, `header_spacing` 52, `dpi` 90, `disable_shrinking` False |
| `specific_paperformat_args` | `{}` — the layout declares no `data-report-*` overrides |
| Page box | 595.28 × 841.89 pt (A4) |
| **Printable body band** | **147.40 pt … 751.18 pt** from the page top (rounded to 147.4 … 751.3 in the tooling) |
| Embedded font | `IRANSans`, CID TrueType, Identity-H, **embedded** |
| SIPANEL report templates | none — `sipanel_sale_scope` adds **no** QWeb report; customer scope text is written into `sale.order.line.name` (`quote_scope_revision.py:191`), i.e. into the native line table |

## 2. FACT — L-02 is reproduced

Five synthetic document shapes were built on `sipanel` (all DRAFT, all prefixed
`SIPANEL-PAGINATION-CHECK-20260920T105500Z`, no email, no confirmation), rendered
before and after the change, rasterised with Poppler at 110 dpi (300 dpi for boundary
crops) and inspected page by page.

| Shape | Order | Description |
|---|---|---|
| A_SHORT | SI-26/385 | short quotation, one scope, no extra notes |
| B_NORMAL | SI-26/386 | normal multi-page quotation |
| C_LONGNOTES | SI-26/387 | long Persian customer notes crossing several pages |
| D_SECTIONS | SI-26/388 | optional + provisional + separately presented customer scope sections |
| E1…E6 | SI-26/389…394 | sweep of filler lengths placing totals/signature at different distances from a page boundary |

**7 of 10 shapes failed the geometry acceptance before the change; 0 of 10 after.**
See `SIPANEL_AUTOMATED_GEOMETRY_RESULTS.md` and `SIPANEL_VISUAL_PAGE_REVIEW_MATRIX.md`.

## 3. FACT — reconciliation with the reported observations

The report that opened L-02 listed four observations of
`SIPANEL_FRESH_POST_D02_QUOTATION_SI-26_368_REDACTED.pdf`. Each was re-checked against
that exact file at 300 dpi, and against fresh reproductions.

| # | Reported | Verdict | Measurement |
|---|---|---|---|
| 1 | page 2 — the table continues into the footer area and the footer region is partially obstructed | **Confirmed, in substance** | The table's outer box is painted down to **753.1 pt**, i.e. **1.8 pt past** the 751.3 pt printable bottom, and the resulting empty bordered rectangle runs **44.7–105.7 pt below the last text line**, stopping ~12 pt above the footer rule. It is a *border-box* intrusion, not a text overlap — no glyph leaves the band. |
| 2 | page 4 begins in the middle of a Persian text line; the top is visibly clipped | **Not reproduced as clipping** | 300 dpi crops of the top and bottom strips of page 4 show every glyph fully drawn. Page 4 starts at y=152.0 pt (band top 147.4 pt) on a clean row boundary. No character box crosses either boundary anywhere in the file. |
| 3 | text continues onto page 5, leaving most of that page blank | **Confirmed as fact, reclassified** | Page 5 carries 3 lines of running prose and begins mid-sentence. Reproduced in C_LONGNOTES. Assessed as an ordinary text continuation, **not** an avoidable orphan — see §6. The genuinely avoidable orphan found is different (E2/E3: a page carrying *only* the signature image). |
| 4 | the previous report's "page breaks on pages 2–4 were clean" is not supported | **Agreed** | The STEP 1C check measured pdfminer *text*-box overlaps only. It did not measure graphics, and it never compared anything to the printable band, because no rasteriser was available in that session. Both gaps are closed here. |

## 4. FACT — root cause, established by experiment

Odoo's bubble layout draws a report table's outer box as an **absolutely positioned
`::before` overlay inside a `position: relative` table** (`web.report_assets_common`,
from `layout_assets/layout_boxed.scss`):

```css
.o_table_boxed-rounded table:not(.o_ignore_layout_styling)        { position: relative; }
.o_table_boxed-rounded table:not(.o_ignore_layout_styling)::before{
    content: ''; position: absolute; top: 0; left: 0; bottom: 0; right: 0;
    pointer-events: none; border: 1px solid #495057;
}
```

The same captured body HTML was re-rendered with the identical wkhtmltopdf arguments
and one injected CSS rule per variant (`evidence/scripts/css_variant_probe.py`,
`probe_run.py`; PDFs in `evidence/probes/`). Trailing-frame = pt of border ink below
the last text line on the page:

| Variant | Injected rule | D_SECTIONS p2 / p3 frame | Verdict |
|---|---|---:|---|
| V0 | — (baseline) | 64.5 / 105.7 | FAIL |
| V1 | `…::before{display:none}` | −2.7 / −2.8 | **defect gone** |
| V5 | `table{position:static}` | −2.7 / −2.8 | **defect gone** |
| V2 | V1 + real `border` on the table | 4.3 / 4.6 | **defect gone, box preserved** |
| V3 | `tbody tr{page-break-inside:avoid}` | 64.5 / 6.3 | not the cause |
| V4 | `.signature_container{page-break-inside:avoid}` | 64.5 / 105.7 | no effect |

Removing the overlay (V1) or removing the positioned containing block (V5) both
eliminate the defect; touching row or signature breaking (V3, V4) does not. The cause
is therefore the overlay, not the row-breaking policy.

**Mechanism.** wkhtmltopdf 0.12.6 does not paginate an absolutely positioned box with
the rows it covers. It emits the overlay once, with the full height of the table, and
relies on the page clip. pdfminer reads the unclipped geometry directly from the
content stream and shows exactly that — on D_SECTIONS before the fix:

```
page 2: rect y = 265.0 … 1665.9 pt   (page box is 0 … 841.9 pt)
page 3: rect y = −339.8 … 1061.1 pt
page 4: rect y = −990.7 …  506.9 pt
```

One rectangle, shifted by one page height per page. Where a tall SIPANEL note row is
pushed to the next page, the clip leaves the box painted over the empty tail and
1.8 pt past the printable bottom.

**Ownership.** The faulty CSS is Odoo core (`web`), not a SIPANEL or Shamsi file. The
repository that owns *this report's print presentation* is `sale_shamsi_report`, which
already contributes to `web.report_assets_common` and already rewrites this template.
The correction is therefore made there and **scoped to the sale order printout**, so
no other report changes.

### Second, independent sub-defect — the signature block

`sale_shamsi_report` appends a signature block after `div[name='so_total_summary']`
with no break protection. When the remaining space is smaller than the block, WebKit
splits it and the **signature image lands alone on a page with no text at all**
(E2, E3 before: page 3 holds 0 characters). `page-break-inside: avoid` is **not** a
usable remedy here — measured on E2, it made WebKit keep the block on page 2 and
overflow it, pushing **12 words to y=771.5 pt, 20 pt inside the footer band**, i.e.
it creates the very defect being fixed. `orphans`/`widows` are ignored by QtWebKit
(no effect measured). Laying the block out as a `display: table` makes WebKit move it
as one unit, with no overflow.

### Third item — table header repetition

`sale.report_saleorder_document` pins the line-table header with an inline
`style="display: table-row-group"`, immediately under Odoo's own comment
*"In case we want to repeat the header, remove `display: table-row-group`"*. So on
every SIPANEL multi-page quotation the price-table column headings appeared once and
never again. `account.report_invoice_document` shows Odoo's sanctioned pattern:
repeat, except when a line description exceeds 30 newlines.

## 5. The change

`sale_shamsi_report`, commit `5680013` — three files, +283/−2 lines
(`evidence/source_diff/sale_shamsi_report_L02.diff`):

| File | Change |
|---|---|
| `views/sale_report_templates.xml` | add `o_sipanel_so_print` to `div.page` (scoping); clear the `thead` inline `display: table-row-group` and re-add it via `t-attf-style` only under Odoo's `has_long_desc` guard; add `o_sipanel_signature_block` to the signature row |
| `static/src/css/report_fonts.css` | disable the `::before` overlay and draw real borders on `.o_main_table` and `.o_total_table`; lay the signature block out as a table — all four rules scoped to `.o_sipanel_so_print` |
| `tests/test_sale_order_shamsi.py` | new `TestSaleOrderPdfPagination` — five rendered-geometry checks (see `SIPANEL_REGRESSION_TEST_RESULTS.md`) |

Deployed with `-u sale_shamsi_report` on `sipanel`. View + asset change only, **no restart**.

## 6. INFERENCE

1. The defect is **state-independent and customer-independent**. It is triggered purely
   by a table that breaks across a page, which any SIPANEL quotation with a long
   customer note does. It was not caused by the STEP 1C cover fix; STEP 1C simply did
   not look for it.
2. The 1.8 pt overshoot past the printable bottom is cosmetically minor; the
   **visible** defect is the 45–106 pt empty bordered rectangle, which a reader reads
   as "the table ran into the footer". Fixing the overlay removes both at once.
3. Repeating the table header costs pages: D_SECTIONS went 4 → 5. Across the other
   nine shapes the page count is unchanged. The trade is one page against a
   customer-facing price table whose continuation pages had no column headings.
4. A final page carrying a few lines of running prose (C_LONGNOTES p5, D_SECTIONS p5)
   is **not** treated as a defect. The text has to go somewhere, and the only
   alternatives are overflowing the footer or truncating customer content, both
   excluded by the brief. The acceptance rule therefore targets pages that carry
   *marks but no readable content*, which is the case that is genuinely avoidable.
5. The same Odoo core overlay bug will affect every other boxed report on this
   database (invoices, pickings, purchase orders) whenever their tables break across
   pages. It was left alone here because the brief asks for the minimum change that
   owns this defect.

## 7. RECOMMENDATION

| Id | Recommendation | Priority |
|---|---|---|
| R-1 | Decide whether the same overlay correction should be applied database-wide (drop the `.o_sipanel_so_print` scope) so customer invoices get it too. One-line change, wider blast radius, needs its own visual pass. | medium |
| R-2 | Report the `::before` overlay pagination bug upstream to Odoo; it affects every `o_table_boxed*` layout under wkhtmltopdf. | low |
| R-3 | Keep `page-break-inside: avoid` out of these report templates. It is a footgun on wkhtmltopdf 0.12.6 — measured overflow of 20 pt into the footer band. Recorded in the CSS comment so it is not "helpfully" re-added. | high |
| R-4 | If the extra page from header repetition is unwelcome for short two-page tables, make repetition conditional on the table actually breaking. Not possible in QWeb without measuring, so it would need a row-count heuristic. | low |
| R-5 | `poppler-utils` is now installed on the host (see §8). Keep it: every future PDF acceptance needs a rasteriser, and its absence is what let L-02 through STEP 1C. | medium |
| R-6 | Prune old recovery points — five now exist under `/opt/odoo/backups`, ~110 MB each, on a filesystem at 90 %. Owner decision; nothing was deleted in this run. | medium |

## 8. Host and production changes made by this run

| Change | Detail | Reversible |
|---|---|---|
| `poppler-utils 24.02.0-1ubuntu9.9` installed on the host | required by the brief ("render every page to PNG using Poppler"); no rasteriser existed on the host or in any container | `sudo apt-get remove poppler-utils` |
| Deferred service restarts from that install | **not applied** — `needrestart` reported "No containers need to be restarted"; docker, dbus, logind were left running | n/a |
| `sale_shamsi_report` source | commit `5680013` on `develop/shamsi-date-core`, not pushed | `git revert 5680013` + `-u sale_shamsi_report` |
| `sipanel` database | module upgrade `sale_shamsi_report` (views + asset bundle); 10 synthetic draft quotations created and then **fully deleted** | recovery point above |
| Configuration | **nothing changed** — `report.url` still `http://127.0.0.1:8072`, website languages still `[en_US, fa_IR]`, paperformat A4 untouched (asserted before and after) | n/a |

## 9. Regression status

| Check | Result |
|---|---|
| page-2 cover date overlap (L-01) still fixed | pass — no body ink above 147.4 pt on any page of any shape; page 2 starts at 166.0 pt (information box) |
| Persian UoMs `عدد` / `ساعت`, never `Units` / `Hours` | pass — identical counts before and after on all 10 shapes |
| IRANSans embedded | pass — `pdffonts`: `IRANSans CID TrueType Identity-H … emb=yes` |
| rial glyph visible | pass — `ریال` present 5× (8× for D_SECTIONS) in every shape, before and after |
| Persian portal operational | pass — `/my/orders/<id>` and `/fa/my/orders/<id>` both HTTP 200 for all 10 orders |
| PDF and portal totals match the quotation | pass — 20/20 fetches contain the order total |
| no leakage (cost, margin, internal notes, internal-only components, tokens, filesystem paths) | pass — raw-byte scan of all 20 deliverable PDFs for `access_token`, `/opt/odoo`, `/mnt/extra-addons`, `127.0.0.1`, `8072`, `/tmp/report`, `INTERNAL-MARKER`, `eligible_cost`, `margin`: zero hits |
| SIPANEL customer-output and security tests | pass — 70 tests, 0 failures (`sipanel_commercial_scope_core` 20, `sipanel_sale_scope` 37, `sipanel_scope_costing` 5, `sipanel_scope_execution` 8). Run once, after the fix: no SIPANEL module was changed by this run, and earlier runs today covered subsets only, so there is no comparable 70-test "before" figure from today. |
| Shamsi suite | pass — 80 tests, 0 failures (75 pre-existing + 5 new). The same suite was run first against the unmodified template with only the new test file deployed: 2 of the 5 new checks failed. |

## 10. Evidence index

| Path | Contents |
|---|---|
| `evidence/pdf_before/`, `evidence/pdf_after/` | the 20 acceptance PDFs |
| `evidence/png_before/`, `evidence/png_after/` | every rendered page, 110 dpi (31 + 32 files) |
| `evidence/contact_sheets/` | 10 before/after contact sheets |
| `evidence/geometry/` | per-shape JSON, `geometry_full.txt`, `rule_replay.txt` |
| `evidence/probes/` | the CSS variant-probe PDFs behind §4 |
| `evidence/logs/` | test logs before/after, recovery-point checksums |
| `evidence/scripts/` | every script used, including the two analysers |
| `evidence/source_diff/` | the `sale_shamsi_report` diff |
| `evidence/portal_results.txt` | the 20 portal fetches |
