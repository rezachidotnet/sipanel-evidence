# SIPANEL Invoice Evidence (STEP 2B live pilot, customer data redacted)

Draft invoice created by the governed flow Quotation -> Confirmation -> Create Invoice.
It was **never posted** and was deleted during cleanup.

| | |
|---|---|
| Source order | `SI-26/960` (Persian quotation) |
| Customer | `<redacted synthetic Persian customer>` |
| Invoice state | **draft** (name is assigned on posting, so it is `False`) |
| Invoice untaxed | 46,800,000 |
| Invoice total | 51,480,000 |
| Order untaxed at confirmation | 48,300,000 |
| Difference | 1,500,000 — the provisional component held back from invoicing |

## Invoice lines

| # | Description | Qty | Unit price | Scope | Revision | Component | Origin key | Source Sale Line |
|---|---|---:|---:|---|---|---|---|---|
| 1 | <PILOT> Gutter accessories (a | 12 | 2,500,000 | — | — | — | `—` | — |
| 2 | بست دیواری | 24 | 450,000 | 348 | 886 | 6118 | `886:d2f9a9fe-4c6d-43cd-a80f-cceee47da25c` | 1770 |
| 3 | گزینه‌های اختیاری | 0 | 0 | — | — | — | `—` | — |
| 4 | <PILOT> Gutter accessories (a | 5 | 0 | — | — | — | `—` | — |
| 5 | بست دیواری | 10 | 450,000 | 348 | 887 | 6123 | `887:f3c2ce29-d3f4-4f3d-9998-7d9398fc3c94` | 1772 |
| 6 | جرثقیل | 1 | 1,500,000 | 348 | 887 | 6124 | `887:ddc60cc4-9bac-432b-ae63-5edd062b7629` | 1773 |

## What is absent, and why

| Component shape | In the invoice | Reason |
|---|---|---|
| INCLUDED (`included_parent`) | no | paid for through the anchor line |
| PROVISIONAL own line (base Scope) | no | `sipanel_invoice_gate = provisional`, held until resolved |
| CUSTOMER_SCOPE | no | `responsibility = customer` — never our revenue |
| INTERNAL_ONLY | no | `disclosure = internal_only` — never disclosed, never billed |
| OPTIONAL own line, accepted | yes | acceptance gave it its governed quantity |

Taxes, fiscal position, currency and rounding are entirely native; the
descriptions are the frozen Persian snapshot text the customer accepted.

## Operational evidence at the same moment

| Measure | Value |
|---|---:|
| `generated_lines` | 4 |
| `stock_moves_from_generated_lines` | 0 |
| `execution_demands` | 0 |
| `purchase_orders` | 0 |
| `mrp_productions` | 0 |
| `mail_mail` | 0 |
