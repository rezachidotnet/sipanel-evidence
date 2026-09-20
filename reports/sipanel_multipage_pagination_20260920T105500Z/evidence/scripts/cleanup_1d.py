# STEP 1D cleanup: remove every synthetic record created for the L-02 validation.
# The rendered PDFs/PNGs in the report directory are the retained audit evidence,
# so nothing needs to stay in the database. Commits at the end.
import json
TS = '20260920T105500Z'
P = f'SIPANEL-PAGINATION-CHECK-{TS}'
env = env(user=2, context={'lang': 'en_US', 'allowed_company_ids': [1]})
assert env.cr.dbname == 'sipanel'
ids = json.load(open('/tmp/sipanel_1d/ids.json'))
docs = dict(ids['docs']); docs.update(ids['docs_E'])
out = {'prefix': P, 'deleted': {}, 'archived': {}, 'errors': {}}

orders = env['sale.order'].browse(sorted(int(v) for v in docs.values()))
for o in orders:
    assert o.state == 'draft', (o.name, o.state)
    assert (o.client_order_ref or '').startswith(P), o.client_order_ref

scopes = env['sipanel.quote.scope'].search([('order_id', 'in', orders.ids)])
revs = scopes.mapped('revision_ids')
comps = revs.mapped('component_ids')
assert all(r.state == 'working' for r in revs), 'a revision is sealed; not a throwaway fixture'
assert not revs.mapped('artifact_ids'), 'artifacts exist; refusing to delete'
counts = {'orders': len(orders), 'order_lines': sum(len(o.order_line) for o in orders),
          'scopes': len(scopes), 'revisions': len(revs), 'components': len(comps)}
lines = scopes.mapped('anchor_line_id')

scopes.write({'current_revision_id': False}); env.cr.flush()   # D-04 workaround
comps.sudo().unlink(); env.cr.flush()
revs.unlink(); env.cr.flush()
scopes.unlink(); env.cr.flush()
lines.unlink(); env.cr.flush()
names = orders.mapped('name')
orders.unlink(); env.cr.flush()
out['deleted'] = dict(counts, order_names=names)

partner = env['res.partner'].browse(int(ids['partner']))
try:
    partner.unlink(); env.cr.flush(); out['deleted']['partner'] = ids['partner']
except Exception as exc:                                   # noqa: BLE001
    partner.write({'active': False}); env.cr.flush()
    out['archived']['partner'] = [ids['partner'], str(exc)[:160]]

leftovers = {}
for model, dom in [
    ('sale.order', [('client_order_ref', 'like', P)]),
    ('sale.order.line', [('order_id.client_order_ref', 'like', P)]),
    ('sipanel.quote.scope', [('order_id.client_order_ref', 'like', P)]),
    ('sipanel.quote.scope.revision', [('quote_scope_id.order_id.client_order_ref', 'like', P)]),
    ('sipanel.quote.scope.artifact', [('order_id.client_order_ref', 'like', P)]),
    ('res.partner', [('name', 'like', P)]),
]:
    leftovers[model] = env[model].sudo().with_context(active_test=False).search_count(dom)
out['leftovers'] = leftovers

since = '2026-09-20 10:49:00'
out['side_effects'] = {
    'mail_mail_since_run': env['mail.mail'].sudo().search_count([('create_date', '>=', since)]),
    'stock_picking': env['stock.picking'].sudo().search_count([('origin', 'in', names)]),
    'mrp_production': env['mrp.production'].sudo().search_count([('origin', 'in', names)]),
    'purchase_order': env['purchase.order'].sudo().search_count([('origin', 'in', names)]),
    'account_move': env['account.move'].sudo().search_count([('invoice_origin', 'in', names)]),
    'project_task': env['project.task'].sudo().search_count([('sale_order_id', 'in', orders.ids)]),
    'execution_demand': env['sipanel.execution.demand'].sudo().search_count([('order_id', 'in', orders.ids)]),
    'execution_batch': env['sipanel.execution.batch'].sudo().search_count([('order_id', 'in', orders.ids)]),
    'new_users_since_run': env['res.users'].sudo().search_count([('create_date', '>=', since)]),
}
out['unchanged_config'] = {
    'report_url': env['ir.config_parameter'].sudo().get_param('report.url'),
    'website_langs': env['website'].sudo().browse(1).language_ids.mapped('code'),
    'paperformat': env.ref('sale.action_report_saleorder').get_paperformat().display_name,
    'margin_top': env.ref('sale.action_report_saleorder').get_paperformat().margin_top,
    'margin_bottom': env.ref('sale.action_report_saleorder').get_paperformat().margin_bottom,
    'version_115_state': env['sipanel.scope.version'].browse(115).state,
    'retained_1C_order_312': env['sale.order'].sudo().with_context(active_test=False).search_count([('id', '=', 312)]),
}
env.cr.commit()
print('CLEANUP_1D=' + json.dumps(out, ensure_ascii=False, default=str))
