# SIPANEL Commercial Reconciliation (STEP 2B, run 20260921T021500Z)

## 1. The invariant

```
Quotation Total = Anchor / Included Amount
                + Separately Billable Lines
                + Accepted Optional Lines
```

Odoo already sums its own order lines correctly, so the arithmetic identity is
not the interesting part. The invariant that needed enforcing is **no component
contributes twice, and every component that should contribute does so exactly
once**.

| Rule | How it holds |
|---|---|
| an INCLUDED component contributes only through the anchor price | it is never projected (`separately_billable` is False) and its `sell_price_status` is `not_applicable` |
| an own-line component contributes only through its generated line | it is projected, and it is **removed from the anchor's customer note bullets** so it is not presented twice either |
| its amount is excluded from the anchor roll-up | the anchor's `price_unit` is operator-set and has never aggregated component prices; components had no selling price at all before this step |
| no component is billed both inside the anchor and separately | `placement` is a single value — `included_parent` and `own_line` are mutually exclusive — and the reconciliation asserts it anyway |
| CUSTOMER_SCOPE and INTERNAL_ONLY never create customer revenue | excluded by `responsibility` / `disclosure` in `separately_billable` |
| removing an own-line component removes only its projection | `_retire_projected_line` touches that one line |
| retries cannot change the total unexpectedly | the upsert is idempotent and the origin key is unique in the database |

### Presentation double-counting

Before this step an own-line component appeared as a bullet in the generated
note (`بست دیواری (صورت‌حساب جداگانه): 24 عدد`). Now that it is a real line,
repeating it as a bullet would show the customer the same thing twice, so
`_build_generated_note` skips `separately_billable` components. `_eligible_rows`
and therefore `_seal_payload` still cover them, so the seal and the acceptance
artifact continue to record the full customer-facing content.

Test: `test_included_component_stays_out_of_the_customer_note_bullets`.

## 2. The explicit per-revision reconciliation

`sipanel.quote.scope.revision` gained a computed reconciliation:

| Field | Meaning |
|---|---|
| `anchor_amount` | untaxed amount on the anchor line |
| `separate_amount` | untaxed total of the projected lines |
| `projected_line_count` | how many lines the revision owns |
| `reconciliation_json` | per-component rows plus a `problems` list |
| `reconciliation_ok` | `problems` is empty |

Each row records the component uid, its resolved label, its quantity, its
`sell_price_status`, and the line id / quantity / subtotal it maps to.

`problems` is raised when:

* a separately-billable component with a product and a non-missing price has **no** line;
* a projected line has **no** eligible component and still carries quantity;
* a line from a **superseded** revision is already invoiced or delivered (a change order must settle it);
* a component is somehow both included and separately billable.

Any problem becomes a **blocking** readiness issue (`SB_RECONCILIATION`), so a
quotation that does not reconcile cannot be sent.

## 3. Live pilot arithmetic

Persian quotation `SI-26/960`: one base Scope (12 m) and one optional Scope (5 m),
each with the six component shapes.

| Stage | Untaxed | Total |
|---|---:|---:|
| draft | 42,300,000 | 46,530,000 |
| sealed | 42,300,000 | 46,530,000 |
| optional accepted | 48,300,000 | 53,130,000 |
| re-sealed | 48,300,000 | 53,130,000 |
| confirmed | 48,300,000 | 53,130,000 |

Line composition at confirmation:

| Line | Kind | Qty | Unit | Subtotal |
|---|---|---:|---:|---:|
| `متعلقات آبرو` + note bullet `ناودان گالوانیزه: 12 m` | anchor (includes the INCLUDED component) | 12 | 2,500,000 | 30,000,000 |
| `بست دیواری` | generated, own line | 24 | 450,000 | 10,800,000 |
| `جرثقیل` | generated, own line, **gate = provisional** | 1 | 1,500,000 | 1,500,000 |
| `گزینه‌های اختیاری` | optional section | — | — | — |
| `متعلقات آبرو` (optional anchor) | anchor | 5 | 0 | 0 |
| `بست دیواری` | generated, optional, accepted | 10 | 450,000 | 4,500,000 |
| `جرثقیل` | generated, optional, accepted | 1 | 1,500,000 | 1,500,000 |

`30,000,000 + 10,800,000 + 1,500,000 + 0 + 4,500,000 + 1,500,000 = 48,300,000` ✓

Acceptance moved the total by exactly `4,500,000 + 1,500,000 = 6,000,000`
(42,300,000 → 48,300,000): the optional lines went from quantity zero to their
governed quantities, and nothing else changed.

The draft invoice is **46,800,000** untaxed — 48,300,000 less the base Scope's
provisional crane (1,500,000), which is gated. No amount appears twice anywhere.

> **CORRECTION (STEP 2B-HARDENING, 2026-09-22).** The original sentence here
> claimed `problems: []` for both Scopes on the strength of
> `evidence/pilot/pilot_result.json` → `reconciliation`. That evidence was a
> dictionary keyed by `display_name`, and **both revisions of this order share
> the same display name**, so one entry overwrote the other and only ONE
> revision was ever present. The claim was not supported by the evidence as
> written.
>
> Regenerated from the retained pilot records, keyed by immutable revision id
> (`reports/sipanel_step2b_hardening_20260922T060000Z/evidence/reconciliation/pilot_reconciliation_by_revision.json`):
>
> | Revision | Quote Scope | Optional | Anchor | Separately billable | Lines | Problems |
> |---:|---:|---|---:|---:|---:|---|
> | **886** | 818 | no | 30,000,000 | 12,300,000 | 2 | `[]` |
> | **887** | 819 | yes, accepted | 0 | 6,000,000 | 2 | `[]` |
>
> `30,000,000 + 12,300,000 + 0 + 6,000,000 = 48,300,000` ✓, matching the order
> total. Both distinct revision records are now present, so the "both Scopes
> reconcile" statement is supported. See
> `SIPANEL_RECONCILIATION_EVIDENCE_CORRECTION.md`.

## 4. What the customer sees versus what is billed

| Component | In the PDF | Billed |
|---|---|---|
| `ناودان گالوانیزه` (included) | yes, as a note bullet under the anchor | inside the anchor price |
| `بست دیواری` (own line) | yes, as its own line | its own line |
| `جرثقیل` (provisional own line) | yes, as its own line, marked provisional | **not yet** — held back from invoicing |
| `درزگیر کارفرما` (customer scope) | **yes** — the customer must know what they supply | **never** |
| `پیچ داخلی` (internal only) | **no** | never |

The customer-scope component being visible is correct and deliberate: it is
`customer_eligible`, so it is disclosed, but `responsibility == 'customer'`
keeps it out of revenue. That pair is exactly what makes the axes orthogonal
rather than a single treatment enum.
