Run sipanel_scope_production_implementation_20260919T145639Z · Verdict: BLOCKED_BEFORE_DATABASE_WRITE · Status: SOURCE WRITTEN AND STATICALLY CHECKED — NOT INSTALLED, NOT RUNTIME VALIDATED (see evidence/EV-02).

# SIPANEL — Implementation Policy Approval Record

## 1. Authorization source

The implementation baseline below is derived from the **management authorization prompt** pasted into this Claude Code session on 2026-09-19 ("CONTINUE THE SIPANEL IMPLEMENTATION ON THE CURRENT HOST … explicit management authorization to proceed with module development, installation, configuration and controlled runtime testing on the existing SIPANEL database on this host"). The prompt text is reproduced in the session transcript; its operative clauses are summarised here. It is a management authorization, **not a professional statutory tax opinion**: statutory tax/accounting validation remains required before live commercial use.

Authorized target: host 194.5.206.76 · container `odoo-sipanel` · database `sipanel` · repository `/home/ubuntu/sipanel_odoo_addons`. Strict tenant boundary: ahanassa, avizsazeh, shahbazi and every other database are out of scope; `odoo-db` is never restarted or reconfigured; no host-wide Docker operations.

## 2. Business decisions applied (implementation baseline)

| ID | Decision | Where implemented |
|---|---|---|
| BQ-01 = B | customer label per target language; label in the quotation language required at Send | `sipanel.quote.scope._readiness_issues` (LABEL_LANG) |
| BQ-02 = B | joint Finance + Sales approval of commercial waivers | `sipanel.quote.waiver` (two approver groups, state APPROVED only when both set) |
| BQ-03 = A | adjustment after acceptance only through an accepted Change Order | `sipanel.quote.scope.action_accept_change_order`, `revision.change_order_ref` |
| BQ-04 | one terminal recognised-cost event per economic cost | `sipanel.cost.recognition.policy` rows + `sipanel.actual.projection` (natural key per source) |
| BQ-05 = A | explicit Release Execution action | `sale.order.action_sipanel_release_execution` |
| BQ-06 = A | visible UNALLOCATED bucket | `sipanel.actual.cost.event.allocation_state`, variance view `unallocated_cost` / `completeness` |
| BQ-07 = A | project linked, never a parallel task | LABOUR adapter links only; owner rule R4 forbids task-creating tracking for bridge owners |
| BQ-08 = B | MVP scope | AM-05 excluded |
| BQ-09 = A | company-currency-only | `sale.order._sipanel_check_currency`; `fx_rate=1.0`, `fx_source='company_currency'` |
| AM-01-R2 | APPROVED — optional = native qty-state line under an optional section | `is_optional`, `acceptance_state`, governed transition |
| AM-02 | APPROVED — five axes, six presets | component axes + `treatment_preset` |
| AM-03-R1 | APPROVED under the route matrix (§3) | costing policies + projection |
| AM-04 | APPROVED — PERCENT_OF_COST derived, never a purchase source | component engine (`qty_kind='none'`, no demand) |
| AM-05 | DEFERRED, excluded from MVP | no pre-contract actual path |

Numeric thresholds remain **TBE** and live in configuration parameters (`sipanel_scope.release_retry_count`, `cost_stale_days`, `min_margin_pct`, `release_backoff_ms`).

## 3. Finance route policy (management-approved; shipped as DRAFT policy rows to be approved by the Finance role with this record as source)

| Route | Project Actual source (terminal event) | Excluded duplicates |
|---|---|---|
| Shared-stock material | validated issue/consumption to Project at governed inventory cost (`stock.move.value` on the done outgoing move) | PO, receipt, internal transfer, vendor bill for the same material |
| Direct project purchase / dropship | posted vendor-bill allocation after delivery/service acceptance | PO commitment, receipt value, payment |
| Manufacturing | finished-product issue to Project at complete governed production cost | raw material, workorder labour/overhead, timesheets on the MO (feed WIP only) |
| Site labour | payroll actual allocated by approved timesheets (timesheet is the driver) | payroll duplicate; estimated recipe hours are never Actual |
| Third-party equipment/service | posted vendor bill **or** approved employee expense, exactly one | PO commitment |
| Company-owned equipment | approved depreciation / operating-cost allocation | equipment purchase price per project |
| Freight / landed cost | DEFERRED (capitalize when directly attributable; disabled until installed support + accounting configuration pass tests) | expense + later material inclusion |
| Returns / credits | linked reversal of the exact original event | double reversal; deletion of monetary history |

WIP, commitment, operational quantity, cost-to-date, recognised P&L cost, invoiced revenue, recognised revenue and collected cash are kept as separate measures (event `layer`, variance columns).

## 4. Role configuration approved

User **Taleghani** (amirmousa1983@gmail.com) is the initial holder of System Administrator, Product Data Steward, Sales, Purchase, Inventory, Accounting/Finance, Scope Release and Execution Release. Groups are configurable; no user id is hard-coded. Segregation-of-duties limitation recorded in `SIPANEL_SECURITY_AND_ROLE_MATRIX.md` §F. **Not applied in this run** (no database write happened).

## 5. Status of this authorization in this run

Code, tests, documentation and bundle were produced under this authorization. The mandatory recovery point and every database write remained blocked by the Claude Code harness permission classifier (evidence/EV-02), so the run stops at `BLOCKED_BEFORE_DATABASE_WRITE`. The authorization remains valid for the next run once the permission rule is added or the scripts are executed by an operator.
