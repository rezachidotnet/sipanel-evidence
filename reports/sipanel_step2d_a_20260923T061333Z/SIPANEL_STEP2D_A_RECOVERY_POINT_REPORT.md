# SIPANEL STEP 2D-A — Recovery point report

Run: 20260923T061333Z — Verdict for this gate: **FAIL (BLOCKED_DISK_CAPACITY)**; no new recovery point created.

## Gate computation (exact replica of scripts/sipanel_recovery_point.sh step 1)

```
# Capacity gate (exact replica of scripts/sipanel_recovery_point.sh step 1) 20260923T061333Z
db_bytes=158236007 filestore_bytes=280395415 addons_bytes=47137906 need_mb~=463 free_mb=1923 MIN_FREE_MB=1500 margin_mb=1460
RESULT: BLOCKED_BACKUP_CAPACITY (script would exit 3): need ~463 MB plus 1500 MB headroom, free 1923 MB, shortfall 40 MB
note: the script was NOT executed, because it reserves DEST (mkdir) before the capacity check and would leave an INVALID-marked directory on failure.
```

## Why the script was not run

Step 0 of the script takes the flock and atomically `mkdir`s the destination; step 1 evaluates capacity and exits 3. The EXIT trap
then writes INVALID_DO_NOT_USE.txt into the reserved directory. Running it while the gate is known to fail would have created an
invalid recovery point (the kind removed in 2C-CLOSEOUT-HARDENING). The arithmetic was reproduced with the same commands instead.

## Existing recovery points (read-only inventory)

| directory | size | state |
|---|---|---|
| sipanel-pre-scope-20260919T164558Z | 109 MB | valid, superseded |
| sipanel-pre-translation-20260921T013000Z | 110 MB | valid, superseded |
| sipanel-pre-sepbill-20260921T021500Z | 110 MB | valid, superseded |
| sipanel-pre-2bhardening-20260922T060000Z | 110 MB | valid, superseded |
| sipanel-pre-step2c-20260922T065650Z | 110 MB | valid, superseded |
| sipanel-pre-2chardening-20260922T083014Z | 111 MB | valid, superseded |
| sipanel-pre-2ccloseout-20260922T111500Z | 112 MB | valid, superseded |
| sipanel-pre-2ccloseouthard-20260923T051626Z | 112 MB | **latest valid** |
| ahanassa-migration-20260821-1644 | 24 MB | other tenant, untouched |
| sipanel-before-kanban-fix-20260717-214400.dump | 18 MB | legacy dump |

INVALID markers found: none.

## Verification of the latest valid point (sipanel-pre-2ccloseouthard-20260923T051626Z)

- SHA256SUMS: all six entries OK (sipanel.dump, filestore-sipanel.tar.gz, addons.tar.gz, installed_modules.txt, container-inspect.json, odoo-sipanel.conf.redacted).
- PostgreSQL dump: `pg_restore --list` readable, 17,574 TOC entries.
- Filestore archive: lists cleanly, single top-level directory `sipanel`.
- Addons archive: lists cleanly, single top-level directory `addons`.
- Redacted configuration: db_password redacted; no admin_passwd key present in the live config file, so none to redact.
- Installed-module inventory: 200 modules; SIPANEL entries: core 19.0.1.1.0, sale_scope 19.0.1.2.3 (pre-upgrade, expected), execution 19.0.1.0.2, costing 19.0.1.0.0, partner_autocomplete_guard 19.0.1.0.0.
- No INVALID marker.

This point therefore remains the authoritative rollback target; it predates the 2C-CLOSEOUT-HARDENING upgrade of sipanel_sale_scope to 19.0.1.2.4 (source commit fce346b), which was itself verified after that run.

Full listing: evidence/recovery_point_inventory.txt.
