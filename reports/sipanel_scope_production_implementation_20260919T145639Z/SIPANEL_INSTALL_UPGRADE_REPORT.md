Run sipanel_scope_production_implementation_20260919T145639Z · Verdict: BLOCKED_BEFORE_DATABASE_WRITE · Status: SOURCE WRITTEN AND STATICALLY CHECKED — NOT INSTALLED, NOT RUNTIME VALIDATED (see evidence/EV-02).

# SIPANEL — Install / Upgrade Report

## 1. Result

| Step | Status |
|---|---|
| Deploy modules to `/opt/odoo/addons` (bind-mounted into `odoo-sipanel`) | NOT_RUN (would require sudo rsync into the Production addons path; blocked by the harness classifier — EV-02) |
| Clean install `-i sipanel_commercial_scope_core,sipanel_sale_scope,sipanel_scope_execution,sipanel_scope_costing` on `sipanel` | NOT_RUN |
| Upgrade `-u sipanel_commercial_scope_core` (cascade) | NOT_RUN (no preceding build) |
| Test run `--test-enable --test-tags /sipanel` | NOT_RUN |
| Container restart of `odoo-sipanel` | **NOT restarted**; before/after health not captured because nothing changed |
| Smoke test after restart | NOT_RUN |

## 2. Procedure (ready; only `odoo-sipanel` / `sipanel`)

`scripts/sipanel_install_and_test.sh install` → copies the four Production modules into `/opt/odoo/addons` (rsync, ownership aligned with the existing custom modules), then runs `odoo -d sipanel --no-http --stop-after-init -i <modules>` inside `odoo-sipanel` (a second Odoo process in the same container; the serving process is not restarted by this step). `… test` additionally deploys `sipanel_scope_demo` and runs the tagged tests (`/sipanel`) with `-u`. `… upgrade` runs `-u sipanel_commercial_scope_core`. After install, restart only `odoo-sipanel` (`docker restart odoo-sipanel`), record `docker ps` before/after, then open a quotation and the SIPANEL menu as smoke test. Never restart `odoo-db` or other tenants.

## 3. Memory caution

The host has ~500 MiB available RAM and ~1.9 GiB swap in use (EV-01). A test run (`--test-enable`) in a second process beside the serving worker may take several hundred MiB; run it when the other tenants are idle and watch `free -m`. If an OOM kill of another tenant is observed, stop and revert (see rollback report).

## 4. Post-install configuration (not executed)

1. Settings → SIPANEL Scope: System plan, Activity plan (create the two analytic plans if absent — B-03), release retry count (TBE), stock issue operation type, default execution project.
2. UoM families: tag m, cm, unit, hour (and any recipe unit) in Configuration → UoM Families.
3. Assign groups to user Taleghani per the authorization (steward, estimator, scope sales, waiver sales, waiver finance, execution owner, finance, cost viewer). Record the segregation-of-duties limitation.
4. Finance approves the nine draft recognition policies with source "management authorization 2026-09-19" (menu Configuration → Recognition Policies).
5. Owner registry: review the five default rules.
6. Keep the cron "refresh actual cost projection" inactive unless Finance opts in.
