#!/usr/bin/env bash
# Build the STEP 2C report bundle: manifest, SHA256SUMS, ZIP + .sha256; verify testzip, every internal entry, external hash, secret scan.
set -euo pipefail
RUN=sipanel_step2c_hardening_20260922T083014Z
REPO=/home/ubuntu/sipanel_odoo_addons
R=$REPO/reports/$RUN
ZIP=$R/SIPANEL_STEP2C_HARDENING_BUNDLE.zip
rm -f "$ZIP" "$ZIP.sha256" "$R/SHA256SUMS" "$R/REPORT_BUNDLE_MANIFEST.txt"
SRC=$(cd $REPO && git rev-parse HEAD)
SHAMSI=$(cd /opt/odoo/addons/sale_shamsi_report && git rev-parse --short HEAD)
{
echo "SIPANEL STEP 2C-HARDENING — BUNDLE MANIFEST"
echo "Run:                    $RUN"
echo "Generated (UTC):        $(date -u +%FT%TZ)"
echo "Verdict:                PASS — demand provenance behaviourally immutable; Native Owner boundary enforced in cancel/reduce;"
echo "                        governed Sales cancellation without demand rights; safe restore instructions in the script"
echo "Target:                 database sipanel, container odoo-sipanel (RestartCount=0, no restart); odoo-db not restarted"
echo "Other tenants:          NOT touched (avizsazeh, shahbazi, ahantorob)"
echo
echo "COMMITS"
echo "  STEP 2C source:                 e01da1973784ccfd692ac13a622707e4c3bae576"
echo "  STEP 2C evidence:               5dc0f41087fe5b8bdef8f5de9c9d0aaa101c16cb"
echo "  STEP 2C-HARDENING source:       $SRC   <- HEAD when this bundle was built"
echo "  STEP 2C-HARDENING evidence:     created AFTER this bundle; given in the final response"
echo
echo "MODULES"
for m in sipanel_commercial_scope_core sipanel_sale_scope sipanel_scope_execution sipanel_scope_costing; do
  v=$(python3 -c "import ast;print(ast.literal_eval(open('$REPO/addons/$m/__manifest__.py').read())['version'])")
  h=$(cd $REPO/addons/$m && find . -type f ! -name '*.pyc' ! -path '*__pycache__*' -printf '%P\0' | sort -z | xargs -0 sha256sum | sha256sum | cut -c1-64)
  printf "  %-32s %-12s tree-sha256(relative) %s\n" "$m" "$v" "$h"
done
echo "  upgraded: sipanel_scope_execution (19.0.1.0.1 -> 19.0.1.0.2); sale_shamsi_report HEAD $SHAMSI, clean"
echo
echo "RECOVERY POINT   /opt/odoo/backups/sipanel-pre-2chardening-20260922T083014Z (verified; NOT in this bundle); none pruned"
echo "TESTS            SIPANEL 240 / 0 (52+141+5+42; 182 methods) | hardening tag 20 / 0 (17/20 failed before) | sale_shamsi_report 80 / 0"
echo "PILOT            SI-26/2094 (bridge, Sales-owned) + SI-26/2095 (native); 32 spoof probes refused; Sales cancel OK; native move untouched; 0 duplicates"
echo "SYNTHETIC DATA   2 active synthetic technical contacts retained (2361, 3483); everything else 0 active"
echo
echo "FILES"
cd "$R"
find . -type f ! -name 'SIPANEL_STEP2C_HARDENING_BUNDLE.zip*' ! -name SHA256SUMS ! -name REPORT_BUNDLE_MANIFEST.txt \
  | sed 's|^\./||' | sort | while read -r f; do printf "  %-78s %9s bytes\n" "$f" "$(stat -c %s "$f")"; done
echo
echo "EXCLUDED: database dumps, filestore, private keys, credentials, unredacted configuration, access tokens, customer secrets."
} > "$R/REPORT_BUNDLE_MANIFEST.txt"
cd "$R"
find . -type f ! -name 'SIPANEL_STEP2C_HARDENING_BUNDLE.zip*' ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > "$R/SHA256SUMS"
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
            if name.startswith('SIPANEL_STEP2C_HARDENING_BUNDLE.zip'):
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
