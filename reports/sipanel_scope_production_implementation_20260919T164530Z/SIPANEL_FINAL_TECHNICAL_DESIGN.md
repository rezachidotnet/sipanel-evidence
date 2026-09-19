Run sipanel_scope_production_implementation_20260919T164530Z · Status: INSTALLED ON sipanel AND RUNTIME-TESTED (49/49 tagged tests green in run #5, C9 pilot smoke green, upgrade green) — see SIPANEL_TEST_RESULTS_PT01_PT32.md and evidence/. Carried forward from run 20260919T145639Z where unchanged; status lines updated.

# SIPANEL — Final Technical Design (AS-BUILT)

The design-level document `reports/sipanel_scope_implementation_rc_20260919T140237Z/SIPANEL_TECHNICAL_DESIGN_FINAL.md` remains the authoritative narrative (§1–§11). This as-built addendum records where the implementation landed and every deviation.

## 1. Files

| Module | Key files |
|---|---|
| core | `models/sipanel_tools.py` (pure helpers: rounding, presets, hashing, cycle detection), `uom_family.py`, `scope.py`, `scope_version.py` (release R1–R12, lock, checksum, immutability), `recipe_line.py`, `audit_event.py`, `favorite.py`, `res_config_settings.py` (+ `sipanel.config` accessors) |
| sale_scope | `models/quote_scope.py` (aggregate, readiness, governed transition, `_create_from_version`), `quote_scope_revision.py` (freeze, totals, margin, note engine, seal/accept/amend), `quote_scope_component.py` (quantity + cost engine, overrides, snapshot provenance), `artifact.py`, `waiver.py`, `sale_order.py` (send/sent/confirm/copy/currency hooks), `sale_order_line.py` (guards, portal edit, note sync); wizards add_scope, refresh_cost, split_move, apply_price, regenerate_note, treatment_transition, replace_recipe; `controllers/portal.py`; portal template + JS patch |
| execution | `owner_rule.py`, `execution_batch.py` (bounded retry, atomic savepoint), `execution_demand.py` (keys, preflight), `execution_target.py`, `adapters.py` (7 modes), `sale_order.py` (release, amendment delta, cancel guard), `scope_version.py` (R4 hook), `quote_scope.py` (project_id) |
| costing | `recognition_policy.py`, `actual_cost_event.py`, `actual_allocation.py`, `projection.py`, `variance.py` (SQL view), `sale_order.py` |
| demo | `data/fixture_master.xml`, `tests/test_fixture.py` |

## 2. Deviations from the design-level document

| # | Design | As built | Reason |
|---|---|---|---|
| D1 | `acceptance_state` computed from anchor qty + optional section | stored Selection written only by `_transition_acceptance` / Add Scope; `is_optional` stored on the scope | governed transitions must be the only writer; `parent_id` is non-durable (SV-04) |
| D2 | `sipanel.scope.version.project_id` on revision | `project_id` added on `sipanel.quote.scope` by the execution module | `sipanel_sale_scope` must not depend on `project` |
| D3 | Release retry with backoff table | `release_retry_count` × `release_backoff_ms` (linear) | thresholds TBE, both configurable |
| D4 | Portal HTML artifact | only TEXT (canonical payload) + best-effort PDF | rendering in test mode returns HTML; text artifact is deterministic evidence |
| D5 | Candidate policies "inactive" | policy rows in state DRAFT; approval action by Finance records the authorization source | management authorization now exists; signature still a Finance action |
| D6 | Override stale via driver comparison | `override_driver_fp` fingerprint of drivers at override/confirm time | deterministic, auditable |
| D7 | Seal hash | includes order `amount_untaxed/total` ⇒ any commercial change after send forces re-send (auto amendment) | conservative mismatch detection (C3-D03) |
| D8 | Amendment acceptance after confirmation | `action_accept_change_order(ref)` seals + accepts the working revision internally (BQ-03=A) | native re-accept impossible once the order is confirmed |
| D9 | LABOUR adapter | links project (+ native task if any); no task creation | BQ-07=A |
| D10 | Variance completeness | per project (UNALLOCATED events keyed by project) | events without target have only dimensions |

## 3. Installed-fact corrections used

IF-01: `stock.move.value` field read in `projection._from_stock_move`/`_from_production`; `product.value` model queried in `_product_cost_snapshot_vals` for provenance. IF-02: `sale_management` dependency; `portal_quote_option_update` overridden; `_can_be_edited_on_portal` extended. IF-03: `sale.order.line.unlink` guard before `_check_line_unlink`.

## 4. Not designed / deferred

Unchanged (see known limitations).
