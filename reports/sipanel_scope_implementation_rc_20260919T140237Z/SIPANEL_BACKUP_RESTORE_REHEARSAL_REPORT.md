Run sipanel_scope_implementation_rc_20260919T140237Z · Verdict: BLOCKED_NOT_ISOLATED · Status: no module was written, installed or tested in this run; nothing below is a PASS.

# SIPANEL — Backup / Restore Rehearsal Report

## Status of this run

**NOT_RUN.** No backup was taken and no restore was performed. There is no isolated target on which a rehearsal could lawfully run (BLOCKED_NOT_ISOLATED.md), and taking a fresh Production backup is a Production action outside this run's authority.

## What exists (inventory only, nothing opened or verified)

| Item | Observation | Verification state |
|---|---|---|
| Scheduled SIPANEL backup | none evidenced (Readiness §6.1, TV-24) | EVIDENCE-DATED; not re-verified this run (host cron listing not read) |
| Generic dump `/opt/odoo/backups/sipanel-before-kanban-fix-20260717-214400.dump` | root-owned, 2026-07-17, ~18.7 MB | listed only; not opened; too old to be a recovery point |
| Manual recovery points under `/home/ubuntu/sipanel_audit/recovery/` | `product_master_cutover_20260916T163338Z`, `test_transaction_cleanup_20260918_…`, `legacy_l1_cleanup_20260918_…`, `final_legacy_cleanup_20260918T083120Z` | directory names only; contents not inspected; integrity unknown |
| Rehearsal restore of 2026-09-15 | produced database `sipanel_staging_rehearsal` (111 MB) and container `odoo-sipanel-staging` (stopped since 2026-09-15 19:45 UTC) on the **same host and PostgreSQL instance** | this run did not verify its integrity; it is stale versus Production (EV-02: product master 2026-09-16 02:56 vs 2026-09-18 08:39; sale orders 2026-09-05 vs 2026-09-18) |

Conclusion: B-07 ("scheduled backup, restore PASS, separate Clone capacity") remains open. A restore that once succeeded on the Production host does not satisfy Readiness §6.3, which requires the restore to succeed on an isolated environment and pass DB/filestore/application smoke tests.

## Required rehearsal procedure (PT-30) — for the next authorized run on a separate host

1. Backup set (Readiness §6.3): consistent `pg_dump` of `sipanel` + matching filestore + custom addon source checksums (`/opt/odoo/addons` is not git-tracked, SV-20) + dependency manifest + config references without secrets + module version list (EV-04) + checksum manifest + retention/off-host policy + named owner and alert recipient.
2. Transfer with SHA256 verification (Runbook A.4).
3. Restore on the isolated host (Runbook A.5), neutralize (A.6), start (A.7).
4. Compare against the capture record:
   - row counts for `res_partner` (count only), `product_template`, `product_product`, `sale_order`, `sale_order_line`, `account_move`, `stock_move`, `mrp_production`, `ir_attachment`;
   - SHA256 of a sample of filestore attachments referenced by `ir_attachment.store_fname` equals the source hashes;
   - trial balance / posted move totals equal on both sides (ledger equality);
   - `database.uuid` and max write dates recorded;
   - after the sipanel_* modules are installed on the clone: Scope revision hashes and sent-artifact hashes survive a second backup/restore cycle (PT-30 invariant).
5. Confirm no live integration: no mail leaves, no cron runs, payment providers disabled, portal reachable only on the clone hostname.
6. Record: capture timestamp, restore timestamp, durations (no target threshold — TBE), operator, discrepancies and disposition.

## Acceptance criteria

PT-30 is PASS only when every comparison in step 4 is equal or every difference is explained and accepted by the infrastructure owner, and step 5 shows zero live-integration events. "Backup created" alone is insufficient (Readiness §6.3).

## Result

NOT_RUN. Owner and schedule of the first rehearsal: TBE.
