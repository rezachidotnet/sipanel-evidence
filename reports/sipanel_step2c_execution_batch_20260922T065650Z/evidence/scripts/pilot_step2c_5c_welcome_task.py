# STEP 2C cleanup: the onboarding "Welcome" task Odoo created for the synthetic execution-owner user.
import json
env = env(user=2, context={'allowed_company_ids': [1]})
assert env.cr.dbname == 'sipanel'
t = env['project.task'].sudo().with_context(active_test=False).browse(2437)
out = {'task': (t.id, t.name, t.project_id.id or None, t.user_ids.mapped('login'), t.create_date)}
assert 'SIPANEL-STEP2C-' in (t.name or '') and not t.timesheet_ids
t.unlink()
out['remaining_tasks_since_0700'] = env['project.task'].sudo().with_context(active_test=False).search_count([('create_date', '>=', '2026-09-22 07:00:00')])
env.cr.commit()
print('WELCOME=' + json.dumps(out, default=str))
