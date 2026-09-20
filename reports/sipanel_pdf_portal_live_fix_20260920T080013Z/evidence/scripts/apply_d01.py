# STEP 1B Action A — D-01: report.url on database sipanel only (management-authorized 2026-09-20). Explicit commit.
import json
assert env.cr.dbname == 'sipanel'
ICP = env['ir.config_parameter'].sudo()
rec = ICP.search([('key', '=', 'report.url')])
before = rec.value
ICP.set_param('report.url', 'http://127.0.0.1:8069')
env.cr.commit()
rec.invalidate_recordset()
after = ICP.get_param('report.url')
print('D01_JSON=' + json.dumps({'db': env.cr.dbname, 'record_id': rec.id, 'before_repr': repr(before), 'after_repr': repr(after),
                                'write_date': str(rec.write_date), 'write_uid': rec.write_uid.id, 'committed': True}))
