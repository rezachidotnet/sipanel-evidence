#!/usr/bin/env bash
# Build the STEP 2C report bundle: manifest, SHA256SUMS, ZIP + .sha256; verify testzip, every internal entry, external hash, secret scan.
set -euo pipefail
RUN=sipanel_step2c_closeout_hardening_20260923T051626Z
REPO=/home/ubuntu/sipanel_odoo_addons
R=$REPO/reports/$RUN
ZIP=$R/SIPANEL_STEP2C_CLOSEOUT_HARDENING_BUNDLE.zip
rm -f "$ZIP" "$ZIP.sha256" "$R/SHA256SUMS" "$R/REPORT_BUNDLE_MANIFEST.txt"
SRC=$(cd $REPO && git rev-parse HEAD)
SHAMSI=$(cd /opt/odoo/addons/sale_shamsi_report && git rev-parse --short HEAD)
{
echo "SIPANEL STEP 2C-CLOSEOUT-HARDENING — BUNDLE MANIFEST"
echo "Run:                    $RUN"
echo "Generated (UTC):        $(date -u +%FT%TZ)"
echo "Verdict:                PASS — sudo action_seal bypass reproduced (7/11 before) and closed (11/11 after, 8/8 live probes refused);"
echo "                        concurrency-safe recovery script (11/11); invalid recovery point removed (116,523,008 bytes)"
echo "Target:                 database sipanel, container odoo-sipanel (RestartCount=0, no restart; /web/health 200); odoo-db not restarted"
echo "Other tenants:          NOT touched (avizsazeh, shahbazi, ahantorob; container states identical before/after)"
echo
echo "COMMITS"
echo "  baseline: 53268efc171c4cdb9640ade494678b601347e1ef (2C-HARDENING src), 6709dcfebb40348af5831fab13f2679b28a94d41 (2C-HARDENING evidence),"
echo "            84748b22ac43f6a292a5f8662d139aeca63fa653 (2C-CLOSEOUT src)"
echo "  STEP 2C-CLOSEOUT-HARDENING source:    $SRC   <- HEAD when this bundle was built"
echo "  STEP 2C-CLOSEOUT-HARDENING evidence:  created AFTER this bundle; given in the final response"
echo
echo "MODULES"
for m in sipanel_commercial_scope_core sipanel_sale_scope sipanel_scope_execution sipanel_scope_costing; do
  v=$(python3 -c "import ast;print(ast.literal_eval(open('$REPO/addons/$m/__manifest__.py').read())['version'])")
  h=$(cd $REPO/addons/$m && find . -type f ! -name '*.pyc' ! -path '*__pycache__*' -printf '%P\0' | sort -z | xargs -0 sha256sum | sha256sum | cut -c1-64)
  hi=$(cd /opt/odoo/addons/$m && find . -type f ! -name '*.pyc' ! -path '*__pycache__*' -printf '%P\0' | sort -z | xargs -0 sha256sum | sha256sum | cut -c1-64)
  printf "  %-32s %-12s tree-sha256(relative) %s  installed=%s\n" "$m" "$v" "$h" "$([ "$h" = "$hi" ] && echo IDENTICAL || echo DIFFERS)"
done
echo "  upgraded: sipanel_sale_scope (19.0.1.2.3 -> 19.0.1.2.4); sale_shamsi_report HEAD $SHAMSI, clean"
echo
echo "RECOVERY POINT   /opt/odoo/backups/sipanel-pre-2ccloseouthard-20260923T051626Z (verified; NOT in this bundle); none pruned except the authorised"
echo "                 invalid directory sipanel-pre-2ccloseout-20260922T105454Z (8 proofs, 116,523,008 bytes reclaimed)"
echo "TESTS            sudo tag 11/0 (7/11 failed before) | sales-seal all 22/0 | SIPANEL 266/0 (52+167+5+42; 204 methods) | sale_shamsi_report 80/0 | restore structural 21/21 | concurrency 11/11"
echo "PILOT            SI-26/2544 sealed by a plain Sales user; 8 pre-sudo probes on SI-26/2545 refused, state unchanged; no leak; no release/invoice/email"
echo "SYNTHETIC DATA   2 active synthetic technical contacts retained (2361, 3483); everything else 0 active"
echo
echo "FILES"
cd "$R"
find . -type f ! -name 'SIPANEL_STEP2C_CLOSEOUT_HARDENING_BUNDLE.zip*' ! -name SHA256SUMS ! -name REPORT_BUNDLE_MANIFEST.txt \
  | sed 's|^\./||' | sort | while read -r f; do printf "  %-78s %9s bytes\n" "$f" "$(stat -c %s "$f")"; done
echo
echo "EXCLUDED: database dumps, filestore, private keys, credentials, unredacted configuration, access tokens, customer secrets."
} > "$R/REPORT_BUNDLE_MANIFEST.txt"
cd "$R"
find . -type f ! -name 'SIPANEL_STEP2C_CLOSEOUT_HARDENING_BUNDLE.zip*' ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > "$R/SHA256SUMS"
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
            if name.startswith('SIPANEL_STEP2C_CLOSEOUT_HARDENING_BUNDLE.zip'):
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
