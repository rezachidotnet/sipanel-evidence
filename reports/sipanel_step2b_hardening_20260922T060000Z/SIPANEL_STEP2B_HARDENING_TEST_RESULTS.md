# SIPANEL STEP 2B-HARDENING Test Results (run 20260922T060000Z)

## 1. Totals

| Suite | Before (STEP 2B) | After hardening |
|---|---|---|
| `sipanel_commercial_scope_core` | 52 | **52** |
| `sipanel_sale_scope` | 119 | **137** (+18) |
| `sipanel_scope_costing` | 5 | **5** |
| `sipanel_scope_execution` | 8 | **8** |
| **SIPANEL total** | **184, 0 failures** | **202, 0 failures** |
| `sale_shamsi_report` | 80, 0 failures | **80, 0 failures** |
| **Grand total** | **264** | **282, 0 failures** |

Logs: `evidence/logs/test_sipanel_hardening.log`,
`evidence/logs/test_shamsi_hardening.log`,
`evidence/logs/test_hardening_only.log` (the 18 new tests in isolation).

`sale_shamsi_report` was not modified: `git status` clean, HEAD `5680013`.

## 2. The 18 new tests

### `TestInvoiceProvenanceAuthorization` (9)

| Test | Asserts |
|---|---|
| `test_plain_create_with_provenance_is_refused` | baseline refusal |
| `test_raw_sipanel_invoice_trace_context_is_refused` | a bare context flag proves nothing |
| `test_raw_sipanel_from_sale_invoice_context_is_refused` | the removed hatch stays removed |
| `test_forged_sale_line_ids_no_longer_exempts_the_payload` | pointing at a **real** generated line confers nothing |
| `test_sudo_is_refused` | the guard is a token, not a permission |
| `test_import_context_is_refused` | `import_file=True` is not authorization |
| `test_guessed_token_is_refused` | a wrong `sipanel_guard_token` fails |
| `test_direct_write_of_provenance_remains_refused` | plain, sudo, raw context and import writes all refused, and the field stays empty |
| `test_genuine_invoice_creation_still_carries_full_provenance` | the real flow keeps all five references and leaves a **draft** invoice |

### `TestPricelistFailsClosed` (5)

| Test | Asserts |
|---|---|
| `test_failed_pricing_leaves_no_governed_price` | error recorded, `sell_price_unit == 0.0`, status `missing` — no `list_price` substitution |
| `test_failed_pricing_blocks_readiness_and_the_seal` | `SB_PRICE_FAILED` blocks; `_sipanel_check_readiness()` raises |
| `test_a_known_zero_reason_cannot_mask_a_pricing_failure` | missing evidence cannot be dressed up as a deliberate zero |
| `test_a_governed_manual_price_clears_the_failure` | a human decision clears it, per component |
| `test_successful_pricing_records_no_error` | the happy path is unaffected |

The remaining 4 of the 18 are the existing `sipanel_sepbill` tests that also
carry the new `sipanel_hardening` tag through their shared fixture class.

## 3. Required coverage confirmed

| Required area | Evidence |
|---|---|
| all SIPANEL module tests | 202, 0 failures |
| `sale_shamsi_report` regression suite | 80, 0 failures |
| STEP 2B security tests | `TestSecurityAndLifecycle` (5) + `TestInvoiceProvenanceAuthorization` (9) |
| quotation → confirmation → draft invoice | `test_genuine_invoice_creation_still_carries_full_provenance`, `test_confirmed_order_produces_the_expected_invoice_line` |
| Persian and English frozen descriptions | `test_invoice_description_uses_the_frozen_resolved_translation`, `test_english_quotation_invoices_in_english` |
| optional accepted / unaccepted | `test_optional_unaccepted_line_is_quantity_zero`, `test_optional_acceptance_gives_the_line_its_governed_quantity`, `test_optional_acceptance_is_idempotent` |
| provisional invoice hold | `test_provisional_line_is_gated_from_invoicing`, `test_provisional_component_creates_no_invoice_line`, `test_resolving_a_provisional_component_lifts_the_gate` |
| duplicate projection / idempotency | `test_repeated_synchronisation_creates_no_duplicate`, `test_database_constraint_refuses_a_second_line_for_one_component`, `test_duplicate_quotation_gets_independent_projected_lines`, `test_amendment_does_not_double_bill_the_same_component` |
| seal-drift invoice gate | `test_seal_drift_blocks_invoice_creation` (plus acceptance and confirmation gates) |

## 4. No assertion was weakened

Two corrections were made to **new** tests during this run; neither loosened an
existing assertion:

| Symptom | Cause | Correction |
|---|---|---|
| `ImportError: cannot import name 'Pricelist'` | guessed the class name of `product.pricelist` | patch the **registry class** `type(self.env['product.pricelist'])`, which does not depend on where Odoo defines it |
| `'SB_PRICE_FAILED' unexpectedly found` after pricing one component | **every** separately-billable component fails while the pricelist is broken — the fail-closed behaviour working correctly | assert per component that *this* component is no longer reported, then price the rest and assert the block clears. This is a **stronger** assertion than the original |

No pre-existing assertion was modified anywhere in this run.

## 5. Iteration record

| Run | Result |
|---|---|
| first full run after the three fixes | 4 errors — all `TestPricelistFailsClosed`, all the wrong patch target |
| `sipanel_hardening` tag only | 1 failure — the per-component assertion above |
| `sipanel_hardening` tag only | **0 failures**, 18 tests |
| full SIPANEL | **0 failures**, 202 tests |
| `sale_shamsi_report` | **0 failures**, 80 tests |
