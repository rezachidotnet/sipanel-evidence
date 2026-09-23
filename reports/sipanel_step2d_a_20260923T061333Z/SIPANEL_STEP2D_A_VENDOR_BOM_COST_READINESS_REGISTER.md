# SIPANEL STEP 2D-A — Vendor / BoM / governed-cost readiness register (D2D-A05)

Read-only inventory of database `sipanel` (evidence/master_data_inventory.txt). Nothing was created or changed.
Status vocabulary: READY = real value present with evidence; TBE = value present but looks like a placeholder, to be evaluated by the business;
NEEDS_BUSINESS_DATA = absent. Owner for every business value: Taleghani (uid 2) unless stated.

## A. Products in the gutter pilot chain

| product (tmpl/variant) | category | type / UoM | sale / purchase | route(s) on product | status |
|---|---|---|---|---|---|
| Custom Gutter (62 / 615, 619) | 02 Components / Drainage Components | consu, UoM 9 (Units) | yes / yes | none (no Manufacture, no MTO) | NEEDS_BUSINESS_DATA: route; list_price 1 IRR and standard_price empty are placeholders (TBE) |
| Strip Sheet (36 / 645) | 01 Materials / Metal Raw Materials | consu, UoM 16 | yes / yes | none (no Buy) | NEEDS_BUSINESS_DATA: route, vendor, price; list_price 2 IRR placeholder (TBE) |
| Gutter Installation (38 / 392) نصب آبرو | 04 Services / Installation | service, UoM 9 | yes / yes | n/a | list_price 1 IRR placeholder (TBE); labour cost NEEDS_BUSINESS_DATA |
| Downspout Installation (68 / 649) نصب ناودان | 04 Services / Installation | service, UoM 9 | yes / yes | n/a | same as above |
| Roof Sandwich Panel (158 / 762–767) | 03 Finished / Sandwich Panels | consu, UoM 11 | yes / yes | none on product; only one active template in the DB carries a route (Dropship) | vendor lines exist, see B |

Internal on-hand quantity for variants 645, 615, 619, 762: none (no stock.quant in internal locations). Shared-stock purchase therefore has no opening stock to draw from.

## B. Vendors and supplier prices (product.supplierinfo — the only three records in the database)

| id | vendor | product | vendor product ref | currency | price | UoM | min qty | validity | status |
|---|---|---|---|---|---|---|---|---|---|
| 17 | ماموت پانل (65, supplier_rank 7) | Roof Sandwich Panel 158 / variant 762 | none | IRR (86) | 1.0 | 11 | 1 | none | TBE — price 1.0 IRR is not a real supplier price |
| 18 | غرب پانل (67, supplier_rank 0) | Roof Sandwich Panel 158 / 762 | none | IRR | 2.0 | 11 | 1 | none | TBE — placeholder price |
| 19 | ماهان پانل (60, supplier_rank 3) | Roof Sandwich Panel 158 / 762 | none | IRR | 3.0 | 11 | 1 | none | TBE — placeholder price |
| — | any vendor | Strip Sheet 645 (gutter raw material) | — | — | — | — | — | — | NEEDS_BUSINESS_DATA (no supplierinfo) |
| — | any vendor | gutter accessories / fasteners / sealants (categories 34, 33, 36) | — | — | — | — | — | — | NEEDS_BUSINESS_DATA |

BUY_DIRECT and shared-stock purchase routes: no product in the gutter chain carries the Buy route (route 6 exists, product_selectable = false, so it must be set on the product or via category). NEEDS_BUSINESS_DATA (route decision + governed price).

## C. Bills of materials (mrp.bom — the only record in the database)

| BoM | product | type | qty / UoM | components | operations | status |
|---|---|---|---|---|---|---|
| 8 (no code) | Custom Gutter (62) | normal | 1 / UoM 9 | Strip Sheet (645) qty 1 in UoM 16 | none | TBE — one component with quantity 1 and no dimensional relation (sheet width/length per metre of gutter) is not a fabrication recipe; no operation, so no workcenter time |

MANUFACTURE route: not set on Custom Gutter; Manufacture route (4) exists, product_selectable = false. NEEDS_BUSINESS_DATA (route + real component quantities + scrap factor).

## D. Workcenters (mrp.workcenter)

| workcenter | hourly cost | status |
|---|---|---|
| none exist (count = 0) | — | NEEDS_BUSINESS_DATA: gutter roll-forming / folding workcenter, hourly cost, capacity, efficiency |

## E. Employee / timesheet cost (hr.employee.hourly_cost)

| employee | user | hourly_cost | status |
|---|---|---|---|
| 1 Taleghani | uid 2 | 0.0 | NEEDS_BUSINESS_DATA |
| 2 iliya taleghani | uid 5 | 0.0 | NEEDS_BUSINESS_DATA |
| 19 shahrzad dayyani | uid 10 | 0 | NEEDS_BUSINESS_DATA |
| installation crew (fabricators, installers) | — | none exist | NEEDS_BUSINESS_DATA: employees or a labour-rate product with a governed cost |

Timesheet lines in the database: 2 (both project lines). No timesheet cost has ever been recognised.

## F. Governed selling price / currency

| item | value | status |
|---|---|---|
| company currency | IRR (86) | READY |
| sipanel_scope.company_currency_only | True | READY (design decision) |
| active pricelist | id 2 "Default", IRR | READY (structure); item prices NEEDS_BUSINESS_DATA |

## G. SIPANEL master data for the pilot

| item | value | status |
|---|---|---|
| gutter Commercial Scope | SIPANEL-PT-GUTTER (91) archived; only active Scope is "Commercial Scope Test" (96) | NEEDS_BUSINESS_DATA: a real, released gutter Scope/Recipe |
| analytic plans | 80 System, 81 Activity configured | READY |
| operational analytic accounts (D2D-A02) | none exist yet (no duplicates found) | to be created when unblocked |
| default execution project | sipanel_scope.default_project_id = 55 | READY (structure) |
| stock issue picking type | sipanel_scope.stock_issue_picking_type_id = 91 | READY (structure) |

## Overall

STEP 2D-B cannot start on real data: every commercial value in the gutter chain is absent or a placeholder (prices 1.0/2.0/3.0 IRR, BoM quantity 1, no workcenter, all hourly costs 0). This is independent of the disk block that stopped STEP 2D-A.
