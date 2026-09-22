# SIPANEL — STEP 2B-HARDENING (run 20260922T060000Z)

| | |
|---|---|
| Started from | local commit `490eb30` |
| Scope | database `sipanel`, container `odoo-sipanel` only |
| Verdict | **PASS** — all three defects corrected, 282 tests green, no synthetic records left active |
| Module changed | `sipanel_sale_scope` 19.0.1.2.0 → **19.0.1.2.1** (the only module whose source changed) |
| Not changed | `sipanel_commercial_scope_core`, `sipanel_scope_costing`, `sipanel_scope_execution`, `sale_shamsi_report` (HEAD `5680013`, clean), `report.url`, website languages, paperformat, Product Master |
| Recovery point | `/opt/odoo/backups/sipanel-pre-2bhardening-20260922T060000Z` (created and verified before the first write) |
| Restart | **none** — `odoo-sipanel` `RestartCount=0`, `StartedAt=2026-09-20T06:40:08Z` |
| Other tenants | untouched — no command addressed `odoo-avizsazeh`, `odoo-shahbazi`, `odoo-ahantorob`, or any database but `sipanel` |
| STEP 2C | **not started** |

---

## 1. Correction 1 — invoice-line provenance authorization

`account.move.line.create()` decided authorization from a plain
`sipanel_from_sale_invoice` context key, and additionally exempted any payload
that supplied `sale_line_ids`. **Both were forgeable**: a context key is an
ordinary RPC argument, and `sale_line_ids` is user-writable data, so a caller
could point at a genuine generated Sale Line and inherit the exemption.

Both checks are removed. Authorization is now `guard(env, 'sipanel_invoice_trace')`
— the process-local token mechanism already used elsewhere — and the genuine path
opens it for exactly one call via
`self.with_context(**guard_ctx('sipanel_invoice_trace'))` in
`sale.order._create_invoices()`. There is no `sale_line_ids` exemption, and no
reference to `sipanel_from_sale_invoice` remains anywhere in the repository.

Nine tests prove refusal (raw `sipanel_invoice_trace`, raw
`sipanel_from_sale_invoice`, real `sale_line_ids`, `sudo`, `import_file`,
guessed token, plain create, and all four write routes) and that the genuine
flow still carries all five provenance references.

Detail: `SIPANEL_INVOICE_PROVENANCE_SECURITY_REPORT.md`.

## 2. Correction 2 — pilot reconciliation evidence

The pilot keyed reconciliation by `display_name`, which **both revisions of the
order share**, so one entry overwrote the other and only one revision was ever
in the evidence. The STEP 2B reports nonetheless said `problems: []` "on both
Scopes" — a claim the evidence did not support.

Evidence is now a list keyed by immutable revision id, with an explicit
`distinct_revision_records_present` flag. Regenerated from the retained pilot
records:

| Revision | Quote Scope | Optional | Anchor | Separately billable | Lines | Problems |
|---:|---:|---|---:|---:|---:|---|
| **886** | 818 | no | 30,000,000 | 12,300,000 | 2 | `[]` |
| **887** | 819 | yes, accepted | 0 | 6,000,000 | 2 | `[]` |

`30,000,000 + 12,300,000 + 0 + 6,000,000 = 48,300,000` ✓ — the pilot order's
untaxed total. The two revisions carry **different** amounts, which is exactly
why a single-entry record could not have described both.

Both affected STEP 2B statements now carry inline corrections. The STEP 2B ZIP
was deliberately not rewritten, so those two markdown files now diverge from the
STEP 2B `SHA256SUMS`; the before/after hashes are recorded in
`SIPANEL_RECONCILIATION_EVIDENCE_CORRECTION.md` §4.

## 3. Correction 3 — pricelist resolution fails closed

`_sell_price_snapshot_vals()` caught every exception and substituted
`product.list_price`. Since `_get_product_price` is where currency conversion
happens, the realistic failure is a missing exchange rate — and the substitute
is in the **company** currency, so a failure produced a plausible number in the
wrong currency, stored as `sell_price_status = 'known'`, and let the quotation
seal.

Now a failed calculation writes **no price**: it records `sell_price_error`, logs
a warning naming the pricelist, product, order and exception, and leaves
`sell_price_status = 'missing'`, which blocks readiness and the seal via a new
`SB_PRICE_FAILED` issue that quotes the underlying error. A "known zero" reason
cannot mask it; only a governed manual price clears it. The absence of a
pricelist is treated separately — that is not a failed calculation, and the
product's own sales price is the governed price.

Native pricelist, currency, UoM and date computation are untouched. **No
exchange rate and no price is invented anywhere.**

Detail: `SIPANEL_PRICELIST_FAIL_CLOSED_REPORT.md`.

## 4. Validation

| Suite | Before | After |
|---|---|---|
| SIPANEL (4 modules) | 184 | **202, 0 failures** |
| `sale_shamsi_report` | 80 | **80, 0 failures** |
| **Total** | 264 | **282, 0 failures** |

All required areas re-covered: SIPANEL modules, Shamsi regression, STEP 2B
security, quotation → confirmation → draft invoice, Persian and English frozen
descriptions, optional accepted/unaccepted, provisional hold, duplicate
projection/idempotency, seal-drift invoice gate.

**No failing assertion was weakened.** Two corrections were made to *new* tests
(a wrong patch target, and an assertion that was too narrow); the second is a
stronger assertion than the original. No pre-existing assertion was modified.

Detail: `SIPANEL_STEP2B_HARDENING_TEST_RESULTS.md`.

## 5. Operational safety

| Item | Value |
|---|---|
| Disk before | 2.6 G free (`free_mb = 2642`), 91 % used |
| Recovery points before | 9, totalling 807 M — **none deleted** |
| Capacity decision | `2642 − 459 = 2183 MB ≥ 1500 MB` headroom → safe to proceed |
| Recovery point created | `/opt/odoo/backups/sipanel-pre-2bhardening-20260922T060000Z`, verified (`pg_restore --list`, `tar -tzf` ×2, SHA256 over all six artefacts) |
| Disk after | 2.5 G free, 91 % used |
| Module upgrades | `sipanel_sale_scope` only (three upgrade cycles: code, test fix, version bump) |
| Restart | none |
| Invoice posted | **no** |
| Email sent | **no** — `mail.mail` created during the run: 0; outgoing queue: 0 |
| Commits pushed | **no** |

Full inventory: `SIPANEL_RECOVERY_POINT_INVENTORY.md`.

## 6. Records

**No active synthetic records remain.** A first check appeared to show four
active quotation Scopes and one active test Scope; that was a defect in the
check, which ran with `active_test=False` and therefore counted archived records.
Re-checked per record:

| Record | State |
|---|---|
| quote Scopes 818, 819 (STEP 2B pilot) | `active=False`, `state=cancelled`, order `SI-26/960` cancelled |
| quote Scopes 217, 218 (STEP 1A) | `active=False`, `state=cancelled`, order `SI-26/312` cancelled |
| Scope 91 `SIPANEL-PT-GUTTER` (demo leftover) | `active=False` |
| invoices for `SI-26/960` | 0 — the draft invoice was deleted in the STEP 2B cleanup |
| revisions 886, 887 | retained, `accepted_sealed` — sealed content is never deleted, by design |

Nothing was created in this run beyond transaction-scoped test data, which rolls
back. The reconciliation evidence was regenerated **read-only** from the retained
records.

## 7. Residual items (unchanged, not actioned)

| Id | Item |
|---|---|
| R-1 | Revenue-side policy for provisional components — the gate is unconditional today |
| R-2 | Exercise execution-batch release against generated lines |
| R-3 | Change-order behaviour when a superseded projected line is already invoiced |
| R-4 | **Prune recovery points — 10 now, filesystem at 91 %.** Needs target-level authorization; a concrete proposal is in the inventory §6 |
| R-5 | Complete or deactivate `ru_RU` |
