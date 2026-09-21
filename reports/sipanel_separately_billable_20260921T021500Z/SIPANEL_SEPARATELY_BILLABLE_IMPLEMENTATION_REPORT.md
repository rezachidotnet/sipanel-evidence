# SIPANEL — Separately-billable Sale Lines and Invoice Lines (STEP 2B)

| | |
|---|---|
| Run | `20260921T021500Z` (2026-09-21 06:15–07:30 UTC) |
| Scope | database `sipanel`, container `odoo-sipanel` only |
| Verdict | **PASS** — own-line components are now real, governed, idempotent Sale Lines that flow natively into invoice lines; 264 tests green; live Quote→Invoice pilot completed and cleaned up |
| Modules changed | `sipanel_sale_scope` 19.0.1.1.0 → **19.0.1.2.0**, `sipanel_commercial_scope_core` (P1 accessor hardening only, version unchanged) |
| Not changed | `sale_shamsi_report` (HEAD `5680013`, clean), `sipanel_scope_costing`, `sipanel_scope_execution`, Product Master, `report.url`, website languages, paperformat |
| Recovery point | `/opt/odoo/backups/sipanel-pre-sepbill-20260921T021500Z` (disk checked first, created and verified before the first write) |
| Restart | **none** — `odoo-sipanel` `RestartCount=0`, `StartedAt=2026-09-20T06:40:08Z` |
| Other tenants | untouched — no command addressed `odoo-avizsazeh`, `odoo-shahbazi`, `odoo-ahantorob`, or any database but `sipanel` |

---

## 1. The orthogonal field that means "separately billable"

**`sipanel.quote.scope.component.placement == 'own_line'`**, from
`sipanel_tools.PLACEMENT`. It was already the installed representation and it
remains the authority. `treatment_preset` — which has a `separately_billable`
value — is a **computed, stored** derivation of the axes via `preset_from_axes`,
a label for the operator, never an input. **No new Billing Treatment enum was
added**, as instructed.

Eligibility is the conjunction of the axes, stored as `separately_billable`:

```
placement == 'own_line'
  and responsibility  == 'sipanel'            # not customer-supplied
  and disclosure      == 'customer_eligible'  # not internal-only
  and active_state    == 'active'
  + belongs to a working revision, has a product and a governed price
```

Acceptance is handled orthogonally, not as an eligibility gate: an unaccepted
option still gets its line, at quantity zero, which is native Odoo behaviour.
Nothing consults the product category.

## 2. What was missing before this step

Components carried **cost** only. All revenue lived on the anchor line's
`price_unit`, and a "billed separately" component existed solely as a sentence
in the generated note (`بست دیواری (صورت‌حساب جداگانه): 24 عدد`). There was no
selling price, no line, and nothing an invoice could be made from.

So this step had to add a governed **revenue** concept before it could project
anything — see §4.

## 3. Sale Line and Invoice Line provenance

Full detail in `SIPANEL_SALE_LINE_PROJECTION_DATA_MODEL.md` and
`SIPANEL_INVOICE_LINE_TRACEABILITY_REPORT.md`.

**On `sale.order.line`** (all `copy=False`, all refused from user input):
`sipanel_is_generated`, `sipanel_origin_key`, `sipanel_source_component_id`,
`sipanel_source_revision_id`, `sipanel_source_quote_scope_id`,
`sipanel_source_scope_id`, `sipanel_snapshot_language`,
`sipanel_placement_snapshot`, `sipanel_certainty_snapshot`,
`sipanel_qty_provenance`, `sipanel_price_provenance`, `sipanel_invoice_gate`.

Origin key = `"{revision_id}:{occurrence_uid}"` — stable within a revision,
distinct across revisions and duplicates. Enforced twice: an idempotent upsert,
and a **partial unique index** verified present in PostgreSQL:

```
CREATE UNIQUE INDEX sale_order_line_sipanel_origin_key_unique
  ON public.sale_order_line (sipanel_origin_key) WHERE (sipanel_origin_key IS NOT NULL)
```

**On `account.move.line`**: `sipanel_source_component_id`,
`sipanel_source_revision_id`, `sipanel_source_quote_scope_id`,
`sipanel_source_scope_id`, `sipanel_origin_key`, `sipanel_source_line_id`.
Nothing in that file computes money.

## 4. Governed selling price

New on the component, mirroring the existing cost-status pattern because the
distinction is the same one: `sell_price_unit`, `sell_price_source`
(`product_list` / `manual` / `not_applicable`), `sell_price_status`
(`known` / `known_zero` / `missing` / `not_applicable`),
`sell_known_zero_reason`, `sell_amount`, plus who/when provenance.

* **missing** — zero with no reason, or an estimate with no product → **blocks the seal**;
* **known_zero** — zero **with** a recorded reason → allowed;
* **not_applicable** — an included component, paid through the anchor.

The initial price is frozen through the order's own pricelist, so currency and
customer pricing stay native. No hardcoded rate and no tax arithmetic anywhere
in SIPANEL code.

## 5. Reconciliation result

`Quotation Total = Anchor/Included + Separately Billable + Accepted Optional`,
enforced as "no component counted twice". A new per-revision reconciliation
(`anchor_amount`, `separate_amount`, `reconciliation_json`, `reconciliation_ok`)
lists every separately-billable component against its line and raises a
**blocking** readiness issue (`SB_RECONCILIATION`) on any problem.

An own-line component is also removed from the note bullets now that it is a
real line, so the customer is not shown the same item twice.

Live pilot: 30,000,000 + 10,800,000 + 1,500,000 + 0 + 4,500,000 + 1,500,000 =
**48,300,000** ✓, with `problems: []` on both Scopes.

## 6. Optional and provisional

| Combination | Behaviour |
|---|---|
| optional + own line, unaccepted | ordinary line at **quantity 0**; not invoiceable |
| optional + own line, accepted | governed quantity; acceptance binds to the current seal; repeating it changes nothing |
| provisional + own line | shown to the customer with its provisional basis; **held back from invoicing** until resolved to firm |

**No approval policy was invented.** The only policy model in the installed
source, `sipanel.cost.recognition.policy`, governs **cost** recognition routes
and has no field that could permit provisional billing. There is therefore no
existing approved policy to honour, and the gate is unconditional until the
component is resolved.

## 7. Procurement ownership

The frozen architecture already decides this per component via `execution_owner`
(`native_line_owner` links only; `component_bridge_owner` creates the demand).
A generated line does **not** get to add a second owner: the native stock rule
is skipped for a generated line whose component is bridge-owned.

Live pilot, 4 generated lines: **0** stock moves from generated lines, 0 POs,
0 MOs. The one picking holds anchor-line moves only.

## 8. Seal drift

Gates 1 (acceptance) and 2 (confirmation) already existed and are now **proven
by test**. Gate 3 (invoice creation) was missing and is implemented. SI-26/312's
hashes were **not** rewritten and no consistency was fabricated. See
`SIPANEL_SEAL_DRIFT_GATE_REPORT.md`.

## 9. STEP 2A prerequisites

| | Result |
|---|---|
| **P1** accessor hardening | the language-context fallback is **deleted**; absence of the ORM accessor now raises `MissingTranslationAccessor`; test simulates unavailability; no behavioural change on installed Odoo 19 |
| **P2** commit reconciliation | `c737034` contains **both** source and reports; the manifest's `8d10567` is the **parent** commit captured before committing — stale, not wrong; the old bundle is not rewritten |
| **P3** seal drift | all three gates proven; the third implemented |

Detail in `SIPANEL_STEP2A_HARDENING_AND_COMMIT_RECONCILIATION.md`.

## 10. FACT / INFERENCE / RECOMMENDATION

### FACT
* `placement == 'own_line'` was already the representation; no enum was added.
* Components had no selling price before this step; revenue existed only on the anchor.
* A generated line raises no native procurement when its component is bridge-owned (measured: 0 moves).
* The invoice gate for drifted content did not exist and now does.
* 264 tests pass; the live pilot completed Quote → seal → accept → re-seal → confirm → draft invoice.

### INFERENCE
* The amendment double-billing defect (§ test results §4) would have reached production if the pilot had not been run: the full test suite was green when it happened. Running it for real is what found it.
* Removing own-line components from the note bullets changes the generated note for **new** quotations. Existing sealed revisions are unaffected because sealed projections are frozen and notes are not regenerated.
* Keeping the snapshot columns and gating on `sipanel_invoice_gate` rather than deleting provisional lines keeps the customer document honest (they see the provisional item) while keeping the invoice correct.

### RECOMMENDATION
| Id | Recommendation | Priority |
|---|---|---|
| R-1 | Decide the revenue-side policy for provisional components. Today the gate is unconditional; if the business wants a controlled override it needs a real approved policy, not an ad-hoc flag. | high |
| R-2 | Exercise the execution-batch release path against generated lines in a controlled pilot. This step proved no *native* duplicate demand; the SIPANEL demand path was covered by transaction tests only. | medium |
| R-3 | Define the change-order behaviour when a superseded revision's line is already invoiced. Today it is left alone and reported as a reconciliation problem — deliberately, rather than guessing. | medium |
| R-4 | Prune old recovery points: 9 now, ~110 MB each, filesystem at 91 %. Needs target-level authorization, so it is not actioned here. | high |
| R-5 | Complete or deactivate `ru_RU` (carried over from STEP 2A). | medium |

## 11. Evidence index

| Path | Contents |
|---|---|
| `evidence/pilot/pilot_result.json` | the full live pilot: line-by-line snapshots at every stage, invoice lines with provenance, operational counts, reconciliation |
| `evidence/pilot/SIPANEL_PILOT_QUOTATION_*_REDACTED.pdf` | before-seal and after-confirm customer PDFs |
| `evidence/logs/upgrade_2b.log`, `upgrade_2b_views.log` | module upgrades |
| `evidence/logs/test_sipanel_final_2b.log`, `test_shamsi_final_2b.log` | final test runs |
| `evidence/logs/test_sepbill_run1..4.log` | the iteration that fixed the test harness |
| `evidence/source_diff/sipanel_step2b.diff` | complete source diff |
| `evidence/scripts/` | pilot and cleanup scripts |
