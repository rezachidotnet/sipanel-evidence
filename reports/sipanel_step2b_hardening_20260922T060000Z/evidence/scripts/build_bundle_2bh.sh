#!/usr/bin/env bash
set -euo pipefail
RUN=sipanel_step2b_hardening_20260922T060000Z
R=/home/ubuntu/sipanel_odoo_addons/reports/$RUN
ZIP=$R/SIPANEL_STEP2B_HARDENING_BUNDLE.zip
rm -f "$ZIP" "$ZIP.sha256" "$R/SHA256SUMS" "$R/REPORT_BUNDLE_MANIFEST.txt"
PARENT=$(cd /home/ubuntu/sipanel_odoo_addons && git rev-parse HEAD)
SHAMSI=$(cd /opt/odoo/addons/sale_shamsi_report && git rev-parse --short HEAD)
{
echo "SIPANEL STEP 2B-HARDENING — BUNDLE MANIFEST"
echo "Run:                 $RUN"
echo "Generated (UTC):     $(date -u +%FT%TZ)"
echo "Started from commit: 490eb30"
echo "Verdict:             PASS — invoice provenance guarded by process-local token,"
echo "                     reconciliation evidence keyed by revision id, pricelist fails closed"
echo "Target:              database sipanel, container odoo-sipanel (RestartCount=0, no restart)"
echo "Other tenants:       NOT touched (avizsazeh, shahbazi, ahantorob, odoo-db untouched)"
echo "Module upgraded:     sipanel_sale_scope 19.0.1.2.1 (the only module whose source changed)"
echo "Not changed:         sale_shamsi_report (HEAD $SHAMSI, clean), commercial_scope_core,"
echo "                     scope_costing, scope_execution, report.url, website languages, paperformat"
echo
echo "COMMITS"
echo "  Parent commit at bundle build:  $PARENT"
echo "     HEAD *before* this run's commit: the manifest and ZIP are themselves committed,"
echo "     so the commit CONTAINING this report is created immediately after and is given"
echo "     in the final response. Same convention as STEP 2A/2B; see the STEP 2B P2 note."
echo
echo "Recovery point:      /opt/odoo/backups/sipanel-pre-2bhardening-20260922T060000Z (verified, NOT in this bundle)"
echo "Disk:                2642 MB free before, ~2.5 G free after; 9 recovery points before, none deleted"
echo "Tests:               SIPANEL 202/202 pass (was 184); sale_shamsi_report 80/80 pass — 282 total"
echo "Reconciliation:      revision 886 anchor 30,000,000 / separate 12,300,000, problems []"
echo "                     revision 887 anchor 0 / separate 6,000,000, problems []"
echo "Records:             no active synthetic records; nothing created beyond rolled-back test data;"
echo "                     no invoice posted; no email sent"
echo
echo "NOTE ON THE STEP 2B DIRECTORY"
echo "  Two STEP 2B markdown files were corrected in place and now diverge from that run's"
echo "  SHA256SUMS. The STEP 2B ZIP was deliberately NOT rewritten; before/after hashes are"
echo "  recorded in SIPANEL_RECONCILIATION_EVIDENCE_CORRECTION.md section 4."
echo
echo "FILES"
cd "$R"
find . -type f ! -name 'SIPANEL_STEP2B_HARDENING_BUNDLE.zip*' ! -name SHA256SUMS ! -name REPORT_BUNDLE_MANIFEST.txt \
  | sed 's|^\./||' | sort | while read -r f; do printf "  %-74s %9s bytes\n" "$f" "$(stat -c %s "$f")"; done
echo
echo "EXCLUDED: database dumps, filestore, container config, private keys, portal access tokens."
} > "$R/REPORT_BUNDLE_MANIFEST.txt"
cd "$R"
find . -type f ! -name 'SIPANEL_STEP2B_HARDENING_BUNDLE.zip*' ! -name SHA256SUMS -print0 \
  | sort -z | xargs -0 sha256sum > "$R/SHA256SUMS"
if grep -rIlE 'BEGIN (RSA|OPENSSH|EC) PRIVATE KEY|(db_password|admin_passwd)[[:space:]]*=[[:space:]]*[^<[:space:]]|access_token=[0-9a-f-]{8}' "$R" >/dev/null 2>&1; then
  echo "SECRET DETECTED, abort" >&2; exit 4
fi
python3 - "$ZIP" "$R" <<'PYZ'
import os, sys, zipfile
zp, root = sys.argv[1], sys.argv[2]
run = os.path.basename(root)
with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for dirpath, _dirs, files in os.walk(root):
        for name in sorted(files):
            if name.startswith('SIPANEL_STEP2B_HARDENING_BUNDLE.zip'):
                continue
            p = os.path.join(dirpath, name)
            z.write(p, os.path.join(run, os.path.relpath(p, root)))
print('entries', len(zipfile.ZipFile(zp).namelist()))
PYZ
(cd "$R" && sha256sum "$(basename "$ZIP")" > "$ZIP.sha256")
echo "BUNDLE $ZIP"; cat "$ZIP.sha256"
