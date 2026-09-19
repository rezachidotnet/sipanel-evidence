Run sipanel_scope_production_implementation_20260919T145639Z · Verdict: BLOCKED_BEFORE_DATABASE_WRITE · Status: SOURCE WRITTEN AND STATICALLY CHECKED — NOT INSTALLED, NOT RUNTIME VALIDATED (see evidence/EV-02).

# SIPANEL — Vertical Pilot Results: C9 "متعلقات آبرو"

## Status: **BLOCKED — NOT EXECUTED** (no database access; EV-02).

The fixture now exists in two forms: (a) `test_addons/sipanel_scope_demo/data/fixture_master.xml` (synthetic products, plans, master V1 released at install, quotation qty 85 m via the pilot test), (b) the shared test fixture `sipanel_commercial_scope_core/tests/common.py::_make_master` used by every suite. All numbers are SYNTHETIC in an artificial currency unit; prefix SIPANEL-PT; no real contact is used.

Oracle asserted by the written tests:

| Quantity | Oracle | Asserting test |
|---|---|---|
| Direct cost | 10547 | test_pt01, test_c9_oracle_from_fixture |
| Derived (contingency 2 % of Gutter+Bracket) | 187 | same |
| Total estimated cost | 10734 | same |
| Customer total 12000 → margin 1266 / 10.55 % | 1266 / 10.55 | test_c9_oracle_from_fixture, test_pt27 (Apply Price) |
| Split Screw + allowance | 10377 / 357 | test_pt06 |
| Actual ledger: bracket 850, screw+allowance 360, sealant 220, crane 450, labour 270, gutter issue value | structural bridge: (actual − direct estimate) − 187 = actual − 10734 | test_pt16_pt21_reconciliation |
| Recognised revenue 12000 | 12000 | same |

Deviation recorded: the gutter's actual issue value in the test comes from the MO cost (coil 60/m, no workorder cost) rather than the oracle's 9000 (which assumes labour/overhead inside the MO); the test asserts the bridge arithmetic with the real MO value instead of hard-coding 9000, so the invariant "parent full value counted once" is proven without fabricating an MO labour cost. The oracle 11150 / 850 therefore remains a documentary target for a fixture with configured workcenter costs.

Evidence per step: none (not executed).
