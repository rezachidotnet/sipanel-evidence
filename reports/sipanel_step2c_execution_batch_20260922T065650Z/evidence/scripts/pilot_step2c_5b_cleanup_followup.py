# STEP 2C cleanup follow-up: the synthetic user's contact (guard quirk in the same transaction), master versions, stray tasks.
import json
TS = '20260922T065650Z'
P = f'SIPANEL-STEP2C-{TS}'
env = env(user=2, context={'lang': 'en_US', 'allowed_company_ids': [1]})
assert env.cr.dbname == 'sipanel'
out = {}
user = env['res.users'].with_context(active_test=False).search([('login', '=', f'{P}-exec')])
out['user'] = (user.id, user.active)
partner = user.partner_id
try:
    with env.cr.savepoint():
        partner.write({'active': False})
    out['user_partner_archived'] = (partner.id, partner.active)
except Exception as exc:  # noqa - Odoo's guard refuses even for the archived user: retained, reported
    out['user_partner_refused'] = (partner.id, str(exc)[:120])
Version = env['sipanel.scope.version']
versions = Version.with_context(active_test=False).search([('scope_id.code', 'like', P)])
out['version_has_active_field'] = 'active' in Version._fields
if 'active' in Version._fields:
    versions.write({'active': False})
out['versions'] = [(v.id, v.state, getattr(v, 'active', None)) for v in versions]
tasks = env['project.task'].with_context(active_test=False).search([('create_date', '>=', '2026-09-22 07:08:00')])
out['tasks_created_during_pilot'] = [(t.id, t.name[:60], t.project_id.id, t.sale_line_id.id or None, t.active, t.create_date) for t in tasks]
synthetic_tasks = tasks.filtered(lambda t: t.project_id.id == 97 or P in (t.name or ''))
assert not synthetic_tasks.mapped('timesheet_ids')
out['deleted_tasks'] = synthetic_tasks.ids
synthetic_tasks.unlink()
out['active_leftovers'] = {
    'res.partner': env['res.partner'].search_count([('name', 'like', P)]),
    'sipanel.scope.version': Version.search_count([('scope_id.code', 'like', P)]),
    'project.task (project 97)': env['project.task'].search_count([('project_id', '=', 97)]),
    'project.task total': env['project.task'].search_count([]),
}
env.cr.commit()
print('CLEANUP2=' + json.dumps(out, ensure_ascii=False, default=str))
