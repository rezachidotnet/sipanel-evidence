# SIPANEL STEP 2D-A — Analytic configuration report (D2D-A02)

Run: 20260923T061333Z — Status: **NOT_EXECUTED** (blocked before the first write). Read-only findings only.

- Plans verified: 80 "SIPANEL System", 81 "SIPANEL Activity"; both referenced by ir.config_parameter (sipanel_scope.system_plan_id / activity_plan_id).
- Duplicate search (name regex over سیستم|آبرو|تأمین|تامین|تدارک|ساخت|نصب, all plans, all companies, active and archived): no match.
  The four permanent accounts (System: سیستم آبرو; Activity: تأمین و تدارک, ساخت, نصب) do not exist in any form and would all have to be created.
- Existing accounts in plans 80/81 are archived synthetic pilot accounts only (ids 1317, 1953 / 249, 250, 1318, 1319, 1954, 2130, 2309). None should be reused: their names carry pilot prefixes.
- Analytic accounts created/reused in this run: none. Analytic lines created: none.
