Run sipanel_scope_implementation_rc_20260919T140237Z · Verdict: BLOCKED_NOT_ISOLATED · Status: no module was written, installed or tested in this run; nothing below is a PASS.

# SIPANEL — Rollback Rehearsal Report

## Status of this run

**NOT_RUN.** Nothing was installed, so nothing could be rolled back; no isolated target exists on which a rehearsal could run.

## Rollback regimes (Roadmap "Rollback / recovery", Master C10-D03)

| Regime | When | Method | What it must never do |
|---|---|---|---|
| R1 — before new live business transactions | between module install and the first real quotation/order/invoice created with the extension | restore the matched DB + filestore + code snapshot taken immediately before install, as one consistent set | leave partially sent customer documents or external submissions unreconciled |
| R2 — after live business transactions | any later point | disable the extension's actions through a tested control (menu/group removal, release action disabled, guards left active), preserve data, reconcile open documents, then choose a roll-forward fix or a formally approved recovery with transaction replay | overwrite live invoices/stock/MO history with an old DB; delete posted documents; use native reversal workflows instead |

Principles:

- **Uninstall is not rollback.** Uninstalling `sipanel_*` removes custom models (snapshots, revisions, demand ledger, allocations, audit) and destroys trace (C10-D03).
- **Roll-forward is preferred** once live transactions exist.
- Extension data is additive; native Product Master, contacts and documents are never remapped by install or rollback.

## Required rehearsal steps (next authorized run, on the clone)

1. Take snapshot S0 (DB + filestore + addon checksums) of the clone before install.
2. Install the four modules; create synthetic Scope data (C9 fixture); take snapshot S1.
3. R1 rehearsal: restore S0 over the clone; verify the clone equals S0 (row counts, attachment hashes, ledger totals, absence of `sipanel_*` tables and `ir_module_module` rows) and starts cleanly.
4. Re-install from S1; create a live-like transaction (confirmed order with Scope, one released demand, one posted invoice).
5. R2 rehearsal: disable extension actions via the tested control; confirm ordinary Sales, Purchase, Inventory, MRP and invoicing continue; confirm sealed revisions, artifact hashes and demand links remain readable; confirm no data loss; document the reconciliation list.
6. Verify PT-30 invariants after each step: historical revisions, artifact hashes, allocations and monetary reconciliation intact, not merely "server starts".
7. Record durations (TBE targets), operator, and every discrepancy.

## Evidence to attach

Snapshot manifests with SHA256, before/after row-count tables, ledger equality output, list of disabled controls, screenshots or logs proving ordinary flows work with the extension disabled, and the named rollback owner.

## Result

NOT_RUN. Rollback owner: TBE. No regime has been exercised.
