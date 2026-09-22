# SIPANEL Disk Capacity and Image Cleanup Report (run 20260922T105454Z)

## 1. Before

```
/dev/vda3   28G   26G   1.1G   96% /        avail = 1,159,946,240 bytes
capacity rule: need_mb=462 (db 157,269,351 + filestore 280,308,082 + addons 47,069,251 bytes)
               free_mb=1107  headroom=645 MB  < 1500 MB  ->  gate FAIL
```

Eight recovery points existed (7 SIPANEL + 1 ahanassa migration + 1 legacy dump), none touched.

## 2. Read-only Docker inventory (`evidence/docker/`)

* `docker_system_df_v_before.txt`, `docker_images_digests_before.txt`, `docker_ps_a_before.txt`,
  `containers_image_ids_before.txt` (11 containers: 5 running, 6 exited; every one inspected for its image ID).
* Images before: `odoo-custom:19-linkpreview` / `…-jdatetime-test` (same ID `653997642a6c…`, 3.38 GB, used by `odoo-shahbazi`),
  `odoo-custom:19-linkpreview-r2` (`22ec8c598145…`, 3.42 GB, used by `odoo-ahantorob`), `postgres:15` (`1b92e7a80c02…`, used by `odoo-db`),
  the untagged Odoo 19 image `1cd111414896…` (used by `odoo-sipanel`, `odoo-avizsazeh` and the 6 stopped containers),
  **`fathyb/carbonyl:latest`** (`77b3686f46a1…`, 405 MB virtual / 117,719,069 bytes content, created 2023-02-18) and
  **`browsh/browsh:latest`** (`6f64eca9946b…`, 1.29 GB virtual / 334,497,402 bytes content, created 2025-07-19).

## 3. Proof that the two images were removable

| Condition | Evidence |
|---|---|
| no running container uses them | `docker ps -a --filter ancestor=…` empty; per-container `inspect` image IDs never match (`pre_deletion_verification.txt`) |
| no stopped container uses them | same inspection over all 11 containers, 0 matches |
| no deployment configuration requires them | `grep -rIl` over `/opt`, `/home`, `/etc`, `/root`, cron and systemd units, plus process list: the only hits are Claude session transcripts, a paste cache and this run's own evidence files (`foreign_image_references.txt`); no Compose file, script, cron, service or process |
| introduced outside the SIPANEL implementation | `journalctl`: `dockerd … image pulled … docker.io/fathyb/carbonyl:latest` at 2026-09-22T09:00:49Z and `browsh/browsh:latest` at 09:01:48Z, during the STEP 2C-HARDENING test run; no SIPANEL script pulls images (`foreign_image_pull_journal.txt`); the pulling client was another Claude project on this host (`…/-home-ubuntu-work-SEO-Control-Center/…jsonl` references them) |
| no shared parent layer with any tagged image | `image_layers.txt`: 0 layers in common with every other image and with each other |

## 4. Deletion (exact image IDs, no prune)

```
docker rmi sha256:77b3686f46a16375004985b522cef8f66e27fabc4a7d80209609bbb20fdfb362   # Untagged: fathyb/carbonyl:latest, Deleted
docker rmi sha256:6f64eca9946b16f83a8f560093c4bde84205ea507fd55ecba50d5d728533b9b6   # Untagged: browsh/browsh:latest, Deleted
```

| Measure | Value |
|---|---|
| `df` available before | 1,159,315,456 bytes |
| `df` available after | 2,852,151,296 bytes |
| **bytes reclaimed** | **1,692,835,840** |
| `docker system df` after | Images 4 (all active), Containers 11 (5 active), Volumes 89 unchanged |
| containers after | `containers_image_ids_after.txt` identical to before (image IDs, status, restart counts, start times) — `CONTAINERS_UNCHANGED` |
| `odoo-sipanel` HTTP health | `GET http://127.0.0.1:8081/web/health` → 200; in-container `/web/health` → 200 |
| tenant containers restarted | none (`odoo-avizsazeh` restarts 74 / started 2026-09-03, `odoo-shahbazi` 74 / 2026-09-03, `odoo-ahantorob` 0 / 2026-09-18, `odoo-db` 0 / 2026-07-16 — unchanged) |

No `prune` command of any kind was used; no volume, container or other image was touched (the 89 local volumes reported reclaimable by Docker were left alone).

## 5. Capacity gate after cleanup

```
need_mb=462  free_mb=2720  headroom=2258 MB  >= 1500 MB  ->  gate PASS
```

## 6. Recovery points after this run

`recovery_points_after_creation.txt`: the eight previous entries unchanged, plus
`sipanel-pre-2ccloseout-20260922T111500Z` (verified: `sha256sum -c` OK for all six artefacts,
TIMESTAMP 20260922T111233Z) and `sipanel-pre-2ccloseout-20260922T105454Z`, which is **INVALID**:
two instances of the recovery script were started by mistake into that directory within the same
second (operator error in this run, log `recovery_point_closeout_INVALID_concurrent_run.log`);
its files may be interleaved. It was not deleted (recovery points are never deleted by an
implementation run) but carries an `INVALID_DO_NOT_USE.txt` marker. The owner may remove it
(116,489,664 bytes) under a separate authorisation.

Disk at the end of the run: see the closeout report and the final response.
