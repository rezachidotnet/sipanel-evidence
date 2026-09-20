# SIPANEL Post-Change Security Check (STEP 1B, run 20260920T080013Z)

Scope: after `report.url` and website `fa_IR` changes on database `sipanel` — leakage in customer output, access control on both language routes, exposure created by the new asset path, and evidence hygiene.

## 1. Leakage (PDF, embedded file, portal HTML, HTML report)

| Item | English-route PDF | Persian-route PDF | Persian portal page | English portal page | Persian HTML report |
|---|---|---|---|---|---|
| `INTERNAL-MARKER-*` (8 planted families) | 0 | 0 | 0 | 0 | 0 |
| cost/margin figures (18 values, any separator) | 0 | 0 | 0 | 0 | 0 |
| internal words (`margin`, `cost`, `analytic`, `supplier`, `recognition`, `audit`, `sipanel_`, `unit_cost`, `occurrence_uid`, `scope_uid`, `sealed_hash`) | 0 | 0 | 0 | 0 | only CSS `margin` (9) |
| 40–64-hex identifiers | 0 | 0 | 0 | 0 | 0 |
| tokens / cookies / paths (`/opt/odoo`, `/mnt/extra-addons`) | 0 | 0 | own token only (redacted) | own token only (redacted) | 0 |
| HTML comments / JSON blobs | n/a | n/a | none | none | `<![endif]` only |
| PDF metadata | Producer/Creator "Odoo", no XMP, no JavaScript | same | | | |
| embedded file | `SI-26_312_ubl_bis3.xml` 6,388 B (native `sale_edi_ubl`; F-02 unchanged, out of scope) | same | | | |

## 2. Access control (unchanged behaviour on both routes)

| Probe | `/my/orders/312` | `/fa/my/orders/312` |
|---|---|---|
| valid token | 200 | 200 |
| no token | 303 → `/my` | 303 → `/my` |
| garbage token | 303 | 303 |
| token of 312 on order 311 / 310 (other customers' real orders) | 303 | 303 / 303 |
| PDF without token | 303 | 303 |
| nonexistent id (STEP 1A) | 303 | — |

## 3. New surface introduced by D-01 (`report.url = http://127.0.0.1:8072`)

* wkhtmltopdf now fetches `/web/assets/*`, `/web/image/*` and static files from the gevent process on the container loopback. Port 8072 is published only on the host loopback (`127.0.0.1:8082 → 8072`, behind the reverse proxy for `/websocket`); it is not reachable from other tenants or the internet beyond what nginx already forwards.
* Asset requests are unauthenticated public routes by design; the signature image request carries Odoo's own attachment access token (already the case with any `report.url`).
* No cookie jar content, credentials or session ids are passed to wkhtmltopdf beyond Odoo's standard `--cookie-jar` temp file (unchanged mechanism).

## 4. Website language change

* Only `website(1).language_ids` changed; `res.lang fa_IR` was already active, no translation import, no menu/page/record changes.
* No portal invitation, e-mail, user or customer record created (`mail.mail` since 08:00: 0; users created: 0; partner 426 still archived).
* The retained quotation 312 was not written (`write_date` 06:44:42 UTC unchanged); native "Quotation viewed" notifications were appended to its chatter by the portal views (messages 3 → 11 across STEP 1A/1B), which is Odoo's own audit of customer views.

## 5. Log review (08:00–08:20 UTC, `evidence/logs/odoo-sipanel_report_and_portal_REDACTED.log`)

| Entry | Assessment |
|---|---|
| `WorkerHTTP (15) timeout after 120s` (08:05:32) | caused by the rejected `127.0.0.1:8069` value (single-worker self-deadlock); rolled back; no recurrence |
| `Exception during request handling … KeyError: 'REQUEST_URI'` (08:07:14, pid 16) | my diagnostic `GET /web/login` on the gevent port; full pages are not served there; reports only need assets/images, which succeed |
| `HostNotFoundError` | 0 since 08:08 |
| other errors/tracebacks | none |

## 6. Evidence hygiene

* Report directory scanned for the live token, `session_id=`, `db_password`, `admin_passwd`, `PRIVATE KEY`: no hits.
* The staged token file (`val/token_1b.json`, mode 600, scratch area) is deleted at the end of the run; it was never written into the report directory or the repository.
* No database dump, filestore, configuration file or unredacted log is included; the recovery point stays under `/opt/odoo/backups` (root-only).
