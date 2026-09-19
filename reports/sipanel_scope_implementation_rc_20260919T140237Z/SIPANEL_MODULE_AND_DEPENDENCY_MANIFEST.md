Run sipanel_scope_implementation_rc_20260919T140237Z · Verdict: BLOCKED_NOT_ISOLATED · Status: DESIGN-LEVEL — NOT RUNTIME VALIDATED — no module was written, installed or tested in this run.

# SIPANEL — Module and Dependency Manifest (boundary validated against installed source)

## 1. Validation basis

The five-module structure proposed in the batch instruction was validated **read-only** against the 196 modules installed on `sipanel` (EV-04) and the installed Odoo 19.0-20260528 source (EV-03). Every dependency below is (a) installed on `sipanel` today and (b) the module that actually defines the hook or field the SIPANEL module needs. No dependency is added "for convenience"; no module is installed to satisfy a dependency (in particular **`sale_margin` and `stock_landed_costs` are not dependencies**).

Two boundary corrections came out of source verification:

| ID | Correction | Anchor |
|---|---|---|
| IF-02 | `is_optional`, `_is_line_optional`, `_can_be_edited_on_portal` and the portal route `/my/orders/<id>/update_line_dict` are defined by **`sale_management`**, not `sale`. `sipanel_sale_scope` therefore depends on `sale_management` (installed 19.0.1.0). | SV-02, SV-03 |
| IF-01 | `stock.move.value` is a **field** of `stock.move`; `product.value` is a model; no `stock.valuation.layer`. `sipanel_scope_costing` depends on `stock_account` for both. | SV-09 |

## 2. Modules

| # | Module | Version | Summary | Depends on (all installed on sipanel) | Production? |
|---|---|---|---|---|---|
| 1 | `sipanel_commercial_scope_core` | 19.0.1.0.0 | Scope identity, versions, recipe lines, release gate, audit events, favorites, role groups, company rules, dimensional UoM contract | `base`, `mail`, `product`, `uom`, `analytic` | yes (future, not this run) |
| 2 | `sipanel_sale_scope` | 19.0.1.0.0 | Quote Scope aggregate, revisions, component snapshots, quantity/cost engine, pricing & margin, notes, seal/artifact, optional/provisional governance, portal guard | `sipanel_commercial_scope_core`, `sale_management`, `portal` | yes (future) |
| 3 | `sipanel_scope_execution` | 19.0.1.0.0 | Owner registry, Release action, batches/demands/targets, adapters, LockError retry, amendment/cancel lineage | `sipanel_sale_scope`, `sale_stock`, `sale_project`, `sale_purchase`, `sale_mrp`, `sale_timesheet`, `purchase_stock`, `mrp`, `project`, `hr_timesheet` | yes (future) |
| 4 | `sipanel_scope_costing` | 19.0.1.0.0 | Recognition policy (Finance-signed route matrix), actual-cost projection, allocations, UNALLOCATED, baseline/forecast/actual variance reports | `sipanel_scope_execution`, `stock_account`, `mrp_account`, `account`, `hr_expense`, `project_account` | yes (future) |
| 5 | `sipanel_scope_demo` | 19.0.1.0.0 | C9 synthetic "متعلقات آبرو" fixture, test users, test master data | `sipanel_commercial_scope_core`, `sipanel_sale_scope`, `sipanel_scope_execution`, `sipanel_scope_costing` | **never** — clone/test only; not a dependency of 1–4 |

Transitive native modules pulled by the above are all already installed (`sale`, `stock`, `purchase`, `account`, `hr`, `resource`, `uom`, `web`, `portal`, `website` via `sale_management`/`portal`… see EV-04). No new native module install is required.

## 3. Why each dependency (hook-level justification)

| Module | Dependency | Needed for | Source anchor |
|---|---|---|---|
| core | `product` | canonical `product.product` references in recipe lines; `standard_price` (company-dependent) read at snapshot time | v0.10 review l.95 |
| core | `uom` | `uom.uom` refs; global rounding fact (`_compute_rounding`) forces engine-owned per-line rounding | SV-10 |
| core | `analytic` | System/Activity = `account.analytic.account` under configured `account.analytic.plan` (applicability config) | SV-16 |
| core | `mail` | chatter/tracking on scope, version, audit | native |
| sale_scope | `sale_management` | `is_optional`, `_is_line_optional`, `_can_be_edited_on_portal`, `portal_quote_option_update` route, quotation templates/sections | SV-02, SV-03 |
| sale_scope | `portal` | `CustomerPortal._document_check_access`, portal record-rule pattern, controller inheritance chain | SV-03 |
| sale_scope | (via sale) `sale` | `sale.order` hooks `action_quotation_send/sent`, `action_confirm/_action_confirm`, `copy_data`, `write`, `_get_order_lines_to_report`; `sale.order.line` `parent_id` compute, `_check_line_unlink`, combo/subsection fields | SV-04, SV-05, SV-06, SV-14 |
| execution | `sale_stock` | NATIVE_LINE_OWNER hook `_action_launch_stock_rule`; `stock_reference_ids` | SV-08, SV-13 |
| execution | `sale_project`, `sale_timesheet` | `_timesheet_service_generation`, `service_tracking` values, project/task links; timesheet context | SV-13 |
| execution | `sale_purchase` | `_purchase_service_generation` (native service RFQ owner) | SV-13 |
| execution | `sale_mrp` | kit (`phantom`) explosion ownership `_get_qty_procurement`/`_bom_find` | SV-13 |
| execution | `purchase_stock`, `mrp`, `project`, `hr_timesheet` | adapter targets: `purchase.order(.line)`, `stock.picking/move`, `mrp.production` (+`reference_ids`), `project.task`, `account.analytic.line` timesheets | SV-08, SV-15 |
| costing | `stock_account` | `stock.move.value` field, `_get_value` waterfall, `product.value`, analytic lines from moves | SV-09, SV-15 |
| costing | `mrp_account` | workorder/MO analytic carriers (`mo_/wc_analytic_account_line_ids`) | SV-15 |
| costing | `account` | `account.move.line` for vendor bills/credits, Anglo-Saxon COGS entries | evidence-dated |
| costing | `hr_expense` | expense route (`analytic_distribution` on `hr.expense`) | SV-15 |
| costing | `project_account` | `project.project.account_id` linkage for Project plan | SV-15 |

## 4. Boundary rules (enforced by manifest design)

- No Odoo core patch; no edit under `/usr/lib/python3/dist-packages/odoo` or `/opt/odoo/addons/*` native or third-party code.
- No dependency on `sale_shamsi_report`, `product_percentage_price`, `cyan_crm_reference*`, `sipanel_partner_autocomplete_guard` (they stay untouched; report-hygiene regression is a test, not a code dependency).
- `sipanel_scope_demo` is never listed in `depends` of modules 1–4 and is excluded from any Production addon set.
- Each module ships `security/ir.model.access.csv`, record rules, `tests/` and `migrations/` folders (19.0.1.0.0 has no migration scripts; additive schema only).
- `auto_install: False`, `installable: True`, `license: LGPL-3` (to be confirmed by the repository owner; TBE), `application: False`.

## 5. Manifest skeletons (to be created in the next authorized run — not created now)

```python
# sipanel_commercial_scope_core/__manifest__.py
{'name': 'SIPANEL Commercial Scope Core', 'version': '19.0.1.0.0', 'category': 'Sales',
 'depends': ['base', 'mail', 'product', 'uom', 'analytic'], 'installable': True, 'auto_install': False,
 'data': ['security/groups.xml', 'security/ir.model.access.csv', 'security/record_rules.xml',
          'data/config_parameters.xml', 'views/*.xml'], 'license': 'LGPL-3'}
# sipanel_sale_scope
{'depends': ['sipanel_commercial_scope_core', 'sale_management', 'portal'], ...}
# sipanel_scope_execution
{'depends': ['sipanel_sale_scope', 'sale_stock', 'sale_project', 'sale_purchase', 'sale_mrp',
             'sale_timesheet', 'purchase_stock', 'mrp', 'project', 'hr_timesheet'], ...}
# sipanel_scope_costing
{'depends': ['sipanel_scope_execution', 'stock_account', 'mrp_account', 'account', 'hr_expense', 'project_account'], ...}
# sipanel_scope_demo  (clone/test only)
{'depends': ['sipanel_commercial_scope_core', 'sipanel_sale_scope', 'sipanel_scope_execution', 'sipanel_scope_costing'], 'demo': [...], ...}
```

## 6. Install / upgrade order

Clean install: 1 → 2 → 3 → 4 (→ 5 on clone only). Upgrade from a preceding test build: `-u sipanel_commercial_scope_core` cascades to dependants. Both paths are **NOT_RUN** in this run (BLOCKED_NOT_ISOLATED).

## 7. Release identity

No addon source exists yet; therefore no module checksums, no commit hash, no Release Candidate ZIP. See `SIPANEL_RELEASE_MANIFEST.txt`.
