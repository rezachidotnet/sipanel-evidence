# SIPANEL STEP 2C-HARDENING Cleanup Report (run 20260922T083014Z)

Prefix `SIPANEL-STEP2CH-20260922T083014Z`. Scripts `pilot_2ch_2_cleanup.py`; evidence `evidence/pilot/pilot_2ch_cleanup.json`.

## Cancelled / deleted / archived

* Orders `SI-26/2094`, `SI-26/2095`: cancelled (no invoice, no done move, asserted first).
* Deleted (draft/cancelled synthetic documents): pickings 1294 (native delivery), 1295, 1296 (SIPANEL site issue) with moves 1893–1895; tasks 3148 (native anchor task, no timesheet) and 3147 (Odoo's onboarding "Welcome" task for the synthetic Sales user). No purchase order and no manufacturing order existed (no vendor, no BoM in this pilot).
* Archived: quote scopes 1905/1906; masters 800/801; products 3525–3528 (templates 2900–2903); project 135; analytic accounts 1953–1955; customer partner 3484; synthetic Sales user 2064; the STEP 2C execution-owner user 1376 (re-activated for the pilot, re-archived).

## Retained lineage (immutable by design)

Orders (cancelled, batches restrict deletion); revisions 2063, 2064, 2065 (`accepted_sealed`); 6 artifacts; generated lines 4104, 4106, 4107; batches 415, 416, 417 (`cancelled`); 5 demands (`cancelled`); 7 target links; 20 audit events; released master versions 962/963 (no archive flag). Earlier records intact: `SI-26/312`, version 115, the 11 STEP 2C batches.

## Finding 7 — synthetic users and their contacts (supported behaviour only, no SQL)

| User | State | Contact | Contact archive | User deletion |
|---|---|---|---|---|
| 1376 `…STEP2C…-exec` | archived, `share=False`, 9 groups (internal only) | 2361, no email, no phone | refused by Odoo's guard (`RedirectWarning`: "contacts linked to an active user") even though the user is archived — reproduced in a fresh transaction | NOT attempted: actor of 18 immutable audit rows and released/requested user of 13 batches; deletion would set-null or violate `actor_user_id` (required) → lineage rewrite |
| 2064 `…STEP2CH…-sales` | archived | 3483, no email, no phone | refused, same guard | NOT attempted: actor of 4 audit rows |

Neither has portal access, a login capability (archived users cannot authenticate) or an operational role (no task, no document ownership after cleanup). Both contacts were renamed with the prefix `[ARCHIVED SYNTHETIC USER]` — the audit trail stores `actor_user_id`, not names, so no immutable evidence changed.

**Exact statement: 2 active synthetic technical contacts retained** (partners 2361 and 3483). All other synthetic records: 0 active (orders not cancelled 0, quote scopes 0, masters 0, products 0, projects 0, tasks 0, analytic accounts 0, active users 0, pickings 0, purchase orders 0, MOs 0, invoices 0, live demands 0, live batches 0).

## Side effects

`mail.mail` 36 → 36; posted `account.move` 0; done stock moves 10 → 10; internal quant quantity 0; purchase orders 7 → 7 (no supplier commitment); MOs 0; pickings 13 → 13; SIPANEL parameters unchanged; other tenants untouched.
