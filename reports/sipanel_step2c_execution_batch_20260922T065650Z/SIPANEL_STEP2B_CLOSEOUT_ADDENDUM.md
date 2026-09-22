# SIPANEL STEP 2B Closeout Addendum (run 20260922T065650Z)

Scope: record the exact STEP 2B-HARDENING commits and replace the ambiguous
restore procedure from the previous recovery reports. Nothing in the STEP 2B or
STEP 2B-HARDENING report directories was modified, and the STEP 2B ZIP was not
rewritten.

## A1. Exact STEP 2B-HARDENING commits

Recorded before any change in this run (`git status --short` was empty).

| Item | Value |
|---|---|
| `git rev-parse HEAD` at start | `3229813d0c0a524c5f282c4ca5618b5b8ad54081` |
| Working tree | clean (no uncommitted or untracked files) |
| Branch | `master` (not pushed) |
| Source commit (STEP 2B-HARDENING code) | **`3229813`** |
| Evidence/bundle commit (STEP 2B-HARDENING reports + ZIP) | **`3229813`** (the same commit) |
| Parent commit | `490eb30f031bd2a3d2dc4e5143756f6021fb4bc1` (STEP 2B) |

`git log --oneline --decorate -10`:

```
3229813 (HEAD -> master) SIPANEL STEP 2B-HARDENING 20260922T060000Z: guard invoice provenance, fix reconciliation evidence, fail closed on pricing
490eb30 SIPANEL STEP 2B 20260921T021500Z: separately-billable Sale Lines and Invoice Lines
c737034 SIPANEL STEP 2A 20260921T013000Z: native Odoo translation fields for Scope and Recipe masters
8d10567 SIPANEL STEP 1D 20260920T105500Z: correct the test-baseline statement and rebuild the bundle
7ae671d SIPANEL STEP 1D 20260920T105500Z: multi-page pagination defect L-02 reproduced and fixed
6820983 SIPANEL STEP 1C 20260920T084541Z: Persian PDF cover overlap reproduced and fixed (sale_shamsi_report b17fbb5), D-02 validated on a fresh quotation
484b884 SIPANEL STEP 1B 20260920T080013Z: D-01 report.url applied (loopback gevent port), fa_IR enabled on website, live PDF/portal validation reports
ca9c474 SIPANEL customer-output validation 20260920T060817Z: reports, redacted evidence, test logs and bundle
0e2d63e SIPANEL customer-output validation 20260920T060817Z: D-02 unit names in quotation language, D-03 portal signature binding
46f4135 SIPANEL run 20260919T164530Z: regenerated manifests, SHA256SUMS and bundle after documentation reconciliation
```

### Why one commit, and what the bundle says about itself

STEP 2B-HARDENING was committed as a **single** commit containing both the
source changes (7 files under `addons/`, +239/-25) and the report directory
(22 files under `reports/`, including the ZIP). Its bundle manifest states
`Started from commit: 490eb30` and `Parent commit at bundle build: 490eb30…`
with an explicit note that the containing commit is created afterwards. So:

* `490eb30` is **not** the STEP 2B-HARDENING commit; it is the parent at
  bundle-build time.
* the commit that contains the hardening source **and** its evidence is
  `3229813`; the ZIP inside it cannot name that hash because it was built
  first (the ambiguity STEP 2C avoids by committing source and evidence
  separately, see Phase E of the STEP 2C report).

### Content verification of `3229813`

Checked with `git show 3229813 -- <file>`:

| Correction | Evidence in the diff |
|---|---|
| Process-local invoice provenance guard | `account_move_line.py`: `_sipanel_trace_guarded()` returns `guard(self.env, 'sipanel_invoice_trace')` only; the `sipanel_from_sale_invoice` context check and the `sale_line_ids` exemption are removed. `sale_order.py`: `_create_invoices` wraps `super()` with `guard_ctx('sipanel_invoice_trace')`. |
| Reconciliation evidence correction | `reports/sipanel_separately_billable_20260921T021500Z/SIPANEL_COMMERCIAL_RECONCILIATION_REPORT.md` (+22/-2) and `SIPANEL_SEPARATELY_BILLABLE_IMPLEMENTATION_REPORT.md` (+10/-1) corrected in place; `evidence/reconciliation/pilot_reconciliation_by_revision.json` keyed by revision id. |
| Pricelist fail-closed | `quote_scope_component.py`: new `sell_price_error` field; `_sell_price_snapshot_vals` no longer substitutes `product.list_price`; `separately_billable.py`: blocking issue `SB_PRICE_FAILED`. |
| Module version | `sipanel_sale_scope/__manifest__.py` 19.0.1.2.0 -> 19.0.1.2.1 |

Residual mentions of `sipanel_from_sale_invoice` in the tree are one code
comment describing the removed mechanism and the regression test that proves
the removed hatch stays closed (`test_raw_sipanel_from_sale_invoice_context_is_refused`).
No code path reads that key.

Installed source parity: `diff -rq` between `addons/<module>` at `3229813` and
`/opt/odoo/addons/<module>` reports IDENTICAL for all four SIPANEL modules.
The STEP 2B-HARDENING directory still verifies (`sha256sum -c SHA256SUMS`: 0
mismatches; bundle `.sha256`: OK).

Installed versions at the start of this run: `sipanel_commercial_scope_core`
19.0.1.1.0, `sipanel_sale_scope` 19.0.1.2.1, `sipanel_scope_execution`
19.0.1.0.0, `sipanel_scope_costing` 19.0.1.0.0.

## A2. Corrected restore procedure (NOT executed)

### The defect in the previous documentation

Every recovery-point report so far (and the last line printed by
`scripts/sipanel_recovery_point.sh`) documents this restore:

```
docker exec -i odoo-db psql -U odoo -d postgres -c "CREATE DATABASE sipanel_restore"
docker exec -i odoo-db pg_restore -U odoo -d sipanel_restore < <point>/sipanel.dump
sudo tar -C /opt/odoo/data/filestore -xzf <point>/filestore-sipanel.tar.gz
```

The database part restores into a separate database, but the archive was
created with `tar -C /opt/odoo/data/filestore -czf … sipanel`, so its entries
are `sipanel/…`. Extracting it with `-C /opt/odoo/data/filestore` writes into
**`/opt/odoo/data/filestore/sipanel`, the live production filestore**,
overwriting current attachments with older ones during what was meant to be a
rehearsal. That procedure must not be used.

### Corrected procedure

Conventions: `<point>` is the resolved recovery-point directory; `<TS>` is a
fresh UTC timestamp; every command marked **DESTRUCTIVE** must only be run
with the exact resolved target shown, never with a glob or an unset variable.
The whole procedure must be run as a rehearsal on a database and filestore
whose names contain `restore_rehearsal`; the live `sipanel` database and
`/opt/odoo/data/filestore/sipanel` are never a target.

```bash
# 0. Fix the targets once and verify them
TS=$(date -u +%Y%m%dT%H%M%SZ)
POINT=$(sudo realpath -e /opt/odoo/backups/sipanel-pre-step2c-20260922T065650Z)   # example point
RDB="sipanel_restore_rehearsal_${TS}"
RFS="/opt/odoo/data/filestore/${RDB}"
test "$RDB" != "sipanel" && test "$RFS" != "/opt/odoo/data/filestore/sipanel" || { echo REFUSED; exit 1; }
sudo sha256sum -c "$POINT/SHA256SUMS"                     # every artefact must print OK

# 1. Database: restore ONLY into the rehearsal database
docker exec -i odoo-db psql -U odoo -d postgres -tAc "select 1 from pg_database where datname='${RDB}'" | grep -q 1 && { echo "exists"; exit 1; }
docker exec -i odoo-db psql -U odoo -d postgres -c "CREATE DATABASE \"${RDB}\" OWNER odoo"
docker exec -i odoo-db pg_restore -U odoo -d "${RDB}" --no-owner --role=odoo < "$POINT/sipanel.dump"
docker exec -i odoo-db psql -U odoo -d "${RDB}" -tAc "select count(*) from ir_module_module where state='installed'"

# 2. Filestore: inspect the archive layout BEFORE extracting anything
sudo tar -tzf "$POINT/filestore-sipanel.tar.gz" | head -5     # expect entries starting with "sipanel/"
sudo tar -tzf "$POINT/filestore-sipanel.tar.gz" | awk -F/ '{print $1}' | sort -u   # must be exactly: sipanel

# 3. Extract into a temporary directory first (never into /opt/odoo/data/filestore)
TMP=$(sudo mktemp -d /opt/odoo/restore_rehearsal_${TS}.XXXX)
sudo tar -C "$TMP" -xzf "$POINT/filestore-sipanel.tar.gz"
sudo test -d "$TMP/sipanel" || { echo "unexpected layout"; exit 1; }

# 4. Install it ONLY under the rehearsal name, with the live owner and permissions
OWNER=$(sudo stat -c '%u:%g' /opt/odoo/data/filestore/sipanel)
sudo test ! -e "$RFS" || { echo "target exists"; exit 1; }
sudo mv "$TMP/sipanel" "$RFS"
sudo chown -R "$OWNER" "$RFS"
sudo chmod -R u+rwX,go-rwx "$RFS"
sudo rmdir "$TMP"
sudo diff <(sudo stat -c '%U:%G %a' /opt/odoo/data/filestore/sipanel) <(sudo stat -c '%U:%G %a' "$RFS")   # same owner/mode

# 5. Neutralise integrations in the rehearsal database BEFORE any Odoo process opens it
docker exec -i odoo-db psql -U odoo -d "${RDB}" <<'SQL'
UPDATE ir_mail_server SET active = false;
UPDATE fetchmail_server SET active = false WHERE true;
UPDATE ir_cron SET active = false;
UPDATE ir_config_parameter SET value = 'http://127.0.0.1:8072' WHERE key = 'report.url';
UPDATE ir_config_parameter SET value = 'http://localhost' WHERE key = 'web.base.url';
DELETE FROM ir_config_parameter WHERE key = 'web.base.url.freeze';
UPDATE res_users SET totp_secret = NULL WHERE totp_secret IS NOT NULL;
SQL
# (also disable any outbound webhook / payment provider rows if present: check ir_module_module for payment_* and website modules)

# 6. Only then, optionally, start a THROW-AWAY Odoo process against the rehearsal DB
#    (never the production container's running service; --no-http keeps it off the network)
docker run --rm --network container:odoo-db -v /opt/odoo/addons:/mnt/extra-addons:ro \
  -v /opt/odoo/data:/var/lib/odoo <odoo-sipanel image id> \
  odoo -d "${RDB}" --db_host=db --db_user=odoo --db_password=<from config> --no-http --stop-after-init --list-db=false

# 7. Cleanup (DESTRUCTIVE - exact rehearsal targets only)
test "$RDB" != "sipanel" || exit 1
docker exec -i odoo-db psql -U odoo -d postgres -c "DROP DATABASE \"${RDB}\""            # DESTRUCTIVE: rehearsal DB
test "$(sudo realpath -e "$RFS")" = "/opt/odoo/data/filestore/${RDB}" || exit 1
sudo rm -rf --one-file-system -- "/opt/odoo/data/filestore/${RDB}"                       # DESTRUCTIVE: rehearsal filestore
```

Rules enforced by the procedure: unique rehearsal names; dump restored only
into the rehearsal database; archive layout inspected before extraction;
extraction into a temporary directory; installation only as
`/opt/odoo/data/filestore/<rehearsal name>`; owner and mode copied from the
live filestore; the live `sipanel` filestore is never a target; integrations
neutralised before any Odoo process starts; cleanup commands name their exact
resolved target and are marked DESTRUCTIVE.

The script `scripts/sipanel_recovery_point.sh` still prints the old
one-liner; it was not changed in this run because the task did not authorise
script edits, and the corrected procedure above supersedes it. Recommended
follow-up: replace that final `echo` with a pointer to this document.

## A3. Recovery-point pruning

Performed in this run under the owner's explicit authorisation; see
`SIPANEL_RECOVERY_POINT_PRUNING_REPORT.md` for the full before/after evidence.
