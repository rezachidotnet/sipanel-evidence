# SIPANEL Invoice Provenance Security (STEP 2B-HARDENING, run 20260922T060000Z)

## 1. The defect

`account.move.line.create()` decided whether a caller could set Scope provenance
(`TRACE_FIELDS`) using two checks, and **both were forgeable**:

```python
if not self.env.context.get('sipanel_from_sale_invoice'):      # (1)
    for vals in vals_list:
        supplied = TRACE_FIELDS & set(vals)
        if supplied and not vals.get('sale_line_ids'):          # (2)
            raise UserError(...)
```

| # | Check | Why it failed |
|---|---|---|
| 1 | a plain context key | any caller can send any context key. `execute_kw` takes a context dictionary as an ordinary argument, so an RPC client could set `sipanel_from_sale_invoice=True` and skip the check entirely |
| 2 | "exempt if `sale_line_ids` is supplied" | `sale_line_ids` is ordinary user-writable data. A caller could point at **any** real generated Sale Line — including someone else's — and inherit the exemption, then write whatever Scope ids they liked |

Either one alone was enough to forge the audit trail that ties invoice revenue
back to a governed Scope component. `sudo()` made no difference, because neither
check was a permission check.

## 2. The correction

Both checks are gone. Authorization is now the process-local guarded token that
the rest of SIPANEL already uses (`sipanel_tools.guard` / `guard_ctx`):

```python
@api.model
def _sipanel_trace_guarded(self):
    return guard(self.env, 'sipanel_invoice_trace')

@api.model_create_multi
def create(self, vals_list):
    if not self._sipanel_trace_guarded():
        for vals in vals_list:
            supplied = TRACE_FIELDS & set(vals)
            if supplied:
                raise UserError(...)
    return super().create(vals_list)
```

`guard()` requires the flag **and** a matching `sipanel_guard_token`, which is a
`uuid4` generated once per Odoo process (`GUARD_TOKEN` in `sipanel_tools`). A
caller cannot send it because it cannot know it.

The genuine path opens the guard for exactly one call:

```python
def _create_invoices(self, grouped=False, final=False, date=None):
    self._sipanel_check_seal_integrity_for_invoice()
    return super(SaleOrder, self.with_context(**guard_ctx('sipanel_invoice_trace')))._create_invoices(
        grouped=grouped, final=final, date=date)
```

so being *inside* `sale.order._create_invoices` — not claiming to be — is what
permits provenance. `write()` uses the same guard and was already correct.

There is no longer any reference to `sipanel_from_sale_invoice` anywhere in the
repository.

## 3. What is now refused

| Attack | Test | Result |
|---|---|---|
| plain create with provenance | `test_plain_create_with_provenance_is_refused` | refused |
| raw `sipanel_invoice_trace=True` context | `test_raw_sipanel_invoice_trace_context_is_refused` | refused |
| raw `sipanel_from_sale_invoice=True` context (the old hatch) | `test_raw_sipanel_from_sale_invoice_context_is_refused` | refused |
| provenance + **real** `sale_line_ids` pointing at a genuine generated line | `test_forged_sale_line_ids_no_longer_exempts_the_payload` | refused |
| `sudo()` | `test_sudo_is_refused` | refused |
| import (`import_file=True`) | `test_import_context_is_refused` | refused |
| guessed token (`sipanel_guard_token='guessed'`) | `test_guessed_token_is_refused` | refused |
| direct `write()` — plain, sudo, raw context, import | `test_direct_write_of_provenance_remains_refused` | refused, and the field stays empty |

## 4. What still works

`test_genuine_invoice_creation_still_carries_full_provenance` runs the real flow
— add Scope, price it, seal, confirm, `_create_invoices()` — and asserts the
resulting invoice line carries **all five** provenance references
(`sipanel_source_revision_id`, `sipanel_source_quote_scope_id`,
`sipanel_source_scope_id`, `sipanel_origin_key`, `sipanel_source_line_id`) and
that the invoice is `draft`.

The broader invoice behaviour is unchanged and still green:
`test_confirmed_order_produces_the_expected_invoice_line`,
`test_invoice_line_carries_source_provenance`,
`test_invoice_description_uses_the_frozen_resolved_translation`,
`test_english_quotation_invoices_in_english`,
`test_included_component_creates_no_invoice_line`,
`test_customer_scope_and_internal_only_create_no_invoice_line`,
`test_provisional_component_creates_no_invoice_line`,
`test_seal_drift_blocks_invoice_creation`.

## 5. Residual note

The guard protects the **provenance fields**, not the invoice itself. A user
with invoice rights can still create an ordinary invoice line by hand — they
simply cannot attach Scope provenance to it, so it will never be counted as
governed Scope revenue. That is the intended boundary: SIPANEL governs its own
audit trail and leaves Accounting's own permissions to Accounting.
