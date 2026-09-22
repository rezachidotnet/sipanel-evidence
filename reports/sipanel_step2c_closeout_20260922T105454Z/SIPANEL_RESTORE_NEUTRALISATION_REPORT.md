# SIPANEL Restore Neutralisation Report (run 20260922T105454Z)

Finding: the rehearsal procedure printed by `scripts/sipanel_recovery_point.sh` neutralised only
`ir_mail_server`, `ir_cron`, `report.url` and `web.base.url`; fetchmail and payment providers were
mentioned in a comment but not implemented.

## Live inventory of optional integration tables in `sipanel` (`evidence/logs/integration_tables_live.txt`)

| Table | Present | Live state (not modified) |
|---|---|---|
| `ir_mail_server` | yes | 1 active |
| `ir_cron` | yes | 34 active |
| `fetchmail_server` | yes | 1 server |
| `payment_provider` | yes | **1 enabled** |
| `payment_acquirer` | no (Odoo 19) | — |
| `base_automation` | no (module not installed) | — |
| `ir_act_server` (`state`, `webhook_url` columns present) | yes | 0 webhook actions |
| `iap_account` | yes | 4 accounts |
| `mail_alias` | yes | present |

## What the printed procedure now does (step 5, before any Odoo process)

One `psql -v ON_ERROR_STOP=1` session against `"${RDB}"` only, inside `BEGIN … COMMIT`, with a
`DO $$ … $$` block that tests every optional table with `to_regclass()` (and the optional columns
with `information_schema.columns`) before touching it, so an absent module never fails the block:

* outgoing mail servers and all crons deactivated; `report.url` → loopback, `web.base.url` → localhost, freeze parameter removed;
* `fetchmail_server` deactivated when installed;
* `payment_provider` / `payment_acquirer` set to `disabled` when installed;
* `base_automation` deactivated when installed; outgoing webhook server actions (`ir_act_server.state = 'webhook'`) lose their `webhook_url`;
* IAP account tokens nulled (no paid outgoing call: SMS, partner autocomplete, OCR …);
* incoming mail aliases blanked;
* followed by a read-only verification query (`mail_servers_active`, `crons_active`).

The live database is never named as a target (the only `psql -d sipanel` would be in the
recovery *backup* mode, not in the printed restore procedure; the structural check
`neutralisation targets the rehearsal database only` asserts the absence of `-d sipanel` in the
printed text). Cleanup targets remain the validated rehearsal database and the literal rehearsal
filestore path; no glob.

## Structural tests

`scripts/test_restore_instructions.py` (committed) runs the script's non-destructive
`restore-instructions <point>` mode and checks 21 properties; result for the point
`sipanel-pre-2chardening-20260922T083014Z`: **21/21 PASS**
(`evidence/logs/restore_instructions_structural_checks.txt`, output in
`evidence/logs/restore_instructions_output.txt`). `bash -n` syntax check OK. The backup mode of the
script was executed in this run to create the verified closeout recovery point.

No restore rehearsal was executed (it would consume ~1 GB of a filesystem that only just passes the
capacity rule and is not required by this step).
