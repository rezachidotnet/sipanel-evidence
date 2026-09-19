Run sipanel_scope_production_implementation_20260919T164530Z · Status: INSTALLED ON sipanel AND RUNTIME-TESTED (49/49 tagged tests green in run #5, C9 pilot smoke green, upgrade green) — see SIPANEL_TEST_RESULTS_PT01_PT32.md and evidence/. Carried forward from run 20260919T145639Z where unchanged; status lines updated.

# SIPANEL — Module and Dependency Manifest (AS-BUILT)

| # | Module | Version | Path | depends (all installed on `sipanel` per EV-04 of the previous run) | Production? |
|---|---|---|---|---|---|
| 1 | `sipanel_commercial_scope_core` | 19.0.1.0.0 | addons/ | base, mail, product, uom, analytic | yes |
| 2 | `sipanel_sale_scope` | 19.0.1.0.0 | addons/ | sipanel_commercial_scope_core, sale_management (IF-02), portal | yes |
| 3 | `sipanel_scope_execution` | 19.0.1.0.0 | addons/ | sipanel_sale_scope, sale_stock, sale_project, sale_purchase, sale_mrp, sale_timesheet, purchase_stock, mrp, project, hr_timesheet | yes |
| 4 | `sipanel_scope_costing` | 19.0.1.0.0 | addons/ | sipanel_scope_execution, stock_account, mrp_account, account, hr_expense, project_account | yes |
| 5 | `sipanel_scope_demo` | 19.0.1.0.0 | test_addons/ | the four above | **never** (test only; not a dependency of 1–4; excluded from the Production addon set) |

Boundary rules honoured: no Odoo core patch; no edit of native or third-party addons; no dependency on `sale_margin`, `stock_landed_costs`, `sale_shamsi_report`, `product_percentage_price`, `cyan_*`; no field on product/uom/stock.move; ORM/ACL/record rules/chatter only; every model, field, hook and wizard maps to a GAP-ID of the design-level GAP matrix (unchanged from run rc_20260919T140237Z).

Installed-fact corrections carried: IF-01 (`stock.move.value` field; `product.value` model — used in `_product_cost_snapshot_vals` and the projection), IF-02 (`sale_management` dependency; controller override of `portal_quote_option_update`), IF-03 (section/note delete guard in `sale.order.line.unlink`).

Install order: 1 → 2 → 3 → 4 (→ 5 on test only). Status: EXECUTED (see this run).

Source inventory and per-file SHA-256: `SHA256SUMS` and `SIPANEL_RELEASE_MANIFEST.txt`.
