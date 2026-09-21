#!/usr/bin/env bash
# Build the STEP 2A report bundle: manifest, SHA256SUMS, ZIP + .sha256.
set -euo pipefail
RUN=sipanel_native_translation_20260921T013000Z
R=/home/ubuntu/sipanel_odoo_addons/reports/$RUN
ZIP=$R/SIPANEL_NATIVE_TRANSLATION_IMPLEMENTATION_BUNDLE.zip
rm -f "$ZIP" "$ZIP.sha256" "$R/SHA256SUMS" "$R/REPORT_BUNDLE_MANIFEST.txt"
REPO_COMMIT=$(cd /home/ubuntu/sipanel_odoo_addons && git rev-parse HEAD)
{
echo "SIPANEL STEP 2A — NATIVE ODOO TRANSLATION FIELDS — REPORT BUNDLE MANIFEST"
echo "Run:                 $RUN"
echo "Generated (UTC):     $(date -u +%FT%TZ)"
echo "Verdict:             PASS — masters natively translatable, 20 terms migrated, nothing lost"
echo "Target:              database sipanel, container odoo-sipanel (RestartCount=0, no restart)"
echo "Other tenants:       NOT touched (avizsazeh, shahbazi, ahantorob, odoo-db untouched)"
echo "Modules upgraded:    sipanel_commercial_scope_core 19.0.1.1.0, sipanel_sale_scope 19.0.1.1.0"
echo "Not changed:         sale_shamsi_report, scope_costing, scope_execution, Product Master,"
echo "                     report.url, website languages, paperformat"
echo "Repo commit:         $REPO_COMMIT (NOT pushed)"
echo "Recovery point:      /opt/odoo/backups/sipanel-pre-translation-20260921T013000Z (verified, NOT in this bundle)"
echo "Tests:               SIPANEL 122/122 pass (was 70), sale_shamsi_report 80/80 pass — 202 total"
echo "Migration:           11 field-records scanned, 10 written, 20 terms (en_US 10, fa_IR 10), 1 blank skipped"
echo "Temporary records:   1 draft quotation + 1 scope + 1 revision + 7 components + 1 partner, all deleted"
echo
echo "FILES"
cd "$R"
find . -type f ! -name 'SIPANEL_NATIVE_TRANSLATION_IMPLEMENTATION_BUNDLE.zip*' ! -name SHA256SUMS ! -name REPORT_BUNDLE_MANIFEST.txt \
  | sed 's|^\./||' | sort | while read -r f; do printf "  %-76s %9s bytes\n" "$f" "$(stat -c %s "$f")"; done
echo
echo "EXCLUDED: database dumps, filestore, container config, private keys, portal access tokens."
echo "REDACTION: none required — the only quotation in this bundle was rendered from synthetic"
echo "          data created for this run and deleted afterwards. Master customer text is the"
echo "          company's own product wording. Preview/verify JSON records value LENGTHS and"
echo "          language keys for legacy data, not raw customer values."
} > "$R/REPORT_BUNDLE_MANIFEST.txt"
cd "$R"
find . -type f ! -name 'SIPANEL_NATIVE_TRANSLATION_IMPLEMENTATION_BUNDLE.zip*' ! -name SHA256SUMS -print0 \
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
            if name.startswith('SIPANEL_NATIVE_TRANSLATION_IMPLEMENTATION_BUNDLE.zip'):
                continue
            p = os.path.join(dirpath, name)
            z.write(p, os.path.join(run, os.path.relpath(p, root)))
print('entries', len(zipfile.ZipFile(zp).namelist()))
PYZ
(cd "$R" && sha256sum "$(basename "$ZIP")" > "$ZIP.sha256")
echo "BUNDLE $ZIP"; cat "$ZIP.sha256"
