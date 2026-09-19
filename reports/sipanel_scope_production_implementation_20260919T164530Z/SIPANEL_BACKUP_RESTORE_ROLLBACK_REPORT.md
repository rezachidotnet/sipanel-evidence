Run sipanel_scope_production_implementation_20260919T164530Z · Target: database `sipanel` on container `odoo-sipanel` (Odoo 19.0-20260528) · Build: source commit 99dd874 (fixes on top of 931f949) · Runner: Claude Code (claude-fable-5-1) · Date: 2026-09-19 UTC

# SIPANEL — Backup / Restore / Rollback Report (EXECUTED)

## Recovery point (pre-change)

Path: `/opt/odoo/backups/sipanel-pre-scope-20260919T164558Z/` (root-only). Contents and checksums verified 6/6 (EV-01). Created **before** the first database write; live DB state at that moment: 196 modules, last sale order write 2026-09-18 07:09.

| File | SHA-256 |
|---|---|
| sipanel.dump | 11351ad8519b9c81f1d59ae5f5dd523397e76f91f3d62c5dc5db4f161dc10d69 |
| filestore-sipanel.tar.gz | 6a508e006be0caa198241304e80457d04632a65c4cd846441542df030c4652b5 |
| addons.tar.gz | f9774d3685e0df53fa842e1c59f8be5849166f246bc628d4c6baeada26b326fc |
| installed_modules.txt | a8313dc71bee6a5c7ed6cb666f89cfaa65fcdbb27280628775335516b7fe3050 |
| container-inspect.json | 92e24cad092896a79f62664e5518ca9093f53b9cc0992eb109634c2e37d03489 |
| odoo-sipanel.conf.redacted | 8fd7a7863ef6d789b91cf0741446d646356c7ac02a5009dbd0a4939832890f60 |

## Restore rehearsal (PT-30, EV-07)

Restored `sipanel.dump` into a separately named temporary database `sipanel_restore_rehearsal_20260919` on `odoo-db` (pg_restore exit 0). Counts restored vs live: modules 196 vs 200 (the 4 new modules), sale orders 14 = 14, partners 88 = 88, product templates 113 vs 114 (one archived synthetic anchor product from the fixture), attachments 1061 vs 1062, last order write 2026-09-18 07:09 vs 2026-09-19 16:52 (the anchor-line writes of the rolled-back tests never persisted; the difference is the module install touching order computes). Filestore archive extracted 713 files into a temp dir (not the live filestore). The rehearsal database was **dropped** immediately after verification (runbook rule; database list after drop recorded). No other tenant database was touched; `odoo-db` was not restarted.

## Rollback

Not required (no failed deployment). Procedure to revert to the pre-change state: stop `odoo-sipanel`; `pg_restore --clean --if-exists -d sipanel` from the dump; extract `filestore-sipanel.tar.gz`; restore `/opt/odoo/addons` from `addons.tar.gz` (removes the sipanel_* folders); start `odoo-sipanel`. Uninstall is not rollback (C10-D03).
