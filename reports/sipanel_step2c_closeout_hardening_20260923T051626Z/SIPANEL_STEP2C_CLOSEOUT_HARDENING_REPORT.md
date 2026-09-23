# SIPANEL STEP 2C-CLOSEOUT-HARDENING Report (run 20260923T051626Z)

| Item | Value |
|---|---|
| Verdict | **PASS** — the sudo `action_seal` bypass is reproduced and closed; the recovery script is concurrency-safe and tested; the invalid recovery point is removed; STEP 2D not started |
| Baseline | `53268ef` (2C-HARDENING source), `6709dcf` (2C-HARDENING evidence), `84748b2` (2C-CLOSEOUT source) — all ancestors of HEAD; working tree clean apart from this report directory; installed trees IDENTICAL |
| Source commit (code + tests + scripts) | **`fce346b93af4da937cb3bcafa4aaca99ef8d1ef5`** (`fce346b`) |
| Evidence/bundle commit | created after this directory was built; given in the final response |
| Modules | `sipanel_sale_scope` **19.0.1.2.4** (was 1.2.3) — the only changed module; core 19.0.1.1.0, execution 19.0.1.0.2, costing 19.0.1.0.0 unchanged |
| Upgraded | `sipanel_sale_scope` (explicit `odoo -u sipanel_sale_scope`; dependents reloaded at unchanged versions; the full-suite path later passed all four as usual) |
| Restart | **none** (`RestartCount=0`, `StartedAt` 2026-09-20T06:40:08Z); `/web/health` 200 |
| Security bypass before fix | `rev.with_user(sales).sudo().action_seal()` and `order.with_user(sales).sudo().action_quotation_sent()` on another salesperson's order, `rev.with_user(plain_user).sudo().action_seal()`, and sudo + raw flags / guessed token / import / genuine transaction flag all **sealed the revision** — 7 of 11 new tests failed with "AccessError not raised" (`evidence/logs/test_sales_seal_sudo_before_fix.log`) |
| Security result after fix | all 7 paths raise `AccessError` with stored revision state, seal hash, artifacts and projection unchanged (tests 11/0; live probes 8/8 refused, `state unchanged`); authorised Sales/Estimator/Sales Manager/root paths succeed with correct `sealed_by_id`, audit actor and checksum |
| Recovery-point concurrency | flock + atomic `mkdir` reservation + INVALID marker on failure; 11/11 simulated checks; real point created through the new path |
| Invalid recovery point | `/opt/odoo/backups/sipanel-pre-2ccloseout-20260922T105454Z` removed after 8 proofs; **116,523,008 bytes reclaimed** |
| New valid recovery point | `/opt/odoo/backups/sipanel-pre-2ccloseouthard-20260923T051626Z` (verified ×6, TIMESTAMP 20260923T052249Z) |
| Disk | 2.2 G free (93 %) at start → 2.3 G after the removal → **2.1 G free (93 %)** at the end (new recovery point + test runs + this directory) |
| Tests | focused sudo tag **11 / 0** (7 / 11 failed before); all Sales-seal tests **22 / 0**; full SIPANEL **266 / 0** (52 + 167 + 5 + 42, 204 methods); `sale_shamsi_report` **80 / 0**; restore structural **21 / 21**; concurrency **11 / 11** |
| Live pilot | `SI-26/2544` sealed/sent by the plain Sales user; 8 pre-sudo probes on `SI-26/2545` refused with state unchanged; no leak in fields/PDF/portal binding/artifacts; no release/invoice/email/supplier/stock/cost |
| Retained synthetic records | 2 active synthetic technical contacts (2361, 3483), unchanged; everything else 0 active |
| Pushed | **no** |

## 1. Preflight (Section 1)

`evidence/logs/preflight.txt`: repository `/home/ubuntu/sipanel_odoo_addons`, branch `master`, HEAD `a025c2a`; the three accepted commits are ancestors; `git status` clean (only the new report directory untracked); all four module trees identical to `/opt/odoo/addons`; versions core 1.1.0 / sale_scope 1.2.3 / execution 1.0.2 / costing 1.0.0; target database `sipanel` (`current_database()`), container `odoo-sipanel` (image `1cd111414896…`, running since 2026-09-20, 0 restarts); disk 2.2 G free; 9 recovery points + the legacy dump; the invalid directory existed with its marker (contents recorded); capacity gate PASS (headroom 1,689 MB); all 11 containers with image IDs and restart counts.

## 2. Findings and corrections

| Finding | Correction | Report |
|---|---|---|
| sudo `action_seal` bypass | non-sudo permission gate for the initiating uid on revision, order and Scope | `SIPANEL_SUDO_SEAL_BYPASS_SECURITY_REPORT.md` |
| recovery-point concurrency | lock, atomic reservation, INVALID marker, tests | `SIPANEL_RECOVERY_POINT_CONCURRENCY_REPORT.md` |
| invalid recovery point | proven and removed | `SIPANEL_INVALID_RECOVERY_POINT_REMOVAL_REPORT.md` |

## 3. Sequence (Section 5)

Invalid directory removed → capacity gate PASS → concurrency-safe script written and tested in temporary directories → fresh recovery point created through the new script and verified → tests deployed alone and the bypass reproduced on the unfixed source → fix deployed, module upgraded, tests green → live pilot and cleanup → source committed (`fce346b`) → this directory and bundle → evidence commit.

## 4. Operational safety

No posted invoice or bill; no email (`mail.mail` 36 → 36); no supplier commitment (PO 7 → 7); no stock movement (done moves 10 → 10); no analytic cost (2 → 2); no execution release (batches 14 → 14, demands 35 → 35); no real customer; Taleghani (uid 2) group set identical before/after; other tenants untouched (`evidence/docker/containers_after.txt`, `evidence/logs/pg_stat_database_after.txt`).

## 5. Observations

| Id | Observation |
|---|---|
| OBS-2CCH-01 | The synthetic "unauthorised" user for the live probe was the archived STEP 2C execution-owner user 1376, temporarily re-activated with only `base.group_user` and re-archived; no new technical contact was created. |
| OBS-2CCH-02 | `_check_seal_permission` now also requires write access on `sipanel.quote.scope` (the seal syncs `current_revision_id`); every existing role that could seal before still can (Estimator, Scope Sales, Sales Manager). |
| carried | OBS-2CC-01/02/03 and the STEP 2D readiness items (see `SIPANEL_STEP2D_FINAL_READINESS_REPORT.md`). |
