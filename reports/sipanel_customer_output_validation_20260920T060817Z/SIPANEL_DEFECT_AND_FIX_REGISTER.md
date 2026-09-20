# SIPANEL Defect and Fix Register — customer output validation (run 20260920T060817Z)

Rule applied: a correction was made only for a demonstrated customer-output defect, with before-fix evidence, the smallest maintainable change, a regression test that fails before and passes after, a fresh recovery point before the module upgrade, and after-fix evidence. Local commit `0e2d63e` (not pushed).

## D-01 — Quotation PDFs are rendered without report CSS/fonts (`report.url` points to an unresolvable host)

| | |
|---|---|
| Severity | High — affects every PDF produced by database `sipanel` (pre-existing, not introduced by SIPANEL) |
| Symptom | customer PDF has no layout/table borders/logo, DejaVu fallback font instead of IRANSans, and the currency symbol `ریال` prints as a missing-glyph box (`evidence/png/quotation_before_unstyled_part02.png`, fonts list in `text_extraction_before_D01_fix.txt` analysis) |
| Root cause | `ir.config_parameter` `report.url` = `"http://odoo:8069\n"` (note the trailing newline). wkhtmltopdf runs inside `odoo-sipanel` and fetches `/web/assets/…/web.report_assets_common…css` from that base URL; `getent hosts odoo` → not resolvable in the container; Odoo logs `wkhtmltopdf: Exit with code 1 due to network error: HostNotFoundError` on every render (log entries 2026-08-27, 2026-09-20 06:12/06:14/06:16) and still returns the unstyled PDF |
| Before-fix evidence | `evidence/pdf/SI-26_312_quotation_as_served_before_D01_fix.pdf` (HTTP customer path), fonts DejaVuSans/NimbusSans, 2 pages |
| Fix (verified, **not applied**) | set `report.url` to `http://127.0.0.1:8069` on database `sipanel` only. Verified inside a rolled-back transaction (`evidence/scripts/dryrun_fix.py`): PDF 134,885 bytes, 3 pages, fonts `IRANSans` only, identical text content, no leakage (`evidence/pdf/SI-26_312_quotation_dryrun_with_D01_fix.pdf`, `png/quotation_dryrun_fixed_part0[12].png`). The parameter was restored by rollback (`after_rollback: "http://odoo:8069\n"`) |
| Why not applied | the Claude Code auto-mode classifier refused the production-wide parameter write ("Modify Shared Resources"). It is a one-line, reversible configuration change for the owner: |

```
docker exec -i odoo-sipanel odoo shell -c /etc/odoo/odoo.conf -d sipanel --no-http <<'EOF'
env['ir.config_parameter'].sudo().set_param('report.url', 'http://127.0.0.1:8069'); env.cr.commit()
EOF
```

Rollback: same command with the previous value `'http://odoo:8069\n'`. No restart needed. Re-check afterwards: print any quotation and confirm the log no longer shows `HostNotFoundError`.

## D-02 — Persian quotation note prints English unit names

| | |
|---|---|
| Severity | Medium — customer output (every Persian quotation) |
| Symptom | note lines `- بست دیواری (صورت‌حساب جداگانه): 24 Units`, `- نصب و راه‌اندازی: 8 Hours` on a `fa_IR` quotation although `uom.uom` carries the translations `عدد` / `ساعت` |
| Root cause | `sipanel_sale_scope/models/quote_scope.py::_create_from_version` snapshots `l.uom_id.name` in the creating user's context language (en_US); same in `wizards/replace_recipe.py`; `quote_scope_component.py::_customer_payload` falls back to `self.uom_id.name` without the quotation language |
| Fix | compute `lang` once (`order.partner_id.lang or user lang or en_US`) and snapshot `l.uom_id.with_context(lang=lang).name`; replace-recipe uses `rev.language`; payload fallback uses `language`. Sealed notes of existing revisions are untouched (immutable by design) |
| Regression test | `tests/test_customer_output.py::test_co01_unit_names_follow_quotation_language` — before: `AssertionError: 'Units' != 'عدد'`; after: pass (English quotation still prints `Units`) |
| After-fix evidence | scope added to draft `SI-26/313` after the upgrade: `uom_name_snapshot ∈ {m, ساعت, عدد}`, note `- بست دیواری (صورت‌حساب جداگانه): 6 عدد`, `- نصب و راه‌اندازی: 8 ساعت` (`evidence/scripts/afterfix.py` output in the validation report) |
| Files | `models/quote_scope.py`, `models/quote_scope_component.py`, `wizards/replace_recipe.py` |

## D-03 — Customer signature path: no acceptance reference, internal error surfaced to the customer

| | |
|---|---|
| Severity | Medium — acceptance/content binding and customer-facing flow |
| Symptom 1 | native portal signature (`/my/orders/<id>/accept` → `action_confirm()` under sudo) accepted the sealed revisions with `acceptance_reference = False` and `accepted_by = OdooBot`; the signature (`signed_by/signed_on`) was linked to the seal only by timing |
| Symptom 2 | after a governed optional-scope acceptance on the portal (a designed customer action), the seal verification at confirm fails for **all** scopes of the order (anchor quantity and order totals are part of every seal payload). Native Odoo surfaced `UserError: Scope SI-26/312 / … changed after it was sent (sealed 874468afa3ab…, now a1f0a421b25d…). Re-send the quotation to seal a new revision.` to the customer as a JSON-RPC error and left the signature written on the order |
| Before-fix evidence | dry-run transcript (rolled back) in `SIPANEL_PORTAL_VALIDATION_MATRIX.md`; `test_co02` failure `False is not true : portal signature must be recorded as the acceptance reference`; `test_co03` `AttributeError: 'sale.order' object has no attribute '_sipanel_acceptance_reference'` |
| Fix | `models/sale_order.py`: new `_sipanel_acceptance_reference()` — explicit reference (change-order path) wins, else `portal_signature:<signed_by>:<signed_on UTC>` when the order carries a signature, else `None`; used by `_sipanel_accept_current_revisions`. `controllers/portal.py`: override of `portal_quote_accept` for Scope-carrying orders — on `UserError` from the seal verification the transaction is rolled back and `{'error': "This quotation has been updated since it was sent. Please ask your sales contact to re-send it before signing."}` is returned (non-scope orders keep native behaviour) |
| Regression tests | `test_co02_portal_signature_is_the_acceptance_reference`, `test_co03_explicit_reference_wins_over_signature` — fail before, pass after. The controller branch is covered by the live HTTP after-fix probe (no HttpCase under `--no-http`) |
| After-fix evidence | `evidence/portal/portal_signature_after_fix.txt`: customer-safe error; order `312` stays `sent`, `signed_by=False`, no signature stored |
| Residual (design, not changed) | the customer still cannot sign until sales re-sends after an option toggle (C3-D03 whole-quotation seal). Options for the owner: (a) keep as is and instruct sales to re-send after customer option choices; (b) let a governed portal transition re-seal automatically (amend + seal without note change) so the customer can sign in one session — this is a governance decision, not a minimal fix, and was deliberately not implemented |

## D-04 — Deleting a working (unsealed) quote scope fails (back office)

| | |
|---|---|
| Severity | Low — operator workflow, not customer output; not fixed in this run |
| Symptom | `sipanel.quote.scope.unlink()` on a scope whose only revision is `working` raises `MissingError: Record does not exist … sipanel.quote.scope.revision(301,)`; deleting components → revisions → scope raises `ForeignKeyViolation … sipanel_quote_scope_current_revision_id_fkey` |
| Root cause (probable) | `current_revision_id` (ondelete restrict) still points to the revision being cascade-deleted, and a related/stored compute re-reads the deleted revision during the cascade |
| Workaround used | `scope.write({'current_revision_id': False})`, then delete components, revisions, scope, anchor line (`evidence/scripts/cleanup.py`) |
| Suggested fix (next run) | in `SipanelQuoteScope.unlink` (working scopes only): clear `current_revision_id`, delete components/revisions explicitly, then `super().unlink()`; add a test |

## Findings (no code change)

| Id | Finding | Recommendation |
|---|---|---|
| F-01 | Website languages = `en_US` only; `/fa_IR/my/orders/…` → 404; portal chrome is English/LTR/Gregorian for `fa_IR` customers; the pre-existing `sale_shamsi_report.portal_sale_fa_customization` never triggers | enable `fa_IR` on the website (Website → Settings → Languages) — loads translations, owner decision; then re-check the portal |
| F-02 | The PDF embeds a Peppol UBL BIS3 order XML (native `sale_edi_ubl`) exposing the anchor product **name** and **internal reference** (`SellersItemIdentification`) | name anchor products and their internal references as customer-facing text; consider whether the UBL attachment is wanted for Iranian customers (Odoo setting on the sales journal/EDI format) |
| F-03 | SEPARATELY_BILLABLE placement (`own_line`) renders as a note bullet with quantity, e.g. `بست دیواری (صورت‌حساب جداگانه): 24 Units`; no separately priced order line is generated automatically | operator adds the billable line manually, or the owner decides to extend the module later |
| F-04 | `data-sipanel-revision-id` / `data-sipanel-seal-hash` visible in portal HTML | by design (GAP-S04); hash is not a secret |
| F-05 | archived demo leftover `SIPANEL-PT-GUTTER` (scope 91) broke `setUpClass` of every SIPANEL test (unique code per company includes archived rows) | fixed in `sipanel_commercial_scope_core/tests/common.py` (code unique per run) — test-only change, same commit |
| F-06 | wkhtmltoimage single-image render shows the cover date overlapping the table (artefact of one tall image; PDF has page breaks) | manual visual check of the 3-page PDF after D-01 |

## Source diff summary (commit `0e2d63e`)

```
addons/sipanel_commercial_scope_core/tests/common.py  |  5 ++++-
addons/sipanel_sale_scope/controllers/portal.py       | 19 +++++++++++++++++++
addons/sipanel_sale_scope/models/quote_scope.py       |  6 ++++--
addons/sipanel_sale_scope/models/quote_scope_component.py | 2 +-
addons/sipanel_sale_scope/models/sale_order.py        | 12 +++++++++++-
addons/sipanel_sale_scope/tests/__init__.py           |  1 +
addons/sipanel_sale_scope/tests/test_customer_output.py | new (68 lines)
addons/sipanel_sale_scope/wizards/replace_recipe.py   |  2 +-
```
