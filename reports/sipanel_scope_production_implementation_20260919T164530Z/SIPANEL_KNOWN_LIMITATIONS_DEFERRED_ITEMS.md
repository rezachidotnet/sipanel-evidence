Run sipanel_scope_production_implementation_20260919T164530Z · Status: INSTALLED ON sipanel AND RUNTIME-TESTED (49/49 tagged tests green in run #5, C9 pilot smoke green, upgrade green) · runtime source commit 99dd874 · reports/evidence commit 13676e4 · bundle commit cbc246f · reconciled 2026-09-19 (documentation only)

# SIPANEL — Known Limitations and Deferred Items (reconciled with the executed run)

## Resolved in this run (no longer limitations)
- The harness permission blocker of run 20260919T145639Z is obsolete: the recovery point was created and verified, the four modules were installed, the registry validated every view/field/SQL constraint, and all 49 tagged tests plus the pilot test ran green against database `sipanel` (evidence/odoo-install-3.log, odoo-test-5.log, odoo-smoke.log, odoo-upgrade.log).
- View XML, field resolution on native models and the partial unique indexes are runtime-validated (install #3, upgrade, five test runs).

## Current limitations (as built, verified at runtime)
1. PDF artifact creation is best-effort: under the test runner Odoo returns HTML, stored as a `portal_html` artifact; the TEXT artifact (canonical customer payload + hash) is the guaranteed sealed evidence. A manual PDF/Portal inspection on the installed instance (report id 848, `sale_shamsi_report` layout override and duplicate xpath) has **not** been performed.
2. Hash mismatch on confirm is order-wide (`amount_untaxed`/`amount_total` included): any commercial change after send forces a re-send, which creates an amendment automatically.
3. Manual-basis "missing vs zero" uses `manual_qty_set`; a master `manual_qty_default=0` is treated as not set. KNOWN_ZERO cost requires an explicit reason (CD-05: Odoo writes a `product.value` row even for a zero price).
4. MANUFACTURE adapter needs a normal BoM; kit (phantom) parents are native-owned only.
5. BUY_DIRECT / EQUIPMENT_SERVICE need a vendor (`product.supplierinfo`); otherwise the batch persists as FAILED with a redacted summary and no document is created (CD-09, PT-15).
6. Site-labour projection includes every employee timesheet on the linked project; timesheet validation is honoured only if a `validated` field exists (enterprise), otherwise all timesheets count.
7. Company-owned equipment has no automatic projection candidate; Finance allocates manually with a reason.
8. The variance view's UNALLOCATED bucket and completeness are per project, not per scope.
9. The C9 oracle values 11150/850 are not asserted literally: the fixture BoM has coil only, so the reconciliation proves the bridge arithmetic with the real MO value (see pilot results).
10. Failed-batch evidence relies on the caller not raising afterwards; the release button opens the FAILED batch instead of raising.
11. Governed hourly costs and workcenter costs are not configured on `sipanel`; real labour/MO actuals will be zero-valued (flagged `cost_source_zero`) until Finance sets them.
12. Numeric thresholds remain TBE (only `release_retry_count=3` and `company_currency_only=True` are set).

## Governance conditions (why the verdict is CONDITIONAL_GO)
- Statutory tax/accounting validation of the recognition routes is outstanding (the management authorization is not a tax opinion).
- One user (Taleghani) holds every SIPANEL role including both waiver halves and Finance approval; a second independent waiver approver is required for real segregation of duties.
- Manual PDF/Portal inspection (item 1) is outstanding.
- Numeric thresholds and governed hourly/workcenter costs (items 11–12) are outstanding.

## Deferred by decision (unchanged)
Supplier offers, BoM estimated-cost explosion, free formulas, workflow engine, custom stock.move dimensions, fourth analytic plan, Work Package, generic BI, rental asset management, automated provisional settlement, landed cost (GAP-E11; policy row approved with terminal model NONE), foreign-currency quotations (GAP-B18; blocked), combo-child anchors (GAP-C08), shared favorites, pre-contract actuals (AM-05 / GAP-E10).
