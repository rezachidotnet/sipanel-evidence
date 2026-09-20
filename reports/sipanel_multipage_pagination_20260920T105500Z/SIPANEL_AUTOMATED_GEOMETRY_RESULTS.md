# SIPANEL Automated Geometry Results (STEP 1D, run 20260920T105500Z)

## 1. What is measured, and against what

The printable band is **not** hard-coded. It is derived from the paperformat the
report actually resolves to (`sale.action_report_saleorder.get_paperformat()` → `A4`,
id 1), which is also what Odoo passes to wkhtmltopdf:

```
body_top    = margin_top                    = 52 mm = 147.40 pt
body_bottom = page_height - margin_bottom   = 841.89 - 32 mm = 751.18 pt
```

Measurements are taken from a **body-only re-render**: the same captured body HTML,
the same wkhtmltopdf arguments, but an empty header and footer document. wkhtmltopdf
lays header and footer out as separate documents, so this does not change pagination
— verified, page counts are identical for all 10 shapes before and after — while
making every mark left on the page body content by construction. That sidesteps the
"is this word part of the footer?" problem, which RTL shaping makes unsolvable:
poppler and pdfminer both emit Arabic presentation forms one glyph at a time.

Tooling: `evidence/scripts/pdf_geometry.py` (poppler `pdftotext -bbox` for text,
`pdftoppm -gray` PGM raster for ink) and `evidence/scripts/rule_replay.py`
(pdfminer.six, the same five rules the regression test applies).

| Column | Meaning |
|---|---|
| `minY` / `maxY` | first / last **text** box edge on the page, pt from the page top |
| `maxInk` | lowest **ink** row on the page (text or border), 150 dpi raster |
| `frame` | `maxInk − maxY`: border ink below the last text line. Bold = violation (>36 pt **and** spanning >50 % of the page width, i.e. a rule, not a signature image) |
| limit | 751.3 pt on every page |

### Per-page geometry (body-only renders, band 147.4pt .. 751.3pt)

| Shape | Pg | before minY | before maxY | before maxInk | before frame | after minY | after maxY | after maxInk | after frame |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A_SHORT | 1 | 147.2 | 621.8 | 524.2 | -97.6 | 147.2 | 621.8 | 524.2 | -97.6 |
|  | 2 | 166.0 | 603.8 | 683.0 | 79.2 | 166.0 | 621.1 | 700.3 | 79.2 |
| B_NORMAL | 1 | 147.2 | 621.8 | 524.2 | -97.6 | 147.2 | 621.8 | 524.2 | -97.6 |
|  | 2 | 166.0 | 656.5 | 751.7 | **95.2** | 166.0 | 657.1 | 661.4 | 4.3 |
|  | 3 | 152.0 | 512.2 | 509.8 | -2.4 | 152.5 | 539.7 | 537.1 | -2.6 |
| C_LONGNOTES | 1 | 147.2 | 621.8 | 524.2 | -97.6 | 147.2 | 621.8 | 524.2 | -97.6 |
|  | 2 | 166.0 | 717.9 | 751.7 | 33.8 | 166.0 | 718.5 | 722.9 | 4.4 |
|  | 3 | 152.0 | 692.3 | 751.7 | **59.4** | 152.5 | 717.9 | 724.8 | 6.9 |
|  | 4 | 152.0 | 738.1 | 735.4 | -2.7 | 152.5 | 750.3 | 747.8 | -2.5 |
|  | 5 | 147.4 | 163.4 | 160.8 | -2.6 | 147.4 | 178.8 | 176.2 | -2.6 |
| D_SECTIONS | 1 | 147.2 | 621.8 | 524.2 | -97.6 | 147.2 | 621.8 | 524.2 | -97.6 |
|  | 2 | 166.0 | 687.2 | 751.7 | **64.5** | 166.0 | 703.2 | 707.5 | 4.3 |
|  | 3 | 152.0 | 646.0 | 751.7 | **105.7** | 152.5 | 702.3 | 706.6 | 4.3 |
|  | 4 | 152.0 | 749.0 | 746.4 | -2.6 | 152.5 | 745.8 | 743.0 | -2.8 |
|  | 5 | — | — | — | — | 147.4 | 194.1 | 191.5 | -2.6 |
| E1 | 1 | 147.2 | 621.8 | 524.2 | -97.6 | 147.2 | 621.8 | 524.2 | -97.6 |
|  | 2 | 166.0 | 645.4 | 724.8 | 79.4 | 166.0 | 647.3 | 726.7 | 79.4 |
| E2 | 1 | 147.2 | 621.8 | 524.2 | -97.6 | 147.2 | 621.8 | 524.2 | -97.6 |
|  | 2 | 166.0 | 691.5 | 686.9 | -4.6 | 166.0 | 632.5 | 637.4 | 4.9 |
|  | 3 | None | None | 226.6 | None | 147.3 | 196.8 | 276.0 | 79.2 |
| E3 | 1 | 147.2 | 621.8 | 524.2 | -97.6 | 147.2 | 621.8 | 524.2 | -97.6 |
|  | 2 | 166.0 | 722.2 | 717.6 | -4.6 | 166.0 | 663.3 | 668.2 | 4.9 |
|  | 3 | None | None | 226.6 | None | 147.3 | 196.8 | 276.0 | 79.2 |
| E4 | 1 | 147.2 | 621.8 | 524.2 | -97.6 | 147.2 | 621.8 | 524.2 | -97.6 |
|  | 2 | 166.0 | 738.8 | 735.8 | -3.0 | 166.0 | 709.3 | 714.2 | 4.9 |
|  | 3 | 150.5 | 170.5 | 249.6 | 79.1 | 147.3 | 196.8 | 276.0 | 79.2 |
| E5 | 1 | 147.2 | 621.8 | 524.2 | -97.6 | 147.2 | 621.8 | 524.2 | -97.6 |
|  | 2 | 166.0 | 660.9 | 751.7 | **90.8** | 166.0 | 661.6 | 666.2 | 4.6 |
|  | 3 | 151.9 | 280.6 | 360.0 | 79.4 | 151.9 | 281.2 | 360.5 | 79.3 |
| E6 | 1 | 147.2 | 621.8 | 524.2 | -97.6 | 147.2 | 621.8 | 524.2 | -97.6 |
|  | 2 | 166.0 | 707.0 | 751.7 | **44.7** | 166.0 | 707.7 | 712.3 | 4.6 |
|  | 3 | 151.9 | 280.6 | 360.0 | 79.4 | 151.9 | 281.2 | 360.5 | 79.3 |

### Violation totals

| Shape | pages before | pages after | violations before | violations after | what failed before |
|---|---:|---:|---:|---:|---|
| A_SHORT | 2 | 2 | 0 | 0 | — |
| B_NORMAL | 3 | 3 | 3 | 0 | frame p2 95.2pt; ink below limit p2; ink above limit p3 |
| C_LONGNOTES | 5 | 5 | 5 | 0 | ink below limit p2; frame p3 59.4pt; ink below limit p3; ink above limit p3; ink above limit p4 |
| D_SECTIONS | 4 | 5 | 6 | 0 | frame p2 64.5pt; ink below limit p2; frame p3 105.7pt; ink below limit p3; ink above limit p3; ink above limit p4 |
| E1 | 2 | 2 | 0 | 0 | — |
| E2 | 3 | 3 | 2 | 0 | orphan p3 |
| E3 | 3 | 3 | 2 | 0 | orphan p3 |
| E4 | 3 | 3 | 0 | 0 | — |
| E5 | 3 | 3 | 3 | 0 | frame p2 90.8pt; ink below limit p2; ink above limit p3 |
| E6 | 3 | 3 | 3 | 0 | frame p2 44.7pt; ink below limit p2; ink above limit p3 |

## 2. Rule replay (pdfminer, the regression test's own rules)

`evidence/geometry/rule_replay.txt`, full output. Rules:

- **R1** no glyph outside the printable body band (tolerance 1 pt)
- **R2** no text line straddling a band edge
- **R3** no graphic primitive emitted outside the page box — the direct signature of an unpaginated absolute overlay
- **R4** no page carrying marks (graphics **or** images) but no text
- R5 (header repetition) is not replayed here: these fixtures are Persian and
  substring matching on shaped RTL text is not trustworthy. R5 is asserted by the
  in-Odoo test, which renders a Latin fixture, and confirmed visually.

```
fixture      tag      pg  R1  R2  R3  R4  verdict
A_SHORT      before    2  0   0   0   0   PASS
B_NORMAL     before    3  0   0   4   0   FAIL   rects at y 265.0…855.0, −339.8…250.2 on an 841.9pt page
C_LONGNOTES  before    5  0   0   6   0   FAIL   rects at y 265.0…1624.3, −339.8…1019.5
D_SECTIONS   before    4  0   0   6   0   FAIL   rects at y 265.0…1665.9, −339.8…1061.1, −990.7…506.9
E1           before    2  0   0   0   0   PASS
E2           before    3  0   0   0   1   FAIL   page 3 carries marks but no text
E3           before    3  0   0   0   1   FAIL   page 3 carries marks but no text
E4           before    3  0   0   0   0   PASS
E5           before    3  0   0   0   0   PASS
E6           before    3  0   0   0   0   PASS
A_SHORT      after     2  0   0   0   0   PASS
B_NORMAL     after     3  0   0   0   0   PASS
C_LONGNOTES  after     5  0   0   0   0   PASS
D_SECTIONS   after     5  0   0   0   0   PASS
E1           after     2  0   0   0   0   PASS
E2           after     3  0   0   0   0   PASS
E3           after     3  0   0   0   0   PASS
E4           after     3  0   0   0   0   PASS
E5           after     3  0   0   0   0   PASS
E6           after     3  0   0   0   0   PASS

SUMMARY: 5 of 10 shapes FAIL before the fix, 0 of 10 FAIL after
```

The raster checker and the pdfminer replay disagree on which *shapes* fail
(7 vs 5), and they should: the raster checker additionally measures the visible
empty bordered tail (E5 45–91 pt, E6, B_NORMAL) which pdfminer cannot see, while
R3/R4 catch the unpaginated rect and the image-only page. Both agree on the
before/after direction and both are clean after the fix.

## 3. Boundary crossings

Before the fix, body ink crosses the band on every page that carries a broken table:

| Shape | Page | Ink above 147.4 pt | Ink below 751.3 pt |
|---|---:|---|---|
| B_NORMAL | 2 | — | y = 751.7 pt |
| B_NORMAL | 3 | y = 146.9 pt | — |
| C_LONGNOTES | 2, 3 | 146.9 pt (p3) | 751.7 pt (p2, p3) |
| C_LONGNOTES | 4 | 146.9 pt | — |
| D_SECTIONS | 2, 3 | 146.9 pt (p3) | 751.7 pt (p2, p3) |
| D_SECTIONS | 4 | 146.9 pt | — |
| E5, E6 | 2 | — | 751.7 pt |
| E5, E6 | 3 | 146.9 pt | — |

All of these are the 1 px table-border hairline, not text. **After the fix there are
zero crossings on any page of any shape**, above or below.

No text crossing was found in any render, before or after: `above`, `below`,
`clipped_top` and `clipped_bottom` are 0 for all 63 pages. The reported "clipped
line" is therefore not present as clipping — see the visual matrix §1 and §3.

## 4. Reproducing

```bash
# rasterise and measure one PDF (needs poppler-utils on the host)
python3 evidence/scripts/pdf_geometry.py <body-only>.pdf --min-run 1 --label X

# re-render body-only PDFs for a captured fixture set, inside the container
bash evidence/scripts/bodyonly_render.sh before|after

# replay the regression rules over a captured set, inside the container
docker exec odoo-sipanel python3 /tmp/rule_replay.py /tmp/sipanel_1d
```
