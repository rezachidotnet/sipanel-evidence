# SIPANEL Recovery-Point Concurrency Report (run 20260923T051626Z)

Finding: `scripts/sipanel_recovery_point.sh` used `sudo mkdir -p "$DEST"` and no lock, so two invocations could write into one destination (this happened on 2026-09-22 and produced the invalid directory removed in this run).

## Correction (`scripts/sipanel_recovery_point.sh`, committed in the source commit)

| Requirement | Implementation |
|---|---|
| refuse an existing DEST before writing anything | `test -e "$DEST"` → `DEST_ALREADY_EXISTS`, exit 7, before any artefact |
| reserve DEST atomically, no `mkdir -p` | `$SUDO mkdir "$DEST"` (no `-p`): the kernel refuses if the directory appeared meanwhile → `DEST_ALREADY_EXISTS`, exit 7 |
| non-blocking recovery-operation lock | `exec 9>>"$RP_LOCK"` + `flock -n 9` on `/run/lock/sipanel_recovery_point.lock` (writer pid recorded); a concurrent invocation gets `RECOVERY_POINT_BUSY`, exit 6, before reservation |
| second concurrent invocation: exit non-zero, no dump/partial archive, no modification of existing points, clear message | proven by the tests below (BUSY / ALREADY_EXISTS paths never reach step 2) |
| failure during creation | `trap on_exit EXIT` with a `COMPLETED` flag: no `RECOVERY_POINT_OK`, `RECOVERY_POINT_FAILED rc=… (marked INVALID, not deleted, not reused)`, `INVALID_DO_NOT_USE.txt` written into DEST; a later run into that DEST is refused (`DEST_ALREADY_EXISTS`); nothing is ever deleted |
| capacity rule and restore-instructions mode | unchanged (`BLOCKED_BACKUP_CAPACITY` exit 3; `restore-instructions <point>`; 21/21 structural checks still pass) |
| testability without real backups | `RP_SIMULATE=1` replaces docker/sudo work with small artefacts from `RP_SIM_SRC`; `RP_SIMULATE_DELAY` and `RP_FAIL_AT=<dump|filestore|addons|verify>` are test hooks; `RP_LOCK` and `DEST` are parameterised. Production behaviour is unchanged when the hooks are unset. |

## Tests (`scripts/test_recovery_point_concurrency.py`, temporary directories only)

```
PASS successful unique destination
PASS destination already exists is refused
PASS no overwrite of a valid recovery point
PASS two concurrent invocations: exactly one succeeds
PASS concurrent loser wrote nothing and winner verifies
PASS concurrent different destinations: loser is BUSY and creates nothing
PASS failure before completion is marked INVALID without RECOVERY_POINT_OK
PASS failed run does not delete or touch the valid point
PASS failed destination is not reused
PASS no mixed checksums across points
PASS failure at verification is marked INVALID
11/11 checks passed
```
Log: `evidence/concurrency/recovery_point_concurrency_tests.txt`.

## Real run with the corrected script

`/opt/odoo/backups/sipanel-pre-2ccloseouthard-20260923T051626Z` was created through the new lock/reservation path (`== 0. lock + reservation` in `evidence/logs/recovery_point_closeout_hardening.log`), completed with `RECOVERY_POINT_OK`, and verifies (`sha256sum -c` OK ×6, TIMESTAMP 20260923T052249Z, no INVALID marker; `evidence/logs/recovery_point_verification.txt`). The lock file `/run/lock/sipanel_recovery_point.lock` exists and holds the last writer's pid.
