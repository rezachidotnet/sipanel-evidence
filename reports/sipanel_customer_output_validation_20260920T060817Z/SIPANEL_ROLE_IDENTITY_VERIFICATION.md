# SIPANEL Role and Identity Verification (run 20260920T060817Z)

Read-only resolution on database `sipanel` before any write (`evidence/scripts/preflight.py`, 06:05 UTC).

## Confirmed operational owner / approver

| Attribute | Value |
|---|---|
| Person (management confirmation) | Reza Taleghani |
| Odoo login | `amirmousa1983@gmail.com` |
| `res.users` id | **2** |
| Display name (partner 3) | `Taleghani` |
| Active | yes |
| Internal user (`share`) | internal (`share = False`) |
| Company | Sipanel (id 1, currency IRR) |
| SIPANEL groups | `sipanel_commercial_scope_core.group_scope_steward`, `group_scope_estimator`, `group_scope_cost_viewer`; `sipanel_sale_scope.group_scope_sales`, `group_scope_waiver_sales`, `group_scope_waiver_finance`; `sipanel_scope_costing.group_scope_finance`; `sipanel_scope_execution.group_scope_execution_owner` (8 of 8) |
| Other key groups | `account.group_account_manager` (Accounting Manager), `sales_team.group_sale_manager`, `base.group_system` (Administrator) |
| Roles as used in this run | creator/steward of the temporary master (release), estimator/sales on the quotation, salesperson of `SI-26/312`, cost viewer for the back-office margin evidence, executor of the module upgrade and cleanup |

## Duplicate-identity check

| Match | Result |
|---|---|
| users whose name matches *taleghani* / *طالقانی* or login contains *reza* | id 2 `Taleghani` (target) and id 5 `iliya taleghani` (`test@test.com`) — a different pre-existing account, not the operational owner, **untouched** |
| partners matching the same names | 3 (`Taleghani`, user 2) and 47 (`iliya taleghani`, user 5) |
| new users created in this run | **none** (test users `sipanel_pt_*` exist only inside rolled-back test transactions; count after the run: 0) |
| active internal users on `sipanel` | 7 |

No second Reza/Taleghani account was created, and the same identity is never counted as two approvers.

## Accepted pilot governance limitation (G-01)

For the controlled-pilot stage a single person (user 2) holds every SIPANEL role, including both waiver sides (`group_scope_waiver_sales` **and** `group_scope_waiver_finance`), Steward, Estimator, Execution Owner and Finance, plus Accounting Manager and System Administrator. Joint approvals (BQ-02 waivers, note review vs. release) are therefore approved by one identity. This is recorded as an accepted limitation per the management decision of 2026-09-20, **not** as an implementation blocker. Segregation of duties is deferred until additional users are introduced; the module's group model already supports it without change.

## Actions attributed to user 2 in this run

* release of temporary version 115; creation of quotation `SI-26/312` and `SI-26/313`; sealing via *mark as sent* (audit `seal` events, `sealed_by_id = 2`);
* provisional-basis edit on component 1840; note regeneration/review;
* order cancel and archiving during cleanup (audit `order_cancel`).

Portal-side actions (`update_line_dict`, `/accept` probe) ran as the public user with the order's access token, as a customer would; the resulting audit event records `actor: portal`.
