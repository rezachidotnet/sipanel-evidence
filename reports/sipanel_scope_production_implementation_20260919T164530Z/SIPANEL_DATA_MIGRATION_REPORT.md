Run sipanel_scope_production_implementation_20260919T164530Z · Status: INSTALLED ON sipanel AND RUNTIME-TESTED (49/49 tagged tests green in run #5, C9 pilot smoke green, upgrade green) — see SIPANEL_TEST_RESULTS_PT01_PT32.md and evidence/. Carried forward from run 20260919T145639Z where unchanged; status lines updated.

# SIPANEL — Data Migration Report

- Initial version of all modules is `19.0.1.0.0`. Schema is **additive only**: new `sipanel_*` tables and nullable columns on `sale_order` (`sipanel_current_seal_hash`, stored computes) and `sale_order_line` (`sipanel_quote_scope_id`, `sipanel_is_anchor`, `sipanel_guard_state`, `sipanel_is_scoped_section`, `sipanel_copied_from_line_id`). No field is added to `product.*`, `uom.uom`, `stock.move`, `stock.move.line` (C0-D06, C0-D11).
- No backfill: existing quotations get no snapshot; `sipanel_has_scopes=False`; ordinary sale lines keep native behaviour (PT-31 test written).
- No `pre-migrate.py` / `post-migrate.py` scripts exist; `migrations/19.0.1.0.0/README.md` in every module records the rule that later versions ship numbered, idempotent scripts.
- Product Master, contacts and telephone numbers are never read or modified by any migration (none exists) and never by module data files (only `ir.config_parameter` keys, groups, draft policy rows, owner-registry defaults, an inactive cron).
- Execution status: **EXECUTED (see this run)** (no install happened; see EV-02).
