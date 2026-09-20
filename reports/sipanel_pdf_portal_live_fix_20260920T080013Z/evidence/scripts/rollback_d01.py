# emergency rollback of report.url to the recorded previous value (single-worker deadlock observed)
import json
assert env.cr.dbname == 'sipanel'
ICP = env['ir.config_parameter'].sudo()
cur = ICP.get_param('report.url')
ICP.set_param('report.url', 'http://odoo:8069\n')
env.cr.commit()
print('ROLLBACK_JSON=' + json.dumps({'was': repr(cur), 'now': repr(ICP.get_param('report.url'))}))
