# SIPANEL Seal-Drift Gate Report (STEP 2B, run 20260921T021500Z)

## 1. What a seal hash covers

`sipanel.quote.scope.revision._seal_payload()`:

```python
{'order', 'scope_uid', 'revision', 'language', 'scope_qty',
 'anchor'          : the anchor line projection (product, qty, price, discount, taxes, subtotal),
 'components'      : the customer-facing rows,
 'final_note'      : the accepted customer text,
 'amount_untaxed', 'amount_total', 'currency'}
```

`_current_seal_hash()` recomputes it with the **live** anchor projection, so it
detects any change to the governed content or to the order's money after the
seal.

## 2. The three gates

| # | Gate | Where | Pre-existing? | Behaviour |
|---|---|---|---|---|
| 1 | customer acceptance | `quote_scope_revision.action_accept` | **yes** | raises; revision stays `sent_sealed` |
| 2 | confirmation | `sale_order.action_confirm` → `_sipanel_accept_current_revisions` → `action_accept` | **yes** | raises |
| 3 | invoice creation | `sale_order._sipanel_check_seal_integrity_for_invoice`, called from `_create_invoices` | **no — added in this step** | raises, naming every drifted Scope |

Gate 3 was the only missing one. It checks the **accepted** revision (falling
back to the current one), skips working and unsealed revisions, and refuses when
the recomputed hash differs:

> Order %s cannot be invoiced: the governed Scope content changed after
> acceptance: … Create an amendment revision and reseal, then invoice.

## 3. Proof

| Requirement | Test | Result |
|---|---|---|
| acceptance refused on drift | `test_seal_drift_blocks_acceptance` | pass — and the state is asserted unchanged afterwards |
| confirmation refused on drift | `test_seal_drift_blocks_confirmation` | pass |
| invoice creation refused when governed content differs from the accepted seal | `test_seal_drift_blocks_invoice_creation` | pass |
| a commercial change after sealing requires a new working revision and a new seal | `test_commercial_change_after_sealing_requires_a_new_revision_and_reseal` | pass |
| prior artifacts and hashes retained | `test_prior_artifacts_are_retained_after_amendment` | pass |
| a sealed generated line cannot be edited directly | `test_sealed_generated_line_cannot_be_edited_directly` | pass |

`test_commercial_change_after_sealing_requires_a_new_revision_and_reseal` walks
the whole boundary: setting a selling price on a sealed revision's component
raises; `action_amend()` produces a new `working` revision; the price is set
there; the note is regenerated; the new revision seals; and the prior revision
still has its `sealed_hash` and its artifacts.

## 4. A legitimate drift that is not a defect

Accepting an optional Scope changes the order total, and the order total is in
every Scope's seal payload, so **every** sealed Scope on that order drifts. This
is pre-existing, and the governed flow already handles it by re-sealing before
confirmation. The existing suite documents it in `test_governance.py`:

```python
# accepting keeps the hash consistent (qty is part of the projection, so re-seal happens on next send)
self.assertNotEqual(rev._current_seal_hash(), rev.sealed_hash)
order.action_quotation_send()     # re-seal
order.action_confirm()
```

The live pilot follows exactly that sequence — seal → accept → **re-seal** →
confirm — and records the drift explicitly
(`evidence/pilot/pilot_result.json` → `drift_after_acceptance`). The first pilot
attempt skipped the re-seal and was correctly refused by gate 2, which is itself
evidence the gate works outside a test.

## 5. The retained cancelled order SI-26/312

Its two sealed revisions still do not recompute to their stored hashes.
**Nothing was rewritten and no consistency was fabricated.** The cause is
unchanged and was established in STEP 2A: the payload includes the live order
totals, and that order was cancelled and edited during the 2026-09-20 runs
(live untaxed 39,500,000 against a sealed projection of 28,500,000).

It cannot become a usable operational record:

| Path | Why it is closed |
|---|---|
| acceptance | `action_accept` requires `sent_sealed` **and** a matching hash — both fail |
| confirmation | a cancelled order cannot be confirmed; acceptance would refuse regardless |
| invoicing | gate 3 refuses drifted governed content |
| editing the sealed revision | `write` refuses content changes on a non-working revision |
| deleting it to "tidy up" | `_unlink_except_working` refuses to delete a sealed revision |

It remains historical drift evidence, which is what it is for.

## 6. Retention on amendment

An amendment never unseals. `action_amend` copies components into a **new**
working revision and leaves the prior revision, its `sealed_hash`, its
`accepted_date` and its artifacts exactly as they were.

The one thing an amendment now also does is retire the **projection** of the
superseded revision, so the same component is not billed twice — the sealed
revision itself is untouched, only its live Sale Lines are replaced. If such a
line is already invoiced or delivered it is left alone and reported as a
reconciliation problem, because withdrawing invoiced revenue is a change-order
decision, not something a synchroniser should do silently.
