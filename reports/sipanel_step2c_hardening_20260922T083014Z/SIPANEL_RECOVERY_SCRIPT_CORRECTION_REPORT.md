# SIPANEL Recovery Script Correction Report (run 20260922T083014Z)

Finding 3: `scripts/sipanel_recovery_point.sh` still ended with the ambiguous
one-line restore (`CREATE DATABASE sipanel_restore` … `tar -C /opt/odoo/data/filestore -xzf …`),
whose filestore step extracts the archived `sipanel/` tree straight onto the
live production filestore. The STEP 2C addendum documented a safe procedure,
but the script itself kept printing the unsafe one.

## What changed in the script

* The unsafe `echo "Restore: …"` line is removed.
* A `print_restore_instructions <point>` function prints the safe rehearsal
  procedure, and the script calls it after `RECOVERY_POINT_OK` with the point
  it just created.
* A new non-destructive mode prints the procedure for any existing point
  without creating a backup:
  `scripts/sipanel_recovery_point.sh restore-instructions <point-dir>`
  (the point directory is resolved with `realpath -e` and must exist).
* The backup logic itself (capacity rule, dump, archives, checksums,
  permissions) is unchanged.

## Properties of the printed procedure

| Requirement | How the printed procedure satisfies it |
|---|---|
| unique rehearsal database | `RDB="sipanel_restore_rehearsal_${TS}"`, refused if equal to `sipanel`; pre-checked for existence |
| dump restored only into that database | `pg_restore -U odoo -d "${RDB}"` — the live database name never appears as a restore target |
| archive layout inspected before extraction | `tar -tzf … \| awk -F/ '{print $1}' \| sort -u` printed before any extraction |
| extraction into a temporary directory | `TMP=$(sudo mktemp -d …)`; `tar -C "$TMP" -xzf …`; layout asserted (`test -d "$TMP/sipanel"`) |
| installed only under the rehearsal filestore name | `sudo mv "$TMP/sipanel" "$RFS"` with `RFS=/opt/odoo/data/filestore/${RDB}`, refused if the target exists |
| never onto the live filestore | the string `tar -C /opt/odoo/data/filestore -xzf` no longer occurs; `RFS` is refused when equal to the live path |
| owner and permissions | owner copied from the live filestore (`stat -c '%u:%g'`), `chmod -R u+rwX,go-rwx` |
| integrations neutralised before any Odoo process | mail servers and crons deactivated, `report.url`/`web.base.url` pointed at loopback, freeze parameter removed — all before the optional throw-away process step |
| cleanup commands for DB and filestore | `DROP DATABASE "${RDB}"` and `rm -rf --one-file-system -- "/opt/odoo/data/filestore/${RDB}"`, both marked `DESTRUCTIVE` |
| destructive targets validated | `[ "$RDB" != "sipanel" ]`, `[ -n "$TS" ]`, and `realpath -e "$RFS"` compared to the literal rehearsal path before `rm` |
| no globs / no unresolved destructive variables | no `*` in any destructive command; the `rm` target is the literal `/opt/odoo/data/filestore/${RDB}` derived from the validated `RDB` |

## Structural test of the generated output (non-destructive)

`scripts/sipanel_recovery_point.sh restore-instructions /opt/odoo/backups/sipanel-pre-2chardening-20260922T083014Z`
was executed (exit 0, nothing created, nothing restored); the output is in
`evidence/logs/restore_instructions_output.txt` and was checked by
`evidence/logs/restore_instructions_structural_checks.txt`:

```
PASS unique rehearsal db name
PASS rehearsal filestore path
PASS archive layout inspected before extraction
PASS extraction into temporary dir
PASS never extracts onto live filestore
PASS live db never a restore target
PASS integrations neutralised before any odoo process
PASS cleanup commands present and marked destructive
PASS destructive targets validated
PASS no broad glob in destructive commands
PASS no unresolved destructive variable (rm target is the literal rehearsal path)
PASS old ambiguous one-liner gone from script
```

`bash -n` syntax check: OK. The full script (backup mode) was also executed
in this run to create `/opt/odoo/backups/sipanel-pre-2chardening-20260922T083014Z`
**before** the script edit (the edit happened after the recovery point; the
printed instructions of that earlier execution are the old ones and are
recorded in `evidence/logs/recovery_point_2ch.log`). No restore was executed.
