# SIPANEL Invoice Line Traceability (STEP 2B, run 20260921T021500Z)

## 1. The governed flow

```
Quotation  ──seal──▶  Sent (sealed)  ──accept──▶  Confirmation  ──Create Invoice──▶  Draft invoice
```

**A manually created Accounting invoice does not discover quotation options, and
is not expected to.** Nothing in this implementation reaches from
`account.move` back into a quotation to find Scope content. Traceability flows
one way only, from the Sale Line that Odoo itself turned into an invoice line.
An operator who needs Scope revenue on an invoice must go through
Quotation → Confirmation → Create Invoice. This is stated again in the operator
guide.

## 2. Fields added to `account.move.line`

Provenance only. **Nothing in `account_move_line.py` computes money** — no
amount, no tax, no currency conversion, no rounding.

| Field | Meaning |
|---|---|
| `sipanel_source_component_id` | the snapshot component that produced the revenue |
| `sipanel_source_revision_id` | the quotation Scope revision |
| `sipanel_source_quote_scope_id` | the quotation Scope instance |
| `sipanel_source_scope_id` | the master Scope |
| `sipanel_origin_key` | the same stable key as the Sale Line |
| `sipanel_source_line_id` | the generated `sale.order.line` |

All `readonly=True, copy=False, ondelete='restrict'` — a component or revision
that is referenced by an invoice line cannot be deleted out from under it.

## 3. How they are filled

`sale.order.line._prepare_invoice_line()` is extended. It calls `super()` first,
so everything Odoo prepared — `quantity`, `price_unit`, `discount`, `tax_ids`,
`product_uom_id`, `sale_line_ids`, the account — is untouched. Two things are
then added:

1. the provenance fields above;
2. `name` is forced to the Sale Line's own `name`, which is the **frozen
   resolved snapshot text** from STEP 2A.

Without (2), Odoo composes the invoice description from the product's display
name, which would be translated **now**, in the invoice's language — a customer
could be invoiced with wording they never accepted. The frozen text is what they
agreed to.

| Requirement | Result |
|---|---|
| invoice-line description uses the frozen resolved snapshot text | `test_invoice_description_uses_the_frozen_resolved_translation` (Persian), `test_english_quotation_invoices_in_english` |
| taxes and fiscal position remain native | untouched by `_prepare_invoice_line`; `test_native_taxes_apply_to_the_generated_line` |
| currency and rounding remain native | never referenced in SIPANEL code |

## 4. What does and does not reach an invoice

| Component shape | Sale Line | Invoice line |
|---|---|---|
| INCLUDED (`included_parent`) | none — paid through the anchor | **no** |
| SEPARATELY BILLABLE (`own_line`, firm) | yes, governed qty and price | **yes** |
| OPTIONAL + own line, not accepted | yes, quantity **0** | **no** (`qty_to_invoice` is 0) |
| OPTIONAL + own line, accepted | yes, governed qty | **yes** |
| PROVISIONAL + own line | yes, visible to the customer | **no** — gated |
| CUSTOMER_SCOPE (`responsibility == 'customer'`) | none | **no** |
| INTERNAL_ONLY (`disclosure == 'internal_only'`) | none | **no** |

Tests: `test_confirmed_order_produces_the_expected_invoice_line`,
`test_included_component_creates_no_invoice_line`,
`test_customer_scope_and_internal_only_create_no_invoice_line`,
`test_provisional_component_creates_no_invoice_line`,
`test_optional_unaccepted_line_is_quantity_zero`.

## 5. The provisional gate

`sipanel_invoice_gate` is non-empty (`provisional` or `unresolved`) while a
generated line must not invoice, and `sale.order._get_invoiceable_lines()`
removes those lines.

**On the "approved recognition policy" escape hatch.** The brief allows
provisional invoicing where "an existing approved recognition policy explicitly
permits it", and forbids inventing one. The installed source has exactly one
policy model, `sipanel.cost.recognition.policy`, and it governs **cost**
recognition routes (`shared_stock`, `direct_purchase`, `mfg_material`, …) with
terminal events like `stock.move` and `account.move.line`. It says nothing about
revenue and has no field that could express "this provisional component may be
billed". There is therefore **no existing approved policy to honour**, and none
was invented: the gate is unconditional until the component is resolved to
`certainty == 'firm'`.

Resolving it lifts the gate — `test_resolving_a_provisional_component_lifts_the_gate`.

## 6. Forgery

`account.move.line.create()` refuses Scope provenance from anything that is not
the governed Sale→Invoice path:

* the flow marks itself with a `sipanel_from_sale_invoice` context, set by
  `sale.order._create_invoices()`;
* a hand-made invoice, an import or an RPC payload that supplies a provenance
  field without a `sale_line_ids` link is refused;
* `write()` refuses any change to provenance outside the projection guard.

`test_invoice_provenance_cannot_be_forged_on_a_manual_invoice`.

## 7. Live pilot evidence

Persian quotation `SI-26/960`, two Scopes (one base, one optional), draft invoice:

| Invoice line | Qty | Unit | Component | Origin key |
|---|---:|---:|---|---|
| anchor (Scope note) | 12 | 2,500,000 | — | — |
| `بست دیواری` | 24 | 450,000 | 6118 | `886:d2f9a9fe…` |
| `گزینه‌های اختیاری` (section) | — | — | — | — |
| anchor (optional Scope) | 5 | 0 | — | — |
| `بست دیواری` | 10 | 450,000 | 6123 | `887:f3c2ce29…` |
| `جرثقیل` | 1 | 1,500,000 | 6124 | `887:ddc60cc4…` |

Order untaxed **48,300,000**; invoice untaxed **46,800,000**. The 1,500,000
difference is exactly the base Scope's provisional crane, correctly held back.
The descriptions are Persian, taken from the frozen snapshot. The invoice was
left in **draft** and was deleted during cleanup; it was never posted.
