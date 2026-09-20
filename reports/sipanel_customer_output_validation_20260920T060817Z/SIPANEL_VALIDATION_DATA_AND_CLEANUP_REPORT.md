# SIPANEL Validation Data and Cleanup Report (run 20260920T060817Z)

Prefix of every temporary record: `SIPANEL-CUSTOMER-OUTPUT-CHECK-20260920T060817Z` (`P` below). Marker strings for leakage tests: `INTERNAL-MARKER-<KIND>-20260920T060817Z`. Created by user id 2 (`amirmousa1983@gmail.com`) through the Odoo shell on database `sipanel`; script `evidence/scripts/create_data.py`; ids in `evidence/validation_record_ids.json`.

## 1. Records created

| Model | Ids | Purpose | Values (all synthetic, marked as validation data) |
|---|---|---|---|
| account.analytic.account | 248 (system, plan 80), 249, 250 (activities, plan 81) | activity/system assignments required by release rule R8 | names carry `P … INTERNAL-MARKER-ANALYTIC` |
| product.product / product.template | 1113–1120 / 488–495 | anchor (service), gutter, bracket, sealant (storable consumables), labour, crane, scaffolding (services), screw | validation unit costs 0 / 731,000 / 9,876 / 55,555 / 4,321 / 8,765,000 / 0 / 123 IRR; internal reference `VAL-*-060817Z`; description marker |
| sipanel.scope | 95 (code `P`) | temporary master | name marker `SCOPENAME` |
| sipanel.scope.version | 115 (released by user 2) | 7 recipe lines 897–903 | labels `متعلقات آبرو (داده آزمایشی)` / `Gutter accessories (validation data)`, customer descriptions fa/en, internal description marker |
| recipe lines | 897 gutter per-scope 1.0 m (included, firm); 898 bracket 2/m (own_line = separately billable); 899 sealant manual 6 (included; set provisional at quote time); 900 labour fixed 8 h, manual estimate 4,321; 901 scaffolding fixed 1, responsibility customer, no_action/customer_responsibility, no_customer_line; 902 screw fixed 20, **internal_only**, label marker; 903 crane fixed 1, manual estimate 8,765,000 | | |
| res.partner | 426 `P مشتری آزمایشی (Synthetic Validation Customer)` | synthetic customer, `lang=fa_IR`, no e-mail/phone, internal note marker | |
| sale.order | 312 `SI-26/312` | validation quotation: client ref/origin `P`, Persian terms note, salesperson user 2 | lines 555 anchor (12 m, 2,500,000, 5 %, tax 10 %), 556 note line (Persian), 557 optional section (`is_optional`), 558 optional anchor (0 m offered 5 m, 2,200,000, tax 10 %) |
| sipanel.quote.scope | 217 (base), 218 (optional) | | revisions 237, 238 (r1, `sent_sealed` at 06:12 UTC by `action_quotation_sent`, no e-mail); provisional basis on sealant component 1840; components 1838–1851 |
| sipanel.quote.scope.artifact | 255 text, 256 pdf (attachment 3955), 257 text, 258 pdf (attachment 3956) | seal-time artifacts (append-only) | |
| sale.order | 313 `SI-26/313` | helper draft for token isolation and after-fix note check (scope 270 / revision 301 added after the upgrade) | deleted |
| mail.message | 9929, 9934 (internal note marker), 9938 (+ later "Quotation viewed" notifications from the validation fetches) | | retained with the cancelled order |

Nothing was sent: `mail.mail` created since 06:00 UTC = 0; outgoing messages on the orders = 0; no portal invitation; no portal user.

## 2. Cleanup performed (script `evidence/scripts/cleanup.py`, committed 06:47 UTC)

| Record | Action | Reason |
|---|---|---|
| `SI-26/313` (order 313) + scope 270 / revision 301 / 7 components / anchor line | **deleted** | draft, never sent; deletion needed the D-04 workaround (clear `current_revision_id` first) |
| `SI-26/312` (order 312) | **cancelled** (`state=cancel`), audit event `order_cancel` logged | sealed scopes/artifacts are audit evidence and cannot be deleted; a cancelled quotation is not sent, confirmed or invoiceable (`qty_to_invoice` lines: 0) |
| quote scopes 217, 218 | **archived** (`active=False`) | sealed revisions retained |
| revisions 237, 238; components 1838–1851; artifacts 255–258; attachments 3955, 3956; audit events | **retained** | append-only SIPANEL audit trail |
| scope master 95 | **archived** | version 115 is `released` and referenced by the retained quotation → restrict-protected |
| version 115 + recipe lines 897–903 | **retained** (under the archived master) | restrict-protected |
| products 1113–1120 (templates 488–495) | **archived** (unlink refused: referenced by order lines/components) | restrict-protected |
| analytic accounts 249, 250 | **archived** (referenced by components) | restrict-protected |
| analytic account 248 | **deleted** (unreferenced) | |
| partner 426 | **archived** (referenced by the retained order) | restrict-protected |

## 3. Verification after cleanup (same script, committed state)

| Check | Result |
|---|---|
| mail.mail since 06:00 UTC / outgoing messages on order 312 | 0 / 0 |
| stock.picking, mrp.production, purchase.order with origin `SI-26/312` | 0 / 0 / 0 |
| account.move with invoice origin `SI-26/312` | 0 |
| project.task for order 312 | 0 |
| sipanel.execution.demand / batch for order 312 | 0 / 0 |
| invoiceable lines on order 312 | 0 |
| test users `sipanel_pt_*` persisted by test runs | 0 (test transactions rolled back; the "Signup email sent" log lines are inside rolled-back test transactions, no mail.mail row exists) |
| test scopes `SIPANEL-PT-GUTTER-*` persisted | 0 |
| portal users for partner 426 | 0 |

## 4. Retained validation records (count and identity)

| Model | Count | Ids | State |
|---|---|---|---|
| sale.order | 1 | 312 (`SI-26/312`) | cancel |
| sale.order.line | 4 | 555, 556, 557, 558 | |
| sipanel.quote.scope | 2 | 217, 218 | archived |
| sipanel.quote.scope.revision | 2 | 237, 238 | sent_sealed (immutable) |
| sipanel.quote.scope.component | 14 | 1838–1851 | |
| sipanel.quote.scope.artifact | 4 | 255–258 | append-only |
| ir.attachment (artifact PDFs) | 2 | 3955, 3956 | res_model artifact, not public |
| sipanel.scope / version / recipe lines | 1 / 1 / 7 | 95 (archived) / 115 (released) / 897–903 | |
| product.product / template | 8 / 8 | 1113–1120 / 488–495 | archived |
| res.partner | 1 | 426 | archived |
| account.analytic.account | 2 | 249, 250 | archived |
| sipanel.scope.audit.event | ≥ 1 on the order + scope/revision events (add_scope ×2, seal ×2, acceptance_transition, order_cancel) | e.g. 986 | retained |

Everything retained carries the prefix `P` in its name/code/reference and can be found with `name ilike 'SIPANEL-CUSTOMER-OUTPUT-CHECK-20260920T060817Z'` (or `client_order_ref` for the order).

## 5. Other state changes on `sipanel` during this run

| Change | Detail |
|---|---|
| Module upgrade | `-u sipanel_sale_scope` at 06:32–06:33 UTC (Odoo also reloaded dependents `sipanel_scope_execution`, `sipanel_scope_costing`); `/opt/odoo/addons/sipanel_sale_scope` synced from commit `0e2d63e`; `/opt/odoo/addons/sipanel_commercial_scope_core/tests/common.py` synced (test-only) |
| Container restart | `odoo-sipanel` once at 06:39:56 UTC |
| Recovery point | `/opt/odoo/backups/sipanel-pre-customer-output-fix-20260920T062942Z` (dump 151 MB db → 21.7 MB custom-format, filestore 279 MB, addons, redacted conf, container inspect, module list; SHA256SUMS verified) |
| Not changed | `report.url` system parameter (D-01, refused by the harness), website languages, taxes, accounting, thresholds, labour rates, other databases, `odoo-db` |
