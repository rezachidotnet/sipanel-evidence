# SIPANEL Commercial Scope — Customer Output Validation (STEP 1 of operational rollout)

| Item | Value |
|---|---|
| Run id / UTC start | `20260920T060817Z` (2026-09-20 06:08 – 06:55 UTC) |
| Final verdict | **PASS_WITH_FINDINGS** |
| Target | database `sipanel`, container `odoo-sipanel` (image 1cd111414896, Odoo 19.0), PostgreSQL container `odoo-db` (read/written for `sipanel` only) |
| Repository | `/home/ubuntu/sipanel_odoo_addons`, branch `master`, start commit `46f4135` (clean tree) |
| Modules validated | `sipanel_commercial_scope_core`, `sipanel_sale_scope`, `sipanel_scope_execution`, `sipanel_scope_costing` — all `installed`, version 19.0.1.0.0 |
| Operational owner / approver | Reza Taleghani, Odoo user id 2, login `amirmousa1983@gmail.com` (see `SIPANEL_ROLE_IDENTITY_VERIFICATION.md`) |
| Source changed | **Yes** — commit `0e2d63e` (sipanel_sale_scope + one test fixture), local only, **not pushed** |
| Module upgraded | **Yes** — `-u sipanel_sale_scope` (Odoo also reloaded its dependents `sipanel_scope_execution`, `sipanel_scope_costing`; no source change in those) |
| `odoo-sipanel` restarted | **Yes, once** (06:39:56 UTC, back serving HTTP after ~9 s) — required because Python model/controller code changed |
| Other tenants | untouched (`odoo-avizsazeh`, `odoo-shahbazi`, `odoo-ahantorob`, `odoo-db` never restarted; no other database read or written) |
| Recovery points | existing `/opt/odoo/backups/sipanel-pre-scope-20260919T164558Z` verified readable (6/6 checksums OK); fresh `/opt/odoo/backups/sipanel-pre-customer-output-fix-20260920T062942Z` created and verified before the upgrade |

## 1. What was validated

An end-to-end, evidence-backed check of what a customer receives from a Scope-carrying quotation on the installed system:

* the quotation **PDF** through the installed report path (`sale.action_report_saleorder`, layout `web.external_layout_bubble` customised by the pre-existing `sale_shamsi_report` module), fetched both through the HTTP portal download path and through the ORM;
* the customer **Portal** page (`/my/orders/<id>?access_token=…`), the governed optional-scope route (`/my/orders/<id>/update_line_dict`) and the customer signature route (`/my/orders/<id>/accept`);
* **Persian/RTL** rendering, customer-visible scope presentation (included, separately billable, optional, provisional, customer responsibility/exclusion, customer notes), commercial figures (qty, UoM, unit price, discount, tax, totals);
* **leakage prevention** (internal-only components, costs, margins, cost sources, analytic accounts, internal notes, audit identifiers, tokens, paths) in PDF text, PDF metadata, PDF embedded files, portal HTML source, HTML comments and JSON;
* **binding and traceability** of the rendered customer content (seal hash ↔ revision ↔ acceptance).

Validation data: one synthetic customer and one temporary released master version, prefix `SIPANEL-CUSTOMER-OUTPUT-CHECK-20260920T060817Z`, quotation `SI-26/312` (sealed and marked *sent* without e-mail) plus helper draft `SI-26/313` (deleted). Details and cleanup in `SIPANEL_VALIDATION_DATA_AND_CLEANUP_REPORT.md`.

## 2. Results at a glance

| Area | Result | Notes |
|---|---|---|
| Quotation PDF renders, content complete | PASS | 2 pages as served today (cover + document), 3 pages with D-01 corrected; all scope lines, notes, totals present |
| Persian characters readable, shaped, RTL | PASS (with D-01 caveat) | Glyphs shaped correctly in both renders; **as served today the report CSS/fonts are not loaded (D-01)**, so the PDF is unstyled, uses DejaVu instead of IRANSans and the currency symbol `ریال` prints as a missing-glyph box |
| Included / separately billable / optional / provisional / customer responsibility / notes | PASS | All six presentation types appear and are distinguishable (see PDF matrix items 5–7) |
| Qty, UoM, unit price, discount, tax, totals consistent | PASS | 12 m × 2,500,000 − 5 % = 28,500,000; tax 10 % = 2,850,000; total 31,350,000 IRR; optional line 0 m / 0 |
| Unit names in a Persian quotation | **DEFECT D-02 → FIXED** | note printed `Units`/`Hours` although `عدد`/`ساعت` exist; new quotations now use the quotation language |
| Internal-only component absent | PASS | `INTERNAL-MARKER-LABEL-*` component never rendered (PDF text, UBL XML, portal HTML) |
| Costs, margin, cost source, supplier, analytic, recognition, audit ids, internal notes absent | PASS | 0 hits for 18 cost figures, 7 marker families, internal field names, 64-hex hashes in PDF text; portal HTML clean except the by-design seal binding attributes |
| Hidden data (metadata, attachments, comments) | PASS with finding F-02 | PDF metadata = Producer/Creator "Odoo"; embedded UBL BIS3 order XML (native `sale_edi_ubl`) carries the anchor **product name and internal reference** — not internal-only data, but master-data naming must be customer-appropriate |
| Portal page renders, same revision as PDF | PASS | binding attributes `data-sipanel-revision-id=238` / seal hash match the sealed revision; totals identical to PDF |
| Portal Persian/RTL | PASS with finding F-01 | Persian content renders; page chrome is `en-US`/LTR because the website has only `en_US` enabled (`/fa_IR/…` → 404), so the pre-existing Persian portal customisation never triggers |
| Optional/provisional not misrepresented as confirmed demand | PASS | optional line qty 0 and amount 0 until the customer accepts; provisional basis text printed next to the item |
| Access control | PASS | no token / wrong token / other order's token / garbage token / nonexistent id → 303 to `/my`; PDF download without token → 303; JSON-RPC without token → redirect |
| Token isolation between quotations | PASS | token of `SI-26/313` on `SI-26/312` refused and vice versa |
| Governed optional acceptance bound to seal | PASS | wrong hash, wrong revision id, missing binding → `stale_link`; correct → `accepted`, qty forced to the sealed scope qty (tamper value 7 ignored), audit event + `acceptance_reference=portal:238:…` |
| Customer signature (acceptance) traceability | **DEFECT D-03 → FIXED** | before: signature acceptance left `acceptance_reference` empty and a seal mismatch after an option toggle surfaced an internal error to the customer; after: reference `portal_signature:<name>:<utc>` recorded, customer-safe refusal message, transaction rolled back |
| Draft working-scope deletion (back office) | **DEFECT D-04 → recorded, not fixed** | `sipanel.quote.scope.unlink()` on an unsealed scope fails (MissingError / FK on `current_revision_id`); outside customer-output scope |

## 3. Defects and findings (summary — full register in `SIPANEL_DEFECT_AND_FIX_REGISTER.md`)

| Id | Severity | Where | Status |
|---|---|---|---|
| D-01 | High (customer output, pre-existing, all PDFs) | system parameter `report.url = "http://odoo:8069\n"` — host `odoo` is not resolvable inside `odoo-sipanel`; wkhtmltopdf logs `HostNotFoundError` and renders without CSS/fonts | **Demonstrated and fix verified in a rolled-back dry run; NOT applied** — the harness refused the production-wide parameter write. One-line correction for the owner is given in the register. |
| D-02 | Medium (customer output) | `sipanel_sale_scope`: UoM name snapshot taken in the creator's language | **Fixed**, regression test `test_co01`, upgraded on `sipanel` |
| D-03 | Medium (acceptance binding / customer flow) | `sipanel_sale_scope`: portal signature path | **Fixed**, regression tests `test_co02`, `test_co03`, upgraded on `sipanel` |
| D-04 | Low (back office) | `sipanel_sale_scope`: unlink of a working quote scope | Recorded; workaround documented; not fixed in this run |
| F-01 | Finding (configuration) | website languages = `en_US` only → portal not Persian/RTL for Persian customers | Owner decision (enable `fa_IR` on the website) |
| F-02 | Finding (master data) | embedded UBL XML exposes anchor product name + internal reference | Name anchor products for customers; no internal-only data leaks |
| F-03 | Finding (design as built) | SEPARATELY_BILLABLE (`own_line`) is presented as a note line with quantity; no separately priced order line is generated automatically | Operator adds the billable line manually; confirm with owner |
| F-04 | Finding (by design) | seal hash + revision id are visible as `data-sipanel-*` attributes on the portal | Not secret (content hash); the access token remains the only secret |
| F-05 | Finding (test infra, fixed) | archived demo leftover `SIPANEL-PT-GUTTER` broke the test fixture (unique code incl. archived) | fixture code now unique per run (commit `0e2d63e`) |
| G-01 | Accepted pilot governance limitation | single person holds Sales, Finance waiver, Steward, Estimator, Cost viewer, Execution owner, Finance and Accounting Manager + System admin | Recorded, not a blocker (management decision 2026-09-20) |

## 4. Tests executed

| Run | Scope | Result |
|---|---|---|
| before-fix, `--test-tags /sipanel_sale_scope:TestCustomerOutput` on the installed (old) code | 3 tests | 2 FAIL (co01 `'Units' != 'عدد'`, co02 reference missing) + 1 ERROR (co03 method absent) — expected |
| after-fix, `-u sipanel_sale_scope --test-enable --test-tags sipanel` | 38 test methods (sale_scope 15 quote engine + 5 governance + 6 security + 3 customer output; execution 6; costing 3) | 0 FAIL, 1 ERROR in `test_co01` caused by a test-side filter (two components share the gutter product); the SQL `duplicate key … anchor_line_unique` line is the expected negative case of `test_pt01` |
| re-run after test correction, `--test-tags /sipanel_sale_scope:TestCustomerOutput,/sipanel_commercial_scope_core` (no upgrade) | 17 test methods (core 14 + customer output 3) | 0 FAIL, 0 ERROR |

Logs: `evidence/test_before_fix_TestCustomerOutput.log`, `evidence/test_after_fix_upgrade_sipanel_sale_scope.log`, `evidence/test_after_fix_core_and_customer_output.log`.

## 5. Manual visual-review items remaining

1. Open `SI-26/312` (state *cancelled*, retained) in the back office and print the quotation **after** the owner applies D-01, to confirm the styled 3-page PDF on the live HTTP path (this run could only prove it in a rolled-back dry run: `evidence/pdf/SI-26_312_quotation_dryrun_with_D01_fix.pdf`, `evidence/png/quotation_dryrun_fixed_part0[12].png`).
2. Page-break placement of long notes across pages was checked by page count and per-page text only; PDF pages could not be rasterised on this host (no `pdftoppm`/`gs`; nothing was installed). The PNG evidence is the same HTML rendered by the same wkhtmltoimage engine as one tall image, so the cover-page overlap seen in `quotation_dryrun_fixed_part01.png` is an artefact of the single-image render, not of the PDF.
3. Portal chrome in Persian after enabling `fa_IR` on the website (F-01).

## 6. Bundle

`SIPANEL_CUSTOMER_OUTPUT_VALIDATION_BUNDLE.zip` + `.sha256`; manifest in `REPORT_BUNDLE_MANIFEST.txt`; per-file digests in `SHA256SUMS`. The bundle contains no password, private key, cookie, live portal token, database dump, filestore or unredacted configuration (tokens replaced by `<REDACTED_ACCESS_TOKEN_*>`; `tokens.json` was never copied out of the scratch area and has been deleted).
