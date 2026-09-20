# SIPANEL Visual Page Review Matrix (STEP 1D, run 20260920T105500Z)

Every page of every acceptance PDF was rendered to PNG with Poppler and looked at.
This matrix records the **visual** verdict. It is deliberately independent of the
automated geometry in `SIPANEL_AUTOMATED_GEOMETRY_RESULTS.md`; disagreements between
the two are listed in §3 and were resolved in favour of the eye.

| | |
|---|---|
| Rasteriser | `pdftoppm` (poppler-utils 24.02.0) |
| Page renders | 110 dpi, `evidence/png_before/` (31 pages), `evidence/png_after/` (32 pages) |
| Boundary crops | 300 dpi strips at the band edges, for the pages where clipping was reported |
| Contact sheets | `evidence/contact_sheets/contact_<SHAPE>.png`, before row above after row |
| Printable band | 147.4 pt … 751.3 pt; at 110 dpi that is y = 225 px … 1148 px of a 1288 px page |

---

## 1. Page-by-page verdict

Legend — **C** cover, **T** line table, **N** customer notes, **$** totals,
**S** signature, **X** terms paragraph.

### A_SHORT — SI-26/385, 2 → 2 pages

| Pg | Before | After |
|---|---|---|
| 1 | C — cover inside its box, no spill | unchanged |
| 2 | T $ S — single-page table, box closes on the last row; nothing near the footer | identical layout; table border now a real border, visually indistinguishable |

**No defect before or after.** Confirms the change is a no-op for short quotations.

### B_NORMAL — SI-26/386, 3 → 3 pages

| Pg | Before | After |
|---|---|---|
| 1 | C — clean | unchanged |
| 2 | T N — **defect:** the table box continues ~95 pt below the last note row as an empty bordered rectangle reaching the footer rule | box closes on the last row |
| 3 | N $ S X — table continues with **no column headers** | **column headers repeated**; totals, signature and terms all complete |

### C_LONGNOTES — SI-26/387, 5 → 5 pages

| Pg | Before | After |
|---|---|---|
| 1 | C — clean | unchanged |
| 2 | T N — table box runs to the printable edge | box closes on the last row |
| 3 | N — **defect:** ~59 pt empty bordered tail; **no column headers** | **headers repeated**; box closes on the last row |
| 4 | N $ S X — no headers; last line sits close to the footer but is fully drawn | **headers repeated**; unchanged otherwise |
| 5 | X — 3 lines of terms, rest blank; begins mid-sentence | same 3 lines — retained as a correct text continuation, see §2 |

### D_SECTIONS — SI-26/388, 4 → **5** pages

| Pg | Before | After |
|---|---|---|
| 1 | C — clean | unchanged |
| 2 | T N — ~64 pt empty bordered tail | box closes on the last row |
| 3 | N + optional section + optional scope row — **worst case: ~106 pt empty bordered rectangle** below the optional row, running to the printable edge; no column headers | **headers repeated**; optional section header and optional scope row intact; box closes on the last row |
| 4 | $ S X — totals, signature, terms | **headers repeated**; optional row + totals |
| 5 | — | X — terms tail |

The optional / provisional / separately-presented content renders identically before
and after: the optional section heading `گزینه‌های اختیاری (Optional – validation)`,
the zero-quantity optional scope row, the provisional component note
`درزگیر سیلیکونی: 6 عدد (مقدار اولیه؛ پس از بازدید محل نهایی می‌شود ...)` and the
separately-billed bullet `بست دیواری (صورت‌حساب جداگانه): 24 عدد`.

### E1 — SI-26/389, 2 → 2 pages

| Pg | Before | After |
|---|---|---|
| 1 | C | unchanged |
| 2 | T N $ S — everything fits | unchanged |

### E2 — SI-26/390, 3 → 3 pages

| Pg | Before | After |
|---|---|---|
| 1 | C | unchanged |
| 2 | T N $ + caption "دپارتمان فروش" + name "Taleghani" | T N $ — the whole signature unit moved off this page |
| 3 | **defect: the signature image alone, no text whatsoever** | caption + name + signature image **together** |

### E3 — SI-26/391, 3 → 3 pages

| Pg | Before | After |
|---|---|---|
| 1 | C | unchanged |
| 2 | T N $ + caption + name | T N $ |
| 3 | **defect: signature image alone, no text** | caption + name + image together |

### E4 — SI-26/392, 3 → 3 pages

| Pg | Before | After |
|---|---|---|
| 1 | C | unchanged |
| 2 | T N $ + caption "دپارتمان فروش" | T N $ |
| 3 | **defect: name + image, caption left behind on page 2** | caption + name + image together |

### E5 — SI-26/393, 3 → 3 pages

| Pg | Before | After |
|---|---|---|
| 1 | C | unchanged |
| 2 | T N — **defect:** ~91 pt empty bordered tail | box closes on the last row; more note text fits |
| 3 | $ S | $ S — unchanged, complete |

### E6 — SI-26/394, 3 → 3 pages

| Pg | Before | After |
|---|---|---|
| 1 | C | unchanged |
| 2 | T N — **defect:** ~45 pt empty bordered tail | box closes on the last row |
| 3 | $ S | $ S — unchanged, complete |

### Reported artefact — `SIPANEL_FRESH_POST_D02_QUOTATION_SI-26_368_REDACTED.pdf` (STEP 1C output, 5 pages)

| Pg | Visual verdict |
|---|---|
| 1 | cover, clean (L-01 fix holding) |
| 2 | information box, table; **the table box continues ~115 pt below the last note row to the printable edge** — this is reported observation #1 |
| 3 | notes + optional section; same empty bordered tail; no column headers |
| 4 | notes, totals, signature, terms. 300 dpi crops of the **top** strip (y 570–870 px) and the **bottom** strip (y 2980–3310 px) show **every glyph fully drawn**. Reported observation #2 (clipping) **is not present.** |
| 5 | 3 lines of terms then blank; begins mid-sentence — reported observation #3, confirmed as fact |

---

## 2. Judgement calls

| Case | Call |
|---|---|
| C_LONGNOTES p5 / D_SECTIONS p5 — a final page holding a few lines of running prose | **Not a defect.** The text has to be somewhere; the alternatives are overflowing the footer or truncating customer content, both excluded by the brief. |
| E2/E3 p3 before — a page holding only the signature image | **Defect.** Avoidable, and avoided: the block is now atomic. |
| E2/E3/E4 p3 after — a page holding the complete signature unit | **Not a defect.** Measured on E2: the unit is 128.7 pt tall and only 120.0 pt remained on page 2. It genuinely does not fit; it now moves whole instead of tearing. |
| Square instead of rounded outer table corners | **Accepted.** The rounded corners of the blue header row come from `thead th` rules and are unchanged; only the 1 px outer box lost its 0.75 rem radius. Side-by-side at 150 dpi the difference is not noticeable. |
| D_SECTIONS 4 → 5 pages | **Accepted.** One extra page in exchange for column headings on every page of a customer-facing price table. |

---

## 3. Where the automated checks and the eye disagreed

All four disagreements were found by looking at the pages, and all four were fixed in
the tooling rather than argued away.

| # | Disagreement | Cause | Resolution |
|---|---|---|---|
| 1 | The raster ink scan passed pages that clearly showed the table box crossing the bottom boundary | the scan required a horizontal run of ≥3 dark pixels; the table's side borders are 1 px vertical hairlines, which produce a 1-pixel run per row | `--min-run` lowered to 1 for body-only renders, where the bands are otherwise pure white. The crossing at 751.7 pt then shows up. |
| 2 | The "border painted into empty space" metric flagged clean pages after the fix | it measured *any* ink below the last text line, so a centred signature image (79 pt tall) looked like a table frame | added a width discriminator: only ink spanning >50 % of the page width counts as a frame. Signature ≈16 % of the width, table border ≈90 %. |
| 3 | The "orphan page" rule did not flag E2/E3 page 3, the clearest defect in the whole set | pdfminer reports an image as `LTImage`/`LTFigure`, never as a rect, so a page holding only the signature image looked empty of marks | images are now counted as marks, in both the offline replay and the in-Odoo regression test |
| 4 | Text-based checks reported 0 occurrences of `ریال`, `عدد`, `ساعت` in PDFs where they are plainly visible | poppler and pdfminer emit Arabic presentation forms one glyph per token and insert layout-driven spaces inside words, so `ساعت` extracts as `سا ع ت` | all Persian content checks now NFKC-normalise and strip whitespace before matching. The same problem killed the first attempt to classify header/footer text by token, which is why the body-only re-render is used instead. |

A fifth, non-disagreement worth recording: pdfminer reports graphic primitives with
their **unclipped** content-stream coordinates. That makes it useless as a measure of
visible ink, but it is the single most direct detector of the L-02a overlay — a
rectangle 1666 pt tall on an 842 pt page can only be an unpaginated absolute box. The
regression test uses it for exactly that.
