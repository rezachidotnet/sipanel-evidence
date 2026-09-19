Run sipanel_scope_production_implementation_20260919T145639Z · Verdict: BLOCKED_BEFORE_DATABASE_WRITE · Status: SOURCE WRITTEN AND STATICALLY CHECKED — NOT INSTALLED, NOT RUNTIME VALIDATED (see evidence/EV-02).

# SIPANEL — Backup / Restore / Rollback Report

| Item | Status |
|---|---|
| Pre-change recovery point | NOT CREATED (see SIPANEL_PRE_CHANGE_RECOVERY_POINT_REPORT.md) |
| Restore rehearsal (PT-30) | NOT_RUN |
| Rollback rehearsal | NOT_RUN — nothing was installed, so there is nothing to roll back; `odoo-sipanel` was not restarted; `/opt/odoo/addons` unchanged |
| Other tenants / `odoo-db` | untouched (no command reached them; EV-01/EV-02) |

## Rollback procedure for the next run (module-level, no other tenant affected)

1. Stop only `odoo-sipanel` (`docker stop odoo-sipanel`).
2. Restore database `sipanel` from `<recovery point>/sipanel.dump` (`pg_restore -U odoo -d sipanel --clean --if-exists` executed inside `odoo-db` against database `sipanel` only), restore the filestore directory from `filestore-sipanel.tar.gz`, restore `/opt/odoo/addons` from `addons.tar.gz` (removes the `sipanel_*` module folders).
3. Start `odoo-sipanel`; verify `docker ps`, log in, open a quotation; confirm `ir_module_module` has no `sipanel_*` rows.
4. Uninstall is **not** rollback (C10-D03): uninstalling the modules removes SIPANEL tables and history; only the recovery point restores the pre-change state.
