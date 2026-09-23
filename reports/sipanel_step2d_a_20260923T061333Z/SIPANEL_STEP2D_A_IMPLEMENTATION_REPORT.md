# SIPANEL STEP 2D-A — Implementation report

Run: sipanel_step2d_a_20260923T061333Z (UTC)
Verdict: **BLOCKED** — BLOCKED_DISK_CAPACITY (recovery-point capacity gate, section 3 of the work order)
Target: database `sipanel`, application container `odoo-sipanel`, PostgreSQL container `odoo-db` (read-only in this run)

## 1. What happened

The work order makes the capacity rule of `scripts/sipanel_recovery_point.sh` authoritative and requires a fresh recovery
point before the first database, configuration or module write. The rule requires `free_mb - need_mb >= 1500`.

| quantity | value |
|---|---|
| pg_database_size(sipanel) | 158,236,007 bytes |
| filestore /opt/odoo/data/filestore/sipanel | 280,395,415 bytes |
| /opt/odoo/addons | 47,137,906 bytes |
| need_mb (sum / 1024 / 1024) | 463 MB |
| free_mb (df -Pm /opt) | 1923–1924 MB (two measurements) |
| margin (free - need) | 1460–1461 MB |
| MIN_FREE_MB | 1500 MB |
| shortfall | 39–40 MB |

Result of the exact replica of the gate: **BLOCKED_BACKUP_CAPACITY** (the script would exit 3).
The script itself was not executed: it reserves the destination directory before the capacity check and, on failure,
leaves an INVALID-marked directory behind. Replicating the arithmetic avoided creating one.

Per section 3 of the work order, when the gate fails: no implementation was started, nothing was deleted (no Docker
image or volume, no /tmp content, no tenant backup, no other tenant's file, no recovery point), a precise disk inventory
was produced (`evidence/disk_inventory.txt`) and the run stops with BLOCKED_DISK_CAPACITY.

## 2. Baseline verification (all read-only, all PASS)

- Repository clean before this run; HEAD = 7dbbd54f8641091712eb9ca500c55bc17eb7a11c.
- Source commit fce346b93af4da937cb3bcafa4aaca99ef8d1ef5 is an ancestor of HEAD. The evidence/bundle commit created after it is
  7dbbd54f8641091712eb9ca500c55bc17eb7a11c ("STEP 2C-CLOSEOUT-HARDENING 20260923T051626Z: sudo-seal security, recovery concurrency, invalid-point removal, test results, pilot, readiness, evidence and bundle").
- Installed module trees under /opt/odoo/addons are byte-identical to the repository for all four SIPANEL modules.
- Module versions (repository manifest = database latest_version): sipanel_commercial_scope_core 19.0.1.1.0, sipanel_sale_scope 19.0.1.2.4, sipanel_scope_execution 19.0.1.0.2, sipanel_scope_costing 19.0.1.0.0.
- Containers: odoo-sipanel Up 3 days (image 1cd111414896, RestartCount 0, started 2026-09-20T06:40:08Z); odoo-db postgres:15 Up 2 months (RestartCount 0). Neither restarted in this run.
- RAM: 1970 MB total, 648 MB available, swap 2797 MB used of 4095 MB.
- Recovery points: eight sipanel-pre-* directories (109–112 MB each) plus one legacy dump; no INVALID marker anywhere; latest valid point
  /opt/odoo/backups/sipanel-pre-2ccloseouthard-20260923T051626Z verified (all six SHA256 entries OK, dump TOC readable with 17,574 entries, archives list cleanly, secrets redacted). See SIPANEL_STEP2D_A_RECOVERY_POINT_REPORT.md.
- Taleghani: res.users id 2, login amirmousa1983@gmail.com, active, company 1 (Sipanel). Not duplicated. Holds Estimator, Scope Steward, Cost & Margin Viewer, Scope Sales, both waiver approver groups, Execution Owner, Finance (cost recognition), plus sales/account/stock/mrp/purchase manager groups and base.group_system.
- Analytic plans: 80 = "SIPANEL System", 81 = "SIPANEL Activity" (configured in ir.config_parameter sipanel_scope.system_plan_id / activity_plan_id).
- Accounts currently in plan 80: 1317, 1953 (both archived synthetic pilot accounts). In plan 81: 249, 250, 1318, 1319, 1954, 2130, 2309 (all archived synthetic pilot accounts). No active permanent operational account exists in either plan.
- Duplicate search for the D2D-A02 names (سیستم آبرو / تأمین و تدارک / ساخت / نصب, hamza-insensitive) found no existing record: the four accounts would have to be created when the run is unblocked.
- Supplier, BoM, workcenter and employee-cost inventory: see SIPANEL_STEP2D_A_VENDOR_BOM_COST_READINESS_REGISTER.md.

## 3. What was NOT done (blocked before the first write)

D2D-A01 role workflow change, D2D-A02 analytic account creation, D2D-A03 change-order settlement R-3, D2D-A04 backoff measurement,
focused tests, full regression, sale_shamsi_report regression, live smoke test, module version bumps, upgrades. No source file,
test, script, database row, configuration parameter or module state was changed. The only new files are this report directory.

## 4. Disk inventory summary (nothing deleted; see evidence/disk_inventory.txt)

| location | MB | on the prohibited-deletion list? |
|---|---|---|
| /var/lib/docker/volumes (89 dangling volumes) | 1456 | yes (volumes) |
| Docker images (4, all in use by containers) | 5334 | yes (images) |
| /tmp total, of which /tmp/claude-1000 612, twelve /tmp/ahanassa-backup-2026083* dirs 78 each | 2227 | yes (/tmp content) |
| /opt/odoo/data/backups | 1374 | tenant backups — yes |
| /opt/odoo/backups (8 sipanel recovery points + ahanassa + legacy dump) | 922 | recovery points — yes without exact authorization |
| /home/ubuntu/ahanassa-* (dir + two tarballs) | 1163 | other tenant's files — yes |
| /home/ubuntu/sipanel_audit/recovery | 293 | not listed; SIPANEL-scope, but no authorization to remove |
| /home/ubuntu/odoo-production-backups | 259 | tenant backups — yes |
| /var/log | 320 | not listed (system) |
| journal | 172 | not listed (system) |
| /var/cache/apt | 107 | not listed (system) |
| container json logs (odoo-sipanel 25, odoo-db 28, odoo-ahantorob 28) | 81 | not listed |
| /swapfile | 4097 | system |

## 5. Smallest actions that would clear the gate (for authorization — none executed)

The gate needs ~40 MB more free space plus a working margin for the run itself (the run creates a ~112 MB recovery point,
which the gate already accounts for, and the test database created by the test runner needs roughly the size of `sipanel` on
top — previous runs passed with a comparable margin). Any one of these would suffice, in order of least risk:

1. Remove the oldest SIPANEL recovery points that are superseded by verified later points, e.g. sipanel-pre-scope-20260919T164558Z (109 MB) and sipanel-pre-translation-20260921T013000Z (110 MB). Requires exact authorization naming the directories.
2. Remove the twelve /tmp/ahanassa-backup-20260830T* directories (12 × 78 MB = 936 MB) — ahanassa tenant scope, requires that tenant's authorization.
3. `docker volume prune` of the 89 dangling volumes (1.5 GB) — requires authorization; first list which volumes belong to which former container.
4. apt cache clean (107 MB) / journal vacuum (~100 MB) — host-level, outside the SIPANEL scope defined for this run.

## 6. Other tenants

No other tenant database or container was read for content, modified, restarted or tested. Only `docker ps`, `docker inspect`
(restart counts, log paths) and file-size listings touched their names.
