# SIPANEL Operator Guide — Quote to Invoice with separately-billable lines

## 1. The only supported flow

```
Quotation  →  Send (seals)  →  [customer accepts options]  →  Re-send (re-seals)  →  Confirm  →  Create Invoice
```

**A manually created invoice in Accounting will not find your Scope options.**
That is deliberate, not a gap: revenue is traced back to a governed Scope
component, and that link is only created when Odoo turns a confirmed Sale Line
into an invoice line. If you start from Accounting you get an ordinary invoice
with no Scope provenance, and it will not include anything from the quotation.

Always go Quotation → Confirmation → Create Invoice.

## 2. Reading a draft quotation

On the order lines you can now tell the kinds apart:

| What you see | What it is |
|---|---|
| a line with the Scope name and bullet text under it | the **anchor** line — everything INCLUDED is paid for here |
| a line with a **Scope line** badge reading `own_line` | a **separately billable** component with its own price |
| the same badge under an optional section, quantity 0 | an **optional** separate line — it costs nothing until the customer accepts |
| a **Invoice hold** column showing `provisional` | shown to the customer, but it will **not** be invoiced yet |
| nothing at all | INTERNAL_ONLY components — never shown, never billed |
| a note bullet naming something the customer supplies | CUSTOMER_SCOPE — disclosed so they know their obligation, never billed |

The technical origin key is hidden unless you are in developer mode.

## 3. Setting a selling price

A separately-billable component needs a governed selling price. It is taken from
the product's sales price through the order's pricelist when the Scope is added.
To override it, use the component's **Selling price** group:

| Status | Meaning | Blocks sending? |
|---|---|---|
| `known` | a real price | no |
| `known_zero` | deliberately zero, **with a recorded reason** | no |
| `missing` | zero with no reason, or an estimate with no product | **yes** |
| `not_applicable` | not separately billable — paid through the anchor | no |

A zero price is only accepted when you say **why**. That is the difference
between "we are giving this away" and "nobody priced it yet", and the quotation
will not go out on the second one.

## 4. What stops a quotation being sent

The readiness drawer blocks on:

| Code | Meaning | Fix |
|---|---|---|
| `SB_PRICE_MISSING` | a separately-billable component has no governed price | set a price, or record a reason for zero |
| `SB_NO_PRODUCT` | a separately-billable component has no invoiceable product | map a product, or change its placement to INCLUDED |
| `SB_ESTIMATE_PRODUCT` | an ESTIMATE_ONLY component is separately billable | resolve it to a real product first — it will never be given a generic "miscellaneous" product |
| `SB_RECONCILIATION` | anchor and separate lines do not reconcile | open the revision's reconciliation and read `problems` |
| `LABEL_LANG` | the customer's language has no translation (STEP 2A) | complete the master translation |

## 5. Synchronising Scope lines

Synchronisation is **automatic**. Adding a Scope, refreshing costs, replacing a
recipe, splitting, moving, changing a treatment or tombstoning a component all
resynchronise the separately-billable lines immediately.

The **Synchronise Scope Lines** button in the order header is a fallback you can
press safely at any time: it is idempotent and will never create a duplicate.

## 6. Options

An optional separate line sits under its optional section at **quantity zero**.
It contributes nothing to the total and cannot be invoiced.

When the customer accepts, its quantity becomes the governed quantity and it
starts contributing. Accepting twice changes nothing.

**Important:** accepting an option changes the order total, which is part of
every Scope's seal. You must **re-send** the quotation before confirming, or
confirmation will refuse with a "changed after it was sent" message. That is the
system protecting the customer's accepted figures, not an error.

## 7. Provisional components

A provisional component appears on the quotation with its provisional basis, so
the customer sees it and its indicative price. It is **held back from
invoicing** until it is resolved to firm.

There is no approval that can override this today. The only recognition policy
in the system governs cost routes, not revenue, and no revenue-approval policy
was invented for this step. Resolve the component — set its certainty to firm
once the quantity and price are final — and the hold lifts.

## 8. After confirmation

| Action | Allowed? |
|---|---|
| edit a generated line by hand | **no** — it is projected from a sealed revision |
| delete a generated line that has been invoiced or delivered | **no** |
| change the commercial content | amend the Scope (new working revision), then reseal |
| invoice after changing governed content without resealing | **no** — invoice creation refuses drifted content |
| cancel the order | yes — downstream demand is cancelled natively, audit provenance is kept |

## 9. Where the money comes from

| On the invoice | Traced back to |
|---|---|
| line description | the **frozen** snapshot text the customer accepted, not a fresh translation |
| quantity, price | the governed component snapshot |
| taxes, fiscal position, currency, rounding | entirely native Odoo |
| provenance | Scope, Scope revision, component, origin key and the source Sale Line, all on the invoice line |
