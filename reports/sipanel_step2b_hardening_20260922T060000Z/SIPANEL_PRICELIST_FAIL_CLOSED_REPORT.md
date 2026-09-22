# SIPANEL Pricelist Fail-Closed Report (STEP 2B-HARDENING, run 20260922T060000Z)

## 1. The defect

`_sell_price_snapshot_vals()` wrapped the pricelist call in a bare
`except Exception` and silently substituted the product's list price:

```python
try:
    price = pricelist._get_product_price(product, 1.0, uom=target_uom,
                                         date=order.date_order, currency=order.currency_id)
    ...
except Exception:          # "pricing must never break the snapshot"
    price = product.with_company(order.company_id).list_price
```

`_get_product_price` is where currency conversion happens. The realistic failure
is a **missing exchange rate**, and the substitute — `product.list_price` — is
denominated in the *company* currency, not the order's. So a pricing failure
produced a plausible-looking number in the wrong currency, wrote it into the
governed snapshot as `sell_price_status = 'known'`, and let the quotation seal
and reach the customer. Nothing anywhere recorded that a calculation had failed.

The comment was the give-away: a snapshot that cannot be priced *should* break,
loudly.

## 2. The correction — option (b), an explicit missing-price state

| Situation | Before | Now |
|---|---|---|
| pricelist computes a price | used | used, unchanged |
| **pricelist raises** | silently replaced by `list_price` | **no price is written**; the failure is recorded in `sell_price_error`; `sell_price_status` becomes `missing`; readiness and the seal are blocked |
| order has no pricelist at all | `list_price` | `list_price`, explicitly — this is not a failed calculation, there is simply no price list to consult, and the product's own sales price is the governed price |
| `placement != 'own_line'` or no product | `not_applicable` | unchanged |

Option (b) was chosen over raising a `UserError` (option a) because the failure
happens while a Scope is being **added** to a quotation, often in bulk. Raising
there would abort the whole Scope creation and leave the operator with no record
of what went wrong; the missing-price state keeps the draft, names the failing
component and the pricing error, and refuses to let it be sent.

New field:

```python
sell_price_error = fields.Char(readonly=True,
    help="Why the customer pricelist could not produce a price. While this is set "
         "the component has no governed price and the quotation cannot be sent.")
```

The failure is also logged at WARNING with the pricelist, the product, the order
and the exception, e.g.

```
SIPANEL: pricelist Default (IRR) could not price SIPANEL-PT-CORE Bracket for order
SI-26/1310 (UserError: no exchange rate for this currency); the component is left
without a governed price.
```

### It cannot be masked

`sell_price_status` consults `sell_price_error` **before** the known-zero rule:

```python
elif c.sell_price_error and c.sell_price_source != 'manual':
    c.sell_price_status = 'missing'
```

so writing a "known zero" reason onto a component whose pricing failed does not
turn missing evidence into a deliberate commercial decision. Only a governed
**manual** price clears it — `action_set_manual_sell_price()` sets
`sell_price_error = False` — which is a human taking responsibility for the
number, exactly as intended.

### Readiness

A new blocking issue quotes the underlying error:

| Code | Message |
|---|---|
| `SB_PRICE_FAILED` | "%(label)s could not be priced by the customer pricelist (%(err)s). No price was invented; set a governed price manually, or fix the pricelist." |

It is raised **instead of** `SB_PRICE_MISSING` for that component, so the
operator sees the cause rather than just the symptom, and it is surfaced in the
component form (`sell_price_error`, shown only when set).

## 3. Native computation preserved

Nothing about Odoo's own pricing changed. The call is still

```python
pricelist._get_product_price(product, 1.0, uom=target_uom,
                             date=order.date_order, currency=order.currency_id)
```

with the order's pricelist, the component's unit, the order's date and the
order's currency. **No exchange rate and no price is invented anywhere** — on
failure the code writes `0.0` with an error string, which the status machinery
classifies as `missing`, not as a price.

## 4. Tests

| Requirement | Test |
|---|---|
| a failing pricelist calculation leaves no governed price | `test_failed_pricing_leaves_no_governed_price` — asserts `sell_price_error` set, `sell_price_unit == 0.0`, status `missing` |
| the chosen fail-closed behaviour blocks | `test_failed_pricing_blocks_readiness_and_the_seal` — `SB_PRICE_FAILED` in the blocking readiness issues, and `_sipanel_check_readiness()` raises |
| the failure cannot be dressed up as a deliberate zero | `test_a_known_zero_reason_cannot_mask_a_pricing_failure` |
| a human decision clears it | `test_a_governed_manual_price_clears_the_failure` |
| success is unaffected | `test_successful_pricing_records_no_error` |

The failure is simulated by patching `_get_product_price` on the
`product.pricelist` **registry class** to raise
`UserError('no exchange rate for this currency')` — the realistic case, and a
patch target that does not depend on where Odoo defines the class.

One assertion was corrected during the run, and it is worth recording why: the
first version asserted that `SB_PRICE_FAILED` disappeared entirely after pricing
a single component. It did not, because **every** separately-billable component
in the fixture fails while the pricelist is broken — which is the fail-closed
behaviour working correctly. The test now asserts per component, then prices the
rest and asserts the block clears. No assertion was weakened.
