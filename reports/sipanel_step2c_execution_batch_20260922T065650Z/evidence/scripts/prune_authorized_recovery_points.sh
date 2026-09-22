#!/usr/bin/env bash
# Deletes EXACTLY the four owner-authorized recovery-point directories. No globs, no variables in targets.
set -euo pipefail
BASE=/opt/odoo/backups
AUTH=(
  /opt/odoo/backups/sipanel-pre-customer-output-fix-20260920T062942Z
  /opt/odoo/backups/sipanel-pre-live-fix-20260920T080013Z
  /opt/odoo/backups/sipanel-pre-layout-fix-20260920T084541Z
  /opt/odoo/backups/sipanel-pre-multipage-20260920T104900Z
)
PROTECTED=(
  /opt/odoo/backups/sipanel-pre-scope-20260919T164558Z
  /opt/odoo/backups/sipanel-pre-translation-20260921T013000Z
  /opt/odoo/backups/sipanel-pre-sepbill-20260921T021500Z
  /opt/odoo/backups/sipanel-pre-2bhardening-20260922T060000Z
)
recovered=0
for t in "${AUTH[@]}"; do
  echo "== validate $t"
  if sudo test -L "$t"; then echo "REFUSED: symlink"; continue; fi
  if ! sudo test -d "$t"; then echo "REFUSED: not a directory"; continue; fi
  rp=$(sudo realpath -e "$t")
  if [ "$rp" != "$t" ]; then echo "REFUSED: realpath '$rp' != authorized path"; continue; fi
  case "$rp" in "$BASE"/*) ;; *) echo "REFUSED: outside $BASE"; continue;; esac
  if [ "$(sudo find "$t" -type l | wc -l)" != "0" ]; then echo "REFUSED: contains symlinks"; continue; fi
  for pr in "${PROTECTED[@]}"; do if [ "$rp" = "$pr" ]; then echo "REFUSED: protected"; continue 2; fi; done
  bytes=$(sudo du -sb "$rp" | cut -f1)
  echo "DELETING exact resolved path: $rp ($bytes bytes)"
  sudo rm -rf --one-file-system -- "$rp"
  if sudo test -e "$rp"; then echo "ERROR: still exists"; exit 5; fi
  echo "DELETED $rp"; recovered=$((recovered + bytes))
done
sync
echo "BYTES_RECOVERED_SUM_OF_DU=$recovered"
