# SIPANEL STEP 2C-HARDENING Report (run 20260922T083014Z)

| Item | Value |
|---|---|
| Verdict | **PASS** — all four review findings corrected, proven by behavioural tests (17/20 failed on the unfixed source) and a minimal live pilot |
| Started from | STEP 2C source `e01da1973784ccfd692ac13a622707e4c3bae576`, evidence `5dc0f41087fe5b8bdef8f5de9c9d0aaa101c16cb` (both verified as commits; HEAD was `5dc0f41`, working tree clean, installed trees IDENTICAL to the repository) |
| Source commit (code + tests + script) | **`53268efc171c4cdb9640ade494678b601347e1ef`** (`53268ef`) |
| Evidence/bundle commit | created after this directory was built; given in the final response |
| Modules | `sipanel_scope_execution` **19.0.1.0.2** (was 1.0.1) — the only module whose source changed; `sipanel_commercial_scope_core` 19.0.1.1.0, `sipanel_sale_scope` 19.0.1.2.2, `sipanel_scope_costing` 19.0.1.0.0 unchanged |
| Upgraded | `sipanel_scope_execution` (via the established test/deploy path `scripts/sipanel_install_and_test.sh test`, which passes all four modules to `odoo -u`; the other three re-loaded at unchanged versions) |
| Restart | none (`RestartCount=0`, `StartedAt` 2026-09-20T06:40:08Z) |
| Recovery point | `/opt/odoo/backups/sipanel-pre-2chardening-20260922T083014Z` (verified; capacity rule 461 MB needed, 2,839 MB free, headroom 2,378 ≥ 1,500 MB); no recovery point pruned or overwritten (7 entries before, 8 after) |
| Tests | SIPANEL **240 / 0 failures** (52 + 141 + 5 + 42 by module statistics, 182 methods); hardening tag **20 / 0** (17 / 20 failed before); `sale_shamsi_report` **80 / 0** |
| Live pilot | orders `SI-26/2094` (bridge, owned by a synthetic Sales user) and `SI-26/2095` (native); 32 spoof probes all refused; Sales cancellation succeeded with the Sales user as audit actor; native move untouched by SIPANEL; 0 duplicates; no invoice/bill/email/real stock; no supplier commitment (no PO at all) |
| Active synthetic records remaining | **2 active synthetic technical contacts retained** (2361 and 3483, the contacts of two archived synthetic users; see `SIPANEL_STEP2C_HARDENING_CLEANUP_REPORT.md`). Everything else: 0 |
| Pushed | **no** |

## 1. Findings and corrections

| # | Finding | Correction (`53268ef`) | Report |
|---|---|---|---|
| 1 | `demand_key` etc. were `readonly=True` only; ORM/RPC/sudo/import writes succeeded | engine token on `create`, immutable provenance set on `write`, engine token for state, `unlink` refused | `SIPANEL_EXECUTION_DEMAND_IMMUTABILITY_REPORT.md` |
| 2 | `cancel_delta`/`reduce_planned` cancelled or reduced native-owned targets; `reversal_required` came from an else-branch | native links observed only; bridge drafts withdrawn; `reversal_required` = executed-target classification; idempotent | `SIPANEL_NATIVE_OWNER_CANCELLATION_BOUNDARY_REPORT.md` |
| 3 | `scripts/sipanel_recovery_point.sh` printed the unsafe one-line restore | safe rehearsal procedure printed by the script; `restore-instructions` mode; structurally tested | `SIPANEL_RECOVERY_SCRIPT_CORRECTION_REPORT.md` |
| 4 | Sales user cancelling their own order got `AccessError` (direct demand writes) | order permission checked first, then a narrow sudo+token service on that order's batches; actor preserved | `SIPANEL_SALES_CANCELLATION_SECURITY_REPORT.md` |
| — | evidence bundle omitted `test_step2c.py` from the diff; "zero active synthetic records" was wrong | full diff `3229813..53268ef` with new files; exact statement of retained contacts | `SIPANEL_STEP2C_EVIDENCE_COMPLETENESS_REPORT.md`, cleanup report |

## 2. Preflight (before any database write)

`git status --short` empty; HEAD `5dc0f41`; `git cat-file -t` = commit for both STEP 2C hashes; `diff -rq` repo vs `/opt/odoo/addons` IDENTICAL for all four modules; disk 2.8 G free (90 %); 7 recovery points (none touched); capacity rule passed and the recovery point was created and verified (`evidence/logs/recovery_point_2ch.log`, SHA256SUMS inside the point).

## 3. Answers to the review questions

* **Do all Demand create/write provenance spoof attempts fail?** Yes. Tests: 8 immutability tests; live: 32 probes (exec-owner, sudo, raw context flag, guessed token, import context, engine token on immutable fields, same-value writes of all 16 immutable fields, 3 forged creates, unlink, Sales writes/cancels) all `AccessError`, stored values unchanged, demand count unchanged.
* **Can Sales cancel an authorised order without general Demand write access?** Yes. Live: `SI-26/2094` (user_id = synthetic Sales user) cancelled by that user; `has_access` write/create/unlink on demands = False/False/False; audit `execution_cancel` actor = the Sales user. Unauthorised user, other order, forged context: refused.
* **Do Native Owner documents remain untouched by SIPANEL cancellation/reduction?** Yes. Live: native delivery move 1893 stayed `confirmed`/20 through two batch cancellations; it became `cancel` only when Odoo cancelled the order. Tests spy on `stock.move._action_cancel` and `write(product_uom_qty)` from `adapters.py`: zero calls for native targets, including the amendment reduction.
* **Does Bridge Owner cancellation still work?** Yes. Live: SIPANEL pickings 1295/1296 and moves 1894/1895 cancelled, demands cancelled, `reversal_required` False everywhere (nothing executed), idempotent on repeat.
* **Restore script corrected?** Yes, in the script itself; 12/12 structural checks pass.
* **Full diff includes `test_step2c.py`?** Yes (`A addons/sipanel_scope_execution/tests/test_step2c.py`, 1 `+++` header), plus `test_step2c_hardening.py`.

## 4. Observations (not changed in this pass)

| Id | Observation |
|---|---|
| OBS-2CH-01 | a plain Sales user (`group_scope_sales` without Cost & Margin Viewer) cannot seal a quotation on send: `action_seal` writes `net_revenue_projection`, a `COST_GROUP` field → `AccessError`. Pre-existing; found while building the Sales fixture (the pilot/tests therefore let the estimator seal and make the order the Sales user's document). Needs a decision for STEP 2D. |
| OBS-2CH-02 | Odoo's `res.partner` archive guard refuses to archive the contact of an archived user even in a fresh transaction (`RedirectWarning`); synthetic users therefore leave an active technical contact each (see cleanup report). |
| OBS-2CH-03 | `_action_cancel` now requires `check_access('write')` on the order; users who could previously cancel through a workflow that bypassed write access (none known) would be refused. |
| carried | OBS-2C-03/04/07/08/09 from STEP 2C remain (native delta allocated_qty semantics, release backoff unset, empty analytic plans 80/81, change-order settlement R-3, no BoM/vendor for real products). |

## 5. Operational safety

No invoice or bill posted (0 posted moves before/after); no email (`mail.mail` 36 → 36 through tests, pilot and cleanup); no real stock consumed (done moves 10 → 10, internal quants 0); no supplier commitment (purchase orders 7 → 7, none for the pilot); SIPANEL parameters unchanged; other tenants untouched (every command targeted `-d sipanel`, `odoo-sipanel` or `odoo-db`; `pg_stat_database` snapshot `evidence/logs/pg_stat_database_after.txt`). Disk at the end: see the final response.
