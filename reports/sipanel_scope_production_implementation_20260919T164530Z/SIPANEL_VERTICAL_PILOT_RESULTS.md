Run sipanel_scope_production_implementation_20260919T164530Z · Target: database `sipanel` on container `odoo-sipanel` (Odoo 19.0-20260528) · Build: source commit 99dd874 (fixes on top of 931f949) · Runner: Claude Code (claude-fable-5-1) · Date: 2026-09-19 UTC

# SIPANEL — Vertical Pilot Results: C9 "متعلقات آبرو" (EXECUTED)

| Step | Evidence | Result |
|---|---|---|
| Fixture | `sipanel_scope_demo` installed for the smoke run only (evidence/odoo-smoke.log); synthetic products/plans/partner/project/master V1 released at install (audit event) | created, then module uninstalled; two restrict-protected leftovers archived |
| PT-01 Add Scope 85 m | test_pt01 + pilot test_c9_oracle_from_fixture | direct 10547, derived 187, total 10734 ✔ |
| Customer 12000 | pilot test | revenue 12000 (±0.5 rounding of price_unit), margin 1266, 10.55 % ✔ |
| PT-02 V2 isolation | test_pt02 | V1 snapshot unchanged ✔ |
| PT-06/07 split | test_pt06 / test_pt07 | 10377 / 357; Screw-alone blocked ✔ |
| PT-10 option | test_pt10 | operator + portal transitions on the sealed revision; stale link refused ✔ |
| PT-14/15 release | test_pt14 / test_pt15 | one batch under double click; LockError retry bounded; adapter failure → FAILED batch, no orphan docs ✔ |
| PT-16…PT-21 actuals | test_pt16_pt21_reconciliation | material = gutter issue value (MO cost from coil, no workorder cost configured) + 850 + 340 + 17 + 220; equipment 450; labour 270; revenue 12000 ✔ |
| PT-23/24 security | security suite | ✔ |
| PT-30 | EV-07 | ✔ |

Deviation kept from the previous run: the oracle's gutter value 9000 assumes MO labour/overhead; the fixture BoM has coil only, so the test proves the bridge arithmetic with the real MO value instead of hard-coding 9000. A workcenter-cost fixture would be required to reproduce 11150/850 literally.

Timing: full tagged suite 194–202 s per run; registry load ≈ 40 s; pilot smoke 1.0 s.
