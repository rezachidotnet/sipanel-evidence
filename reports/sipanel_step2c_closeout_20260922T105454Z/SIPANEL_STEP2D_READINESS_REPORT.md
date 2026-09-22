# SIPANEL STEP 2D Readiness Report (after STEP 2C-CLOSEOUT, 2026-09-22)

STEP 2D (business configuration and the real business pilot) was **not** started. Code-side, STEP 2A–2C and their hardening/closeout passes are complete and accepted; the items below are what still stands between the installed system and a real pilot.

| # | Blocker / decision | Owner | Status |
|---|---|---|---|
| 1 | Analytic accounts in the production plans 80 (System) and 81 (Activity): release preflight requires them; the plans hold none (OBS-2C-07) | business / accounting | **blocking** |
| 2 | Change-order settlement of a superseded generated line that is already invoiced or delivered (R-3 / OBS-2C-08): currently left untouched and flagged | business + finance | **blocking for amendments after invoicing** |
| 3 | Vendors (supplier prices) and BoMs for real products: BUY_DIRECT needs a seller, MANUFACTURE needs a BoM; none exist in production (OBS-2C-09) | purchasing / production | blocking for those routes only |
| 4 | Release backoff `sipanel_scope.release_backoff_ms` unset: a concurrent second click fails immediately with "retry exhausted" (OBS-2C-04) | operations | decision |
| 5 | Sales users adding Scopes to quotations (OBS-2CC-02): today the Estimator prepares and Sales sends | management | decision |
| 6 | Disk headroom: 2.5 G free (91 %) after this run; Docker reports 5.3 GB of images and 1.5 GB of volumes as reclaimable (all attached to existing containers or unused volumes — needs explicit authorisation); invalid duplicate recovery point `sipanel-pre-2ccloseout-20260922T105454Z` (116 MB) may be removed | owner | recommended before STEP 2D test runs |
| 7 | Recovery script should refuse an existing `DEST` (OBS-2CC-04) | implementation | recommended |
| 8 | Two synthetic technical contacts remain active (2361, 3483) — cosmetic, cannot be archived through supported behaviour | — | informational |

Ready: ownership invariant proven on both paths; demand provenance immutable; Native Owner boundary enforced; governed Sales cancellation and Sales seal/send without cost visibility; invoice provenance guard; pricelist fail-closed; safe, complete restore rehearsal procedure; recovery-point discipline; 333 automated tests green.
