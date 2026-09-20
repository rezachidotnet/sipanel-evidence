# STEP 1C cleanup: delete the fresh draft quotation, its working scopes and the synthetic partner. Commits at end.
import json
env = env(user=2, context={'lang': 'en_US', 'allowed_company_ids': [1]})
out = {'deleted': {}, 'archived': {}, 'retained': {}}
o = env['sale.order'].browse(368)
assert o.state == 'draft' and o.client_order_ref.startswith('SIPANEL-PDF-LAYOUT-CHECK-')
scopes = env['sipanel.quote.scope'].search([('order_id', '=', o.id)])
revs = scopes.mapped('revision_ids'); comps = revs.mapped('component_ids')
assert all(r.state == 'working' for r in revs) and not revs.mapped('artifact_ids')
lines = scopes.mapped('anchor_line_id')
n = {'scopes': len(scopes), 'revisions': len(revs), 'components': len(comps), 'order_lines': len(o.order_line)}
scopes.write({'current_revision_id': False}); env.cr.flush()   # D-04 workaround
comps.sudo().unlink(); env.cr.flush()
revs.unlink(); env.cr.flush()
scopes.unlink(); env.cr.flush()
lines.unlink(); env.cr.flush()
name = o.name; o.unlink(); env.cr.flush()
out['deleted']['order'] = name; out['deleted'].update(n)
partner = env['res.partner'].browse(509)
try:
    partner.unlink(); env.cr.flush(); out['deleted']['partner'] = 509
except Exception as e:
    partner.write({'active': False}); out['archived']['partner'] = (509, str(e)[:120])
P = 'SIPANEL-PDF-LAYOUT-CHECK-20260920T084541Z'
inv = {}
for model, dom in [('sale.order', [('client_order_ref', 'like', P)]), ('sipanel.quote.scope', [('order_id.client_order_ref', 'like', P)]),
                   ('res.partner', [('name', 'like', P)]), ('sipanel.quote.scope.artifact', [('order_id.client_order_ref', 'like', P)]),
                   ('mail.message', [('model', '=', 'sale.order'), ('res_id', '=', 368)]), ('sipanel.scope.audit.event', [('res_model', '=', 'sale.order'), ('res_id', '=', 368)]),
                   ('sipanel.scope.audit.event', [('res_model', '=', 'sipanel.quote.scope'), ('res_id', 'in', scopes.ids)])]:
    M = env[model].sudo().with_context(active_test=False); inv.setdefault(model, []).append(M.search_count(dom))
out['retained_inventory'] = inv
out['side_effects'] = {
    'mail_mail_since_0845': env['mail.mail'].sudo().search_count([('create_date', '>=', '2026-09-20 08:45:00')]),
    'stock_picking': env['stock.picking'].sudo().search_count([('origin', 'ilike', 'SI-26/368')]),
    'mrp_production': env['mrp.production'].sudo().search_count([('origin', 'ilike', 'SI-26/368')]),
    'purchase_order': env['purchase.order'].sudo().search_count([('origin', 'ilike', 'SI-26/368')]),
    'account_move': env['account.move'].sudo().search_count([('invoice_origin', 'ilike', 'SI-26/368')]),
    'project_task': env['project.task'].sudo().search_count([('sale_order_id', '=', 368)]),
    'execution_demand': env['sipanel.execution.demand'].sudo().search_count([('order_id', '=', 368)]),
    'execution_batch': env['sipanel.execution.batch'].sudo().search_count([('order_id', '=', 368)]),
    'new_users_since_0845': env['res.users'].sudo().search_count([('create_date', '>=', '2026-09-20 08:45:00')]),
    'version_115_state': env['sipanel.scope.version'].browse(115).state, 'scope_95_active': env['sipanel.scope'].with_context(active_test=False).browse(95).active,
    'report_url': env['ir.config_parameter'].sudo().get_param('report.url'), 'website_langs': env['website'].sudo().browse(1).language_ids.mapped('code'),
}
env.cr.commit()
print('CLEANUP_1C=' + json.dumps(out, ensure_ascii=False, default=str))
