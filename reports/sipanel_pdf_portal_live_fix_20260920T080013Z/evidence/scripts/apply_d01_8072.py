# STEP 1B Action A (revised): report.url -> gevent loopback port 8072, because workers=1 makes port 8069 deadlock. Explicit commit.
import json
assert env.cr.dbname == 'sipanel'
ICP = env['ir.config_parameter'].sudo()
rec = ICP.search([('key', '=', 'report.url')])
before = rec.value
ICP.set_param('report.url', 'http://127.0.0.1:8072')
env.cr.commit()
rec.invalidate_recordset()
print('D01_JSON=' + json.dumps({'record_id': rec.id, 'before_repr': repr(before), 'after_repr': repr(ICP.get_param('report.url')), 'write_date': str(rec.write_date), 'committed': True}))
