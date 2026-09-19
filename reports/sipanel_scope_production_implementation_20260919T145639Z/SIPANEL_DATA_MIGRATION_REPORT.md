Run sipanel_scope_production_implementation_20260919T145639Z · Verdict: BLOCKED_BEFORE_DATABASE_WRITE · Status: SOURCE WRITTEN AND STATICALLY CHECKED — NOT INSTALLED, NOT RUNTIME VALIDATED (see evidence/EV-02).

# SIPANEL — Data Migration Report

- Initial version of all modules is `19.0.1.0.0`. Schema is **additive only**: new `sipanel_*` tables and nullable columns on `sale_order` (`sipanel_current_seal_hash`, stored computes) and `sale_order_line` (`sipanel_quote_scope_id`, `sipanel_is_anchor`, `sipanel_guard_state`, `sipanel_is_scoped_section`, `sipanel_copied_from_line_id`). No field is added to `product.*`, `uom.uom`, `stock.move`, `stock.move.line` (C0-D06, C0-D11).
- No backfill: existing quotations get no snapshot; `sipanel_has_scopes=False`; ordinary sale lines keep native behaviour (PT-31 test written).
- No `pre-migrate.py` / `post-migrate.py` scripts exist; `migrations/19.0.1.0.0/README.md` in every module records the rule that later versions ship numbered, idempotent scripts.
- Product Master, contacts and telephone numbers are never read or modified by any migration (none exists) and never by module data files (only `ir.config_parameter` keys, groups, draft policy rows, owner-registry defaults, an inactive cron).
- Execution status: **NOT_RUN** (no install happened; see EV-02).
