# SIPANEL Temporary Data Cleanup Report (STEP 2B, run 20260921T021500Z)

## 1. What the pilot created

All prefixed `SIPANEL-SEPBILL-PILOT-20260921T021500Z`, all synthetic.

| Model | Created |
|---|---:|
| `product.product` | 6 (anchor, gutter, bracket, crane, sealant, screws) |
| `sipanel.scope` + `sipanel.scope.version` | 1 + 1 (released) |
| `sipanel.scope.recipe.line` | 5 (one per treatment shape) |
| `res.partner` | 1 (Persian) |
| `sale.order` | 1 (SI-26/960) |
| `sipanel.quote.scope` | 2 (one base, one optional) |
| `sipanel.quote.scope.revision` | 4 (2 original + 2 from the re-seal amendment) |
| generated `sale.order.line` | 4 |
| `sipanel.quote.scope.artifact` | 8 |
| `account.move` | 1 **draft** invoice |

## 2. Deleted

| Item | Result |
|---|---|
| the draft invoice | **deleted** — verified `state == 'draft'` first; the script asserts and refuses if anything is posted |

## 3. Cancelled, archived, retained — and why

Sealed revisions and their artifacts **cannot be deleted by design**. That
immutability is precisely what this step tested (`_unlink_except_working`
refuses), so the cleanup does not break it to tidy up. It cancels and archives
instead, and lists exactly what remains.

| Item | Action | Why |
|---|---|---|
| order SI-26/960 | **cancelled and retained** | `sale.order` has no `active` field, so it cannot be archived; it carries sealed revisions and cannot be deleted. Same disposition as the retained SI-26/312. |
| 2 quotation Scopes (818, 819) | archived (`active = False`) | sealed revisions attached |
| 4 sealed revisions (884–887) | retained | sealed content is never deleted |
| 8 artifacts (797–804) | retained | acceptance evidence |
| 4 generated Sale Lines (1770–1773) | retained on the cancelled order | provenance evidence for this report |
| pilot master Scope (348) + version (414) | archived | a **released** version can never be deleted |
| 6 pilot products | archived | referenced by the retained revisions |
| 1 partner (1488) | archived | referenced by the retained order |

**Nothing synthetic is visible to an operator.** Post-cleanup counts of *active*
records carrying the pilot prefix:

| Model | Active |
|---|---:|
| `sipanel.quote.scope` | 0 |
| `sipanel.scope` | 0 |
| `product.product` | 0 |
| `res.partner` | 0 |
| `account.move` | 0 |
| `sale.order` | 1 — the cancelled order (no `active` field exists to hide it) |

## 4. The cancelled order cannot become operational

| Path | Why it is closed |
|---|---|
| confirmation | the order is `cancel` |
| acceptance | its revisions are already `accepted_sealed`; re-acceptance is idempotent and hash-checked |
| invoicing | its only invoice was deleted, and the new invoice gate checks seal integrity |
| its generated lines | immutable — projected from sealed revisions |
| its Scopes | archived |

## 5. Side effects — none

| Model | Count |
|---|---:|
| emails sent during the run | **0** |
| posted journal entries | **0** |
| purchase orders from the order | 0 |
| manufacturing orders from the order | 0 |
| stock pickings from the order | 1, `cancel` — anchor-line moves only, **0** moves from generated lines |

No external communication was generated and no invoice was posted.

## 6. Configuration unchanged

| Setting | Value |
|---|---|
| `report.url` | `http://127.0.0.1:8072` |
| website 1 languages | `['en_US', 'fa_IR']` |
| installed languages | `en_US`, `fa_IR`, `ru_RU` |
| paperformat | untouched |
| Product Master | not redesigned; only synthetic pilot products were created and archived |

`ru_RU` was **not** given placeholder translations. It remains fail-closed: a
Russian-language quotation would be refused at seal, by design.

## 7. Earlier audit records intact

| Record | Status |
|---|---|
| order 312 (SI-26/312, cancelled) | present |
| master version 115 | present |
| version 111's missing recipe / checksum | **untouched** — not repaired, not fabricated |
| total artifacts on the database | 12 (4 from earlier runs + 8 from this pilot) |

## 8. Filesystem

| Location | Action |
|---|---|
| `odoo-sipanel:/tmp/pilot_before.pdf`, `/tmp/pilot_after.pdf` | copied into the report, then removed |
| `/opt/odoo/backups/sipanel-pre-sepbill-20260921T021500Z` | **retained** — this run's recovery point (~110 MB) |
| `/opt/odoo/addons/sipanel_*` | updated by `rsync` from the repository (the deployment path) |

## 9. Disk

Checked **before** creating the recovery point, as required: 2.8 GB free,
`/opt/odoo/backups` at 697 MB across 8 entries, and the script's own capacity
guard (needs ~456 MB plus 1.5 GB headroom) passed. Nothing was deleted — no
older recovery point was removed, since that needs explicit target-level
authorization. Free space is now ~2.7 GB and this remains the most pressing
housekeeping item carried forward.
