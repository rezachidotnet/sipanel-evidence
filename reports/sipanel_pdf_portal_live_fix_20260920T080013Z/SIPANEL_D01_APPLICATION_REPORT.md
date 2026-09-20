# SIPANEL D-01 Application Report — `report.url` on database `sipanel` (STEP 1B, run 20260920T080013Z)

| Item | Value |
|---|---|
| Authorisation | management-authorized STEP 1B (2026-09-20); operational owner user id 2 (`amirmousa1983@gmail.com`) |
| Target | database `sipanel`, container `odoo-sipanel` only (`odoo-db` used only for the `sipanel` dump in the recovery point) |
| Parameter record | `ir.config_parameter` id 53, key `report.url` |
| **Previous value** | `'http://odoo:8069\n'` (17 characters, trailing newline) |
| **New value** | `'http://127.0.0.1:8072'` (loopback, Odoo gevent/longpolling port) |
| Applied at | 2026-09-20 08:08:08 UTC, ORM `set_param`, explicit `env.cr.commit()` (`evidence/scripts/apply_d01_8072.py`) |
| Restart | **none** (parameter is read at every render; runtime evidence confirmed the change took effect immediately) |
| Result | **D-01 applied and live-verified** — with a documented deviation from the literal value in the task |

## 1. Why not `http://127.0.0.1:8069` (the value from the task and the STEP 1A dry run)

The literal value was applied first (08:02:42 UTC, `evidence/scripts/apply_d01.py`) and immediately validated through the customer HTTP path. The PDF request **hung**:

| Time (UTC) | Evidence |
|---|---|
| 08:03:33 | HTTP worker pid 15 starts wkhtmltopdf for `/my/orders/312?…&report_type=pdf` |
| 08:05:32 | `ERROR odoo.service.server: WorkerHTTP (15) timeout after 120s` — the only HTTP worker was killed; the customer request returned nothing (`curl` code 000) |
| 08:05:33 | replacement worker pid 150 spawned; only then were the asset requests from wkhtmltopdf served (`GET /web/assets/…report_assets_common.rtl…css 200`) |
| config (redacted recovery-point copy) | `workers = 1`, `limit_time_real = 120`, `gevent_port = 8072`, `proxy_mode = True` |

Root cause: with `workers = 1` the single prefork HTTP worker is busy waiting for wkhtmltopdf, while wkhtmltopdf asks **the same worker** on port 8069 for the CSS/JS/image assets — a self-deadlock that ends only when the worker is killed by `limit_time_real`. The STEP 1A dry run did not show this because it rendered from the Odoo shell (a separate process), not from the HTTP worker. During the two minutes the site was unresponsive for everyone (the owner was browsing the back office at that moment), so the value was **rolled back at 08:06** to the recorded previous value (`evidence/scripts/rollback_d01.py`).

## 2. Revised minimal correction: loopback port 8072

The Odoo gevent server (pid `odoo gevent server`, port 8072, normally used for websocket/longpolling) runs the same WSGI application in a separate process. In-container probes showed it serves every resource type the report needs, quickly, without touching the HTTP worker:

| Resource | HTTP | Size | Time |
|---|---|---|---|
| `/web/assets/1/f3a065c/web.report_assets_common.rtl.autoprefixed.min.css` | 200 | 437,589 B | 0.11 s (first hit 3.6 s) |
| `/web/assets/1/d12ac26/web.report_assets_pdf.rtl.autoprefixed.min.css` | 200 | 6,397 B | 0.07 s |
| `/web/assets/5439b38/web.report_assets_common.min.js` | 200 | 155,999 B | 0.09 s |
| `/web/image/website/1/logo`, `/web/static/img/placeholder.png` | 200 | 9,491 B / 6,078 B | < 0.2 s |
| `/web/login` (full page — **not** needed by reports) | 500 (`KeyError: 'REQUEST_URI'`, gevent WSGI environ) | — | the one exception in the log at 08:07:14 is this diagnostic probe |

This keeps the correction inside the container on the loopback interface, without host aliases, Docker networking changes, config-file edits, additional workers or a restart. After applying it:

| Check | Result |
|---|---|
| live PDF via `/my/orders/312?access_token=…&report_type=pdf` (English route) | HTTP 200, `application/pdf`, 134,803 B, 7.06 s |
| live PDF via `/fa/my/orders/312?…&report_type=pdf` (Persian route) | HTTP 200, 134,819 B, 5.37 s |
| asset requests | served by the gevent process (`longpolling: 127.0.0.1 - - GET /web/assets/… 200`, `GET /web/image/…signature.png 200`) |
| `HostNotFoundError` / worker timeouts in the log since 08:08 | **0** |
| fonts embedded | `IRANSans` only (before: DejaVuSans, NimbusSans) |
| pages | 3 (before: 2, unstyled) |

## 3. Alternatives for the owner (not applied)

| Option | What it needs | Trade-off |
|---|---|---|
| A. keep `report.url = http://127.0.0.1:8072` (applied) | nothing | relies on the gevent process serving `/web/assets` and `/web/image` (standard Odoo application code); if a future Odoo upgrade restricts that process to websocket routes, PDFs would fall back to unstyled again (visible immediately in the log as network errors) |
| B. `workers = 2` in `/opt/odoo/odoo-sipanel.conf` + restart of `odoo-sipanel`, then `report.url = http://127.0.0.1:8069` | root config edit, restart, ~150–300 MB more RAM | Odoo's documented setup for reports; the host has 2 GB RAM shared by four tenants (497 MB available at run time), so this is a capacity decision |
| C. previous value `http://odoo:8069\n` | one `set_param` | unstyled PDFs, missing `ریال` glyph (D-01 symptom) |

## 4. Rollback

```
docker exec -i odoo-sipanel odoo shell -c /etc/odoo/odoo.conf -d sipanel --no-http <<'EOF'
env['ir.config_parameter'].sudo().set_param('report.url', 'http://odoo:8069\n'); env.cr.commit()
EOF
```

No restart required. Full rollback record in `SIPANEL_CONFIGURATION_CHANGE_AND_ROLLBACK.md`.
