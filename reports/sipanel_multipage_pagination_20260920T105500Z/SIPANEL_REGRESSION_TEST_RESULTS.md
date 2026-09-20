# SIPANEL Regression Test Results (STEP 1D, run 20260920T105500Z)

## 1. Summary

| Suite | Command | Before the fix | After the fix |
|---|---|---|---|
| `sale_shamsi_report` | `odoo -d sipanel --no-http --stop-after-init -u sale_shamsi_report --test-enable --test-tags shamsi_characterization` | **80 tests, 2 failures** (both the new L-02 checks) | **80 tests, 0 failures** |
| SIPANEL modules | `scripts/sipanel_install_and_test.sh test` (`-u sipanel_commercial_scope_core,sipanel_sale_scope,sipanel_scope_execution,sipanel_scope_costing --test-tags sipanel`) | 70 tests, 0 failures (STEP 1C baseline) | **70 tests, 0 failures** |
| Totals | | | **150 tests, 0 failures** |

SIPANEL module breakdown after the fix: `sipanel_commercial_scope_core` 20,
`sipanel_sale_scope` 37, `sipanel_scope_costing` 5, `sipanel_scope_execution` 8.
Logs: `evidence/logs/test_shamsi_L02_before_fix.log`,
`evidence/logs/test_shamsi_L02_after_fix.log`, `evidence/logs/test_sipanel_after_fix.log`.

## 2. The new regression test

`sale_shamsi_report/tests/test_sale_order_shamsi.py::TestSaleOrderPdfPagination`
(tag `shamsi_characterization`), 5 tests, ~35 s.

**It does not search template source strings.** It renders the report and measures
the output. Design:

1. Build a fixture order with one long product description and six long customer-note
   lines so the line table genuinely breaks across pages (the test skips if fewer
   than 3 pages result).
2. Render **body-only**: `_render_qweb_html` → `_prepare_html` → `_build_wkhtmltopdf_args`
   → `_run_wkhtmltopdf`, passing the real arguments but an empty header and footer
   document. Pagination is unchanged (verified: identical page counts), and everything
   left on the page is body content by construction. This matters because RTL shaping
   makes text-based "is this the footer?" classification unusable.
3. Take the printable band from `report.get_paperformat()`, so the test keeps
   measuring the real exclusion areas if the margins are ever reconfigured.
4. Parse with pdfminer.six (present in the container; poppler is not).
5. Skip, loudly, if wkhtmltopdf produces nothing or if the rendered PDF carries no
   table borders at all — the latter means the report assets were unreachable over
   `report.url` and the geometry would otherwise pass vacuously.

| Test | Asserts |
|---|---|
| `test_no_text_enters_the_header_or_footer_exclusion_area` | no glyph box lies in, or past, the non-printable margins (1 pt tolerance) |
| `test_no_page_starts_or_ends_on_a_split_text_line` | no glyph box straddles a band edge with more than the tolerance on both sides |
| `test_table_frame_is_paginated_with_its_rows` | no graphic primitive is emitted outside the page box — the direct signature of an unpaginated absolutely positioned table overlay |
| `test_no_page_holds_marks_without_any_text` | no page carries graphics **or images** but no text — catches a bare frame page and a signature image torn from its caption |
| `test_line_table_header_repeats_on_continuation_pages` | every page that continues the line table shows the column header (case-insensitive: the layout uppercases `thead`) |

## 3. Before/after evidence for the new test

Run on Production against the **unmodified** template and CSS
(`evidence/logs/test_shamsi_L02_before_fix.log`, exit 1):

```
FAIL: TestSaleOrderPdfPagination.test_table_frame_is_paginated_with_its_rows
AssertionError: [(2, 218.9, 1716.5, 842), (2, 219.5, 1715.8, 842),
                 (3, -385.9, 1111.7, 842), (3, -385.3, 1111.0, 842),
                 (4, -990.7, 506.9, 842), (4, -990.1, 506.2, 842)] is not false :
  a table frame is painted outside the page box instead of being paginated with its rows

FAIL: TestSaleOrderPdfPagination.test_line_table_header_repeats_on_continuation_pages
AssertionError: [2, 3, 4] is not false : page(s) [2, 3, 4] continue the line table
  without repeating the 'Description' column header
```

After the fix (`evidence/logs/test_shamsi_L02_after_fix.log`, exit 0):

```
odoo.tests.stats: sale_shamsi_report: 80 tests 40.83s 978 queries
```

The other three rules pass in both runs on this fixture, because it does not place
the signature or a text line on a page boundary. They are not dead weight:

- `test_no_text_enters_the_header_or_footer_exclusion_area` is what rejected the
  obvious "fix" for the signature orphan. Adding `page-break-inside: avoid` to the
  signature row pushed 12 words to y=771.5 pt, 20 pt inside the footer band.
- `test_no_page_holds_marks_without_any_text` is demonstrated against the E2/E3
  captures by the offline replay below.

## 4. Offline replay of the same rules over all 10 shapes

`evidence/scripts/rule_replay.py` applies R1–R4 to the captured body-only renders, so
the before/after verdict per document shape is reproducible without re-running Odoo:

```
SUMMARY: 5 of 10 shapes FAIL before the fix, 0 of 10 FAIL after
  B_NORMAL, C_LONGNOTES, D_SECTIONS  -> R3, table frame not paginated
  E2, E3                             -> R4, page carries marks but no text
```

Two corrections were made to the rules during this run, both after a page was looked
at and the rule disagreed (see the visual matrix §3): images now count as marks
(pdfminer reports them as `LTImage`/`LTFigure`, never as rects, so R4 was originally
blind to the signature-only page), and the header comparison is case-insensitive
because the layout uppercases `thead`.

## 5. Pre-existing tests re-verified

| Area | Test | Result |
|---|---|---|
| L-01 cover bound | `TestShamsiTemplateStructure::test_sale_report_cover_page_is_bounded` | pass |
| Shamsi template structure | `TestShamsiTemplateStructure::test_sale_report_template_structure`, `test_expected_view_inheritance_references` | pass — the new xpaths did not disturb the expected inheritance |
| Shamsi date conversion, portal branches, calendar / purchase / discuss patches | remaining 72 tests | pass |
| D-02 Persian unit names | `sipanel_sale_scope/tests/test_customer_output.py` (`عدد`, `ساعت`, not `Units`/`Hours`) | pass |
| D-03 portal signature binding | `sipanel_sale_scope/tests/test_customer_output.py` | pass |
| Governance, security, quote engine, costing, execution | remaining SIPANEL tests | pass |

The `duplicate key value violates unique constraint "sipanel_quote_scope_anchor_line_unique"`
line in the SIPANEL log is a test asserting that constraint fires, not a failure:
`grep -cE 'odoo\.addons\..*: (FAIL|ERROR):'` over that log returns **0**.

## 6. Non-test regression checks

| Check | Method | Result |
|---|---|---|
| IRANSans embedded | `pdffonts` on every after-PDF | `IRANSans CID TrueType Identity-H emb=yes` |
| rial glyph | NFKC-folded text search | `ریال` present in all 10 shapes, count identical before/after |
| Persian UoMs | NFKC-folded text search | `عدد` and `ساعت` present, `Units`/`Hours` absent, counts identical before/after |
| Persian portal | `curl` via `Host: odoo.sipanelco.ir` on `/my/orders/<id>` and `/fa/my/orders/<id>` | 20/20 HTTP 200 |
| totals match | order total string present in each portal page | 20/20 |
| no leakage | raw-byte scan of all 20 PDFs for `access_token`, `/opt/odoo`, `/mnt/extra-addons`, `127.0.0.1`, `8072`, `/tmp/report`, `INTERNAL-MARKER`, `eligible_cost`, `margin` | 0 hits |
| site health after the upgrade | `/web/login` 200, `/my` 303 | healthy |
