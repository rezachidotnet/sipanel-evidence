Run sipanel_scope_implementation_rc_20260919T140237Z · Verdict: BLOCKED_NOT_ISOLATED · Status: no module was written, installed or tested in this run; nothing below is a PASS.

# SIPANEL — Vertical Pilot Results: C9 "متعلقات آبرو"

## Status

**BLOCKED — NOT EXECUTED.** No clone, no source, no fixture data was created. The pilot design below is restated from Master C9 so that the next authorized run has the arithmetic oracle in the same directory as its results. All numbers are **SYNTHETIC TEST DATA** in an artificial currency unit (CU); they are not product facts, engineering consumption rates or financial thresholds (C9-D01).

## Fixture (synthetic oracle)

Scope: gutter run, quantity 85 m, master version V1 released with customer labels; V2 (adds an outlet) exists only to prove version isolation (PT-02). Clone-only customer/project/system; tax and discount zero in the arithmetic base; company currency = quote currency (BQ-09).

| Occurrence | Qty basis | Final qty | Unit cost CU | Total CU | Activity / execution mode |
|---|---|---:|---:|---:|---|
| Gutter | PER_SCOPE_QTY 1 m/m | 85 m | 100 | 8500 | MFG / MANUFACTURE (full cost) |
| Bracket | PER_SCOPE_QTY 2 unit/m | 170 unit | 5 | 850 | INS / STOCK_ISSUE |
| Screw | PER_SCOPE_QTY 4 unit/m | 340 unit | 1 | 340 | INS / STOCK_ISSUE |
| Sealant | MANUAL | 10 cartridge | 20 | 200 | INS / STOCK_ISSUE |
| Installation labour | FIXED | 8 hour | 30 | 240 | INS / LABOUR |
| Base crane service | FIXED | 1 service | 400 | 400 | EQP / EQUIPMENT_SERVICE |
| Quantity allowance screw | PERCENT_OF_QUANTITY 5 % of Screw only | 17 unit | 1 | 17 | INS / STOCK_ISSUE |
| Internal contingency | PERCENT_OF_COST 2 % of Gutter+Bracket only | no demand qty | derived | 187 | GEN / NO_ACTION (non-execution) |

Oracle values:

| Quantity | Value |
|---|---:|
| Direct cost total | 10547 CU |
| Derived cost (contingency) | 187 CU |
| Total estimated cost | 10734 CU |
| Customer total (untaxed) | 12000 CU |
| Estimated margin amount | 1266 CU |
| Estimated margin % | 10.55 % |
| Split oracle (PT-06): source / destination | 10377 / 357 CU, sum 10734 |
| Example explicit reprice after split: source / destination | 11500 / 500 CU, total 12000; margins 1123 / 143, sum 1266 |
| Actual synthetic ledger after execution (PT-21) | Gutter issue 9000 (incl. its raw/labour) + Bracket 850 + Screw/allowance 360 + Sealant 220 + labour 270 + crane 450 = 11150 CU |
| Recognised gross margin on 12000 posted revenue | 850 CU |
| Variance bridge | direct actual 11150 − direct estimate 10547 = +603; unused non-execution contingency −187; net +416 vs baseline 10734 |

Rules the pilot must prove, not assume: contingency has no actual event and is never fabricated as expense; raw material and MO labour that built the Gutter are not added again to 9000; forecast is not substituted for baseline; a split of Screw alone blocks (PT-07).

## Evidence the future run must attach per step

| Step | Required evidence |
|---|---|
| Fixture creation | clone identity, synthetic product ids created on the clone (never Production ids), master V1 release audit event |
| PT-01 Add Scope | snapshot record ids, component table export (redacted), cost 10734, zero execution records query result |
| PT-02 V2 isolation | byte/value diff of V1 snapshot before/after V2 release and cost change |
| PT-06/07 split | lineage ids, source/destination cost, blocked-split error text |
| PT-10 option | operator transition audit, portal `update_line_dict` call log on current sealed revision and on a stale link (rejected), section reorder/delete attempt with anchor unchanged |
| PT-14/15 release | two concurrent Release logs showing one demand key, `LockError` catch + retry log, adapter failure rollback proof (no orphan PO/MO/picking) |
| PT-16…PT-21 actuals | selected native event ids (`stock.move` value field / `product.value` / `account.analytic.line` / vendor bill / timesheet, per SV-09/SV-15/SV-17), exclusion list, reconciliation to 11150 and 850, UNALLOCATED bucket value |
| PT-23/24 security | denied RPC/export/portal attempts with error text per role, sealed-revision write attempts rejected |
| PT-30 | restore rehearsal report cross-reference |
| Timing | task durations recorded; no invented performance threshold (TBE) |

## Result

Not executed. No PASS, FAIL or measured value exists for any pilot step.
