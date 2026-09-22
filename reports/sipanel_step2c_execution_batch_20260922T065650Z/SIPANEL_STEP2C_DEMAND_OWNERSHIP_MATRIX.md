# SIPANEL STEP 2C — Demand-Ownership Matrix (run 20260922T065650Z)

Invariant: `one component → one operational demand owner → one actual-cost source`.
Source: `evidence/pilot/stage2_release.json` (orders A, A2, B before the fixes) and
`evidence/pilot/stage4_verify_after_fix.json` (A3, C, B2 and the amendments).
"Native record" = a stock move / PO line / task launched by the native Sale line
itself; "SIPANEL demand" = `sipanel.execution.demand`; "downstream" = the record
the adapter created or linked; "cost source" = the single document the actual-cost
projection reads for that component (draft documents produce an `operational`
/ `commitment` event with amount 0 and no allocation until executed).

## 1. After the fixes (source `e01da19`)

| Order | Component (id) | Rev | Placement / mode | Generated revenue line | Operational owner | Native record from generated line | SIPANEL demand | Downstream document | Cost source | Expected / actual / dup | Result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A3 `SI-26/1724` | bracket 20 u | 1676 | own_line / stock_issue | 3332 (20) | COMPONENT_BRIDGE | none (0 moves) | 1512 (created) | picking 786 + move 1124 (draft) | move 1124 | 1 / 1 / 0 | PASS |
| A3 | crane 1 u | 1676 | own_line / equipment_service | 3333 (1) | COMPONENT_BRIDGE | none | 1513 (created) | PO P26200 line 200 (draft) | PO line 200 | 1 / 1 / 0 | PASS |
| A3 | gutter 10 m | 1676 | included / manufacture | — (anchor) | COMPONENT_BRIDGE | none | 1514 (created) | MO 171 (draft, project 97) | MO 171 | 1 / 1 / 0 | PASS |
| A3 | labour 8 h | 1676 | included / labour | — | COMPONENT_BRIDGE | none | 1515 (linked) | project 97 (linked_existing) | project timesheets (none) | 1 / 1 / 0 | PASS |
| C `SI-26/1725` | bracket 20 u | 1677 | own_line / stock_issue | 3335 (20) | COMPONENT_BRIDGE | none | 1516 | picking 787 + move 1127 | move 1127 | 1 / 1 / 0 | PASS (then cancelled) |
| C | crane 1 u | 1677 | own_line / equipment_service | 3336 (1) | COMPONENT_BRIDGE | none | 1517 | PO P26201 line 201 | PO line 201 | 1 / 1 / 0 | PASS |
| C | gutter 10 m | 1677 | included / manufacture | — | COMPONENT_BRIDGE | none | 1518 | MO 172 | MO 172 | 1 / 1 / 0 | PASS |
| C | labour 8 h | 1677 | included / labour | — | COMPONENT_BRIDGE | none | 1519 | project 97 | — | 1 / 1 / 0 | PASS |
| B2 `SI-26/1726` | bracket 20 u (11221) | 1678 | own_line / native_anchor_covered | 3338 (20) | NATIVE_LINE | delivery move 1130 (picking 788) | 1520 (linked) | move 1130 (native_anchor_covered) | move 1130 | 1 / 1 / 0 | PASS |
| B2 | labour 8 h | 1678 | included / native_anchor_covered | — | NATIVE_LINE | anchor task 2749 | 1521 (linked) | task 2749 | task timesheets (none) | 1 / 1 / 0 | PASS |
| A `SI-26/1445` after CO-A | bracket 30 u (c4d8b4e4) | 1380→**1679** | own_line / stock_issue | 2745 (→0) retired, **3339 (30)** | COMPONENT_BRIDGE | none | 1123 (20) + delta 1522 (+10) | picking 600/move 848 + picking 789/move 1131 | moves 848 + 1131 (sum 30) | 30 / 30 / 0 | PASS |
| A after CO-A | crane 1 u | 1679 | own_line / equipment_service | 2746 (→0), 3340 (1) | COMPONENT_BRIDGE | none | 1124 (1) | PO line 164 | PO line 164 | 1 / 1 / 0 | PASS |
| A after CO-A | gutter 10 m | 1679 | included / manufacture | — | COMPONENT_BRIDGE | none | 1125 | MO 126 | MO 126 | 1 / 1 / 0 | PASS |
| A after CO-A | labour 8 h | 1679 | included / labour | — | COMPONENT_BRIDGE | none | 1126 | project 97 | — | 1 / 1 / 0 | PASS |
| B2 after CO-B2 | bracket 30 u | 1678→**1680** | own_line / native_anchor_covered | 3338 (→0, move 1130 cancelled), **3341 (30)** | NATIVE_LINE | move 1132 (30) in picking 788 | 1520 (20) + delta 1523 (+10, linked) | move 1132 | move 1132 | 30 / 30 / 0 | PASS |

Every row: exactly one operational owner, no native record next to a bridge
demand, no bridge document next to a native record, one downstream document per
component (plus one delta document per accepted quantity increase), one cost
source per document, zero duplicates.

## 2. Before the fixes (measured, then corrected)

| Order | Component | Owner | Generated line | Native record | SIPANEL demand | Downstream | Finding |
|---|---|---|---|---|---|---|---|
| A `SI-26/1445` | bracket 20 u (9311) | BRIDGE | 2745 | none | 1123 | picking 600 + move 848 | PASS (unchanged by the fixes) |
| A | crane / gutter / labour | BRIDGE | 2746 / — / — | none | 1124 / 1125 / 1126 | PO line 164 / MO 126 / project 97 | PASS |
| B `SI-26/1447` | bracket 20 u (9319) | NATIVE | 2751 | delivery move 847 | 1121 | **task 2438 (anchor's)** — move 847 not linked | **CD-2C-02** |
| B | labour 8 h (9320) | NATIVE | — | anchor task 2438 | 1122 | task 2438 | PASS |
| A2 `SI-26/1446` | all four | BRIDGE | 2748 / 2749 | none | 1127–1130 `failed` (batch 197) then **batch 198 `released` with 0 demands** | none | **CD-2C-01** |

## 3. Generated Sale Line as revenue projection only

For all 13 generated lines of the pilot (`2745, 2746, 2748, 2749, 2751, 3332,
3333, 3335, 3336, 3338, 3339, 3340, 3341`) the count of native stock moves is 0
under the bridge owner, and exactly 1 (the native owner's own delivery move)
under the native owner; no generated line ever appears as a second owner
alongside a SIPANEL demand for the same component.
