Run sipanel_scope_production_implementation_20260919T164530Z · Target: database `sipanel` on container `odoo-sipanel` (Odoo 19.0-20260528) · Build: source commit 99dd874 (fixes on top of 931f949) · Runner: Claude Code (claude-fable-5-1) · Date: 2026-09-19 UTC

# SIPANEL — Install / Upgrade Report (EXECUTED)

| Step | Command (only `odoo-sipanel` / `sipanel`) | Evidence | Result |
|---|---|---|---|
| Deploy | rsync of the four modules into `/opt/odoo/addons` (bind-mounted at `/mnt/extra-addons`), ownership aligned | — | OK |
| Install #1 | `odoo -d sipanel --no-http --stop-after-init -i <4 modules>` | odoo-install.log | FAILED: `Invalid field 'category_id' in 'res.groups'` (CD-01); transaction rolled back, nothing persisted |
| Install #2 | same | odoo-install-2.log | FAILED: external id of the new privilege record (my own patch error); rolled back |
| Install #3 | same | odoo-install-3.log | **OK** — 4 modules loaded (197–200/200), registry 43 s; 2 warnings (CD-02) fixed before the test runs |
| Test runs #1–#5 | `-u <4 modules> --test-enable --test-tags sipanel` (+ demo module deployed, not installed) | odoo-test-1..5.log, 3b/4b targeted | #1 16 failures → #2 7 → #3 3 → #4 1 → **#5 0 / 49** |
| Upgrade | `-u sipanel_commercial_scope_core` (cascades to dependants) | odoo-upgrade.log | **OK**, no warnings |
| Smoke | `-i sipanel_scope_demo --test-enable --test-tags sipanel_pilot` | odoo-smoke.log | **OK** 1/1 |
| Demo removal | `button_immediate_uninstall` of `sipanel_scope_demo` via odoo shell; leftovers archived | odoo-demo-uninstall.log, odoo-demo-leftovers.log | uninstalled; products 7→1 (archived), partner/project/plans removed, scope master archived |
| Configuration | `scripts/sipanel_configure.py` via odoo shell | odoo-configure.log | OK (see §Configuration) |
| Restart | `docker restart odoo-sipanel` only | EV-08 | HTTP 200 after 4 s; JSON-RPC version 19.0; registry smoke OK; other containers untouched; `odoo-db` not restarted |

Installed module versions on `sipanel`: sipanel_commercial_scope_core 19.0.1.0.0, sipanel_sale_scope 19.0.1.0.0, sipanel_scope_execution 19.0.1.0.0, sipanel_scope_costing 19.0.1.0.0 (sipanel_scope_demo: uninstalled). Module count 196 → 200.

## Configuration applied (management-approved)

| Item | Value |
|---|---|
| System plan | account.analytic.plan 80 "SIPANEL System" (created) |
| Activity plan | account.analytic.plan 81 "SIPANEL Activity" (created) |
| UoM families | 14 mappings: m/cm/km/mm=length, Units/Dozens=count, Hours/Days=time, kg/g/Ton=mass, L/m³=volume, m²=area |
| Stock-issue operation type | stock.picking.type 91 "SIPANEL Site Issue" (internal, WH/Stock → location "SIPANEL Site", usage customer) — created |
| Default execution project | project.project 55 "SIPANEL Execution (default)" — created |
| Numeric thresholds | left TBE (only `release_retry_count=3` shipped default; `company_currency_only=True`) |
| Recognition policies | 9 rows APPROVED by the Finance role holder with source "Management authorization 2026-09-19 …; statutory tax/accounting validation still required"; freight/landed cost row has terminal model NONE (deferred) |
| Foreign-currency Scope quotations | blocked (`company_currency_only=True`) |
| Roles | user Taleghani (id 2) received the 8 SIPANEL groups (see security matrix §E) |

Memory during runs: 100–250 MiB free, 500–690 MiB available; no OOM event; all tenant containers stayed Up (EV-08).
