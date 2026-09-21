#!/usr/bin/env bash
# Build the STEP 2B report bundle: manifest, SHA256SUMS, ZIP + .sha256.
set -euo pipefail
RUN=sipanel_separately_billable_20260921T021500Z
R=/home/ubuntu/sipanel_odoo_addons/reports/$RUN
ZIP=$R/SIPANEL_SEPARATELY_BILLABLE_IMPLEMENTATION_BUNDLE.zip
rm -f "$ZIP" "$ZIP.sha256" "$R/SHA256SUMS" "$R/REPORT_BUNDLE_MANIFEST.txt"
PARENT=$(cd /home/ubuntu/sipanel_odoo_addons && git rev-parse HEAD)
SHAMSI=$(cd /opt/odoo/addons/sale_shamsi_report && git rev-parse --short HEAD)
{
echo "SIPANEL STEP 2B — SEPARATELY BILLABLE SALE AND INVOICE LINES — BUNDLE MANIFEST"
echo "Run:                 $RUN"
echo "Generated (UTC):     $(date -u +%FT%TZ)"
echo "Verdict:             PASS — own-line components are governed, idempotent Sale Lines"
echo "                     that flow natively into invoice lines"
echo "Target:              database sipanel, container odoo-sipanel (RestartCount=0, no restart)"
echo "Other tenants:       NOT touched (avizsazeh, shahbazi, ahantorob, odoo-db untouched)"
echo "Modules upgraded:    sipanel_sale_scope 19.0.1.2.0; sipanel_commercial_scope_core (P1 only)"
echo "Not changed:         sale_shamsi_report (HEAD $SHAMSI, clean), scope_costing, scope_execution,"
echo "                     Product Master, report.url, website languages, paperformat"
echo
echo "COMMITS — see SIPANEL_STEP2A_HARDENING_AND_COMMIT_RECONCILIATION.md (P2)"
echo "  Parent commit at bundle build:  $PARENT"
echo "     This is HEAD *before* this run's commit, because the manifest and the ZIP are"
echo "     themselves committed. The commit that CONTAINS this report directory is created"
echo "     immediately after this bundle and is reported in the STEP 2B final response."
echo "     The STEP 2A manifest recorded its parent the same way; that value was stale,"
echo "     not incorrect, and the old bundle is deliberately not rewritten."
echo
echo "Recovery point:      /opt/odoo/backups/sipanel-pre-sepbill-20260921T021500Z (verified, NOT in this bundle)"
echo "Tests:               SIPANEL 184/184 pass (was 122); sale_shamsi_report 80/80 pass — 264 total"
echo "Live pilot:          Persian quotation -> seal -> optional acceptance -> re-seal -> confirm"
echo "                     -> DRAFT invoice (never posted, deleted in cleanup)"
echo "Temporary records:   draft invoice deleted; order cancelled and retained; Scopes, pilot master,"
echo "                     products and partner archived; sealed revisions and artifacts retained by design"
echo
echo "FILES"
cd "$R"
find . -type f ! -name 'SIPANEL_SEPARATELY_BILLABLE_IMPLEMENTATION_BUNDLE.zip*' ! -name SHA256SUMS ! -name REPORT_BUNDLE_MANIFEST.txt \
  | sed 's|^\./||' | sort | while read -r f; do printf "  %-76s %9s bytes\n" "$f" "$(stat -c %s "$f")"; done
echo
echo "EXCLUDED: database dumps, filestore, container config, private keys, portal access tokens."
echo "REDACTION: every document here was produced from synthetic data created for this run."
echo "          The invoice evidence redacts the customer identifier; no invoice was posted."
} > "$R/REPORT_BUNDLE_MANIFEST.txt"
cd "$R"
find . -type f ! -name 'SIPANEL_SEPARATELY_BILLABLE_IMPLEMENTATION_BUNDLE.zip*' ! -name SHA256SUMS -print0 \
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
            if name.startswith('SIPANEL_SEPARATELY_BILLABLE_IMPLEMENTATION_BUNDLE.zip'):
                continue
            p = os.path.join(dirpath, name)
            z.write(p, os.path.join(run, os.path.relpath(p, root)))
print('entries', len(zipfile.ZipFile(zp).namelist()))
PYZ
(cd "$R" && sha256sum "$(basename "$ZIP")" > "$ZIP.sha256")
echo "BUNDLE $ZIP"; cat "$ZIP.sha256"
