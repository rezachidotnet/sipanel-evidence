# SIPANEL `fa_IR` Portal Enablement Report (STEP 1B, run 20260920T080013Z)

## 1. Before state (read-only preflight, `evidence/scripts/preflight_1b.py`)

| Item | Value |
|---|---|
| Website | id 1 `sipanel`, domain `https://odoo.sipanelco.ir`, company Sipanel (only website on the database) |
| Default website language | `en_US` |
| Enabled website languages | `en_US` only |
| `res.lang` `fa_IR` | exists, **already active**, name `Persian / فارسی`, direction `rtl`, `url_code = fa` |
| Translations | already loaded for the active language (e.g. `uom.uom` "Units" → `عدد`, `sale.order.type_name` → `پیش فاکتور`); `.po` files present in the image for `base`, `web`, `portal`, `website`, `sale`, `sale_management` |
| Persian route | `/fa/my/orders/312` → 404, `/fa_IR/my/orders/312` → 404 |

## 2. Change applied (native path, `evidence/scripts/enable_fa.py`)

| Step | Detail |
|---|---|
| ORM write | `website(1).write({'language_ids': [(4, <fa_IR id>)]})`, explicit commit at 2026-09-20 08:09:04 UTC |
| Default language | unchanged (`en_US`) |
| `en_US` | kept |
| Translation loading | **not triggered** — `fa_IR` was already active, so `res.lang._activate_lang` was not needed and no `.po` import ran; no records were changed except `website.language_ids` |
| Other websites | none exist; nothing else touched |
| Portal invitations / e-mail / customer records | none created, none sent, none changed (`mail.mail` since 08:00: 0; new users: 0; partner 426 stays archived) |

## 3. Cache propagation (required extra step)

After the commit the running HTTP worker still answered 404 on `/fa/…`: `website.write` clears the registry cache **in the writing process**, but a plain shell commit does not raise the cross-process cache signal that a request-driven write (back-office UI) would. A second read-only-in-data script (`evidence/scripts/signal_cache.py`) ran `registry.clear_cache()` (default, `routing`, `templates`) and `registry.signal_changes()`; from the next request on, the worker served the Persian route. No restart was needed. Equivalent in the UI: saving the website language setting in *Website → Configuration → Settings* performs the same signalling automatically.

## 4. After state and routes

| Route | Result |
|---|---|
| `/fa/my/orders/312?access_token=…` | **200**, 41,294 B, `<html lang="fa-IR">`, RTL asset bundles (`web.assets_frontend.rtl…`) |
| `/fa_IR/my/orders/312?access_token=…` | **301 → `/fa/my/orders/312?…`** — Odoo 19 uses the language `url_code` (`fa`) as prefix; the `fa_IR` spelling is redirected natively |
| `/my/orders/312?access_token=…` (English, default language) | 200, unchanged |
| `/en/my/orders/312?…` | 303 → unprefixed URL (default language has no prefix) |
| `/fa/my/orders/312?…&report_type=pdf` | 200, PDF (IRANSans, 3 pages) |
| `/fa/web/login`, `/web/login` | 200 / 200 |
| `/fa/my` (no session) | 303 → `/web/login?redirect=/my` (native) |
| `/` | 404 — **pre-existing**: the website homepage page is unpublished (`website.page` `/` `is_published=False`, 404 already logged on 2026-09-19 23:13 and 2026-09-20 07:27 UTC); not caused by this change |

`website` after: `default_lang = en_US`, `language_ids = [en_US, fa_IR]`, `write_date 2026-09-20 08:09:04`.

## 5. What Persian customers now get

* Portal page in Persian with RTL layout (`sale_shamsi_report.portal_sale_fa_customization` now triggers: Shamsi date `1405/06/29`, Persian document number row, Persian title), see `SIPANEL_LIVE_PORTAL_VALIDATION_REPORT.md`.
* The language is chosen by URL prefix / the customer's `res.partner.lang`; an existing customer link without prefix still opens the English page (default language unchanged, as required). Odoo adds the `/fa` prefix automatically in links generated for a `fa_IR` partner (`_get_share_url` → `url_for` with the partner language); this was not exercised because no invitation may be sent in this run.

## 6. Rollback

```
docker exec -i odoo-sipanel odoo shell -c /etc/odoo/odoo.conf -d sipanel --no-http <<'EOF'
fa = env['res.lang'].sudo().search([('code','=','fa_IR')]); env['website'].sudo().browse(1).write({'language_ids': [(3, fa.id)]})
env.registry.clear_cache(); env.registry.signal_changes(); env.cr.commit()
EOF
```

`res.lang fa_IR` stays active as before (it was active before this run).
