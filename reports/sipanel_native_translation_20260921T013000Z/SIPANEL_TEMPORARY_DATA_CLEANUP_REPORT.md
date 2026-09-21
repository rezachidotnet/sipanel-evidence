# SIPANEL Temporary Data Cleanup Report (STEP 2A, run 20260921T013000Z)

## 1. Created and removed

One synthetic end-to-end quotation, prefixed `SIPANEL-XLATE-CHECK-20260921T013000Z`,
created to prove the Persian resolution path against the real master and then
deleted.

| Model | Created | Removed |
|---|---:|---:|
| `sale.order` | 1 (SI-26/599, draft) | 1 |
| `sale.order.line` | 1 | 1 |
| `sipanel.quote.scope` | 1 | 1 |
| `sipanel.quote.scope.revision` | 1 (working, never sealed) | 1 |
| `sipanel.quote.scope.component` | 7 | 7 |
| `res.partner` | 1 (id 795) | 1 |

Leftovers with the run prefix after cleanup: `sale.order` 0,
`sipanel.quote.scope` 0, `res.partner` 0.

Deletion used the documented D-04 workaround (clear `current_revision_id`, flush,
then components → revision → scope → anchor line → order).

## 2. Side effects — none

| Model | Count |
|---|---:|
| `mail.mail` created during the run | 0 |
| `stock.picking` | 0 |
| `account.move` | 0 |
| `mrp.production` | 0 |
| `purchase.order` | 0 |
| `sipanel.execution.demand` | 0 |

No email was sent and no procurement, invoice, picking, manufacturing, task or
execution demand was created.

## 3. Retained on purpose — the migrated translations

The migrated master translations are **not** temporary data. They are the point
of this step and they stay:

| Record | Retained |
|---|---|
| version 115 | `customer_label` `{en_US, fa_IR}`, `customer_description` `{en_US, fa_IR}`, `checksum_algo=v1` |
| version 111 | `customer_label` `{en_US, fa_IR}`, `checksum_algo=v1` |
| 7 recipe lines | `customer_label` `{en_US, fa_IR}` each — 14 terms |

## 4. Retained from earlier runs — untouched

| Record | Status |
|---|---|
| `sale.order` 312 (SI-26/312, cancelled) | present |
| 2 sealed revisions | present, `write_date` unchanged (2026-09-20 06:21) |
| 4 acceptance artifacts | present, `write_date` unchanged (2026-09-20 06:12), stored text still hashes to its recorded hash |
| STEP 1D evidence and reports | untouched |

## 5. Configuration re-asserted after cleanup

| Setting | Value | Expected |
|---|---|---|
| `report.url` | `http://127.0.0.1:8072` | unchanged |
| website 1 languages | `['en_US', 'fa_IR']` | unchanged |
| report paperformat A4 margins | 52 / 32 mm | unchanged |
| installed languages | `en_US`, `fa_IR`, `ru_RU` | unchanged |

`ru_RU` was **not** activated by this step; it was already installed. The test
suite activates `fa_IR` idempotently through `_activate_lang`, which is a no-op
here because it was already active.

## 6. Filesystem

| Location | Action |
|---|---|
| `odoo-sipanel:/tmp/xlate_e2e.pdf` | removed (copied into the report first) |
| host scratchpad | session-scoped, not part of the deliverable |
| `/opt/odoo/backups/sipanel-pre-translation-20260921T013000Z` | **retained** — this run's recovery point, ~110 MB |
| `/opt/odoo/addons/sipanel_*` | updated by `rsync` from the repository (the deployment path, not temporary data) |

## 7. Note on disk

`/` was at **90 % (2.9 GB free)** before this run and six recovery points now
exist under `/opt/odoo/backups` at ~110 MB each. Nothing was deleted; pruning the
older ones remains an owner decision, and it is becoming the more pressing of the
two housekeeping items carried forward from STEP 1D.
