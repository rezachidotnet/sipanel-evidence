# SIPANEL Recovery Point Inventory (STEP 2B-HARDENING, run 20260922T060000Z)

Taken **before** the first database write of this run, as required.

## 1. Disk before

```
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda3        28G   24G  2.6G  91% /
free_mb = 2642
```

## 2. Existing recovery points (none deleted)

| Path | Size | TIMESTAMP | Modified |
|---|---:|---|---|
| `/opt/odoo/backups/ahanassa-migration-20260821-1644` | 24M | — | 2026-08-21 16:44:47 |
| `/opt/odoo/backups/sipanel-before-kanban-fix-20260717-214400.dump` | 18M | (file) | 2026-07-17 21:44:07 |
| `/opt/odoo/backups/sipanel-pre-scope-20260919T164558Z` | 109M | 20260919T164558Z | 2026-09-19 16:47:06 |
| `/opt/odoo/backups/sipanel-pre-customer-output-fix-20260920T062942Z` | 110M | 20260920T062942Z | 2026-09-20 06:30:30 |
| `/opt/odoo/backups/sipanel-pre-live-fix-20260920T080013Z` | 110M | 20260920T080105Z | 2026-09-20 08:01:51 |
| `/opt/odoo/backups/sipanel-pre-layout-fix-20260920T084541Z` | 110M | 20260920T084732Z | 2026-09-20 08:48:26 |
| `/opt/odoo/backups/sipanel-pre-multipage-20260920T104900Z` | 110M | 20260920T105047Z | 2026-09-20 10:51:44 |
| `/opt/odoo/backups/sipanel-pre-translation-20260921T013000Z` | 110M | 20260921T012651Z | 2026-09-21 01:27:34 |
| `/opt/odoo/backups/sipanel-pre-sepbill-20260921T021500Z` | 110M | 20260921T062120Z | 2026-09-21 06:22:05 |
| **total** | **807M** | | 9 entries |

**No recovery point was deleted in this run.** Pruning still needs explicit
target-level authorization and has not been given.

## 3. Capacity decision

The recovery-point script refuses to run unless free space exceeds the required
size plus 1500 MB of headroom:

```
db_bytes=155,860,327  filestore_bytes=279,033,032  addons_bytes=46,896,260
need_mb ≈ 459        free_mb = 2642
2642 − 459 = 2183 ≥ 1500  →  safe to proceed
```

Capacity was sufficient, so the run continued. Had it not been, the run would
have stopped before any database write.

## 4. Recovery point created

```
/opt/odoo/backups/sipanel-pre-2bhardening-20260922T060000Z
```

Verified by the script: `pg_restore --list` on the dump, `tar -tzf` on both
archives, then SHA256 over every artefact.

| Artefact | SHA256 |
|---|---|
| `sipanel.dump` | `66572e581b9b304206c06802bf4be6effaa58bc3f3f73ae2345dfa7e9882fdb6` |
| `filestore-sipanel.tar.gz` | `cd12a83e3f9b008ffeb9bf513a1e53a9ce7e9a5091d4947316336a417c35cc23` |
| `addons.tar.gz` | `a79197af4c05fceb6d58f00b127519bbc375108febd4aefd706520823a8f6bf8` |
| `installed_modules.txt` | `966d6d34fe20956de5e5f1a78ae6857fdaea7015062a48a73123887243b668db` |
| `container-inspect.json` | `62b61e7aaa173b18be3d6b5cd3f35877d55bf02cfb72198580e0726d6e0df21d` |
| `odoo-sipanel.conf.redacted` | `8fd7a7863ef6d789b91cf0741446d646356c7ac02a5009dbd0a4939832890f60` |

Also copied to `evidence/logs/recovery_point_SHA256SUMS.txt`. The recovery point
itself is **not** in the bundle: it contains a full database dump and filestore.

## 5. Restore

```
docker exec -i odoo-db psql -U odoo -d postgres -c "CREATE DATABASE sipanel_restore"
docker exec -i odoo-db pg_restore -U odoo -d sipanel_restore \
  < /opt/odoo/backups/sipanel-pre-2bhardening-20260922T060000Z/sipanel.dump
sudo tar -C /opt/odoo/data/filestore -xzf \
  /opt/odoo/backups/sipanel-pre-2bhardening-20260922T060000Z/filestore-sipanel.tar.gz
```

## 6. Disk after

Recorded at the end of the run, after the recovery point and the report bundle:
see `SIPANEL_STEP2B_HARDENING_REPORT.md` §"Operational safety". The filesystem
remains the most pressing housekeeping item: **10 recovery points now exist**,
eight of them SIPANEL points of ~110 MB each, on a filesystem above 90 %.

Recommended (needs authorization, not actioned): retain the most recent two
SIPANEL points plus `sipanel-pre-scope-20260919T164558Z` as the pre-implementation
baseline, and remove the four intermediate 2026-09-20 points, recovering ~440 MB.
