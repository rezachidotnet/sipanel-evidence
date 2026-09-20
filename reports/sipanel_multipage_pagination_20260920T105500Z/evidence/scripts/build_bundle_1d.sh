#!/usr/bin/env bash
# Build the STEP 1D report bundle: manifest, SHA256SUMS, ZIP + .sha256.
set -euo pipefail
RUN=sipanel_multipage_pagination_20260920T105500Z
R=/home/ubuntu/sipanel_odoo_addons/reports/$RUN
ZIP=$R/SIPANEL_MULTIPAGE_PAGINATION_BUNDLE.zip
rm -f "$ZIP" "$ZIP.sha256" "$R/SHA256SUMS" "$R/REPORT_BUNDLE_MANIFEST.txt"

SHAMSI_COMMIT=$(cd /opt/odoo/addons/sale_shamsi_report && git rev-parse HEAD)
REPO_COMMIT=$(cd /home/ubuntu/sipanel_odoo_addons && git rev-parse HEAD)

{
echo "SIPANEL STEP 1D — MULTI-PAGE PAGINATION (L-02) — REPORT BUNDLE MANIFEST"
echo "Run:                 $RUN"
echo "Generated (UTC):     $(date -u +%FT%TZ)"
echo "Verdict:             PASS — L-02 reproduced, root cause fixed, 10/10 shapes clean"
echo "Target:              database sipanel, container odoo-sipanel (RestartCount=0, no restart)"
echo "Other tenants:       NOT touched (avizsazeh, shahbazi, ahantorob, odoo-db untouched)"
echo "Fix commit:          sale_shamsi_report $SHAMSI_COMMIT (branch develop/shamsi-date-core, NOT pushed)"
echo "Reports commit:      sipanel_odoo_addons $REPO_COMMIT (NOT pushed)"
echo "Recovery point:      /opt/odoo/backups/sipanel-pre-multipage-20260920T104900Z (verified, root-only, NOT in this bundle)"
echo "Tests:               sale_shamsi_report 80/80 pass (2 failed before the fix); SIPANEL modules 70/70 pass"
echo "Temporary records:   10 draft quotations + 11 scopes + 11 revisions + 77 components + 1 partner created and fully deleted"
echo
echo "FILES"
cd "$R"
find . -type f ! -name 'SIPANEL_MULTIPAGE_PAGINATION_BUNDLE.zip*' ! -name SHA256SUMS ! -name REPORT_BUNDLE_MANIFEST.txt \
  | sed 's|^\./||' | sort | while read -r f; do printf "  %-78s %9s bytes\n" "$f" "$(stat -c %s "$f")"; done
echo
echo "EXCLUDED: database dumps, filestore, container config, private keys, portal access tokens,"
echo "          prepared body HTML (carried signed image URLs and absolute paths)."
echo "REDACTION: none required — every document in this bundle was rendered from synthetic data"
echo "          created for this run and deleted afterwards; the only real-world content is the"
echo "          company's own letterhead and the salesperson block that appears on every quotation."
} > "$R/REPORT_BUNDLE_MANIFEST.txt"

cd "$R"
find . -type f ! -name 'SIPANEL_MULTIPAGE_PAGINATION_BUNDLE.zip*' ! -name SHA256SUMS -print0 \
  | sort -z | xargs -0 sha256sum > "$R/SHA256SUMS"

# refuse to ship anything secret-looking
if grep -rIlE 'BEGIN (RSA|OPENSSH|EC) PRIVATE KEY|(db_password|admin_passwd)[[:space:]]*=[[:space:]]*[^<[:space:]]|access_token=[0-9a-f-]{8}' "$R" >/dev/null 2>&1; then
  echo "SECRET DETECTED, abort" >&2
  grep -rIlE 'BEGIN (RSA|OPENSSH|EC) PRIVATE KEY|(db_password|admin_passwd)[[:space:]]*=[[:space:]]*[^<[:space:]]|access_token=[0-9a-f-]{8}' "$R" >&2
  exit 4
fi

python3 - "$ZIP" "$R" <<'PYZ'
import os, sys, zipfile
zp, root = sys.argv[1], sys.argv[2]
run = os.path.basename(root)
with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for dirpath, _dirs, files in os.walk(root):
        for name in sorted(files):
            p = os.path.join(dirpath, name)
            if name.startswith('SIPANEL_MULTIPAGE_PAGINATION_BUNDLE.zip'):
                continue
            z.write(p, os.path.join(run, os.path.relpath(p, root)))
print('entries', len(zipfile.ZipFile(zp).namelist()))
PYZ
(cd "$R" && sha256sum "$(basename "$ZIP")" > "$ZIP.sha256")
echo "BUNDLE $ZIP"
cat "$ZIP.sha256"
