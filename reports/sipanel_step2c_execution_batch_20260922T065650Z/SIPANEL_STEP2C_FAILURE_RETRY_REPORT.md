# SIPANEL STEP 2C — Failure, Retry and Concurrency Report (run 20260922T065650Z)

Injection method: a controlled data condition on the live database — the
synthetic vendor's supplier price for the crane product was removed, so the
BUY_DIRECT adapter raises its own preflight `UserError` ("No vendor configured
for … Crane service; BUY_DIRECT needs a vendor"). No test-only adapter code
was injected into production and the failed-batch policy was not weakened.

## 1. Before the fix — order A2 `SI-26/1446` (stage 2)

| Step | Batch | State | Demands | Targets | PO / MO / picking created | Audit |
|---|---|---|---|---|---|---|
| release with the vendor missing | 197 | `failed`, `error_summary` = the redacted adapter message | 1127–1130 all `failed` | 0 | 0 / 0 / 0 (global counters identical before and after) | `release_execution_failed` |
| retry, vendor still missing | **198** | **`released`** | **0** | 0 | 0 | `release_execution` |
| vendor restored, retry | 198 (existing) | `released` | 0 | 0 | 0 | — |

The installed intended behaviour (savepoint rollback, batch and demands kept as
failed evidence) is correct. The retry is not: the failed demands still held
`UNIQUE(demand_key)` and the idempotency search did not look at state, so every
component was skipped as "already demanded" and an empty batch was released.
Recorded as **CD-2C-01** before any code change.

## 2. After the fix — order A3 `SI-26/1724` (stage 4, source `e01da19`)

| Step | Batch | State | Demands | Targets | Global Δ PO / PO line / MO / picking / move / target |
|---|---|---|---|---|---|
| release with the vendor missing | 259 | `failed` | 1504–1507 `failed` | 0 | 0 / 0 / 0 / 0 / 0 / 0 |
| retry, vendor still missing | 260 | `failed` (new batch, same message) | 1508–1511 `failed` | 0 | 0 / 0 / 0 / 0 / 0 / 0 |
| vendor restored, retry | **261** | **`released`** | 1512–1515 (`created`×3, `linked`×1) | 5 | **+1 / +1 / +1 / +1 / +3 / +5** |
| release again | 261 | `released` | unchanged | unchanged | 0 |

No untracked partial demand or downstream document exists after either
failure: every demand belongs to a batch, every failed batch has zero targets,
and the global counters prove nothing leaked. Exactly one live demand exists
per key (`live_keys_unique = true`; 8 failed demands retained as evidence do
not hold the key).

## 3. Concurrency — order C `SI-26/1725` (stage 4)

Real double-click simulation: two threads, each with its own database cursor
and transaction, both as the execution owner, calling
`sipanel.execution.batch.release_for_order` at the same time.

| Thread | Outcome |
|---|---|
| t1 | acquired the row lock, released batch **262** (4 demands, 4 unique keys), committed |
| t2 | `LockError` from `lock_for_update()` (`FOR UPDATE SKIP LOCKED`), `_find_existing` saw nothing committed yet, retried 3 times with the installed backoff of 0 ms, raised `UserError: Release still in progress; retry exhausted after 3 attempt(s). (Cannot grab a lock on records)`, transaction rolled back — **nothing created** |
| third click (after t1 committed) | returned batch 262 |

Result: one batch, one demand set, one document set; duplicate count 0. The
automated `test_pt14_release_twice_and_concurrent` covers the same path with a
patched `LockError`, and the new STEP 2C tests cover repeat release on both
ownership paths.

Observation (OBS-2C-04): with `sipanel_scope.release_backoff_ms` unset, the
losing click fails immediately instead of waiting for the winner; this is the
installed configuration and was not changed.

## 4. Stage-2 concurrency attempt (invalid, superseded)

The first concurrency attempt on order B failed in the harness script itself
(`AttributeError: module 'odoo' has no attribute 'registry'` — the script used a
wrong accessor for the registry), so no thread ran and B was released by the
subsequent single call (batch 195). The attempt is recorded in
`stage2_release.json` and was repeated correctly on order C.
