Run sipanel_scope_production_implementation_20260919T164530Z · Status: INSTALLED ON sipanel AND RUNTIME-TESTED (49/49 tagged tests green in run #5, C9 pilot smoke green, upgrade green) — see SIPANEL_TEST_RESULTS_PT01_PT32.md and evidence/. Carried forward from run 20260919T145639Z where unchanged; status lines updated.

# SIPANEL — Known Limitations and Deferred Items

## Blockers of this run
1. **Harness permission**: every Production DB/config access denied ⇒ no recovery point, no install, no tests, no pilot, no rollback rehearsal (EV-02). Remedy: permission rule or operator-run scripts.

## Implementation limitations (as built, to be verified at runtime)
2. Statically checked only: view XML validity against Odoo 19 (`<chatter/>`, `column_invisible`, settings blocks), field resolution on native models and SQL constraints have not been loaded by a registry.
3. PDF artifact creation is best-effort (`_render_qweb_pdf` wrapped in try/except); the TEXT artifact (canonical customer payload + hash) is the guaranteed sealed evidence. In test mode Odoo returns HTML instead of PDF.
4. Portal HTML artifact kind is defined but not generated in MVP.
5. Hash mismatch on confirm is order-wide (amount_untaxed/total included): any commercial change after send requires a re-send (automatic amendment on re-send).
6. Manual-basis "missing vs zero" uses `manual_qty_set`; master `manual_qty_default=0` is treated as not set.
7. MANUFACTURE adapter needs a normal BoM; kit (phantom) parents are native-owned only.
8. BUY_DIRECT needs a vendor (`product.supplierinfo`); otherwise the batch fails atomically (by design, PT-15).
9. Site-labour projection includes every employee timesheet on the linked project; timesheet validation is honoured only if a `validated` field exists (enterprise), else all timesheets count.
10. Company-owned equipment allocation has no automatic candidate; Finance allocates manually.
11. `sipanel.scope.variance` unallocated bucket is per project (not per scope); completeness is project-wide.
12. Portal JS patch depends on the export name `SaleUpdateLineButton` of `sale_management`; verified in the extracted source (`static/src/interactions/sale_update_line_button.js`).
13. C9 oracle 11150/850 not asserted literally (see pilot report deviation).

## Deferred by decision (unchanged)
Supplier offers, BoM estimated-cost explosion, free formulas, workflow engine, custom stock.move dimensions, fourth analytic plan, Work Package, generic BI, rental asset management, automated provisional settlement, landed cost (GAP-E11), foreign-currency quotations (GAP-B18), combo-child anchors (GAP-C08), shared favorites, pre-contract actuals (AM-05 / GAP-E10).

## Configuration prerequisites (B-01, B-03, B-09)
System/Activity analytic plans; UoM family tags; stock-issue operation type; default project; governed hourly costs; report id 848 decision; `sale_shamsi_report` duplicate xpath fix request to its owner.
