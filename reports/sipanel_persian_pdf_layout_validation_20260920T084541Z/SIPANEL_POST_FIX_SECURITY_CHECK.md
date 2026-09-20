# SIPANEL Post-Fix Security Check (STEP 1C, run 20260920T084541Z)

## 1. Leakage in the fresh post-D-02 quotation `SI-26/368`

Back office at render time: eligible cost 18,144,382 IRR, margin 10,355,618 IRR, unit costs 731,000 / 9,876 / 55,555 / 4,321 / 8,765,000 / 123, internal-only component (20 screws, marker label), internal chatter note, partner internal note, analytic account markers.

| Output | Markers | Cost/margin figures | Internal words / ids | Tokens / paths |
|---|---|---|---|---|
| before-fix PDF (ORM) | 0 | 0 | 0 | 0 |
| after-fix PDF (ORM) | 0 | 0 | 0 | 0 |
| after-fix PDF (HTTP, Persian route) | 0 | 0 | 0 | 0 |
| Persian portal page | 0 | 0 | 0 | own access token only (redacted in evidence) |

PDF structure: metadata Producer/Creator "Odoo", no XMP, no JavaScript, two footer links, one embedded UBL BIS3 order XML (`SI-26_368_ubl_bis3.xml`, 7,751 B, native `sale_edi_ubl`; same nature as F-02 — customer-facing commercial data plus anchor product name/reference, no internal-only data).

## 2. Access control (Persian route, draft quotation)

| Probe | Result |
|---|---|
| `/fa/my/orders/368?access_token=<valid>` | 200 |
| `/fa/my/orders/368` (no token) | 303 → `/my` |
| `…&report_type=pdf` with token | 200 `application/pdf` |
| optional-quantity widget / `data-sipanel-*` binding | not rendered on a draft (not yet sealed) order — correct per the SIPANEL guard (`sent_sealed` only) |

## 3. Template change surface

The change adds one CSS declaration and alters two spacer heights in an existing QWeb template; no new field, route, or data exposure. QWeb expressions unchanged (`doc.name`, `doc.partner_id.name`, `doc.date_order_shamsi`/`doc.date_order`). The structural test asserts the date field is rendered once inside the cover.

## 4. Process hygiene

* Source edited through the module's git working tree (`/opt/odoo/addons/sale_shamsi_report`), file ownership preserved (`messagebus`), committed locally as `b17fbb5`; not pushed.
* Upgrade limited to `sale_shamsi_report`; no restart; HTTP health 200 afterwards; no `HostNotFoundError`/timeouts logged.
* Report directory scanned for UUID-shaped tokens, `session_id=` values, `db_password=`, `admin_passwd=`, private keys: none (the portal HTML is token-redacted; `validation_record_ids.json` contains ids and text only).
* Staged token file deleted after the HTTP render; no dump, filestore or configuration file included; recovery point stays root-only under `/opt/odoo/backups`.
