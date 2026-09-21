# SIPANEL Procurement Ownership and Double Counting (STEP 2B, run 20260921T021500Z)

## 1. The frozen ownership architecture already decides this

Ownership is **not** a new decision taken because a Sale Line now exists. It was
already modelled, per component, and this step honours it.

`sipanel.quote.scope.component.execution_owner` (computed, stored):

```python
if c.execution_mode == 'no_action' or c.responsibility == 'customer':
    c.execution_owner = 'none'
elif c.execution_mode == 'native_anchor_covered':
    c.execution_owner = 'native_line_owner'
else:
    c.execution_owner = (c.revision_id.quote_scope_id.source_version_id
                         .anchor_owner_mode or 'component_bridge_owner')
```

and `sipanel.execution.adapter.create_or_link()`:

```python
if demand.owner == 'native_line_owner' and demand.execution_mode != 'native_anchor_covered':
    # NATIVE_LINE_OWNER demands are LINKED only, never CREATED (C8-D01)
    return self._adapt_native_anchor_covered(demand)
```

So:

| `execution_owner` | Who raises operational demand | What SIPANEL execution does |
|---|---|---|
| `native_line_owner` | the native Sale line | links only, never creates |
| `component_bridge_owner` | SIPANEL execution | creates the demand |
| `none` | nobody (customer responsibility, or no action) | nothing |

## 2. What STEP 2B adds

A generated Sale Line is a **commercial** projection. Left alone, Odoo would
treat it like any other line and launch its own stock rule on confirmation —
which, for a `component_bridge_owner` component, would be a **second** owner for
one component: SIPANEL execution creating the demand and native Sale procurement
creating it again.

`sale.order.line._action_launch_stock_rule()` is therefore overridden to skip a
generated line whose component is bridge-owned:

```python
for line in self:
    comp = line.sipanel_source_component_id
    if line.sipanel_is_generated and comp and comp.execution_owner == 'component_bridge_owner':
        continue        # SIPANEL execution owns this component's demand
    native |= line
return super(SaleOrderLine, native)._action_launch_stock_rule(...)
```

A generated line whose component is `native_line_owner` is **not** skipped: there
the native line is the owner by design, and SIPANEL execution only links.

No second owner is ever chosen merely because a Sale Line now exists.

## 3. Result: one component, one demand, one path

Live pilot, Persian order `SI-26/960`, confirmed, with four generated lines:

| Measure | Value |
|---|---:|
| generated Sale Lines | 4 |
| **stock moves originating from generated lines** | **0** |
| stock moves on the order in total | 2 — both from the **anchor** lines |
| purchase orders from the order | 0 |
| manufacturing orders from the order | 0 |
| SIPANEL execution demands | 0 (no execution batch was released in the pilot) |
| emails sent | 0 |

The one picking that exists (`WH/OUT/00056`) contains only anchor-product moves,
tied to sale lines 1763 and 1767, both `sipanel_is_generated = False`. The
generated lines contributed nothing to it.

## 4. Project cost is not double-booked

Cost recognition is untouched by this step. The existing guarantee holds for the
same reason it held before:

* `sipanel.cost.recognition.policy` defines exactly one **terminal** event per
  economic cost per route (`TERMINAL` = `stock.move`, `account.move.line`,
  `account.analytic.line`, `hr.expense`, `mrp.workorder`, `none`), with
  `excluded_models_json` for explicit duplicate exclusions;
* a generated Sale Line adds **revenue**, not cost. It creates no
  `stock.move`, no `purchase.order.line` and no analytic cost line of its own —
  measured above as zero;
* because the bridge-owned line launches no stock rule, shared-stock purchase
  and project consumption keep exactly the routes they had before this step.

Tests: `test_generated_line_does_not_add_a_second_procurement_owner`,
`test_one_component_yields_one_execution_demand` (asserts at most one demand per
component **and** no stock move from a generated line).

## 5. Cancellation

Order cancellation is unchanged and still native: `_action_cancel` logs a Scope
audit event and defers to Odoo, which cancels the downstream picking. In the
pilot the picking moved to `cancel` with the order. No audit provenance was
deleted — the sealed revisions, their artifacts and the generated lines with
their provenance all survive cancellation.

## 6. Honest boundary

The pilot confirmed an order and created a draft invoice, but did **not**
release an execution batch, so the SIPANEL demand-creation path was exercised by
transaction tests rather than by the live pilot. The measurement that matters
for this report — that a generated line raises no native procurement of its own —
was taken live and is zero.
