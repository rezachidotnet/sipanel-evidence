# SIPANEL STEP 2C-CLOSEOUT Report (run 20260922T105454Z)

| Item | Value |
|---|---|
| Verdict | **PASS** — host capacity recovered by exact-ID image removal, OBS-2CH-01 fixed with a narrow seal service, restore neutralisation completed and structurally tested, live Sales seal/send proven; STEP 2D not started |
| Baseline | STEP 2C-HARDENING source `53268efc171c4cdb9640ade494678b601347e1ef`, evidence `6709dcfebb40348af5831fab13f2679b28a94d41` (both ancestors of HEAD; working tree was clean; installed trees IDENTICAL) |
| Source commit (code + tests + scripts) | **`84748b22ac43f6a292a5f8662d139aeca63fa653`** (`84748b2`) |
| Evidence/bundle commit | created after this directory was built; given in the final response |
| Modules | `sipanel_sale_scope` **19.0.1.2.3** (was 1.2.2) — the only module whose source changed; `sipanel_commercial_scope_core` 19.0.1.1.0, `sipanel_scope_execution` 19.0.1.0.2, `sipanel_scope_costing` 19.0.1.0.0 unchanged |
| Upgraded | `sipanel_sale_scope` (explicit `odoo -u sipanel_sale_scope`, which makes Odoo reload its dependents `sipanel_scope_execution` / `sipanel_scope_costing` at unchanged versions); the full-suite deploy path later passed all four modules to `-u` as it always does |
| Restart | **none** (`RestartCount=0`, `StartedAt` 2026-09-20T06:40:08Z); HTTP `/web/health` 200 after the image removal and at the end |
| Disk | 1.1 G free (96 %) at start → 2.7 G after image removal → **2.5 G free (91 %)** at the end (after one valid and one invalid recovery point, this report directory and test runs) |
| Images deleted | `sha256:77b3686f46a1…` (`fathyb/carbonyl:latest`), `sha256:6f64eca9946b…` (`browsh/browsh:latest`) — **1,692,835,840 bytes reclaimed**; no prune, no other image, container or volume touched |
| Recovery point | `/opt/odoo/backups/sipanel-pre-2ccloseout-20260922T111500Z` (verified) created after the capacity gate passed and before any source/database write. `…-20260922T105454Z` is an INVALID duplicate (concurrent run) left in place with a marker — see the capacity report §6 |
| Tests | focused Sales-seal tag **11 / 0** (10 / 11 failed before the fix); full SIPANEL **253 / 0** (52 + 154 + 5 + 42 by module statistics, 193 methods); `sale_shamsi_report` **80 / 0**; restore structural checks **21 / 21** |
| Live pilot | `SI-26/2314` sealed and sent by a plain Sales user (no cost/finance/execution/manager group); audit actor = that user; checksum valid; 17 spoof/leak probes refused; PDF/portal-readable data/artifact text free of cost, margin and net-revenue; no release, no invoice, no email, no supplier commitment, no stock movement, no analytic cost |
| Retained synthetic records | 2 active synthetic technical contacts (2361, 3483) — unchanged from STEP 2C-HARDENING; everything else 0 active |
| Pushed | **no** |

## 1. Preflight (Section A)

`evidence/logs/preflight.txt`: repository `/home/ubuntu/sipanel_odoo_addons`, branch `master`, HEAD `6709dcf`, both accepted commits are ancestors, `git status --short` empty, all four module trees IDENTICAL to `/opt/odoo/addons`, versions core 1.1.0 / sale_scope 1.2.2 / execution 1.0.2 / costing 1.0.0, container `odoo-sipanel` (image `1cd111414896…`, running since 2026-09-20), database `sipanel` (150 MB), 11 containers with their image IDs, 8 recovery points, disk 1.1 G free, capacity gate **FAIL** (headroom 645 MB) → Section B executed before any write.

## 2. Host capacity recovery (Section B)

See `SIPANEL_DISK_CAPACITY_AND_IMAGE_CLEANUP_REPORT.md`. After removal the gate passed (headroom 2,258 MB) and the recovery point was created.

## 3. OBS-2CH-01 — Sales seal/send (Section C)

See `SIPANEL_SALES_SEAL_SECURITY_REPORT.md`. Summary: `action_seal` now (1) verifies, as the real user, native write access on the revision and on the exact `sale.order`; (2) writes the internally computed projection (`commercial_projection_json`, `net_revenue_projection`, `fx_*`) for that one revision through `sudo()` + the process-local token `sipanel_seal_projection_service`, opened only inside `action_seal`; (3) keeps `sealed_by_id` and the audit actor as the initiating user. `write()` refuses those fields for anyone without the token (sudo, raw flag, guessed token, import, direct write). No group granted, no field-level security removed, Taleghani (uid 2) group set identical before/after (`evidence/acl/taleghani_uid2_groups_*.txt`).

## 4. Restore script completeness (Section D)

See `SIPANEL_RESTORE_NEUTRALISATION_REPORT.md` (fetchmail, payment providers/acquirers, automation rules, outgoing webhook actions, IAP tokens, mail aliases, mail servers, crons; `to_regclass()` detection; one `ON_ERROR_STOP` transaction on the rehearsal database only; 21/21 structural checks by the committed `scripts/test_restore_instructions.py`).

## 5. Recovery point and implementation (Section E)

Capacity gate PASS → recovery point created and verified → minimal file changes (`quote_scope_revision.py`, `__manifest__.py`, new `tests/test_sales_seal.py`, `tests/__init__.py`, `scripts/sipanel_recovery_point.sh`, new `scripts/test_restore_instructions.py`) → version bump → source committed first (`84748b2`) → module upgraded → no restart.

## 6. Tests and pilot (Section F)

See `SIPANEL_STEP2C_CLOSEOUT_TEST_RESULTS.md`, `SIPANEL_STEP2C_CLOSEOUT_PILOT_RESULT.json`, `SIPANEL_STEP2C_CLOSEOUT_CLEANUP_REPORT.md`.

## 7. Observations

| Id | Observation |
|---|---|
| OBS-2CC-01 | `missing_cost_count` (an integer count on the revision, no amount) is readable by Sales users; it is used by readiness messages. Not a cost figure; recorded for completeness. |
| OBS-2CC-02 | A plain Sales user still cannot *add* a Scope to a quotation (component creation writes cost snapshots). The governed division of labour is: Estimator prepares, Sales sends. Decide in STEP 2D whether Sales should add Scopes. |
| OBS-2CC-03 | The live database has 1 enabled payment provider, 1 fetchmail server, 4 IAP accounts and 34 active crons — the rehearsal neutralisation now covers all of them; nothing was changed live. |
| OBS-2CC-04 | Operator error in this run started two recovery-point scripts into the same directory; the invalid directory is marked and reported, not deleted. The script itself does not refuse an existing `DEST`; adding such a refusal is recommended for STEP 2D. |
| carried | OBS-2C-04/07/08/09, OBS-2CH-02 (see the readiness report). |

## 8. Operational safety

No posted invoice or bill (posted moves 0); no email (`mail.mail` 36 → 36 across tests, pilot and cleanup); no supplier commitment (purchase orders 7 → 7); no stock movement (done moves 10 → 10); no project/analytic cost (analytic lines 2 → 2); no execution release (batches 14 → 14, demands 35 → 35); no real customer (synthetic partner archived); other tenants untouched (`containers_after.txt`, `pg_stat_database_after.txt`; every command targeted `sipanel`, `odoo-sipanel` or `odoo-db`).
