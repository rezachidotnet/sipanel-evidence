Run sipanel_scope_production_implementation_20260919T145639Z · Verdict: BLOCKED_BEFORE_DATABASE_WRITE · Status: SOURCE WRITTEN AND STATICALLY CHECKED — NOT INSTALLED, NOT RUNTIME VALIDATED (see evidence/EV-02).

# SIPANEL — Implementation Log (chronological, UTC 2026-09-19)

| # | Step (prompt sequence) | Action | Result |
|---|---|---|---|
| 1 | Revalidate preflight / target identity | `hostname`, `docker ps -a`, `docker inspect` mounts, `free`, `df`, `sudo du` filestore, `docker context ls` | host 194.5.206.76 = Production; `odoo-sipanel` Up; filestore 269 MiB; disk 4.0 GiB free; RAM ~500 MiB available (EV-01) |
| 2 | Mandatory recovery point | `docker exec odoo-db psql/pg_dump …`, `sudo sed` config, `sudo tar` filestore | **DENIED by the Claude Code auto-mode classifier ("Production Reads")** three times (EV-02). Recovery point NOT created ⇒ no DB write allowed afterwards. Script `scripts/sipanel_recovery_point.sh` written for operator execution. |
| 3 | Authorization record | `SIPANEL_IMPLEMENTATION_POLICY_APPROVAL_RECORD.md` | written; statutory validation still required |
| 4 | Verify installed APIs | `docker create` + `docker cp` of image 1cd111414896 source (no container started); grep of `lock_for_update`, `models.Constraint/UniqueIndex`, `sale_management` portal route/JS/template, `product.value`, `stock.move.value`, `stock.reference`, `uom._compute_quantity`, `sale.order` hooks, `_select_seller`, `_bom_find`, `is_storable` valuation, `group_ids`, `Environment` mapping, `_render_qweb_pdf` | all anchors confirmed; corrections: `env.get` → membership check; storable products required for valuation |
| 5 | Module skeletons and manifests | 5 modules, manifests, `migrations/19.0.1.0.0/README.md`, security folders | written |
| 6 | Slice A — foundations | `sipanel_commercial_scope_core` models, security (4 groups, ACL, rules), views, settings, tests (`test_tools`, `test_scope_lifecycle`, `test_recipe_validation`) | written; tests NOT RUN |
| 7 | Slice B — quotation and estimation | `sipanel_sale_scope` aggregate/revision/component engine, artifacts, waivers, hooks, 7 wizards, views, tests (`test_quote_engine`) | written; tests NOT RUN |
| 8 | Slice C — optional/provisional/portal sealing | governed transition, controller override, portal template + JS patch, section guards, tests (`test_governance`, `test_security`) | written; tests NOT RUN |
| 9 | Static verification | py_compile (all files), XML parse, manifest data existence, ACL model refs, `%(…)d`/`ref` resolution, stubbed-odoo import of every package incl. tests | passed after: manifest load-order fix (wizard actions before scope views), psycopg2 stub, removal of an invalid `project_id` field on the revision (EV-03) |
| 10 | Slice D — controlled execution | `sipanel_scope_execution` owner registry (+5 default rules), batch with bounded LockError retry and atomic savepoint, demands/targets with unique keys, 7 adapters, amendment delta, cancel guard, tests (`test_release`) | written; tests NOT RUN |
| 11 | Slice E — actual cost and reporting | `sipanel_scope_costing` policies (9 draft rows), event projection, allocations, SQL variance view, inactive cron, tests (`test_actuals`) | written; tests NOT RUN |
| 12 | Demo fixture | `test_addons/sipanel_scope_demo` C9 master V1 + pilot smoke test | written; NOT installed |
| 13 | PT-01…PT-32, pilot, security, regression, install/upgrade, rollback rehearsal | — | **NOT EXECUTED** (blocked at step 2) |
| 14 | Independent code review (forked reviewer vs. extracted Odoo 19 source) | findings in `reports/REVIEW_FINDINGS_fork.md` | see §Review below |
| 15 | Commit, bundle | local git commits; `SIPANEL_PRODUCTION_IMPLEMENTATION_BUNDLE.zip` + sha256 | see release manifest |

## Restart / tenant statement

`odoo-sipanel` was **not** restarted. `odoo-db` and every other tenant container were not touched. No command read or wrote databases ahanassa, avizsazeh, shahbazi or any other database. `/opt/odoo/addons` unchanged.

## Review

An independent forked reviewer compared the source with the extracted Odoo 19 build (`evidence/EV-04_CODE_REVIEW_FINDINGS.md`, 20 findings). Disposition before commit:

| # | Severity | Finding | Fix applied |
|---|---|---|---|
| 1 | BLOCKER | `Environment.get()` does not exist | membership check `'model' in self.env` (scope.py, scope_version.py) |
| 2–3 | BLOCKER | `copy_data({'occurrence_key'/'occurrence_uid': False})` breaks NOT NULL defaults | key popped after copy_data; set only when keeping uids (scope_version.py, quote_scope_revision.py, split_move.py) |
| 4 | BLOCKER | `UNIQUE(occurrence_uid)` contradicts amendment lineage | `UNIQUE(revision_id, occurrence_uid)` |
| 5 | BLOCKER | `write({'state': 'draft'})` on a released version not refused | any `state` write outside the release transaction raises |
| 6 | BLOCKER | second-cursor lock tests raise in the wrong place | `patch.object(..., 'lock_for_update', side_effect=LockError)` in both tests |
| 7 | HIGH | outer savepoint rolled back the FAILED batch record | lock without savepoint; savepoint only around demand creation (IntegrityError retry) and adapters |
| 8 | HIGH | `export_data` needs `base.group_allow_export` | granted to the sales test user |
| 9 | HIGH | price_unit rounding vs. oracle `places=2` | `delta=0.5` / `delta=0.02` tolerances; taxes cleared on the anchor in fixtures |
| 10 | HIGH | negative delta cancelled the original demand | `reduce_planned()` on the latest positive delta (draft targets reduced; cancelled only at zero) + test adjusted |
| 11 | MEDIUM | fake `__export__` xids in import tests | real xid from `export_data(['id'])` |
| 12 | MEDIUM | `_make_master` rebinds class attributes | attributes bound only for the default code |
| 13 | MEDIUM | fixture products not storable | `is_storable=True` for consumables in the shared fixture and coil |
| 14 | MEDIUM | OFFERED scope qty overwritten on recompute | stored `offered_scope_qty` used by the compute |
| 15 | MEDIUM | `note_reviewed` never reset on stale | computed reset in `_compute_note_stale` |
| 16 | LOW | chained assertion | rewritten |
| 17 | LOW | revenue events `unpolicied` | `unpolicied` only when `policy_missing` |
| 18 | LOW | invalid `hr.expense` states | `approved/posted/in_payment/paid` |
| 19 | LOW | HTML stored as PDF in test mode | non-pdf render stored as `portal_html` with `text/html` |
| 20 | LOW | `@api.depends('id')` | removed |

Static checks re-run after the fixes: py_compile OK, XML OK (44 files), stubbed import OK (EV-03 procedure). Runtime validation still NOT EXECUTED.
