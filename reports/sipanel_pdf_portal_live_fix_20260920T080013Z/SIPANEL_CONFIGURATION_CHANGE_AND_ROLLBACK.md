# SIPANEL Configuration Change and Rollback Record (STEP 1B, run 20260920T080013Z)

| Item | Value |
|---|---|
| Final verdict | **PASS_WITH_FINDINGS** |
| Database / container | `sipanel` / `odoo-sipanel` only; `odoo-db` used for the `sipanel` dump only; other tenants (`odoo-avizsazeh`, `odoo-shahbazi`, `odoo-ahantorob`) untouched |
| Git | HEAD `ca9c474` before and after (working tree clean before; only this report directory added). **No source change, no code commit, no module upgrade** in this run; D-02/D-03 (`0e2d63e`) untouched |
| `odoo-sipanel` restart | **none** |
| Recovery points | previous `/opt/odoo/backups/sipanel-pre-customer-output-fix-20260920T062942Z` verified (6/6 checksums OK); fresh `/opt/odoo/backups/sipanel-pre-live-fix-20260920T080013Z` created 08:00–08:01 UTC and verified (dump sha256 `4d79c4ab…`, need ≈455 MB, free 3,296 MB) — `evidence/recovery_point.log` |
| Capacity at start | disk 3,296 MB free on `/opt`; RAM 497 MB available; `odoo-sipanel` healthy (`/web/login` 200, up ~1 h) |

## Change log (UTC, all via ORM in `odoo shell`, explicit commits)

| # | Time | Object | Before | After | Script | Status |
|---|---|---|---|---|---|---|
| 1 | 08:02:42 | `ir.config_parameter` 53 `report.url` | `'http://odoo:8069\n'` | `'http://127.0.0.1:8069'` | `apply_d01.py` | **rolled back** at ~08:06 (single-worker deadlock, worker timeout at 08:05:32) |
| 2 | ~08:06 | same | `'http://127.0.0.1:8069'` | `'http://odoo:8069\n'` | `rollback_d01.py` | restored exact previous value |
| 3 | 08:08:08 | same | `'http://odoo:8069\n'` | **`'http://127.0.0.1:8072'`** | `apply_d01_8072.py` | **applied, live-verified, kept** |
| 4 | 08:09:04 | `website` 1 `language_ids` | `[en_US]` | `[en_US, fa_IR]` (default `en_US` unchanged) | `enable_fa.py` | **applied, kept** |
| 5 | ~08:11 | registry caches (no data) | stale worker cache (Persian route 404) | `clear_cache()` + `signal_changes()` | `signal_cache.py` | propagation only |

Not changed: `web.base.url` (`https://odoo.sipanelco.ir`), `res.lang` records (fa_IR was already active), `/opt/odoo/odoo-sipanel.conf` (`workers = 1` etc.), Docker networking/host aliases, taxes, accounting, thresholds, labour costs, quotation 312 (read-only use), any other website or database.

## Rollback procedures

**R-1 — `report.url` (D-01)**

```
docker exec -i odoo-sipanel odoo shell -c /etc/odoo/odoo.conf -d sipanel --no-http <<'EOF'
env['ir.config_parameter'].sudo().set_param('report.url', 'http://odoo:8069\n'); env.cr.commit()
EOF
```
Effect: PDFs return to the unstyled state (D-01 symptom). No restart.

**R-2 — website Persian language (F-01)**

```
docker exec -i odoo-sipanel odoo shell -c /etc/odoo/odoo.conf -d sipanel --no-http <<'EOF'
fa = env['res.lang'].sudo().search([('code','=','fa_IR')])
env['website'].sudo().browse(1).write({'language_ids': [(3, fa.id)]})
env.registry.clear_cache(); env.registry.signal_changes(); env.cr.commit()
EOF
```
Effect: `/fa/…` routes return 404 again; English route unaffected. No restart.

**R-3 — full restore** (only if needed): `pg_restore` of `/opt/odoo/backups/sipanel-pre-live-fix-20260920T080013Z/sipanel.dump` into a fresh database plus filestore tar, as printed by `scripts/sipanel_recovery_point.sh` (never restore over a running production DB without stopping `odoo-sipanel` first; this run did not need it).

## Findings carried forward

| Id | Finding | Owner decision |
|---|---|---|
| D-01-B | `workers = 1` makes any `report.url` on the HTTP port self-deadlock; the applied loopback gevent port avoids it without config/restart | keep 8072, or move to `workers = 2` + restart + `report.url = http://127.0.0.1:8069` when RAM allows (see D-01 report §3) |
| F-01 (closed) | Persian portal chrome now loads; existing unprefixed links still open English by design (default language unchanged) | none required; consider `fa_IR` as default website language if all customers are Persian |
| O-2 | website homepage `/` is unpublished (404, pre-existing) | cosmetic, outside SIPANEL scope |
| F-02 / F-03 / D-04 | unchanged, excluded from this run | as per STEP 1A register |
