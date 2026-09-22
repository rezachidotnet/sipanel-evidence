# SIPANEL STEP 2C — Execution Batch and Demand-Ownership Validation (run 20260922T065650Z)

| Item | Value |
|---|---|
| Verdict | **PASS_WITH_DEFECTS_FIXED** — the ownership invariant holds on the installed release path after three defects found by the live pilot were corrected |
| Target | database `sipanel`, container `odoo-sipanel` only; PostgreSQL container not restarted; no other tenant touched |
| STEP 2B-HARDENING commits | source **and** evidence: `3229813` (single commit; parent `490eb30`) — see `SIPANEL_STEP2B_CLOSEOUT_ADDENDUM.md` |
| STEP 2C source commit (code + tests) | **`e01da1973784ccfd692ac13a622707e4c3bae576`** (`e01da19`) |
| STEP 2C evidence/bundle commit | created after this report directory was built; given in the final response (this bundle cannot contain its own hash) |
| Recovery point | `/opt/odoo/backups/sipanel-pre-step2c-20260922T065650Z` (115,209,271 bytes, verified) created before the first STEP 2C database write |
| Module versions after this run | `sipanel_commercial_scope_core` 19.0.1.1.0 (unchanged) · `sipanel_sale_scope` **19.0.1.2.2** (was 1.2.1) · `sipanel_scope_execution` **19.0.1.0.1** (was 1.0.0) · `sipanel_scope_costing` 19.0.1.0.0 (unchanged) |
| Modules upgraded | `sipanel_sale_scope`, `sipanel_scope_execution` (the two whose source changed). The test runs use the established deploy path `scripts/sipanel_install_and_test.sh test`, which passes all four SIPANEL modules to `odoo -u`; core and costing were re-loaded at unchanged versions. |
| Restart | **none** (`RestartCount=0`, `StartedAt=2026-09-20T06:40:08Z` unchanged) |
| Tests | SIPANEL **214 / 0 failures** (52 + 141 + 5 + 16 by Odoo module statistics; 162 test methods) · `sale_shamsi_report` **80 / 0** · STEP 2C tag alone **8 / 0** (6 of 8 failed on the unfixed source) |
| Live pilot | 6 synthetic orders `SI-26/1445, 1446, 1447, 1724, 1725, 1726` (prefix `SIPANEL-STEP2C-20260922T065650Z`), all cancelled and cleaned; no invoice/bill posted; no email sent; no real stock consumed |
| Pushed | **no** |

## 1. Objective and method

Exercise the real installed Execution Batch release path against confirmed
quotation Scopes containing separately-billable generated Sale Lines and prove
that every component has exactly one operational demand owner:

`one component → one operational demand owner → one actual-cost source`

Method: (1) inspect the installed source and the live schema; (2) create a
verified recovery point; (3) run a fully synthetic pilot on `sipanel` in five
stages (`evidence/scripts/pilot_step2c_*.py`, all committed to the database
with JSON evidence in `evidence/pilot/`); (4) measure before changing code; (5)
fix, test, upgrade, re-verify live on fresh orders; (6) clean up.

## 2. Installed facts (Phase B) — verified vs inferred

All statements below marked **V** were verified by reading the installed source
(`/opt/odoo/addons/<module>`, identical to the repository at `3229813`) and by
querying the live database (`evidence/logs/preflight_db.json`). Statements
marked **I** are inferences.

| Item | Installed name / behaviour | |
|---|---|---|
| Execution batch | `sipanel.execution.batch` (`REL/<order>/<id>`), states `planned → validated → released / failed / cancelled`; key `UNIQUE(order_id, revision_set_hash, action_uid)`; `revision_set_hash = sha256(sorted accepted revision ids)` | V |
| Execution demand | `sipanel.execution.demand`; one per eligible physical component (`eligible_for_rollup`, `qty_kind='physical'`, mode ≠ `no_action`); `demand_key = sha256([occurrence_uid, delta_uid, execution_mode, owner])` with `delta_uid = acceptance_reference or "rev:<id>"`; states `planned/linked/created/in_progress/fulfilled/cancelled/failed` | V |
| Execution adapter | `sipanel.execution.adapter` (AbstractModel) dispatching `_adapt_<execution_mode>`: `stock_issue` → draft internal picking + move on operation type 91 (`WH/Stock → SIPANEL Site`), `buy_direct`/`equipment_service` → draft PO line for the product's seller (no RFQ sent), `manufacture` → draft MO from the normal BoM, `labour` → link project (+ anchor task if any; never a timesheet), `native_anchor_covered` → link only, `no_action` → fulfilled | V |
| `component_bridge_owner` / `native_line_owner` | `sipanel.quote.scope.component.execution_owner` (stored compute): `none` for `no_action`/customer responsibility; `native_line_owner` when `execution_mode='native_anchor_covered'`; else the master version's `anchor_owner_mode`. The registry `sipanel.execution.owner.rule` (5 rules in production: default `component_bridge_owner`; `task_global_project`/`task_in_project` and the `stock_rule` fallback → `native_line_owner`) is enforced at master release (R4) | V |
| Demand `source_key` | there is no field literally named `source_key` on the demand; the immutable source key is **`demand_key`** (readonly, derived as above). `sipanel.actual.cost.event.source_key` is the cost-side key (`make_key(model, res_id, component_type, company)`) | V |
| Release state machine | `release_for_order`: bounded retry (`sipanel_scope.release_retry_count`=3, backoff param unset → 0 ms) around `order.lock_for_update()` (`FOR UPDATE SKIP LOCKED` → `LockError`); `_find_existing` returns an existing released/planned/validated batch for the same revision set; preflight issues → batch `failed` + `UserError`; adapters run in one savepoint: any `UserError` rolls back everything they created, batch and demands stay as `failed` evidence | V |
| Project/System/Activity propagation | demand carries `project_id` (scope project or `sipanel_scope.default_project_id`=55), `system_id` (component or scope), `activity_id` (component); PO line gets `analytic_distribution` = {project analytic account, system, activity}; MO gets `project_id`; stock moves carry no analytic field in Odoo 19 (`analytic_distribution` absent on `stock.move`, `mrp.production`, `project.task`) | V |
| Retry / idempotency | second click → same batch (`_find_existing`); demand-level idempotency by `demand_key`; `IntegrityError` on a concurrent key → invalidate + return existing | V |
| Failure / rollback | savepoint rollback of adapter output; batch `failed`, demands `failed`, audit `release_execution_failed`; error text redacted (`_redact`) | V |
| Cancellation / amendment | `sale.order._action_cancel` refuses when a target is `done`, else `action_cancel_planned` → `cancel_delta` per demand (PO line qty 0, MO cancel, move cancel, otherwise `reversal_required`); `action_sipanel_release_amendment_delta` creates signed delta demands on an `amend:<rev>` batch, negative deltas reduce the latest positive demand (`reduce_planned`) | V |
| Estimate-to-Actual lineage | `sipanel.actual.projection.refresh_order` builds `sipanel.actual.cost.event` rows per target document (draft/undone documents → layer `operational`/`commitment`, inclusion `excluded_duplicate`, amount 0) keyed by `source_key`, with `sipanel.actual.allocation` per demand only when included | V |
| Production baseline | 0 batches / 0 demands / 0 targets before this run (the release path had never run live); analytic plans 80 (System) and 81 (Activity) exist with **0 accounts**; default project 55; stock-issue type 91; 9 approved cost policies; no MO and no BoM in production; `mail.mail` 36; posted moves 0 | V |
| Native route on a generated line | a `consu` product line in state `sale` launches the warehouse delivery route (`ship_only`) on confirmation unless `sipanel_sale_scope` skips it (bridge-owned generated lines) | V (measured: 0 moves for bridge, 1 move for native) |
| Kit explosion / MTO / dropship | not exercised; MTO route active, none of the pilot products used it | I (NOT_EXERCISED) |

## 3. Pilot design (Phase C)

Synthetic only, prefix `SIPANEL-STEP2C-20260922T065650Z`: analytic accounts
System 1317 (plan 80), Activity INS 1318 / MFG 1319 (plan 81); project 97
(analytic account 1320); execution-owner user 1376 (all real group gates);
products anchor-A 2644 (service, `service_tracking=no` → bridge), anchor-B 2645
(service, `task_global_project`, project 97 → native), bracket 2646 (storable),
gutter 2647 (storable, BoM 41 on coil 2648), crane 2649 (service), labour 2650
(service); vendor 2362 with a supplier price on the crane; customer 2363.

Masters: **A** (scope 557, version 663, `component_bridge_owner`): A1 bracket
`own_line`/`stock_issue` rate 2, A2 crane `own_line`/`equipment_service` fixed
1, A3 gutter included/`manufacture` rate 1, A4 labour included/`labour` fixed
8 h. **B** (scope 558, version 664, `native_line_owner`): B1 bracket
`own_line`/`native_anchor_covered` rate 2, B2 labour included/`native_anchor_covered`
fixed 8 h. Each quotation: 10 m, sealed, confirmed (acceptance sealed).

| Order | Scope / accepted revision | Purpose |
|---|---|---|
| `SI-26/1445` (A) | 1280 / 1380 → amended to 1679 | Scenario A clean release, repeat release, amendment |
| `SI-26/1446` (A2) | 1281 / 1381 | partial failure + retry **before** the fix (defect evidence) |
| `SI-26/1447` (B) | 1282 / 1382 | Scenario B **before** the fix (defect evidence) |
| `SI-26/1724` (A3) | 1547 / 1676 | partial failure + retry **after** the fix |
| `SI-26/1725` (C) | 1548 / 1677 | real two-transaction concurrency; cancellation lineage |
| `SI-26/1726` (B2) | 1549 / 1678 → amended to 1680 | Scenario B **after** the fix; native amendment |

## 4. Results

### Scenario A — component bridge owner (orders A, A3, C)

| Proof | Result | Evidence |
|---|---|---|
| projection creates exactly one generated Sale Line per own-line component | PASS — A: lines 2745 (bracket, key `1380:c4d8b4e4…`) and 2746 (crane) | stage1 |
| confirmation creates no native stock/procurement demand from a generated line | PASS — `stock_moves_from_generated_lines = 0`, no PO, no MO, no task on A/A2/A3/C | stage1, stage4 |
| release creates exactly one execution demand per component | PASS — A batch 196: demands 1123–1126 (4 physical components, 4 unique keys) | stage2 |
| immutable source key tied to revision/component | PASS — `demand_key = sha256([occurrence_uid, "rev:1380", mode, owner])`, readonly; asserted by `test_bridge_owner_…` | stage2, tests |
| downstream adapter creates or links exactly one operational record | PASS — bracket → picking 600 + move 848 (draft, 20 units); crane → PO P26164 line 164 (draft); gutter → MO WH/MO/00126 (draft, 10 m, project 97); labour → project 97 linked, no timesheet | stage2 |
| releasing again creates nothing | PASS — releases 2/3/4 all return batch 196; document counts unchanged | stage2 |
| retry after completion creates nothing | PASS — same (also A3 batch 261 and C batch 262 re-released → same batch) | stage2/4 |
| no duplicate Purchase/Stock/MRP/Project/analytic record | PASS — see `SIPANEL_STEP2C_DOUBLE_COUNTING_RECONCILIATION.md` | stage2/4 |

Note: batch 196 was released by uid 2 (the production administrator account,
which is itself an Execution Owner) because the pilot's "non-owner" probe used
that uid; the refusal for a non-owner is covered by the automated test
`test_release_creates_one_demand_per_component`. All other batches were released
by the synthetic owner 1376.

### Scenario B — native line owner (orders B, B2)

| Proof | Before fix (B) | After fix (B2) |
|---|---|---|
| native Sale Line creates the normal Odoo demand | PASS — generated line 2751 → delivery move 847 (picking 599, `confirmed`); anchor line 2750 → task 2438 | PASS — line 3338 → move 1130 (picking 788); anchor 3337 → task 2749 |
| SIPANEL links to that native demand | **FAIL (CD-2C-02)** — demand 1121 linked task 2438 (the anchor's), not move 847 | PASS — demand 1520 → `stock.move 1130 native_anchor_covered` |
| SIPANEL creates no second operational demand | PASS — no SIPANEL picking/PO/MO on B or B2 | PASS |
| generated revenue line is not an additional demand owner | PASS — one move per line, no bridge document | PASS |
| provenance Scope → revision → component → Sale Line → operational document | incomplete (wrong document) | PASS — 1549 → 1678 → component 11221 → line 3338 → move 1130 |

### C2 idempotency and concurrency (order C)

Two real transactions (two cursors, two threads, both as the execution owner)
released `SI-26/1725` simultaneously: thread 1 acquired the row lock and
released batch 262 (4 demands); thread 2 got `LockError` (`FOR UPDATE SKIP LOCKED`),
retried 3 times with the installed 0 ms backoff and raised
`UserError: Release still in progress; retry exhausted after 3 attempt(s)`,
creating **nothing**. A third click after the winner committed returned batch
262. Result: one batch, 4 unique keys, one document set.

### C3 partial failure (orders A2 before, A3 after)

| Step | Before fix (A2) | After fix (A3) |
|---|---|---|
| vendor removed → release | batch 197 `failed`, 4 demands `failed`, 0 targets, global PO/MO/picking counts unchanged (rollback works) | batch 259 `failed`, same rollback |
| retry without fixing | **batch 198 `released` with 0 demands, 0 documents (CD-2C-01)** | batch 260 `failed` again, 0 documents |
| vendor restored → retry | still batch 198: the order can never be executed | batch 261 `released`: 4 demands, 5 targets, +1 PO line, +1 MO, +1 picking, exactly once |
| release again | 198 | 261 (nothing additional) |

### C4 cancellation and amendment

* **Amendment, bridge (A):** `action_amend` on the confirmed order was refused
  before the fix by Odoo's own rule (CD-2C-03, measured in stage 3a). After
  the fix: new revision 1679 accepted through change order
  `SIPANEL-STEP2C-…-CO-A`; superseded lines 2745/2746 retained at quantity 0;
  new lines 3339 (30 units) / 3340 (1); prior artifacts intact (2); delta
  release created exactly one demand (+10, batch 264) → picking 789 / move 1131;
  signed demand for the bracket occurrence sums to 30; a second delta call
  created nothing; reconciliation problems `[]`.
* **Amendment, native (B2):** revision 1680; superseded line 3338 → 0 and its
  native move 1130 cancelled by Odoo; new line 3341 (30) → move 1132; delta
  demand 1523 (+10, native) linked move 1132; no second delivery order.
* **Cancellation (C):** batch 262 and its 4 demands `cancelled`; SIPANEL
  picking 787 / move 1127 `cancel`; MO 172 `cancel`; PO line 201 quantity 0 (PO
  stays draft); project link demand and picking demand flagged
  `reversal_required` (see OBS-2C-01); every target link retained; audit
  `order_cancel`. Nothing deleted by the cancellation.
* **Unresolved change-order cases (reported, not guessed):** a superseded
  generated line that is already invoiced or delivered is left untouched and
  flagged in the reconciliation (`test_invoiced_superseded_line_is_left_alone_and_flagged`);
  the financial settlement of that case (R-3) is a STEP 2D decision.

### C5 propagation and C6 matrix

See `SIPANEL_STEP2C_PROJECT_SYSTEM_ACTIVITY_TRACE.md` and
`SIPANEL_STEP2C_DEMAND_OWNERSHIP_MATRIX.md`.

## 5. Defects (recorded before the code change, fixed in `e01da19`)

| Id | Module | Defect (measured) | Correction | Regression test |
|---|---|---|---|---|
| **CD-2C-01** | `sipanel_scope_execution` | failed demands kept `UNIQUE(demand_key)` and the idempotency search ignored state → retry after a failed batch produced a `released` batch with **no demand and no document** (A2 batch 198); the order was stuck | partial unique index `(demand_key) WHERE state <> 'failed'` + `_live_by_key()` used by both idempotency lookups; failed batches/demands retained unchanged. Upgrade log: `Dropped CONSTRAINT sipanel_execution_demand_demand_key_unique`, index `sipanel_execution_demand_demand_key_live_unique` created | `test_retry_after_failure_creates_the_full_demand_set_exactly_once` (FAIL before: `'released' != 'failed'`) |
| **CD-2C-02** | `sipanel_scope_execution` | native-owner demand of an own-line component linked the **anchor's** task instead of its own line's delivery move (B demand 1121 → task 2438; move 847 unlinked) | `_native_line_of(demand)`: the component's own generated line when it exists, else the anchor; link only, never create | `test_native_owner_own_line_links_its_own_native_demand_and_creates_none` (FAIL before: `('stock.move', …) not found in {('project.task', …)}`) |
| **CD-2C-03** | `sipanel_sale_scope` | `_retire_superseded_projection` unlinked prior-revision lines; on a confirmed order Odoo raises *"Once a sales order is confirmed, you can't remove one of its lines … Set the quantity to 0 instead"* → every amendment of a confirmed order with generated lines was refused | when `line._check_line_unlink()` refuses, the line is neutralised (quantity 0, never deleted) — Odoo's prescription and the branch already used for consumed lines; invoiced/delivered lines still untouched and flagged | `TestAmendmentAfterConfirmation` (2 tests, ERROR before) and `test_amendment_after_release_with_generated_lines_keeps_lineage_and_adds_one_delta` |

No existing assertion was removed, bypassed or weakened. Two assertions of the
**new** tests were corrected during the run (an ORM `readonly` field does not
raise on write; cancelling released execution needs the execution owner's
environment) — both are documented in `SIPANEL_STEP2C_TEST_RESULTS.md`.

## 6. Observations for STEP 2D (not changed in this step)

| Id | Observation |
|---|---|
| OBS-2C-01 | `cancel_delta` sets `reversal_required` for `stock.picking` and `project.project` target links (else-branch) although the picking's move was cancelled and a project link has nothing to reverse — operator noise, no data effect |
| OBS-2C-02 | `cancel_delta` / `reduce_planned` act on `native_anchor_covered` targets (native-owned moves). In the pilot the superseded native move was already cancelled by the line quantity change, so nothing was reduced twice, but SIPANEL should not manipulate native-owned documents (C8-D01) |
| OBS-2C-03 | a native delta demand's `allocated_qty` is the linked move's full quantity (30), not the delta (10): the link means "covered by", not "allocated" |
| OBS-2C-04 | `sipanel_scope.release_backoff_ms` is unset (0): under real contention the losing click fails immediately with "retry exhausted" (creates nothing; the next click returns the batch). Setting a backoff is a configuration decision |
| OBS-2C-05 | cancelling an order that has released execution needs write access on demands (AccessError for sales users) — needs a governed message or an execution-owner rule |
| OBS-2C-06 | uid 2 (production administrator) is a member of the Execution Owner group |
| OBS-2C-07 | **blocker for a real STEP 2D pilot:** production analytic plans 80/81 hold no accounts; release preflight requires System and Activity, so real masters cannot be released until the business populates them |
| OBS-2C-08 | change-order settlement of an invoiced/delivered superseded line (R-3) stays open: left alone and flagged |
| OBS-2C-09 | BUY_DIRECT requires a supplier price; no BoM and no MO exist in production, so the manufacture route is installed but NOT_CONFIGURED for real products |
| OBS-2C-10 | Odoo refuses to archive the contact of the (archived) synthetic user (`RedirectWarning` even in a fresh transaction); partner 2361 (no email/phone) remains active |
| OBS-2C-11 | `scripts/sipanel_recovery_point.sh` still prints the ambiguous one-line restore; superseded by the addendum's procedure |

## 7. Operational safety

* No invoice or vendor bill posted (`account.move` posted count 0 before and after; no `account.move` for the pilot orders).
* No email sent (`mail.mail` 36 before, 36 after every stage).
* No real stock consumed (done moves 10 before and after; internal quant quantity 0; every pilot picking was draft/confirmed then cancelled and deleted).
* Product Master records unrelated to the pilot untouched; tax/accounting policies untouched; SIPANEL configuration parameters unchanged (5 owner rules, params identical to preflight).
* Other tenants: every database command named `-d sipanel` and every `docker exec` targeted `odoo-sipanel` or `odoo-db` (`psql`/`pg_dump` on `sipanel`/`postgres` only); `odoo-avizsazeh`, `odoo-shahbazi`, `odoo-ahantorob`, `odoo-db` `StartedAt`/`RestartCount` unchanged (`docker inspect`); `pg_stat_database` snapshot in `evidence/logs/pg_stat_database_after.txt`.
* Disk: 2.5 G free (91 %) at start → 2.9 G after pruning → 2.8 G (90 %) after the new recovery point and this report directory.
