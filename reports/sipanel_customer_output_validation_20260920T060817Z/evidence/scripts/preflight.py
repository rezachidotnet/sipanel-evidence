# read-only preflight (no commit)
import json
out = {}
out['db'] = env.cr.dbname
out['modules'] = {m.name: (m.state, m.latest_version) for m in env['ir.module.module'].sudo().search([('name', 'like', 'sipanel%')])}
U = env['res.users'].sudo().with_context(active_test=False)
u = U.search([('login', '=', 'amirmousa1983@gmail.com')])
out['user'] = [{'id': x.id, 'login': x.login, 'name': x.name, 'active': x.active, 'share': x.share, 'company': x.company_id.name,
                'sipanel_groups': sorted(g.get_external_id().get(g.id, '') for g in x.group_ids if 'sipanel' in (g.get_external_id().get(g.id, '') or '')),
                'other_key_groups': sorted(g.get_external_id().get(g.id, '') for g in x.group_ids if any(k in (g.get_external_id().get(g.id, '') or '') for k in ('sales_team.', 'account.', 'base.group_system', 'base.group_user', 'base.group_erp_manager')))}
               for x in u]
dups = U.search(['|', '|', ('name', 'ilike', 'taleghani'), ('name', 'ilike', 'طالقانی'), ('login', 'ilike', 'reza')])
out['name_matches'] = [{'id': x.id, 'login': x.login, 'name': x.name, 'active': x.active} for x in dups]
P = env['res.partner'].sudo().with_context(active_test=False)
out['partner_matches'] = [{'id': p.id, 'name': p.name, 'active': p.active, 'is_user': bool(p.user_ids)} for p in P.search(['|', ('name', 'ilike', 'taleghani'), ('name', 'ilike', 'طالقانی')])]
out['company'] = {'id': env.company.id, 'name': env.company.name, 'currency': env.company.currency_id.name}
out['users_count_internal'] = U.search_count([('share', '=', False), ('active', '=', True)])
print('PREFLIGHT_JSON=' + json.dumps(out, ensure_ascii=False, default=str))
