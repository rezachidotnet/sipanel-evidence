Run sipanel_scope_implementation_rc_20260919T140237Z · Verdict: BLOCKED_NOT_ISOLATED · Status: no module was written, installed or tested in this run; nothing below is a PASS.

# SIPANEL — Installation and Configuration Runbook (design-level, NOT RUNTIME VALIDATED)

Purpose: give the next authorized run a step-by-step path from "no clone" to "modules installed and configured on an isolated clone". Nothing in this file was executed in this run. Every command is written for the clone host; none may be run against the Production host `194.5.206.76` (EV-01) except the explicitly labelled recovery-point capture in A.3, which itself requires separate authorization.

Authority: Readiness v1.0 §6 (infrastructure/clone), Roadmap "Clone isolation" and "Production deployment runbook requirements", Master C10 "Migration, gates, deferred", EV-01…EV-04, SV-01…SV-20.

---

## Part A — Clone provisioning on a separate isolated host

### A.1 Why a separate host

- Production host has 1.9 GiB RAM, 106–348 MiB available, 1.9 GiB swap in use, 4.0 GiB free disk, five containers previously OOM-killed (EV-01).
- Readiness §6.1: "do not run the Clone beside Production on the current host".
- Readiness §6.2: clone must have no access to `ahanassa`, `avizsazeh`, `shahbazi`; the shared `odoo-db` container hosts all of them (EV-02).
- The existing `sipanel_staging_rehearsal` database is on the same PostgreSQL instance and is a stale 2026-09-15 recovery point (EV-02). It is not an acceptable clone.

### A.2 Minimum clone specification (requirements, not measurements)

| Item | Requirement | Note |
|---|---|---|
| Host | dedicated VM/host, not shared with any Production Odoo | separate from `194.5.206.76` |
| RAM | ≥ 4 GiB headroom beyond the Odoo worker limits for `--test-enable` runs | Production config uses `limit_memory_hard=2684354560`; test runs load full registry + test fixtures |
| Disk | ≥ 10 GiB free including DB restore, filestore copy, logs and the RC build | `sipanel` DB is 135 MB (EV-02); filestore size **TBE — measured at recovery-point capture** |
| PostgreSQL | dedicated 15.18 instance (matches SV-01) containing only the clone DB and `postgres` | no other tenant DBs on the instance |
| Odoo runtime | image `sha256:1cd111414896…` (the image running `odoo-sipanel`, EV-01) or a rebuild from the identical `19.0-20260528` source | Python 3.12.3 |
| Addons path | copy of `/opt/odoo/addons` custom set (SV-18/19; not git-tracked, SV-20) + the five `sipanel_*` modules from the RC | checksum both sets |
| Network | outbound SMTP/HTTP blocked or routed to a sink; no public DNS name of Production | portal reachable only on a clone hostname |
| Identity | DB name `sipanel_clone_<YYYYMMDD>`, distinct DB role, `dbfilter=^sipanel_clone_<YYYYMMDD>$`, `list_db=False` | visible banner in UI and logs |

### A.3 Recovery-point capture on Production — SEPARATE AUTHORIZATION REQUIRED, NOT PERFORMED

This is a Production read action. It was **not** performed in this run and is listed only so the next run knows what it needs.

1. Approved quiet window or Odoo stopped for the capture, so that DB and filestore are one consistent point (Readiness §6.2, §6.3).
2. `pg_dump -Fc` of database `sipanel` executed as the Production DB role, credentials from the secret store (`<DB_PASSWORD_FROM_SECRET_STORE>`), never on the command line.
3. `rsync -a` of `/opt/odoo/data/filestore/sipanel/` taken in the same window.
4. Record: capture timestamp (UTC), `database.uuid` (`6a18f226-5a5b-11f1-aa67-d7045c504f39`, EV-02), max write dates for `product_template` and `sale_order`, sizes, SHA256 of the dump and of a filestore tar.
5. Do not copy `/opt/odoo/secrets`, Odoo `.conf` files with passwords, or any other database.

### A.4 Transfer

```
# on the clone host, after scp/rsync of the artefacts
sha256sum -c RECOVERY_POINT.sha256      # must print OK for dump and filestore tar
```

Reject any artefact whose checksum does not match; do not "repair" a partial transfer.

### A.5 Restore on the clone host

```
# placeholders only; run on the CLONE host
export PGPASSWORD='<CLONE_DB_PASSWORD_FROM_SECRET_STORE>'
createuser  -h <clone_pg_host> -U postgres sipanel_clone_app
createdb    -h <clone_pg_host> -U postgres -O sipanel_clone_app sipanel_clone_<YYYYMMDD>
pg_restore  -h <clone_pg_host> -U postgres -d sipanel_clone_<YYYYMMDD> --no-owner --role=sipanel_clone_app sipanel_<capture_ts>.dump
mkdir -p /opt/odoo-clone/data/filestore/sipanel_clone_<YYYYMMDD>
tar -xf filestore_sipanel_<capture_ts>.tar -C /opt/odoo-clone/data/filestore/sipanel_clone_<YYYYMMDD> --strip-components=1
```

Note: the filestore directory name must equal the clone DB name, otherwise attachments resolve to nothing.

### A.6 Neutralization before first start — runs ONLY on the clone DB

Run inside one transaction on `sipanel_clone_<YYYYMMDD>` before Odoo is started for the first time. Every statement below is idempotent and reversible on the clone only.

```sql
-- CLONE ONLY. Abort if current_database() is not the clone.
DO $$ BEGIN
  IF current_database() !~ '^sipanel_clone_' THEN
    RAISE EXCEPTION 'Refusing: % is not a clone database', current_database();
  END IF;
END $$;

BEGIN;
-- 1. Outbound / inbound mail
UPDATE ir_mail_server SET active = false;
UPDATE fetchmail_server SET active = false;
-- 2. Scheduled actions: everything off until individually reviewed (Readiness §6.2)
UPDATE ir_cron SET active = false;
-- 3. Payment providers
UPDATE payment_provider SET state = 'disabled' WHERE state <> 'disabled';
-- 4. SMS / WhatsApp / gateway / IAP / OAuth / webhook parameters
--    (keys to be enumerated from the clone's ir_config_parameter at clone time; examples)
UPDATE ir_config_parameter SET value = 'NEUTRALIZED_CLONE'
 WHERE key ILIKE 'sms%' OR key ILIKE '%whatsapp%' OR key ILIKE '%gateway%'
    OR key ILIKE '%webhook%' OR key ILIKE '%oauth%' OR key ILIKE 'iap.%' OR key ILIKE '%api_key%';
-- 5. Base URL and clone banner
UPDATE ir_config_parameter SET value = 'http://<clone-hostname>:<port>' WHERE key = 'web.base.url';
INSERT INTO ir_config_parameter (key, value, create_uid, create_date, write_uid, write_date)
VALUES ('sipanel.clone_identity', 'sipanel_clone_<YYYYMMDD> on <clone-hostname>', 1, now(), 1, now())
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value;
UPDATE res_company SET name = name || ' [CLONE ' || '<YYYYMMDD>' || ']';
-- 6. Admin password rotation is done through Odoo after start (never a plaintext SQL update of a hash copied from Production).
COMMIT;
```

Additional container-level neutralization:

- Odoo config for the clone: `db_name`/`dbfilter` = clone only, `list_db = False`, `smtp_server` unset or pointed at a sink (e.g. a local MailHog-type sink), `proxy_mode` as needed for the clone hostname.
- Do not mount `/opt/odoo/secrets` or Production `.conf` files.
- Firewall: block egress to SMTP (25/465/587) and to any Production integration endpoint.

### A.7 First start and smoke test

```
docker run -d --name odoo-sipanel-clone ... <image> odoo server --config=/etc/odoo/odoo-clone.conf
```

Smoke checks (record output in the test register):

1. Login page shows the clone banner in company name.
2. `ir.config_parameter` `sipanel.clone_identity` visible in Settings → Technical.
3. `database.uuid` printed and stored as the clone identity (it will differ from Production after the first Odoo start only if regenerated; if it equals Production's, record that fact — identity is then the DB name + host).
4. No cron runs (Settings → Technical → Scheduled Actions all inactive).
5. No mail leaves: send a test mail from the clone to a controlled address and confirm it lands in the sink, not in a real mailbox.
6. Portal `/my/orders` works on the clone hostname only.

### A.8 Clone identity in every test record

Each PT record must carry: clone DB name, host, `database.uuid`, recovery-point capture timestamp, Odoo build (`19.0-20260528`), RC commit hash, custom addon set checksum.

---

## Part B — Module installation on the clone

### B.1 Addon layout

```
/opt/odoo-clone/addons/           # copy of /opt/odoo/addons (SV-18..SV-20), checksummed
/opt/odoo-clone/sipanel_addons/   # from the RC ZIP: the four Production modules
/opt/odoo-clone/sipanel_test_addons/  # sipanel_scope_demo — clone/test only
```

`addons_path = /mnt/extra-addons,/mnt/sipanel-addons,/mnt/sipanel-test-addons` on the clone. The Production addon set never receives `/mnt/sipanel-test-addons`.

### B.2 Install order (dependency order, see SIPANEL_MODULE_AND_DEPENDENCY_MANIFEST.md)

```
odoo -c /etc/odoo/odoo-clone.conf -d sipanel_clone_<YYYYMMDD> -i sipanel_commercial_scope_core --stop-after-init
odoo -c /etc/odoo/odoo-clone.conf -d sipanel_clone_<YYYYMMDD> -i sipanel_sale_scope            --stop-after-init
odoo -c /etc/odoo/odoo-clone.conf -d sipanel_clone_<YYYYMMDD> -i sipanel_scope_execution       --stop-after-init
odoo -c /etc/odoo/odoo-clone.conf -d sipanel_clone_<YYYYMMDD> -i sipanel_scope_costing         --stop-after-init
# clone/test only:
odoo -c /etc/odoo/odoo-clone.conf -d sipanel_clone_<YYYYMMDD> -i sipanel_scope_demo            --stop-after-init
```

Installing all four in one `-i a,b,c,d` call is acceptable once the per-module install has been proven; the first run uses the explicit order to isolate failures.

### B.3 Clean-database install test

```
createdb -h <clone_pg_host> -U postgres -O sipanel_clone_app sipanel_clean_<YYYYMMDD>
odoo -c /etc/odoo/odoo-clone.conf -d sipanel_clean_<YYYYMMDD> -i sale_management,purchase_stock,mrp_account,sale_project,sale_timesheet,sale_purchase,sale_mrp,hr_expense --stop-after-init
odoo -c /etc/odoo/odoo-clone.conf -d sipanel_clean_<YYYYMMDD> -i sipanel_commercial_scope_core,sipanel_sale_scope,sipanel_scope_execution,sipanel_scope_costing --stop-after-init
```

### B.4 Module tests

```
odoo -c /etc/odoo/odoo-clone.conf -d sipanel_clean_<YYYYMMDD> \
     -i sipanel_scope_demo --test-enable --test-tags /sipanel_commercial_scope_core,/sipanel_sale_scope,/sipanel_scope_execution,/sipanel_scope_costing,/sipanel_scope_demo \
     --stop-after-init --log-level=test
```

Then the same on the restored clone (`sipanel_clone_<YYYYMMDD>`) for install-on-real-data behaviour. Test log files are attached to the PT register with the clone identity.

### B.5 Upgrade from the preceding build

```
# with the previous RC already installed on the clone
odoo -c /etc/odoo/odoo-clone.conf -d sipanel_clone_<YYYYMMDD> -u sipanel_commercial_scope_core,sipanel_sale_scope,sipanel_scope_execution,sipanel_scope_costing --stop-after-init
```

Migration scripts (`migrations/<version>/pre-*.py`, `post-*.py`) must be deterministic and additive (C10-D03). Verify with a before/after `\d` diff and row counts.

---

## Part C — Configuration after install (on the clone)

### C.1 Roles and groups (SIPANEL_SECURITY_MATRIX.md)

- All groups are created by `sipanel_commercial_scope_core` and are empty on install; nothing is hard-coded to a user.
- Initial business role holder: the existing active internal user "Taleghani" **only when explicitly configured** by the administrator after login/identity verification (Roadmap "Data and migration boundaries"). Do not create a new administrator.
- Record the segregation-of-duties limitation if one user receives Steward + Estimator + Sales + Finance + Execution + Administration.

### C.2 Settings parameters

| Parameter | Meaning | Value source |
|---|---|---|
| `sipanel.scope.system_plan_id` | analytic plan used as System dimension | created on clone per B-03 (SV-16); Production value TBE |
| `sipanel.scope.activity_plan_id` | analytic plan used as Activity dimension | same |
| `sipanel.scope.project_plan_id` | existing Project plan | EVIDENCE-DATED: only Project plan exists |
| `sipanel.scope.company_currency_only` | BQ-09 guard; foreign-currency quotations blocked | `True` for MVP |
| `sipanel.scope.release_retry_max` | bounded retry count on `LockError` (SV-07) | TBE, small integer, no production tuning yet |
| `sipanel.scope.clone_identity` | banner text | set in A.6 |

### C.3 Owner registry rules

Seed rows mapping `product.service_tracking` / product type / route to `NATIVE_LINE_OWNER` vs `COMPONENT_BRIDGE_OWNER` (SV-13). Review every anchor product mapping with Steward + Finance before Release is enabled (Master C1 "Anchor mapping").

### C.4 Recognised-cost policy rows

Rows are seeded only from the **Finance-signed** BQ-04 route matrix (MISSING_INPUT in this run). Until signed, `sipanel_scope_costing` reports every route as `POLICY_PENDING` and no recognised-cost sum is presented as complete.

### C.5 Decimal precision and UoM (B-01)

1. Record the current value of decimal precision `Product Unit` on the clone (EVIDENCE-DATED: 0 on Production; shipped default 2 per SV-11).
2. Change it to the proposed value on the clone only; run the Purchase/Inventory/MRP/invoice regression on existing documents (this is a global change — SV-10 shows all UoM rounding derives from it).
3. Activate `cm` (EVIDENCE-DATED inactive) and verify `_compute_quantity` chain m ↔ cm ↔ mm (SV-10).
4. Do not change `Product Price` precision without written Finance approval.

### C.6 Company-currency guard (B-06)

Verify that a quotation whose `currency_id` ≠ company currency is blocked at Add Scope, Send and Confirm, and that the block message names BQ-09. Native fallback to 1.0 exists (SV-12); the guard must not rely on native behaviour.

### C.7 Report hygiene (B-09)

1. Report action id `848` on `sale.order` — EVIDENCE-DATED from the v0.10 audit; on the clone inspect it, decide disable/remove, record decision. Not touched in this run.
2. `sale_shamsi_report` overrides global `web.external_layout_bubble` (SV-18, `views/sale_report_templates.xml:156`); render invoice, purchase and stock PDFs on the clone to confirm no unintended layout change.
3. Duplicate xpath on `span[@t-field='sale_order.commitment_date']` (`views/sale_portal_templates.xml:41` and `:59`); render portal order page and record whether both apply or one errors.

### C.8 Analytic configuration (B-03)

Create System and Activity plans, set `default_applicability`/`applicability_ids` (SV-16), grant analytic groups to the intended users, enable `analytic_costs` on the operation types selected by Finance only (EVIDENCE-DATED: disabled on all 13). Set governed non-zero `hourly_cost` for pilot employees on the clone (SV-17; EVIDENCE-DATED zero).

---

## Part D — Production deployment

**NOT AUTHORIZED BY THIS RUN.** `PRODUCTION_DEPLOYMENT_REQUIRES_SEPARATE_EXPLICIT_AUTHORIZATION`.

A future authorized change window would need, at minimum (Roadmap "Production deployment runbook requirements", Readiness §20):

1. Go-Live form signed; all PT-01…PT-32 PASS or approved NOT_APPLICABLE; B-01…B-10 closed for the enabled scope.
2. Fresh backup of `sipanel` DB + filestore + `/opt/odoo/addons` checksum manifest + config references (no secrets), and a **verified restore** of that backup on the clone host.
3. Copy of the four Production modules (never `sipanel_scope_demo`) into `/opt/odoo/addons` — which is not git-tracked (SV-20), so the release manifest's SHA256 list is the only integrity anchor; verify with `sha256sum -c` after copy.
4. Install order as in B.2 with `--stop-after-init`, then service restart in the approved window.
5. Smoke checks: login, ordinary quotation without Scope unchanged (PT-31), PDF render, portal page, no new cron activated, no mail burst.
6. Stop criteria: wrong target DB, permission error, failed restore check, any unexpected Product/contact change, schema conflict, security leakage, duplicate demand, cost mismatch, RAM/disk below the approved baseline (Readiness §16).
7. Rollback owner and regime chosen beforehand (SIPANEL_ROLLBACK_REHEARSAL_REPORT.md).
