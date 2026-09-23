# SIPANEL STEP 2D Final Readiness Report (after STEP 2C-CLOSEOUT-HARDENING, 2026-09-23)

Code-side, STEP 2A–2C including hardening, closeout and closeout-hardening are complete: ownership invariant on both paths, immutable demand provenance, Native Owner boundary, governed Sales cancellation, Sales seal/send without cost visibility (now safe against pre-sudoed calls), invoice provenance guard, pricelist fail-closed, safe and complete restore rehearsal procedure, concurrency-safe recovery points, 346 automated tests green. STEP 2D was **not** started.

| # | Blocker / decision before the real business pilot | Owner | Status |
|---|---|---|---|
| 1 | Analytic accounts in production plans 80 (System) and 81 (Activity) — release preflight requires them; none exist (OBS-2C-07) | business / accounting | **blocking** |
| 2 | Change-order settlement of an invoiced/delivered superseded generated line (R-3 / OBS-2C-08): currently left untouched and flagged | business + finance | **blocking for amendments after invoicing** |
| 3 | Supplier prices and BoMs for real products (BUY_DIRECT / MANUFACTURE routes) (OBS-2C-09) | purchasing / production | blocking for those routes |
| 4 | `sipanel_scope.release_backoff_ms` unset (OBS-2C-04) | operations | decision |
| 5 | Whether Sales users may add Scopes themselves (today: Estimator prepares, Sales sends) (OBS-2CC-02) | management | decision |
| 6 | Disk: 2.1 G free (93 %). Docker still reports 5.3 GB of images (all attached to containers) and 1.5 GB of unused volumes as reclaimable; `/tmp` holds ~1.8 GB of ahanassa backups and an older 432 MB Claude scratchpad — all outside SIPANEL authorisation | owner | recommended before STEP 2D test runs (each full SIPANEL test run needs ~0.5 GB transient) |
| 7 | Two synthetic technical contacts remain active (2361, 3483) — cosmetic | — | informational |

Removed since the previous readiness report: the recovery-script concurrency hardening (done) and the invalid recovery point (removed).
