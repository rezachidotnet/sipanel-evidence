Run sipanel_scope_production_implementation_20260919T145639Z · Verdict: BLOCKED_BEFORE_DATABASE_WRITE · Status: SOURCE WRITTEN AND STATICALLY CHECKED — NOT INSTALLED, NOT RUNTIME VALIDATED (see evidence/EV-02).

# SIPANEL — Pre-change Recovery Point Report

## Result: **NOT CREATED — BLOCKED (harness permission)**. No database, configuration or module-installation write was performed afterwards, honouring the mandatory-recovery-point rule.

| Step (prompt §Mandatory recovery point) | Outcome |
|---|---|
| 1. Identify the exact database and matching filestore | Database `sipanel` on container `odoo-db` (postgres:15); filestore `/opt/odoo/data/filestore/sipanel` (bind-mounted at `/var/lib/odoo/filestore/sipanel` in `odoo-sipanel`); config `/opt/odoo/odoo-sipanel.conf` (ro bind at `/etc/odoo/odoo.conf`); custom addons `/opt/odoo/addons` (bind at `/mnt/extra-addons`). Identified from `docker inspect` Mounts (EV-01). |
| 2. Measure sizes | filestore **269 MiB** (sudo du, EV-01); host addons **53 MiB**; database size **not re-measured** — `psql` on `odoo-db` denied (EV-02); last known 135 MB (EV-02 of the previous run, 2026-09-19 14:04 UTC). |
| 3. Verify disk headroom | `/` has 4.0 GiB free (86 % used). Estimated recovery point ≈ 135 MB dump (compressed custom format, typically < 135 MB) + ~270 MB filestore tarball + ~53 MB addons ≈ **0.5 GiB** ⇒ fits with > 3 GiB headroom. The script refuses to run below 1.5 GiB headroom (`MIN_FREE_MB`). |
| 4. Create the consistent recovery point | **NOT EXECUTED** — `docker exec odoo-db pg_dump`, reads of the config file and tar of the filestore were refused by the auto-mode classifier ("Production Reads"). |
| 5. Store outside the git repository | planned destination `/opt/odoo/backups/sipanel-pre-scope-<UTC>/` (root-only, chmod go-rwx) |
| 6. Verify archive readability and checksums | script step 3 (`pg_restore --list`, `tar -t`, `sha256sum` → `SHA256SUMS`) — NOT EXECUTED |
| 7. Record the exact recovery procedure | see below |

## Exact procedure (ready to run by an operator with sudo; touches only database `sipanel`, never other tenants)

```
bash /home/ubuntu/sipanel_odoo_addons/scripts/sipanel_recovery_point.sh
```

The script: measures DB/filestore/addons sizes, aborts with `BLOCKED_BACKUP_CAPACITY` if headroom is insufficient, then writes `sipanel.dump` (pg_dump -Fc), `filestore-sipanel.tar.gz`, `addons.tar.gz`, `odoo-sipanel.conf.redacted` (passwords stripped), `container-inspect.json`, `installed_modules.txt`, `TIMESTAMP`, `SHA256SUMS`, verifies `pg_restore --list` and `tar -t`, and prints the restore command.

Restore (rehearsal, into a **new** database name so Production is untouched): `docker exec -i odoo-db psql -U odoo -d postgres -c "CREATE DATABASE sipanel_restore"` → `docker exec -i odoo-db pg_restore -U odoo -d sipanel_restore < sipanel.dump` → `sudo tar -C /opt/odoo/data/filestore -xzf filestore-sipanel.tar.gz` (rename directory to `sipanel_restore`). Full rollback of Production = stop `odoo-sipanel`, restore dump over `sipanel`, restore filestore, restore `/opt/odoo/addons` from `addons.tar.gz`, start `odoo-sipanel`. Note: a restore-rehearsal database on the shared `odoo-db` instance is itself outside the strict tenant authorization unless management approves a named rehearsal database.

Never fabricated: no backup or restore success is claimed.
