# SIPANEL Sale Line Projection — Data Model (STEP 2B, run 20260921T021500Z)

## 1. The authority: no new enum

The installed source already represents "billed separately" through orthogonal
axes. `sipanel_tools.PLACEMENT` is:

```python
PLACEMENT = [
    ('included_parent',  'Included in parent line'),
    ('own_line',         'Own customer line'),      # <- separately billable
    ('no_customer_line', 'No customer line'),
]
```

`treatment_preset` (which contains a `separately_billable` value) is a
**computed, stored** field derived from the axes by `preset_from_axes(...)`, not
an input. It is a label for the operator, never the authority. **No new Billing
Treatment enum was added.**

Eligibility is the conjunction of the axes, computed and stored on the
component as `separately_billable`:

| Condition | Field / value |
|---|---|
| billed on its own customer line | `placement == 'own_line'` |
| ours to sell, not customer-supplied | `responsibility == 'sipanel'` |
| may be shown to the customer | `disclosure == 'customer_eligible'` |
| live, not tombstoned or transferred away | `active_state == 'active'` |
| belongs to the current working revision | only `state == 'working'` revisions are synchronised |
| has a governed selling quantity and price | `product_id` set and `sell_price_status != 'missing'` |

Acceptance is handled orthogonally rather than as an eligibility gate: an
unaccepted optional component still gets its line, at quantity zero, which is
native Odoo optional-product behaviour.

Nothing consults the product category.

## 2. Governed selling price (new, on `sipanel.quote.scope.component`)

Revenue had no representation before this step — components carried cost only,
and all revenue sat on the anchor line's `price_unit`. The new fields mirror the
existing cost-status pattern exactly, because the distinction that matters is
the same one:

| Field | Type | Purpose |
|---|---|---|
| `sell_price_unit` | Monetary | governed selling price per component unit, quotation currency |
| `sell_price_source` | Selection | `product_list` / `manual` / `not_applicable` |
| `sell_price_status` | Selection, computed, stored | `known` / `known_zero` / `missing` / `not_applicable` |
| `sell_known_zero_reason` | Text | why it is deliberately zero |
| `sell_price_user_id`, `sell_price_date` | — | who set a manual price and when |
| `sell_price_snapshot_date` | Datetime | when it was frozen from the product |
| `sell_amount` | Monetary, computed | `final_qty × sell_price_unit` |

`sell_price_status` rules:

* `not_applicable` — not separately billable (an included component is paid for
  through the anchor; giving it a price of its own is what would double-count);
* `missing` — an `estimate_only` component with no product, **or** a zero price
  with no recorded reason;
* `known_zero` — zero **with** a recorded reason;
* `known` — otherwise.

`missing` blocks the seal. `known_zero` does not. These are not the same thing
and the model refuses to conflate them.

The initial price is frozen through the order's own pricelist
(`pricelist._get_product_price(...)`) so currency and customer pricing stay
native — no hardcoded rate anywhere, and no tax arithmetic in SIPANEL code.

## 3. Provenance (new, on `sale.order.line`)

All `copy=False`: a duplicated quotation must get its own projection from its
own components, never inherit another quotation's provenance.

| Field | Meaning |
|---|---|
| `sipanel_is_generated` | projected from a governed Scope component |
| `sipanel_origin_key` | `"{revision_id}:{occurrence_uid}"` — stable within a revision, globally unique |
| `sipanel_source_component_id` | the snapshot component |
| `sipanel_source_revision_id` | the quotation Scope revision |
| `sipanel_source_quote_scope_id` | the quotation Scope instance |
| `sipanel_source_scope_id` | the master Scope |
| `sipanel_snapshot_language` | the resolved snapshot language (STEP 2A) |
| `sipanel_placement_snapshot` | the treatment at projection time |
| `sipanel_certainty_snapshot` | firm / provisional at projection time |
| `sipanel_qty_provenance` | `"{basis}:{final_qty}"` |
| `sipanel_price_provenance` | `"{sell_price_source}:{sell_price_status}"` |
| `sipanel_invoice_gate` | non-empty while the line must not invoice |

### Idempotency, enforced twice

```python
_sipanel_origin_key_unique = models.UniqueIndex(
    "(sipanel_origin_key) WHERE sipanel_origin_key IS NOT NULL")
```

Verified in the database after the upgrade:

```
CREATE UNIQUE INDEX sale_order_line_sipanel_origin_key_unique
  ON public.sale_order_line USING btree (sipanel_origin_key)
  WHERE (sipanel_origin_key IS NOT NULL)
```

and in the application by the upsert in `_sync_separately_billable_lines()`,
which keys existing lines by origin key and writes only what differs. A retry, a
module upgrade, a double click or four consecutive synchronisations produce the
same line set — `test_repeated_synchronisation_creates_no_duplicate` — and the
database refuses a forged duplicate outright —
`test_database_constraint_refuses_a_second_line_for_one_component`.

## 4. Customer-facing content of a generated line

| Aspect | Source |
|---|---|
| description | `component.customer_label_resolved` — the frozen STEP 2A snapshot |
| quantity | `component.final_qty`, or 0 while an option is unaccepted |
| unit | `component.uom_id` |
| unit price | `component.sell_price_unit` |
| product | `component.product_id` |
| taxes, fiscal position | **native** — Odoo computes them from the product; SIPANEL sets no tax |
| currency, rounding | **native** — the order's |

Master translations are never re-read. The line repeats what the quotation
froze, which is what the customer was shown.

## 5. Automatic synchronisation

Synchronisation is automatic, not a button. Every governed transition — add
scope, refresh cost, replace recipe, split, move, treatment transition,
tombstone, amend — ends in a component `create`, `write` or `unlink`, so the
projection is resynchronised from that single choke point
(`_sipanel_resync_projection`). Because the upsert is idempotent, being called
several times in one transaction is harmless.

`action_sipanel_sync_scope_lines` ("Synchronise Scope Lines") exists as a
visible, repeatable fallback only.

Sealed revisions are skipped entirely: a sealed projection is frozen, and a
change needs a new working revision.

## 6. Retiring a projection

| Situation | Behaviour |
|---|---|
| component no longer eligible (tombstoned, treatment changed, deactivated) | its line is deleted if untouched, or set to quantity zero if it already carries invoice or delivery history |
| revision superseded by an amendment | the prior revision's lines are deleted, so the same component is never billed twice |
| a superseded line is already invoiced or delivered | left alone, and reported as a reconciliation problem for a change order to settle — the projection does not guess |

The middle row was found by the live pilot, not by the first test pass: an
amendment created a second projection while the first was still live, which
double-billed the order. It is now covered by
`test_amendment_does_not_double_bill_the_same_component`.
