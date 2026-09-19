Run sipanel_scope_production_implementation_20260919T145639Z · Verdict: BLOCKED_BEFORE_DATABASE_WRITE · Status: SOURCE WRITTEN AND STATICALLY CHECKED — NOT INSTALLED, NOT RUNTIME VALIDATED (see evidence/EV-02).

# SIPANEL — Security and Role Matrix (AS-BUILT)

## A. Groups created (no user assigned by data files)

| XML id | Name | Implies |
|---|---|---|
| `sipanel_commercial_scope_core.group_scope_cost_viewer` | Cost &amp; Margin Viewer | base.group_user |
| `sipanel_commercial_scope_core.group_scope_steward` | Scope Steward | base.group_user |
| `sipanel_commercial_scope_core.group_scope_estimator` | Estimator | base.group_user, group_scope_cost_viewer |
| `sipanel_commercial_scope_core.group_scope_auditor` | Auditor (read-only) | base.group_user |
| `sipanel_sale_scope.group_scope_sales` | Scope Sales | sales_team.group_sale_salesman |
| `sipanel_sale_scope.group_scope_waiver_sales` | Waiver — Sales approver | sales_team.group_sale_manager |
| `sipanel_sale_scope.group_scope_waiver_finance` | Waiver — Finance approver | account.group_account_manager |
| `sipanel_scope_execution.group_scope_execution_owner` | Execution Owner | base.group_user |
| `sipanel_scope_costing.group_scope_finance` | Finance (cost recognition) | account.group_account_manager, sipanel_commercial_scope_core.group_scope_cost_viewer |

## B. Access control lists (ir.model.access.csv, as shipped)

| Module | Model | Group | R | W | C | U |
|---|---|---|---|---|---|---|
| sipanel_commercial_scope_core | sipanel.scope | group_scope_steward | 1 | 1 | 1 | 1 |
| sipanel_commercial_scope_core | sipanel.scope | group_scope_estimator | 1 | 0 | 0 | 0 |
| sipanel_commercial_scope_core | sipanel.scope | base.group_user | 1 | 0 | 0 | 0 |
| sipanel_commercial_scope_core | sipanel.scope.version | group_scope_steward | 1 | 1 | 1 | 1 |
| sipanel_commercial_scope_core | sipanel.scope.version | base.group_user | 1 | 0 | 0 | 0 |
| sipanel_commercial_scope_core | sipanel.scope.recipe.line | group_scope_steward | 1 | 1 | 1 | 1 |
| sipanel_commercial_scope_core | sipanel.scope.recipe.line | base.group_user | 1 | 0 | 0 | 0 |
| sipanel_commercial_scope_core | sipanel.scope.audit.event | base.group_user | 1 | 0 | 1 | 0 |
| sipanel_commercial_scope_core | sipanel.scope.favorite | base.group_user | 1 | 1 | 1 | 1 |
| sipanel_commercial_scope_core | sipanel.uom.family | base.group_user | 1 | 0 | 0 | 0 |
| sipanel_commercial_scope_core | sipanel.uom.family | group_scope_steward | 1 | 1 | 1 | 1 |
| sipanel_commercial_scope_core | sipanel.uom.family | base.group_system | 1 | 1 | 1 | 1 |
| sipanel_sale_scope | sipanel.quote.scope | base.group_user | 1 | 0 | 0 | 0 |
| sipanel_sale_scope | sipanel.quote.scope | group_scope_sales | 1 | 1 | 1 | 0 |
| sipanel_sale_scope | sipanel.quote.scope | sipanel_commercial_scope_core.group_scope_estimator | 1 | 1 | 1 | 0 |
| sipanel_sale_scope | sipanel.quote.scope | sales_team.group_sale_manager | 1 | 1 | 1 | 1 |
| sipanel_sale_scope | sipanel.quote.scope.revision | base.group_user | 1 | 0 | 0 | 0 |
| sipanel_sale_scope | sipanel.quote.scope.revision | group_scope_sales | 1 | 1 | 1 | 0 |
| sipanel_sale_scope | sipanel.quote.scope.revision | sipanel_commercial_scope_core.group_scope_estimator | 1 | 1 | 1 | 0 |
| sipanel_sale_scope | sipanel.quote.scope.revision | sales_team.group_sale_manager | 1 | 1 | 1 | 1 |
| sipanel_sale_scope | sipanel.quote.scope.component | base.group_user | 1 | 0 | 0 | 0 |
| sipanel_sale_scope | sipanel.quote.scope.component | group_scope_sales | 1 | 1 | 1 | 0 |
| sipanel_sale_scope | sipanel.quote.scope.component | sipanel_commercial_scope_core.group_scope_estimator | 1 | 1 | 1 | 1 |
| sipanel_sale_scope | sipanel.quote.scope.component | sales_team.group_sale_manager | 1 | 1 | 1 | 1 |
| sipanel_sale_scope | sipanel.quote.scope.artifact | base.group_user | 1 | 0 | 0 | 0 |
| sipanel_sale_scope | sipanel.quote.scope.artifact | group_scope_sales | 1 | 0 | 1 | 0 |
| sipanel_sale_scope | sipanel.quote.scope.artifact | base.group_portal | 1 | 0 | 0 | 0 |
| sipanel_sale_scope | sipanel.quote.waiver | base.group_user | 1 | 0 | 0 | 0 |
| sipanel_sale_scope | sipanel.quote.waiver | group_scope_sales | 1 | 1 | 1 | 0 |
| sipanel_sale_scope | sipanel.quote.waiver | sipanel_commercial_scope_core.group_scope_estimator | 1 | 1 | 1 | 0 |
| sipanel_sale_scope | sipanel.quote.waiver | group_scope_waiver_sales | 1 | 1 | 1 | 0 |
| sipanel_sale_scope | sipanel.quote.waiver | group_scope_waiver_finance | 1 | 1 | 1 | 0 |
| sipanel_sale_scope | sipanel.wizard.add.scope | base.group_user | 1 | 1 | 1 | 1 |
| sipanel_sale_scope | sipanel.wizard.refresh.cost | base.group_user | 1 | 1 | 1 | 1 |
| sipanel_sale_scope | sipanel.wizard.refresh.cost.line | base.group_user | 1 | 1 | 1 | 1 |
| sipanel_sale_scope | sipanel.wizard.split.move | base.group_user | 1 | 1 | 1 | 1 |
| sipanel_sale_scope | sipanel.wizard.split.move.line | base.group_user | 1 | 1 | 1 | 1 |
| sipanel_sale_scope | sipanel.wizard.apply.price | base.group_user | 1 | 1 | 1 | 1 |
| sipanel_sale_scope | sipanel.wizard.regenerate.note | base.group_user | 1 | 1 | 1 | 1 |
| sipanel_sale_scope | sipanel.wizard.treatment.transition | base.group_user | 1 | 1 | 1 | 1 |
| sipanel_sale_scope | sipanel.wizard.replace.recipe | base.group_user | 1 | 1 | 1 | 1 |
| sipanel_scope_execution | sipanel.execution.owner.rule | base.group_user | 1 | 0 | 0 | 0 |
| sipanel_scope_execution | sipanel.execution.owner.rule | base.group_system | 1 | 1 | 1 | 1 |
| sipanel_scope_execution | sipanel.execution.owner.rule | group_scope_execution_owner | 1 | 1 | 1 | 0 |
| sipanel_scope_execution | sipanel.execution.batch | base.group_user | 1 | 0 | 0 | 0 |
| sipanel_scope_execution | sipanel.execution.batch | group_scope_execution_owner | 1 | 1 | 1 | 0 |
| sipanel_scope_execution | sipanel.execution.demand | base.group_user | 1 | 0 | 0 | 0 |
| sipanel_scope_execution | sipanel.execution.demand | group_scope_execution_owner | 1 | 1 | 1 | 0 |
| sipanel_scope_execution | sipanel.execution.target | group_scope_execution_owner | 1 | 1 | 1 | 0 |
| sipanel_scope_execution | sipanel.execution.target | sipanel_commercial_scope_core.group_scope_steward | 1 | 0 | 0 | 0 |
| sipanel_scope_execution | sipanel.execution.target | sipanel_commercial_scope_core.group_scope_estimator | 1 | 0 | 0 | 0 |
| sipanel_scope_execution | sipanel.execution.target | sipanel_commercial_scope_core.group_scope_auditor | 1 | 0 | 0 | 0 |
| sipanel_scope_execution | sipanel.execution.target | sipanel_commercial_scope_core.group_scope_cost_viewer | 1 | 0 | 0 | 0 |
| sipanel_scope_costing | sipanel.cost.recognition.policy | sipanel_commercial_scope_core.group_scope_cost_viewer | 1 | 0 | 0 | 0 |
| sipanel_scope_costing | sipanel.cost.recognition.policy | sipanel_commercial_scope_core.group_scope_auditor | 1 | 0 | 0 | 0 |
| sipanel_scope_costing | sipanel.cost.recognition.policy | group_scope_finance | 1 | 1 | 1 | 0 |
| sipanel_scope_costing | sipanel.actual.cost.event | sipanel_commercial_scope_core.group_scope_cost_viewer | 1 | 0 | 0 | 0 |
| sipanel_scope_costing | sipanel.actual.cost.event | sipanel_commercial_scope_core.group_scope_auditor | 1 | 0 | 0 | 0 |
| sipanel_scope_costing | sipanel.actual.cost.event | sipanel_scope_execution.group_scope_execution_owner | 1 | 0 | 0 | 0 |
| sipanel_scope_costing | sipanel.actual.cost.event | group_scope_finance | 1 | 1 | 1 | 1 |
| sipanel_scope_costing | sipanel.actual.allocation | sipanel_commercial_scope_core.group_scope_cost_viewer | 1 | 0 | 0 | 0 |
| sipanel_scope_costing | sipanel.actual.allocation | sipanel_commercial_scope_core.group_scope_auditor | 1 | 0 | 0 | 0 |
| sipanel_scope_costing | sipanel.actual.allocation | sipanel_scope_execution.group_scope_execution_owner | 1 | 0 | 0 | 0 |
| sipanel_scope_costing | sipanel.actual.allocation | group_scope_finance | 1 | 1 | 1 | 1 |
| sipanel_scope_costing | sipanel.scope.variance | sipanel_commercial_scope_core.group_scope_cost_viewer | 1 | 0 | 0 | 0 |
| sipanel_scope_costing | sipanel.scope.variance | sipanel_commercial_scope_core.group_scope_auditor | 1 | 0 | 0 | 0 |
| sipanel_scope_costing | sipanel.scope.variance | sipanel_commercial_scope_core.group_scope_estimator | 1 | 0 | 0 | 0 |

Note: `model_x_y` ids are rendered with dots; `sipanel_quote_scope` = `sipanel.quote.scope` etc. Portal users have no ACL on any SIPANEL model except read on `sipanel.quote.scope.artifact` restricted by record rule to their own sealed artifacts.

## C. Record rules (as shipped)

| Module | Rule id | Model | Groups | Domain |
|---|---|---|---|---|
| sipanel_commercial_scope_core | `rule_scope_company` | sipanel.scope | global | `[('company_id', 'in', company_ids)]` |
| sipanel_commercial_scope_core | `rule_scope_version_company` | sipanel.scope.version | global | `[('company_id', 'in', company_ids)]` |
| sipanel_commercial_scope_core | `rule_scope_version_released_for_non_steward` | sipanel.scope.version | base.group_user | `['&#124;', ('state', '!=', 'draft'), '&#124;', ('create_uid', '=', user.id), ('scope_id.owner_user_id', '=', user.id)]` |
| sipanel_commercial_scope_core | `rule_scope_version_steward_all` | sipanel.scope.version | group_scope_steward, group_scope_auditor, group_scope_estimator | `[(1, '=', 1)]` |
| sipanel_commercial_scope_core | `rule_recipe_line_company` | sipanel.scope.recipe.line | global | `[('company_id', 'in', company_ids)]` |
| sipanel_commercial_scope_core | `rule_audit_event_company` | sipanel.scope.audit.event | global | `[('company_id', 'in', company_ids)]` |
| sipanel_commercial_scope_core | `rule_favorite_own` | sipanel.scope.favorite | global | `[('user_id', '=', user.id)]` |
| sipanel_sale_scope | `rule_quote_scope_company` | sipanel.quote.scope | global | `[('company_id', 'in', company_ids)]` |
| sipanel_sale_scope | `rule_quote_scope_revision_company` | sipanel.quote.scope.revision | global | `[('company_id', 'in', company_ids)]` |
| sipanel_sale_scope | `rule_quote_scope_component_company` | sipanel.quote.scope.component | global | `[('company_id', 'in', company_ids)]` |
| sipanel_sale_scope | `rule_artifact_company` | sipanel.quote.scope.artifact | base.group_user | `[('company_id', 'in', company_ids)]` |
| sipanel_sale_scope | `rule_waiver_company` | sipanel.quote.waiver | global | `[('company_id', 'in', company_ids)]` |
| sipanel_sale_scope | `rule_quote_scope_sales_own` | sipanel.quote.scope | sales_team.group_sale_salesman | `['&#124;', ('order_id.user_id', '=', user.id), ('order_id.user_id', '=', False)]` |
| sipanel_sale_scope | `rule_quote_scope_sales_all` | sipanel.quote.scope | sales_team.group_sale_salesman_all_leads, sales_team.group_sale_manager, sipanel_commercial_scope_core.group_scope_estimator, sipanel_commercial_scope_core.group_scope_auditor, sipanel_commercial_scope_core.group_scope_steward | `[(1, '=', 1)]` |
| sipanel_sale_scope | `rule_portal_artifact_own` | sipanel.quote.scope.artifact | base.group_portal | `[('revision_id.quote_scope_id.order_id.partner_id', 'child_of', user.partner_id.commercial_partner_id.id), ('revision_id.state', 'in', ['sent_sealed', 'accepted_sealed'])]` |
| sipanel_scope_execution | `rule_batch_company` | sipanel.execution.batch | global | `[('company_id', 'in', company_ids)]` |
| sipanel_scope_execution | `rule_demand_company` | sipanel.execution.demand | global | `[('company_id', 'in', company_ids)]` |
| sipanel_scope_execution | `rule_target_company` | sipanel.execution.target | global | `[('company_id', 'in', company_ids)]` |
| sipanel_scope_execution | `rule_owner_rule_company` | sipanel.execution.owner.rule | global | `[('company_id', 'in', company_ids)]` |
| sipanel_scope_costing | `rule_policy_company` | sipanel.cost.recognition.policy | global | `[('company_id', 'in', company_ids)]` |
| sipanel_scope_costing | `rule_event_company` | sipanel.actual.cost.event | global | `[('company_id', 'in', company_ids)]` |
| sipanel_scope_costing | `rule_alloc_company` | sipanel.actual.allocation | global | `[('company_id', 'in', company_ids)]` |
| sipanel_scope_costing | `rule_variance_company` | sipanel.scope.variance | global | `[('company_id', 'in', company_ids)]` |

## D. Field-level groups (as shipped)

Cost/margin fields (`unit_cost`, `cost_uom_*`, `cost_source_date`, `cost_source_company_id`, `product_value_id`, `manual_cost_*`, `cost_amount`, `stale_cost`, `direct_cost_total`, `derived_cost_total`, `eligible_cost_total`, `offered_cost_total`, `net_revenue_projection`, `margin_amount`, `margin_percent`, `margin_percent_na`, `sipanel_total_cost`, `sipanel_total_margin`, apply-price previews, all variance columns) carry `groups='sipanel_commercial_scope_core.group_scope_cost_viewer'`, so `read`, `search_read`, `export_data`, reports and chatter honour the restriction at ORM level (PT-23 / S-07). Reason fields (`override_reason`, `manual_cost_reason`, `known_zero_reason`, waiver `reason`) are limited to estimator/auditor/cost-viewer/sales groups. Audit `before_json`/`after_json` are limited to cost viewer + auditor.

## E. Controller / RPC / leakage guards (as shipped)

| Surface | Guard (file) |
|---|---|
| `/my/orders/<id>/update_line_dict` | `sipanel_sale_scope/controllers/portal.py`: Scope anchors are routed through `sipanel.quote.scope._transition_acceptance(actor='portal', revision_id, seal_hash)`; stale link ⇒ generic `{'error': 'stale_link'}`; non-scope lines fall through to native. |
| `sale.order.line._can_be_edited_on_portal` | override: anchors editable only when the scope is optional and the current revision is SENT_SEALED. |
| Portal template | `views/sale_portal_templates.xml` injects `data-sipanel-revision-id` / `data-sipanel-seal-hash`; `static/src/interactions/sipanel_update_line_button.js` sends them. |
| Sealed revision / released version mutation | Python `write`/`unlink`/`create` guards (models), not ACL-only ⇒ import/RPC/sudo cannot bypass (PT-24). |
| Section reorder/delete | `sale.order.line.write/unlink` guards on scoped sections and anchors while sealed (IF-03). |
| Company currency | `sale.order._sipanel_check_currency` on add/send/confirm/write of currency or pricelist (BQ-09). |
| Logging / errors | batch `error_summary` redacts e-mails and phone-like numbers; portal errors generic. |

## F. Initial role holder and segregation-of-duties limitation (documentary; NOT applied — no DB write happened)

Management authorized the existing internal user **Taleghani** (login amirmousa1983@gmail.com) as initial holder of System Administrator, Product Data Steward (`group_scope_steward`), Sales (`group_scope_sales` + native), Purchase, Inventory, Accounting/Finance (`group_scope_finance`, `group_scope_waiver_finance`, `group_scope_waiver_sales`), Scope Release (`group_scope_estimator`), Execution Release (`group_scope_execution_owner`). No user id, login or e-mail is written in any data file or code; the assignment is a post-install configuration step (runbook in `SIPANEL_INSTALL_UPGRADE_REPORT.md` §4) that was **not executed** in this run.

Because one person holds Sales, Finance, Purchase, Inventory, Execution and Administration simultaneously, the joint waiver (BQ-02=B), Finance policy approval (BQ-04), Release Execution and native approvals are all exercisable by one person. This is an **acknowledged single-person governance limitation**, not simulated segregation. Compensating control: every privileged action writes an immutable `sipanel.scope.audit.event` with actor, reason and correlation uid; groups are configurable so roles can be separated later without code changes.

## G. Security tests (written, NOT EXECUTED)

See `SIPANEL_SECURITY_TEST_RESULTS.md`.
