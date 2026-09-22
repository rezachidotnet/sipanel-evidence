#!/usr/bin/env bash
# Build the STEP 2C report bundle: manifest, SHA256SUMS, ZIP + .sha256; verify testzip, every internal entry, external hash, secret scan.
set -euo pipefail
RUN=sipanel_step2c_execution_batch_20260922T065650Z
REPO=/home/ubuntu/sipanel_odoo_addons
R=$REPO/reports/$RUN
ZIP=$R/SIPANEL_STEP2C_EXECUTION_BATCH_BUNDLE.zip
rm -f "$ZIP" "$ZIP.sha256" "$R/SHA256SUMS" "$R/REPORT_BUNDLE_MANIFEST.txt"
SRC=$(cd $REPO && git rev-parse HEAD)
SHAMSI=$(cd /opt/odoo/addons/sale_shamsi_report && git rev-parse --short HEAD)
{
echo "SIPANEL STEP 2C — EXECUTION BATCH BUNDLE MANIFEST"
echo "Run:                    $RUN"
echo "Generated (UTC):        $(date -u +%FT%TZ)"
echo "Verdict:                PASS_WITH_DEFECTS_FIXED — one component -> one operational demand owner -> one actual-cost source"
echo "                        holds on the installed release path after CD-2C-01/02/03 were corrected"
echo "Target:                 database sipanel, container odoo-sipanel (RestartCount=0, no restart); odoo-db not restarted"
echo "Other tenants:          NOT touched (avizsazeh, shahbazi, ahantorob)"
echo
echo "COMMITS"
echo "  STEP 2B-HARDENING source commit:    3229813d0c0a524c5f282c4ca5618b5b8ad54081"
echo "  STEP 2B-HARDENING evidence commit:  3229813d0c0a524c5f282c4ca5618b5b8ad54081 (same single commit; parent 490eb30)"
echo "  STEP 2C source commit (code+tests): $SRC   <- HEAD when this bundle was built"
echo "  STEP 2C evidence/bundle commit:     created AFTER this bundle; it cannot be named here and is given in the final response"
echo
echo "MODULES"
for m in sipanel_commercial_scope_core sipanel_sale_scope sipanel_scope_execution sipanel_scope_costing; do
  v=$(python3 -c "import ast;print(ast.literal_eval(open('$REPO/addons/$m/__manifest__.py').read())['version'])")
  h=$(find $REPO/addons/$m -type f ! -name '*.pyc' ! -path '*__pycache__*' -print0 | sort -z | xargs -0 sha256sum | sha256sum | cut -c1-64)
  printf "  %-32s %-12s tree-sha256 %s\n" "$m" "$v" "$h"
done
echo "  upgraded: sipanel_sale_scope (19.0.1.2.1 -> 19.0.1.2.2), sipanel_scope_execution (19.0.1.0.0 -> 19.0.1.0.1)"
echo "  sale_shamsi_report: HEAD $SHAMSI, clean, not modified"
echo
echo "RECOVERY POINTS"
echo "  pruned (owner-authorised, 458,612,231 bytes by du; df avail 2,635,862,016 -> 3,094,478,848):"
echo "    /opt/odoo/backups/sipanel-pre-customer-output-fix-20260920T062942Z"
echo "    /opt/odoo/backups/sipanel-pre-live-fix-20260920T080013Z"
echo "    /opt/odoo/backups/sipanel-pre-layout-fix-20260920T084541Z"
echo "    /opt/odoo/backups/sipanel-pre-multipage-20260920T104900Z"
echo "  created: /opt/odoo/backups/sipanel-pre-step2c-20260922T065650Z (115,209,271 bytes, verified; NOT in this bundle)"
echo
echo "TESTS   SIPANEL 214 / 0 failures (52+141+5+16; 162 methods) | sale_shamsi_report 80 / 0 | STEP 2C tag 8 / 0 (6/8 failed before the fixes)"
echo "PILOT   6 synthetic orders SI-26/1445,1446,1447,1724,1725,1726 (prefix SIPANEL-STEP2C-20260922T065650Z); all cancelled and cleaned;"
echo "        no invoice/bill posted, no email sent, no real stock consumed; retained lineage listed in SIPANEL_STEP2C_TEMPORARY_DATA_CLEANUP.md"
echo
echo "FILES"
cd "$R"
find . -type f ! -name 'SIPANEL_STEP2C_EXECUTION_BATCH_BUNDLE.zip*' ! -name SHA256SUMS ! -name REPORT_BUNDLE_MANIFEST.txt \
  | sed 's|^\./||' | sort | while read -r f; do printf "  %-78s %9s bytes\n" "$f" "$(stat -c %s "$f")"; done
echo
echo "EXCLUDED: database dumps, filestore, private keys, credentials, unredacted configuration, access tokens, customer secrets."
} > "$R/REPORT_BUNDLE_MANIFEST.txt"
cd "$R"
find . -type f ! -name 'SIPANEL_STEP2C_EXECUTION_BATCH_BUNDLE.zip*' ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > "$R/SHA256SUMS"
# secret scan (fail closed); `password=False` in new_test_user(...) is a literal no-password flag, not a credential
PAT='BEGIN (RSA|OPENSSH|EC|PGP) PRIVATE KEY|(db_password|admin_passwd|password)[[:space:]]*=[[:space:]]*[^<[:space:]]|access_token=[0-9a-f-]{8}|AKIA[0-9A-Z]{16}'
HITS=$(grep -rInE "$PAT" "$R" | grep -vE 'password[[:space:]]*=[[:space:]]*(False|None)' || true)
if [ -n "$HITS" ]; then echo "SECRET DETECTED, abort" >&2; echo "$HITS" >&2; exit 4; fi
echo "secret scan: clean"
python3 - "$ZIP" "$R" <<'PYZ'
import os, sys, zipfile, hashlib
zp, root = sys.argv[1], sys.argv[2]
run = os.path.basename(root)
with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for dirpath, _dirs, files in os.walk(root):
        for name in sorted(files):
            if name.startswith('SIPANEL_STEP2C_EXECUTION_BATCH_BUNDLE.zip'):
                continue
            p = os.path.join(dirpath, name)
            z.write(p, os.path.join(run, os.path.relpath(p, root)))
z = zipfile.ZipFile(zp)
assert z.testzip() is None, 'testzip failed'
# verify every SHA256SUMS entry against the zip content
sums = dict(line.split('  ', 1)[::-1] for line in z.read(os.path.join(run, 'SHA256SUMS')).decode().splitlines())
bad = 0
for name, h in sums.items():
    data = z.read(os.path.join(run, name[2:] if name.startswith('./') else name))
    if hashlib.sha256(data).hexdigest() != h:
        bad += 1; print('MISMATCH', name)
print('zip entries', len(z.namelist()), 'sha entries verified', len(sums), 'mismatches', bad)
assert bad == 0
PYZ
(cd "$R" && sha256sum "$(basename "$ZIP")" > "$ZIP.sha256" && sha256sum -c "$ZIP.sha256")
echo "BUNDLE $ZIP"; cat "$ZIP.sha256"
