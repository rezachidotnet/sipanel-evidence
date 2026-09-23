# SIPANEL Invalid Recovery-Point Removal Report (run 20260923T051626Z)

Authorised target (exact): `/opt/odoo/backups/sipanel-pre-2ccloseout-20260922T105454Z`.
Evidence: `evidence/removal/invalid_recovery_point_removal.txt` (the first attempt refused itself because a
filesystem-wide `fuser -m` probe reported every process using `/`; the re-run used a directory-scoped
`fuser -v` and `lsof +D`, both empty).

| Proof | Result |
|---|---|
| `realpath -e` equals the exact authorised path | PASS (`/opt/odoo/backups/sipanel-pre-2ccloseout-20260922T105454Z`) |
| basename begins with `sipanel-pre-2ccloseout-` | PASS |
| `INVALID_DO_NOT_USE.txt` exists | PASS |
| not the valid point `…-20260922T111500Z` (compared by realpath) | PASS |
| not a symlink | PASS |
| not a mount point (`mountpoint -q`) | PASS |
| not referenced by any running process (`lsof +D` 0 lines, `fuser -v` on the directory and its files: 0 processes) | PASS |
| not the latest valid recovery point (latest valid by TIMESTAMP: `20260922T111233Z` = `…-20260922T111500Z`) | PASS |

Recorded before deletion: size 116,489,664 bytes (`du -sb`); marker contents
"INVALID RECOVERY POINT - DO NOT USE. Written by two concurrent runs of scripts/sipanel_recovery_point.sh at 2026-09-22T11:11Z …";
`df` available 2,254,774,272 bytes.

Deletion: `sudo rm -rf --one-file-system -- /opt/odoo/backups/sipanel-pre-2ccloseout-20260922T105454Z` (the resolved path, no glob), then `sync`; the path no longer exists.

After: `df` available 2,371,297,280 bytes → **116,523,008 bytes reclaimed** (du size 116,489,664 plus directory blocks). The valid point `…-20260922T111500Z` re-verified (`sha256sum -c` OK ×6). No other recovery point was touched; inventory after removal lists the eight previous entries plus the valid closeout point.
