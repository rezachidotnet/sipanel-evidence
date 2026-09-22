# SIPANEL STEP 2C-CLOSEOUT Cleanup Report (run 20260922T105454Z)

Prefix `SIPANEL-STEP2CCO-20260922T105454Z`; evidence `evidence/pilot/pilot_closeout_sales_seal.json` (cleanup section).

## Cancelled / archived

* Orders `SI-26/2314` (sealed by the Sales user) and `SI-26/2315` (never sealed): cancelled.
* Archived: quote scopes 2117/2118, master 865, products 3770–3772 (templates too), synthetic customer 3788, analytic account 2130 (plan 81), synthetic Sales user 2064 re-archived (with the reduced group set).

## Retained (immutable lineage that cannot be deleted safely)

* Revisions 2288 (`sent_sealed`) and 2289 (`working`, of the cancelled unsent order — sealed revisions can never be deleted, a working revision of a cancelled order is kept with its order); artifacts 2199/2200; master version 1040 (released, no archive flag); 6 audit events; the two cancelled orders themselves.
* No execution batch, demand, target, picking, purchase order, manufacturing order, task, invoice or analytic line was created by this pilot.

## Active synthetic records, stated exactly

**2 active synthetic technical contacts retained**: partners 2361 (`[ARCHIVED SYNTHETIC USER] SIPANEL-STEP2C-… Execution Owner`) and 3483 (`[ARCHIVED SYNTHETIC USER] SIPANEL-STEP2CH-… Sales User`) — contacts of archived synthetic users, no email, no phone, no portal access, no login; Odoo's supported partner-archive guard refuses to archive them and deleting the users would rewrite immutable audit lineage (STEP 2C-HARDENING cleanup report). No new technical contact was created in this run (the STEP 2C-HARDENING Sales user was reused). All other synthetic records: 0 active (orders not cancelled 0, quote scopes 0, masters 0, products 0, partners 0, analytic accounts 0, active synthetic users 0, invoices 0, pickings 0).

## Side effects

`mail.mail` 36 → 36; posted `account.move` 0; done stock moves 10 → 10; purchase orders 7 → 7; batches 14 → 14; demands 35 → 35; analytic lines 2 → 2; SIPANEL parameters unchanged; other tenants untouched.
