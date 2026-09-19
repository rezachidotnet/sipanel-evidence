Run sipanel_scope_production_implementation_20260919T164530Z · Status: AS-BUILT from the installed source (commit 99dd874), INSTALLED ON sipanel AND RUNTIME-TESTED (49/49 green).

# SIPANEL — Security and Role Matrix (AS-BUILT, applied on sipanel)

## A. Groups created (privilege 'SIPANEL Commercial Scope'; no user assigned by data files)

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

## B. Access control lists (as installed)

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

## C. Record rules (as installed)

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

## D. Field-level groups, controller guards, internal-flag guard (as installed)

Cost/margin fields carry `groups='sipanel_commercial_scope_core.group_scope_cost_viewer'` (ORM-level: read, search_read, export, reports, chatter). Reason fields are limited to estimator/auditor/cost-viewer/sales groups; audit payloads to cost viewer + auditor. Portal: no ACL on internal models; artifacts readable only for own sealed revisions (rule). Portal quantity transition bound to the current sealed revision id + seal hash (`controllers/portal.py`, template + JS). All internal transaction flags (seal, release, governed transition, note sync, apply price, policy approval, waiver approval, projection) are bound to a process-local token (`sipanel_tools.guard_ctx/guard`, CD-12): a spoofed RPC context cannot unlock them (tested in `test_pt16_pt21_reconciliation`).

## E. Initial role holder (APPLIED on sipanel by `scripts/sipanel_configure.py`, evidence/odoo-configure.log)

User **Taleghani** (login amirmousa1983@gmail.com, internal, active) now holds: Scope Steward, Estimator, Cost & Margin Viewer, Scope Sales, Waiver — Sales approver, Waiver — Finance approver, Execution Owner, Finance (cost recognition) — in addition to the native Administrator/Sales/Purchase/Inventory/Accounting rights already held. No user id, login or e-mail is in any module data file or code; the login is a parameter of the configuration script.

**Acknowledged segregation-of-duties limitation:** one person can create a waiver and approve both its Sales and Finance halves, approve recognition policies, release execution and approve native Purchase/MRP documents. This is a single-person governance limitation, not simulated segregation. Compensating control: every privileged action writes an immutable `sipanel.scope.audit.event` (actor, reason, before/after, correlation uid); roles are configurable groups and can be split to a second person without code changes.

## F. Security tests

Executed: see `SIPANEL_SECURITY_TEST_RESULTS.md` (S-01…S-10 all PASS in run #5).
