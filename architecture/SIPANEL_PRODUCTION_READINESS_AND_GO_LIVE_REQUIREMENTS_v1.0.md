# SIPANEL Odoo 19 — Production Readiness & Go-Live Requirements v1.0

**Document status:** CONTROLLED READINESS SPECIFICATION  
**Architecture baseline:** SIPANEL Commercial Scope / Recipe / Estimation v0.12  
**Target:** Odoo `19.0-20260528 Community` — database `sipanel`  
**Prepared:** 2026-09-19  
**Authorization:** This document is **not** permission to write code, install a module, change configuration, create a clone, or modify Production.

---

## 1. Purpose and decision boundary

این سند تمام شروط لازم برای عبور از معماری به توسعه، تست، استقرار و شروع بهره‌برداری واقعی را در یک محل جمع می‌کند.

دو مجوز مستقل وجود دارد:

1. **BUILD AUTHORIZATION:** اجازه توسعه و تست فقط روی Clone ایزوله و نام‌گذاری‌شده.
2. **PRODUCTION AUTHORIZATION:** اجازه استقرار نسخه مشخص و آزموده‌شده روی دیتابیس `sipanel` در بازه زمانی مشخص.

صدور مجوز اول به معنی صدور مجوز دوم نیست. اجرای Production فقط وقتی مجاز است که تمام Gateهای اجباری این سند `PASS` باشند و فرم Go-Live در بخش 20 امضا شده باشد.

## 2. Current readiness verdict

| Area | Current status | Production consequence |
|---|---|---|
| C1–C10 architecture | Complete as PROVISIONAL v0.12 | باید پس از تصویب BQ/AM به Freeze نهایی تبدیل شود |
| Frozen decisions | 15 FROZEN decisions preserved | بدون Change Request قابل تغییر نیستند |
| New architecture decisions | 44 PROVISIONAL | قبل از Build باید baseline مصوب شوند |
| Installed source/data audit | 24/24 TV evidenced read-only | اثبات Runtime نیست |
| Runtime tests | PT-01…PT-32 NOT_RUN | Production ممنوع تا اجرای Clone tests |
| Finance cost policy | BQ-04 proposal available | امضای مسئول مالی و Clone reconciliation لازم است |
| Backup/restore | scheduled SIPANEL backup not evidenced; restore NOT_RUN | Blocker قطعی Production |
| Clone capacity | Production host برای Clone موازی مناسب نیست | Clone روی host جدا یا پس از ارتقای تأییدشده |
| Security roles | target matrix designed; not configured/tested | ACL and leakage tests required |
| FX | currency rates empty; silent 1.0 risk | MVP فقط ارز پایه شرکت |

**Overall verdict:** `NOT_PRODUCTION_READY`  
**Next legitimate milestone:** `FINAL ARCHITECTURE FREEZE → BUILD AUTHORIZATION → ISOLATED CLONE`.

## 3. Non-negotiable architecture invariants

موارد زیر باید در طراحی فنی، کد، تست و استقرار حفظ شوند:

- Product ≠ Commercial Scope
- Commercial Scope ≠ Recipe
- Recipe ≠ Manufacturing BoM
- Billing Treatment ≠ Product classification
- Estimate ≠ Commitment ≠ Actual
- Project ≠ System ≠ Activity ≠ Product Category
- Product Master فریز‌شده دوباره طراحی یا تکثیر نشود.
- هر Scope Snapshot ارسالی/پذیرفته‌شده immutable و قابل ردیابی باشد.
- هر هزینه اقتصادی دقیقاً یک terminal recognized-cost event داشته باشد.
- اجرای Component و اجرای native anchor هرگز برای یک تقاضا هم‌زمان owner نباشند.
- هیچ هزینه، حاشیه سود، توضیح داخلی یا contingency داخلی در PDF/Portal/Invoice مشتری افشا نشود.
- هیچ Estimate به‌طور خودکار سند حسابداری، خرید، انبار، MRP، Timesheet یا Invoice نسازد.

نقض هر invariant فوق `NO-GO` است.

## 4. Required business and amendment freeze

### 4.1 Batch business decisions recommended for approval

| ID | Required final selection | Production rule | Final status required |
|---|---|---|---|
| BQ-01 | B — زبان هدف quotation اجباری | نبود متن تأییدشده زبان مقصد، Send را block کند | APPROVED/FROZEN |
| BQ-02 | **B — Finance + Sales مشترک** | waiver قیمت/حاشیه با reason و audit؛ threshold=`TBE` | APPROVED/FROZEN |
| BQ-03 | A — accepted Change Order only | actual cost/quantity خودکار invoice نشود | APPROVED/FROZEN |
| BQ-04 | route matrix بخش 5 | یک terminal cost event برای هر economic cost | FINANCE_APPROVED/FROZEN |
| BQ-05 | A — explicit Bridge Release | Native owner در Confirm؛ Bridge owner فقط Release | APPROVED/FROZEN |
| BQ-06 | A — dimensions MVP + visible UNALLOCATED | incomplete allocation پنهان نشود | APPROVED/FROZEN |
| BQ-07 | A — Project at Confirm where native tracking owns it | Bridge فقط link کند و Project/Task تکراری نسازد | APPROVED/FROZEN |
| BQ-08 | B — pre-contract cost = period overhead in MVP | AM-05 و pre-sales actual از MVP خارج | APPROVED/DEFERRED |
| BQ-09 | A — company-currency-only MVP | foreign-currency quote fail-closed | FINANCE_APPROVED/FROZEN |

هر عدد مربوط به minimum margin، stale-cost age، tolerance یا performance target تا وجود baseline و owner برابر `TBE` باقی می‌ماند.

### 4.2 Amendment disposition required

| Amendment | Required disposition |
|---|---|
| AM-01-R2 | APPROVE — explicit `anchor_line_id`، sealed transition، portal/operator audit، section mutation guard |
| AM-02 | APPROVE — Billing Treatment presets بر محورهای مستقل responsibility/acceptance/certainty/visibility |
| AM-03-R1 | APPROVE with signed Finance route matrix |
| AM-04 | APPROVE — percentage cost derived است، direct source نیست |
| AM-05 | DEFER FROM MVP |

### 4.3 Freeze deliverable

قبل از Build باید یک فایل Architecture Freeze جدید صادر شود که شامل موارد زیر باشد:

- 15 تصمیم FROZEN قبلی بدون تغییر متن؛
- تصمیم‌های جدید مصوب با شناسه و rationale؛
- BQ-01…BQ-09 مصوب؛
- AM-01-R2…AM-05 disposition؛
- فهرست DEFERRED و What Not to Build؛
- hash بسته مبنا؛
- نام و تاریخ approverها؛
- عبارت روشن `IMPLEMENTATION AUTHORIZATION: NOT INCLUDED`.

## 5. Iran finance and tax policy required before build

این بخش policy پیشنهادی است و باید توسط مسئول مالی/مشاور مالیاتی شرکت با توجه به قراردادها، فعالیت واقعی و مقررات جاری ایران امضا شود.

### 5.1 Recognized project-cost route matrix

| Route | Single Project Actual event | Operational/financial prerequisites | Excluded duplicates |
|---|---|---|---|
| Shared-stock material | validated issue/consumption to Project at governed inventory cost | approved picking/consumption, Project dimensions, return link | PO, receipt, internal transfer, vendor bill value for same consumption |
| Direct Project purchase/dropship | posted vendor-bill allocation after delivery/service acceptance | vendor tax invoice, acceptance evidence, Project allocation | PO commitment, receipt value and payment as additional costs |
| Manufacturing material + labour | finished-product issue to Project at complete governed production cost | WIP, raw issue, production completion, labour/overhead policy | raw, workorder, timesheet and finished issue summed together |
| Site labour | payroll actual allocated using approved timesheets | non-zero governed employee cost; payroll and insurance evidence | estimate hours and duplicate payroll/timesheet cost |
| Third-party equipment/service | posted vendor bill or approved employee expense, exactly one | service acceptance and Project allocation | PO, draft expense and payment duplicates |
| Company-owned equipment | approved depreciation/operating-cost allocation | asset register and documented allocation basis | equipment purchase price or full-company depreciation |
| Freight/landed cost | capitalized into attributable inventory/production cost | enable only after installed capability and policy pass Clone | direct expense plus later capitalized material cost |
| Return/credit | linked reversal of original selected event | reference to original model/record/amount/quantity | deletion or independent second reversal |

### 5.2 Standard Cost control

- consumption is initially valued at the approved standard cost;
- standard costs have a documented review owner and review event;
- purchase/production variances are reconciled at period close;
- attributable variance is a linked `VALUATION_ADJUSTMENT`, not a second vendor-bill cost;
- missing or stale standard cost is visible and follows an approved blocking/waiver rule; threshold remains `TBE`;
- changing costing method is outside this project unless separately approved and tested.

### 5.3 WIP, revenue and advances

The system/reporting must keep separate:

- committed cost;
- received/operational quantity;
- WIP;
- Project operational cost-to-date;
- recognized P&L cost;
- invoiced revenue;
- recognized revenue;
- collected cash.

Required policy:

- quotation confirmation is not revenue recognition;
- customer advance is not automatically revenue;
- goods revenue follows documented control/delivery acceptance;
- fabrication/installation revenue follows approved performance obligations and evidence of progress/acceptance;
- provisional amount and variation enter invoicing only through an accepted Change Order;
- credit notes and returns remain linked to the original transaction.

### 5.4 Iran tax and statutory controls

- Quotation/Scope/Estimate is not a fiscal invoice.
- Each invoiceable line has an approved goods/service identifier and tax mapping.
- VAT and other tax rates are date-effective configuration, never hard-coded in custom logic.
- `INTERNAL_ONLY` and `CUSTOMER_SCOPE` do not enter the invoice tax base.
- Optional scope becomes invoiceable only after governed customer acceptance.
- corrections, cancellations and returns use linked fiscal references.
- deductible cost must retain vendor invoice/evidence, business purpose, period and approval trail.
- installation/contracting agreements are classified for Social Security Article 38 applicability before confirmation.
- contracts subject to Article 38 retain contract, deduction, subcontractor and clearance-certificate evidence; final-payment control follows the then-current rule.
- no legacy withholding automation is enabled without a current written legal basis.
- statutory currency is the company accounting currency; Toman may be display-only if governed, while stored/accounted amounts remain unambiguous.

### 5.5 Finance sign-off evidence

Required file/evidence:

- signed BQ-04 route matrix;
- WIP and revenue-recognition policy;
- overhead inclusion/exclusion matrix;
- Standard Cost review and variance policy;
- return/credit mapping;
- company-currency-only approval;
- invoice identifier/tax mapping ownership;
- Article 38 contract-classification procedure;
- names, roles, signature dates and effective date.

## 6. Infrastructure and environment prerequisites

### 6.1 Current blockers

Verified host facts at evidence date:

- approximately 1.9 GiB RAM;
- approximately 830 MiB available RAM;
- 28 GiB disk with approximately 4 GiB free / 85% used;
- no evidenced scheduled SIPANEL backup;
- restore rehearsal not performed.

Therefore:

- do not run the Clone beside Production on the current host;
- use a separate isolated host, or complete and revalidate an approved capacity upgrade;
- do not install/upgrade any module until scheduled backup and tested restore exist.

### 6.2 Clone requirements

- separate DB name, storage, filestore, ports and domain;
- production mail disabled or redirected to a sink;
- cron/jobs disabled until individually reviewed;
- payment, webhook, SMS, portal, external API and callback endpoints neutralized;
- production URLs and OAuth callbacks replaced;
- secrets protected and rotated where cloning exposes them;
- minimum necessary PII; real contact phone numbers preserved but never used for outbound tests;
- database and filestore copied as one consistent recovery point;
- clone identity visibly shown in UI and logs;
- no access to other databases such as ahanassa, avizsazeh or shahbazi.

### 6.3 Backup requirements

Backup set must include:

- consistent PostgreSQL database backup;
- matching filestore;
- custom addon source and exact commit/release;
- dependency manifest;
- recoverable Odoo configuration references without exposing secrets;
- package/module versions;
- checksum manifest;
- retention and off-host copy policy;
- named backup owner and alert recipient.

`Backup created` is insufficient. A restore must succeed on an isolated environment and pass DB/filestore/application smoke tests.

## 7. Odoo configuration prerequisites

The following must be configured and evidenced on Clone before Production:

- active/valid Scope UoMs including required `cm` handling;
- dimensional compatibility enforced by Scope/Recipe logic because this Odoo build does not enforce old UoM categories;
- Product UoM decimal precision impact tested globally;
- Product Price precision unchanged unless Finance explicitly approves it;
- Project, System and Activity analytic plans with applicability rules;
- selected analytic cost carriers enabled only where route policy requires them;
- company-currency-only quotation guard;
- taxes, fiscal positions, invoice policies and product/service identifiers;
- employee/project labour cost policy; zero hourly costs cannot generate valid Actual Cost;
- customer language and approved translations;
- scheduled backup and monitoring;
- outgoing email/integration configuration for controlled go-live;
- report actions and layouts cleaned and regression-tested.

Installed facts that implementation must respect:

- no `sale.order.option`; optional scope uses ordinary sale lines with quantity state;
- no per-UoM rounding/category enforcement;
- only Project analytic plan currently exists;
- `sale_margin` is not installed and shall not be installed merely for this project;
- use `stock.reference`, `stock.move.value` and `product.value` for this Odoo 19 build;
- `lock_for_update` contention raises `LockError` and requires idempotent retry;
- Scope anchors must not be combo children in MVP;
- `stock_landed_costs` is not currently installed.

## 8. Security, roles and segregation

### 8.1 Required role groups

- Scope/Recipe Viewer
- Scope/Recipe Editor
- Scope Release Manager
- Sales Operator
- Sales Manager / Commercial Waiver
- Cost Viewer
- Finance Approver
- Execution Release Manager
- Purchase/Inventory/MRP Operator
- Auditor / Read-only Reviewer
- System Administrator

### 8.2 Initial assignment constraint

The existing user **Taleghani — `amirmousa1983@gmail.com`** may initially hold the operational roles requested by management, but:

- groups remain configurable and must not be hard-coded to this user;
- Finance + Sales dual approval cannot be represented as independent control if one person performs both; this concentration must be explicitly accepted and logged or a second approver added;
- cost/margin access must not reach Portal, customer PDF, public RPC or unauthorized export;
- administrator privileges do not automatically confer business approval in custom workflow logic;
- every privileged override records user, time, reason, before/after and linked revision.

### 8.3 Mandatory security tests

- record rules by company and role;
- create/write/release/archive/copy restrictions;
- direct ORM/RPC/import bypass attempts;
- Portal stale-link and revision mismatch;
- PDF, attachment, export and chatter leakage;
- cost/margin field access;
- cross-company/cross-project access;
- scoped section delete/reorder after seal;
- optional acceptance replay/idempotency;
- no exposure of personal contact information.

Any unauthorized read or write is `NO-GO`.

## 9. Module and source-control requirements

- no Odoo core patch;
- additive, namespaced module(s) with a documented dependency graph;
- Native → Configuration → Convention → Small Extension → Custom Module preference order;
- every customization links to a documented GAP and decision ID;
- no modification of unrelated custom modules without an explicit compatibility change;
- versioned manifest, changelog and migration scripts;
- deterministic install and upgrade;
- clean uninstall is not considered rollback;
- no destructive data migration without separately approved mapping and recovery test;
- repository branch, commit hash, reviewer and release tag recorded;
- static checks, module tests and code review must pass before Clone integration;
- secrets, credentials and Production dumps never committed.

## 10. Data and migration requirements

- preserve verified baseline: 113 templates / 81 active / 149 variants / 101 active / 73 canonical templates;
- preserve Frozen Product Master and canonical variants;
- no duplicate Product merely to represent Scope/Recipe/Activity;
- no bulk category/UoM/route cleanup as an incidental migration;
- ordinary Sales lines remain functional and unchanged;
- existing operational documents are treated as test/history according to the business statement, but are not deleted automatically;
- real contact records and phone numbers are preserved;
- new schema is additive;
- no fabricated historical Scope snapshots or Actuals;
- every imported Scope/Recipe/version has source reference, owner, validation result and import batch;
- migration dry-run produces counts, rejected rows and before/after checksums;
- migration is repeated successfully from a clean Clone before Production.

## 11. Required implementation slices and exit gates

| Slice | Scope | Exit evidence |
|---|---|---|
| A — Foundations | Scope identity/version, Recipe, ACL, release validation, usage trace | immutable released version, concurrency control, permissions and UoM guard PASS |
| B — Quote estimation | Snapshot, quantity/cost engine, overrides, split, notes, pricing view | PT-01…PT-12 plus applicable PT-24…PT-32 PASS |
| C — Optional/provisional | explicit anchor, portal/operator acceptance, tax/pricelist recompute, section guard | stale/replayed acceptance rejected; ordinary native option behavior unchanged |
| D — Execution Bridge | owner registry, Release, PO/stock/MRP/project adapters, idempotency | PT-13…PT-20 and PT-22 PASS; no duplicate demand |
| E — Actual reporting | selected cost projection, UNALLOCATED, variance and C9 pilot | PT-21, PT-29, PT-30 and complete finance reconciliation PASS |

Each slice may be deployed to Clone independently. Production enablement must be progressive and reversible through tested feature/config boundaries.

## 12. Mandatory runtime tests

All PT-01…PT-32 must have `PASS`, or be explicitly `NOT_APPLICABLE` with approved rationale. No `BLOCKED`, `FAIL` or unexplained `NOT_RUN` may remain on an enabled Production path.

Minimum coverage:

- add released Scope and immutable cost/recipe snapshot;
- master version upgrade does not alter old quotation;
- dimensional UoM conversion and incompatible-unit rejection;
- quantity/cost overrides and stale-override warning;
- percentage cycle/self/cross-scope/double-count rejection;
- split with dependency relocation and cost conservation;
- customer-note regeneration/staleness/manual preservation;
- quotation duplicate without acceptance/execution link copy;
- operator and Portal optional acceptance bound to sealed revision;
- INTERNAL_ONLY/CUSTOMER_SCOPE leakage prevention;
- missing Product/cost/UoM/readiness blockers;
- native anchor versus Bridge single ownership;
- concurrent Release with `LockError`, retry and unique idempotency key;
- atomic rollback on partial adapter failure;
- shared-stock consumption without purchase/receipt/bill double count;
- MRP finished cost without raw/labour/finished duplication;
- direct purchase, service, returns and credit mapping;
- timesheet/payroll single labour source;
- amendments, cancellations and partial/backorder flows;
- estimate/baseline/forecast/commitment/actual reconciliation;
- role, ACL, RPC, import, Portal, PDF and attachment security;
- foreign-currency block and absence of silent 1.0 conversion;
- taxes, discounts, fiscal positions and invoice creation;
- Product UoM precision regression;
- report layout and custom-module compatibility;
- backup/restore and rollback rehearsal;
- performance observation with thresholds still `TBE` until approved baseline.

## 13. Vertical acceptance pilot

The `متعلقات آبرو` scenario must run end-to-end on Clone:

Customer Line → Scope → Recipe → Quantity → Cost → Selling Price → Margin → Customer Note → Split Screw → Confirmation → Release → Procurement → Stock → Gutter Fabrication → Installation → Timesheet → Actual Cost → Invoice → Estimate vs Actual.

Pilot evidence must include:

- master and test-data identifiers;
- expected and actual quantities/costs;
- one owner per demand;
- customer artifact hash and accepted revision;
- PO/picking/MO/project/timesheet/invoice trace;
- recognized-cost source for each route;
- double-counting proof;
- returns/negative/security tests;
- rollback result;
- unresolved variance explanation;
- Finance, Sales, Operations and technical sign-off.

Synthetic values in architecture are test oracles only and are not Production prices, rates or thresholds.

## 14. Reporting acceptance

Required Production reports:

- Quote estimated cost and margin by Scope/System/Activity;
- accepted sealed baseline;
- current forecast;
- commitments;
- received/operational quantities;
- WIP;
- Project Actual Cost by selected terminal source;
- `UNALLOCATED` amount and allocation completeness;
- invoiced and recognized revenue;
- Estimate vs Actual variance;
- quantity, price, labour and approved valuation adjustments;
- reversals/returns/credits;
- version and change-order history;
- permissions and override audit.

Reports must reconcile to selected native sources. A dashboard total without source record identifiers is not acceptable evidence.

## 15. Customer document and Portal acceptance

- exact sent PDF/customer payload is sealed and hashed;
- acceptance references the exact order/scope revision and artifact;
- stale links fail closed;
- sent/accepted scoped data cannot be silently edited;
- section deletion/reorder cannot re-parent or detach Scope anchor;
- Customer PDF and Portal expose only approved customer fields;
- cost, margin, internal activity, internal contingency and supplier data are absent from payload, not merely hidden with CSS;
- Persian/English direction, fonts and translation completeness are reviewed;
- invoice description is traceable to the accepted commercial revision;
- ordinary non-Scope quotation behavior passes regression.

## 16. Report hygiene blockers

Before Production:

- investigate and remove/disable or document stray report action id `848`;
- regression-test `sale_shamsi_report` global override of `web.external_layout_bubble`;
- resolve duplicate `commitment_date` Portal xpath behavior;
- validate quotation, order, invoice and Portal layouts in supported languages;
- prove that no internal cost fields reach rendered reports or attachments.

## 17. Deployment runbook requirements

The approved runbook must state exact values, not placeholders, for:

- target database confirmation: `sipanel`;
- server/host identity;
- addon paths and target release tag/hash;
- module dependency/version list;
- backup timestamp and checksum;
- DB/filestore consistency boundary;
- migration and configuration sequence;
- named operator and observer;
- approved change window;
- expected downtime or zero-downtime claim with evidence;
- stop conditions;
- smoke-test sequence;
- communications/escalation path;
- enablement order and feature boundaries;
- rollback owner and decision deadline.

Required enablement order:

1. schema/module installed but business features disabled where technically supported;
2. master data and internal release validation;
3. internal estimation;
4. customer quotation and sealed acceptance;
5. execution adapters route by route;
6. Actual Cost and reporting.

If tested feature isolation does not exist, use separate reviewed deployments rather than assuming a flag.

## 18. Mandatory stop conditions

Immediately stop cutover when any of the following occurs:

- target is not unambiguously database `sipanel`;
- backup or restore verification fails;
- DB and filestore recovery points do not match;
- disk/RAM headroom is below the approved deployment baseline;
- module dependency or schema migration differs from the reviewed release;
- unexpected Product, variant, contact, quotation or invoice mutation appears;
- cost/margin leakage occurs;
- duplicate PO/picking/MO/task/timesheet/cost is created;
- ordinary Sales workflow regression fails;
- fiscal/tax configuration is incomplete;
- sealed revision or Portal acceptance can be bypassed;
- security denial tests fail;
- monetary reconciliation has an unexplained difference;
- rollback owner is unavailable.

## 19. Rollback and recovery

### Before any new live business transaction

If the agreed recovery boundary is still valid, restore database, filestore, addon release and configuration as one matched set; verify startup and smoke tests.

### After any new live business transaction

- do not overwrite live transactions with an old database;
- disable new extension actions using the tested control;
- preserve current records and evidence;
- reconcile sent quotes, accepted options, PO/picking/MO, invoices and external integrations;
- choose an approved roll-forward fix or a controlled restore with transaction replay;
- use native reversals for posted accounting/stock documents;
- never delete posted records to simulate rollback.

Uninstalling the module is not rollback because custom snapshots, trace and allocations may be removed. PT-30 must prove the chosen recovery process.

## 20. Go/No-Go approval form

Production authorization is valid only when every required row is completed.

| Gate | Required evidence | Owner | Status | Evidence reference / date / signature |
|---|---|---|---|---|
| Architecture Freeze | approved final decision baseline and deferred list | Business owner + architect | PENDING |  |
| Finance/Tax | signed section 5 policies and BQ-04 | Finance/tax owner | PENDING |  |
| Build Authorization | named repo, clone, scope and development permission | Business owner | PENDING |  |
| Code Review | release hash, dependency manifest, review PASS | Technical owner | PENDING |  |
| Clone Integration | clean install/upgrade and ordinary-flow regression | Technical owner | PENDING |  |
| PT Test Pack | PT-01…PT-32 disposition and evidence | QA + process owners | PENDING |  |
| Security | ACL/Portal/PDF/RPC/import tests PASS | Security/admin owner | PENDING |  |
| Finance Reconciliation | route totals, WIP, variance and reversals reconcile | Finance owner | PENDING |  |
| Tax/Invoice | identifiers, taxes, fiscal invoice and Article 38 process approved | Tax owner | PENDING |  |
| Backup/Restore | scheduled backup + isolated restore rehearsal PASS | Infrastructure owner | PENDING |  |
| Capacity | Production and Clone capacity evidence | Infrastructure owner | PENDING |  |
| Deployment Runbook | exact steps, window, operators and stop rules | Technical owner | PENDING |  |
| Rollback Rehearsal | PT-30 and recovery evidence PASS | Technical + business | PENDING |  |
| Business Acceptance | C9 pilot and customer artifacts approved | Sales/Operations | PENDING |  |
| Production Authorization | explicit approval of release and change window | Authorized owner | PENDING |  |

**GO rule:** all enabled-path rows = `PASS/APPROVED`, no open blocker, exact release hash and recovery point recorded.  
**NO-GO rule:** any `PENDING`, `FAIL`, `BLOCKED`, unexplained `NOT_RUN`, missing signature or mismatched release.

## 21. Required production release evidence pack

The final release pack must contain:

1. Final Architecture Freeze and decision register
2. Approved BQ/AM register
3. Finance/Tax policy and BQ-04 route matrix
4. Source-code release manifest and checksums
5. Module dependency and configuration manifest
6. Data/migration mapping and dry-run results
7. PT-01…PT-32 test report with attachments
8. Security and privacy test report
9. Customer PDF/Portal acceptance evidence
10. Finance reconciliation and double-counting report
11. Backup inventory and restore-rehearsal report
12. Deployment runbook
13. Rollback/recovery runbook
14. Go/No-Go signed approval
15. Post-deployment smoke checklist
16. Known limitations, deferred items and support contacts

No fabricated PASS report is permitted. Missing evidence remains `NOT_RUN` or `PENDING`.

## 22. Post-deployment controls

Immediately after cutover:

- verify target release/module/configuration;
- run read-only smoke checks and one authorized controlled flow;
- compare Product/contact/order counts to the approved boundary;
- check cron, mail and integrations;
- verify PDF/Portal output and cost privacy;
- inspect duplicate demand and idempotency logs;
- reconcile first authorized estimate, commitment, stock/MRP, cost and invoice chain;
- verify scheduled backup completion and alerts;
- record every exception in an issue register.

Observation duration and numeric alert thresholds remain `TBE` until a measured baseline and accountable owner approve them.

## 23. Deferred / explicitly not in MVP

- multi-currency quotation and unmanaged FX;
- supplier-offer automation;
- automatic landed-cost simulation without installed/policy support;
- general expression language or cross-Scope percentage graph;
- nested percentage costing;
- pre-contract Actual Cost generated from Recipe;
- universal BI/reporting framework;
- custom dimensions on `stock.move` / `stock.move.line`;
- fourth analytic plan or custom Work Package;
- advanced customer-owned stock custody;
- rental-asset lifecycle;
- automatic invoice from Actual Cost;
- Product Master redesign;
- installation of `sale_margin` merely to satisfy this scope.

## 24. Current blocker register

| ID | Blocker | Closure evidence |
|---|---|---|
| B-01 | UoM precision, inactive cm, dimensional/rounding gap | Clone regression and approved configuration |
| B-02 | AM-01-R2 / AM-02 legal-transition wording | approved amendment and combination table |
| B-03 | System/Activity analytics absent/disabled | configured plans, applicability, groups and route tests |
| B-04 | BQ-04 recognized-cost policy | signed matrix + PT-16…PT-21 reconciliation |
| B-05 | seal and acceptance binding absent | implementation + stale/replay/section-mutation tests |
| B-06 | currency rates absent / silent 1.0 risk | company-currency block; governed FX deferred |
| B-07 | backup/restore/capacity | scheduled backup, restore PASS, separate Clone capacity |
| B-08 | roles and privileges | approved role matrix and ACL tests |
| B-09 | report hygiene | id 848/layout/xpath resolution and rendered regression |
| B-10 | open BQ/CF/AM scope | final freeze and deferred map |

Until B-01…B-10 are closed for the enabled scope, Production authorization remains `DENIED_PENDING_GATES`.

---

## Final statement

این سند فهرست کامل شرایط شروع Production است؛ اما خودش مجوز اجرا نیست. مجوز معتبر فقط با تکمیل بخش 20، ثبت release hash، recovery point، بازه استقرار و امضای مسئولان صادر می‌شود.
