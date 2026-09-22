# SIPANEL Recovery-Point Pruning Report (run 20260922T065650Z)

Authorisation: the owner explicitly authorised deletion of exactly four
recovery-point directories, named below. Nothing else was authorised and
nothing else was deleted.

## 1. Before

```
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda3        28G   24G  2.5G  91% /
avail_bytes = 2,635,862,016
```

Inventory of `/opt/odoo/backups/` before pruning (bytes from `du -sb`):

| Path | Bytes | Modified (UTC) |
|---|---:|---|
| `ahanassa-migration-20260821-1644` | 24,696,190 | 2026-08-21 16:44 |
| `sipanel-before-kanban-fix-20260717-214400.dump` | 18,709,786 | 2026-07-17 21:44 |
| `sipanel-pre-scope-20260919T164558Z` (protected) | 113,663,953 | 2026-09-19 16:47 |
| `sipanel-pre-customer-output-fix-20260920T062942Z` (**target 1**) | 114,887,015 | 2026-09-20 06:30 |
| `sipanel-pre-live-fix-20260920T080013Z` (**target 2**) | 114,570,881 | 2026-09-20 08:01 |
| `sipanel-pre-layout-fix-20260920T084541Z` (**target 3**) | 114,571,705 | 2026-09-20 08:48 |
| `sipanel-pre-multipage-20260920T104900Z` (**target 4**) | 114,582,630 | 2026-09-20 10:51 |
| `sipanel-pre-translation-20260921T013000Z` (protected) | 114,611,255 | 2026-09-21 01:27 |
| `sipanel-pre-sepbill-20260921T021500Z` (protected) | 114,650,657 | 2026-09-21 06:22 |
| `sipanel-pre-2bhardening-20260922T060000Z` (protected) | 115,229,870 | 2026-09-22 05:13 |

## 2. Per-target validation (all four passed)

For each target, before deletion (`evidence/pruning/before_targets.txt`):

| Check | T1 customer-output-fix | T2 live-fix | T3 layout-fix | T4 multipage |
|---|---|---|---|---|
| `realpath -e` equals the authorised path | yes | yes | yes | yes |
| Is a directory, not a symlink | yes | yes | yes | yes |
| Contains no symlinks | 0 | 0 | 0 | 0 |
| Inside `/opt/odoo/backups/` | yes | yes | yes | yes |
| Not one of the four protected SIPANEL points | confirmed | confirmed | confirmed | confirmed |
| Owner / mode | root:root 700 | root:root 700 | root:root 700 | root:root 700 |
| mtime (UTC) | 2026-09-20 06:30:30 | 2026-09-20 08:01:51 | 2026-09-20 08:48:26 | 2026-09-20 10:51:44 |
| `TIMESTAMP` file | 20260920T062942Z | 20260920T080105Z | 20260920T084732Z | 20260920T105047Z |
| Bytes (`du -sb`) | 114,887,015 | 114,570,881 | 114,571,705 | 114,582,630 |

Contained `SHA256SUMS` (recorded verbatim before deletion):

```
T1 sipanel-pre-customer-output-fix-20260920T062942Z
ac665c38749a0fc89b637f46693a4c1b62ca173335186b0203533e3b6473352f  sipanel.dump
dcd73d2fec6b30e3e0e265af410e0e7948be5adec38af5794ff0ff5ef30ebde6  filestore-sipanel.tar.gz
40160678d848a422a3393a1dbd0fba9d6ebb9bd1895ca3152e701b380de5cdea  addons.tar.gz
2a267258222594c563af7ed99a8eacd5580f2ee68aeae9a251bede811f5327aa  installed_modules.txt
b32521f4144889aafdebb80265e7ec7dc6fc32f58cfc0f1957081482784dfe50  container-inspect.json
8fd7a7863ef6d789b91cf0741446d646356c7ac02a5009dbd0a4939832890f60  odoo-sipanel.conf.redacted

T2 sipanel-pre-live-fix-20260920T080013Z
4d79c4ab3d76dfe8fef6653f6f4e4cc9c95d38b0b064d962d48b991c0a85b20e  sipanel.dump
f4ec6442c98a9a4e1dbccb4ef728067dd0fdc9d0ebcfcf6ecc3414f6e27e8baf  filestore-sipanel.tar.gz
e28a8939a79fcff15038a874e0653a610b6af61547b8dba9d87f9d4acef2a51f  addons.tar.gz
2a267258222594c563af7ed99a8eacd5580f2ee68aeae9a251bede811f5327aa  installed_modules.txt
62b61e7aaa173b18be3d6b5cd3f35877d55bf02cfb72198580e0726d6e0df21d  container-inspect.json
8fd7a7863ef6d789b91cf0741446d646356c7ac02a5009dbd0a4939832890f60  odoo-sipanel.conf.redacted

T3 sipanel-pre-layout-fix-20260920T084541Z
e35e343af42c88395f5cb5c7052fcf6aa6fd964a36d41f8402b1f4fab63fefe9  sipanel.dump
f4ec6442c98a9a4e1dbccb4ef728067dd0fdc9d0ebcfcf6ecc3414f6e27e8baf  filestore-sipanel.tar.gz
ef3ab867ce06984cebebf623e3e3af47512623e83a38e6ab620168907df80db5  addons.tar.gz
2a267258222594c563af7ed99a8eacd5580f2ee68aeae9a251bede811f5327aa  installed_modules.txt
62b61e7aaa173b18be3d6b5cd3f35877d55bf02cfb72198580e0726d6e0df21d  container-inspect.json
8fd7a7863ef6d789b91cf0741446d646356c7ac02a5009dbd0a4939832890f60  odoo-sipanel.conf.redacted

T4 sipanel-pre-multipage-20260920T104900Z
5fb48991fe350145dfed6c30a9875c58a2c88862f93fe936c3c29b8237aba71e  sipanel.dump
1cccb77301c121f4118e42832556b4e12ec3075cd2174b632deeb33dde1139e4  filestore-sipanel.tar.gz
2116b7b7c2e717ebb5ce3fcc0ec760a9f60cebdd4f50e0fa67aa32a96268307e  addons.tar.gz
2a267258222594c563af7ed99a8eacd5580f2ee68aeae9a251bede811f5327aa  installed_modules.txt
62b61e7aaa173b18be3d6b5cd3f35877d55bf02cfb72198580e0726d6e0df21d  container-inspect.json
8fd7a7863ef6d789b91cf0741446d646356c7ac02a5009dbd0a4939832890f60  odoo-sipanel.conf.redacted
```

## 3. Deletion

Script: `evidence/scripts/prune_authorized_recovery_points.sh` (targets are
four literal absolute paths; no globs, no unresolved variables, no recursive
parent). Each target was re-validated inside the script (symlink refusal,
directory check, `realpath` equality, prefix check, inner-symlink count,
protected-list check) immediately before `rm -rf --one-file-system -- "<resolved path>"`,
and the script verified the path no longer exists afterwards. Log:
`evidence/pruning/prune_run.log`.

```
DELETED /opt/odoo/backups/sipanel-pre-customer-output-fix-20260920T062942Z   (114,887,015 bytes)
DELETED /opt/odoo/backups/sipanel-pre-live-fix-20260920T080013Z              (114,570,881 bytes)
DELETED /opt/odoo/backups/sipanel-pre-layout-fix-20260920T084541Z            (114,571,705 bytes)
DELETED /opt/odoo/backups/sipanel-pre-multipage-20260920T104900Z             (114,582,630 bytes)
```

No validation failed, so no target was skipped. `sync` was run after the
deletions.

## 4. After

```
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda3        28G   24G  2.9G  90% /
avail_bytes = 3,094,478,848
```

| Measure | Value |
|---|---:|
| Sum of `du -sb` of the four targets | **458,612,231 bytes** |
| `df` available delta (after − before) | **458,616,832 bytes** (the extra 4,605 bytes are the freed directory blocks) |

Remaining inventory (`evidence/pruning/after_df_and_inventory.txt`):

| Path | Bytes |
|---|---:|
| `ahanassa-migration-20260821-1644` | 24,696,190 |
| `sipanel-before-kanban-fix-20260717-214400.dump` | 18,709,786 |
| `sipanel-pre-scope-20260919T164558Z` | 113,663,953 |
| `sipanel-pre-translation-20260921T013000Z` | 114,611,255 |
| `sipanel-pre-sepbill-20260921T021500Z` | 114,650,657 |
| `sipanel-pre-2bhardening-20260922T060000Z` | 115,229,870 |

The four protected SIPANEL points were verified readable after pruning:
`sha256sum -c SHA256SUMS` printed `OK` for all six artefacts of each point
(24/24), and each `TIMESTAMP` file was read.

Nothing else was deleted: the two non-SIPANEL entries
(`ahanassa-migration-20260821-1644`, `sipanel-before-kanban-fix-20260717-214400.dump`)
were not authorised and were not touched.

## 5. STEP 2C recovery point created afterwards

`/opt/odoo/backups/sipanel-pre-step2c-20260922T065650Z` (115,209,271 bytes),
created by `scripts/sipanel_recovery_point.sh` **before** the first STEP 2C
database write, after the capacity check
`db 155,811,175 + filestore 279,033,032 + addons 46,826,752 bytes ≈ 459 MB; free 2,956 MB; 2956 − 459 = 2,497 ≥ 1,500 MB headroom`.
Verified by the script (`pg_restore --list`, `tar -tzf` on both archives,
SHA256 over every artefact); log `evidence/logs/recovery_point_step2c.log`,
checksums `evidence/logs/recovery_point_SHA256SUMS.txt`. Disk after creation:
2.8 G available (90 %). Seven entries now exist in `/opt/odoo/backups/`.
