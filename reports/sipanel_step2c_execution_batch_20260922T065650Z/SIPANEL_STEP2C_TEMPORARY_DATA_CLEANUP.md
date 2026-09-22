# SIPANEL STEP 2C — Temporary Data Cleanup (run 20260922T065650Z)

Scripts: `evidence/scripts/pilot_step2c_5_cleanup.py`,
`…5b_cleanup_followup.py`, `…5c_welcome_task.py`; evidence
`evidence/pilot/stage5_cleanup.json`, `stage5b_cleanup_followup.json`,
`stage5c_welcome_task.json`. Prefix of every synthetic record:
`SIPANEL-STEP2C-20260922T065650Z`.

## 1. Cancelled

All six pilot orders (`SI-26/1445, 1446, 1447, 1724, 1726` in this step;
`SI-26/1725` earlier in stage 4) were cancelled through the execution owner
(`action_cancel` → `action_cancel_planned`), which cancelled every released
batch and demand and their planned documents. Safety assertions before
cancelling: no invoice for the orders, no `done` move.

## 2. Deleted (draft or cancelled synthetic operational documents, deletion safe)

| Model | Records |
|---|---|
| `stock.picking` | 599, 600, 786, 787, 788, 789 (all `cancel` at deletion) with moves 847, 848, 1124, 1127, 1130, 1131, 1132 |
| `mrp.production` | 126, 171, 172 (cancelled, never started) |
| `purchase.order` | P26164 (164), P26200 (200), P26201 (201) — draft, cancelled, deleted; never sent |
| `project.task` | 2438, 2749 (native anchor tasks, no timesheets) and 2437 (Odoo's onboarding "Welcome …" task for the synthetic user) |
| `mrp.bom` | 41 |
| `product.supplierinfo` | 97 (removed during the pilot), 120 |

## 3. Archived (referenced by retained lineage, cannot be deleted safely)

| Model | Records |
|---|---|
| `sipanel.quote.scope` | 1280, 1281, 1282, 1547, 1548, 1549 |
| `sipanel.scope` (masters) | 557 (A), 558 (B) |
| `product.product` / `product.template` | 2644–2650 / 2019–2025 |
| `res.partner` | 2362 (vendor), 2363 (customer) |
| `res.users` | 1376 (execution owner) |
| `project.project` | 97 |
| `account.analytic.account` | 1317, 1318, 1319 (plans 80/81), 1320 (project account) |

## 4. Retained, and why

| Model | Records | Reason |
|---|---|---|
| `sale.order` (state `cancel`) | 1445, 1446, 1447, 1724, 1725, 1726 | `sipanel.execution.batch.order_id` is `ondelete=restrict`; sealed revisions hang off the orders; `sale.order` has no archive flag |
| `sipanel.quote.scope.revision` (all `accepted_sealed`) | 1380, 1381, 1382, 1676, 1677, 1678, 1679, 1680 | sealed content is immutable by design |
| `sipanel.quote.scope.artifact` | 16 (1229–1234, 1517–1526) | sealed artifacts |
| generated `sale.order.line` | 2745, 2746, 2748, 2749, 2751, 3332, 3333, 3335, 3336, 3338, 3339, 3340, 3341 | lines of confirmed-then-cancelled orders; Odoo forbids deletion |
| `sipanel.execution.batch` | 195, 196, 198, 261, 262, 263, 264, 265 `cancelled`; 197, 259, 260 `failed` | release evidence and lineage (`ondelete=restrict` chain) |
| `sipanel.execution.demand` | 30 (18 cancelled, 12 failed) | lineage; failed demands are the CD-2C-01 evidence |
| `sipanel.execution.target` | 22 | lineage (their target documents were deleted where draft; `target_record().exists()` handles that) |
| `stock.reference` | `SIPANEL/SI-26/1445/a72acd2b`, `…/1724/ce7391aa`, `…/1725/24bb178c` | referenced by targets (`ondelete=restrict`) |
| `sipanel.scope.audit.event` | 43 rows of this pilot (seal, accept, amend, release, failure, cancel …) | required audit events |
| `sipanel.scope.version` | 663, 664 (`released`) | a released master version has no archive flag and is never deleted; its master is archived |
| `res.partner` 2361 | the archived synthetic user's contact (no email/phone) | Odoo's `res.partner.write` guard refuses to archive a contact linked to a user, even after the user was archived (`RedirectWarning`, reproduced in a fresh transaction) — OBS-2C-10 |

## 5. Zero active synthetic records (operator view)

`active_leftovers` after cleanup: orders not cancelled 0; quote scopes 0;
masters 0; products 0; partners 1 (2361, see above); users 0; projects 0; tasks
0 (project 97 and since 07:00 today); analytic accounts 0; pickings 0; purchase
orders 0; manufacturing orders 0; BoMs 0; invoices 0; demands not
cancelled/failed 0; batches not cancelled/failed 0.

## 6. Side-effect checks

| Check | Result |
|---|---|
| invoice / vendor bill posted | none (posted `account.move` 0 before and after; no `account.move` for the pilot orders) |
| email sent | none (`mail.mail` 36 before, 36 after) |
| real stock consumed | none (`done` moves 10 before and after; internal quant quantity 0) |
| unrelated Product Master records | untouched (only the 7 prefixed products created and archived) |
| SIPANEL configuration | unchanged (`report.url`, 6 `sipanel_scope.*` parameters, 5 owner rules identical to preflight) |
| earlier audit records | intact: `SI-26/312`, master version 115, STEP 2B pilot revisions 886/887 |
| other tenants | untouched (see the execution-batch report §7) |
