import json
from odoo.exceptions import UserError
env = env(user=2, context={'lang': 'en_US', 'allowed_company_ids': [1]})
ids = json.load(open('/tmp/sipanel_val/ids.json'))
P = ids['prefix']; out = {'deleted': {}, 'archived': {}, 'retained': {}, 'errors': {}}
SO = env['sale.order']
# --- order B (draft, working scope only): delete scope, then the order (lines cascade)
ob = SO.browse(ids['order_b'])
sb = env['sipanel.quote.scope'].search([('order_id', '=', ob.id)])
sb_revs = sb.mapped('revision_ids'); sb_comps = sb_revs.mapped('component_ids')
assert all(r.state == 'working' for r in sb_revs)
n_comp, n_rev, n_scope = len(sb_comps), len(sb_revs), len(sb)
sb_line = sb.anchor_line_id
# D-04 workaround: plain scope.unlink() fails (MissingError/FK on current_revision_id); clear the pointer first
sb.write({'current_revision_id': False}); env.cr.flush()
sb_comps.sudo().unlink(); env.cr.flush()
sb_revs.unlink(); env.cr.flush()
sb.unlink(); env.cr.flush()
sb_line.unlink(); env.cr.flush()
out['deleted']['order_b_scope'] = {'scopes': n_scope, 'revisions': n_rev, 'components': n_comp}
assert ob.state == 'draft'
ob_name = ob.name; ob.unlink()
out['deleted']['order_b'] = ob_name
# --- order 312: cancel (sealed scopes cannot be deleted: audit evidence), then archive scopes
o = SO.browse(ids['order'])
o.with_context(disable_cancel_warning=True)._action_cancel()
out['order_312'] = {'name': o.name, 'state': o.state}
scopes = env['sipanel.quote.scope'].browse([ids['scope1'], ids['scope2']])
scopes.write({'active': False})
out['archived']['quote_scopes'] = scopes.ids
out['retained']['revisions_sealed'] = [(r.id, r.name, r.state) for r in scopes.mapped('revision_ids')]
out['retained']['artifacts_append_only'] = [(a.id, a.kind, a.attachment_id.id or None) for a in scopes.mapped('revision_ids.artifact_ids').sudo()]
out['retained']['audit_events'] = env['sipanel.scope.audit.event'].sudo().search_count(['|', ('res_id', 'in', scopes.ids + scopes.mapped('revision_ids').ids), ('res_model', '=', 'sale.order'), ('res_id', '=', o.id)])
# --- master data: version referenced by quotation -> archive scope master; products/partner/analytic referenced -> archive
sm = env['sipanel.scope'].browse(ids['scope']); sm.write({'active': False}); out['archived']['scope_master'] = sm.id
out['retained']['version'] = (ids['version'], env['sipanel.scope.version'].browse(ids['version']).state)
prods = env['product.product'].browse(ids['products'])
for p in prods:
    try:
        with env.cr.savepoint():
            p.unlink(); out['deleted'].setdefault('products', []).append(p.id)
    except Exception as e:
        p.write({'active': False}); p.product_tmpl_id.write({'active': False}); out['archived'].setdefault('products', []).append(p.id)
aa = env['account.analytic.account'].browse(ids['analytic_accounts'])
for a in aa:
    try:
        with env.cr.savepoint():
            a.unlink(); out['deleted'].setdefault('analytic', []).append(a.id)
    except Exception as e:
        a.write({'active': False}); out['archived'].setdefault('analytic', []).append(a.id)
partner = env['res.partner'].browse(ids['partner']); partner.write({'active': False}); out['archived']['partner'] = partner.id
# --- side-effect verification
mails = env['mail.mail'].sudo().search([('create_date', '>=', '2026-09-20 06:00:00')])
out['side_effects'] = {
    'mail_mail_since_06:00': [(m.id, m.model, m.res_id, m.state, (m.email_to or '')[:40]) for m in mails],
    'mail_messages_outgoing_for_312': env['mail.message'].sudo().search_count([('model', '=', 'sale.order'), ('res_id', '=', o.id), ('message_type', '=', 'email_outgoing')]),
    'stock_picking': env['stock.picking'].sudo().search_count([('origin', 'ilike', 'SI-26/312')]),
    'mrp_production': env['mrp.production'].sudo().search_count([('origin', 'ilike', 'SI-26/312')]),
    'account_move': env['account.move'].sudo().search_count([('invoice_origin', 'ilike', 'SI-26/312')]),
    'project_task': env['project.task'].sudo().search_count([('sale_order_id', '=', o.id)]),
    'execution_demand': env['sipanel.execution.demand'].sudo().search_count([('order_id', '=', o.id)]),
    'execution_batch': env['sipanel.execution.batch'].sudo().search_count([('order_id', '=', o.id)]),
    'purchase_order': env['purchase.order'].sudo().search_count([('origin', 'ilike', 'SI-26/312')]),
    'test_users_left': env['res.users'].sudo().with_context(active_test=False).search_count([('login', 'like', 'sipanel_pt_%')]),
    'test_scopes_left': env['sipanel.scope'].sudo().with_context(active_test=False).search_count([('code', 'like', 'SIPANEL-PT-GUTTER-%')]),
    'portal_users_for_partner': env['res.users'].sudo().with_context(active_test=False).search_count([('partner_id', '=', partner.id)]),
    'invoiceable_lines_312': env['sale.order.line'].sudo().search_count([('order_id', '=', o.id), ('qty_to_invoice', '>', 0)]),
}
# --- inventory of everything still carrying the prefix
inv = {}
for model, dom in [('sale.order', [('client_order_ref', 'like', P)]), ('sale.order.line', [('order_id.client_order_ref', 'like', P)]),
                   ('sipanel.quote.scope', [('order_id.client_order_ref', 'like', P)]), ('sipanel.quote.scope.revision', [('order_id.client_order_ref', 'like', P)]),
                   ('sipanel.quote.scope.component', [('revision_id.order_id.client_order_ref', 'like', P)]), ('sipanel.quote.scope.artifact', [('order_id.client_order_ref', 'like', P)]),
                   ('ir.attachment', [('res_model', '=', 'sipanel.quote.scope.artifact'), ('name', 'like', 'SI-26/312%')]),
                   ('sipanel.scope', [('code', '=', P)]), ('sipanel.scope.version', [('scope_id.code', '=', P)]), ('sipanel.scope.recipe.line', [('version_id.scope_id.code', '=', P)]),
                   ('product.product', [('name', 'like', P)]), ('product.template', [('name', 'like', P)]), ('res.partner', [('name', 'like', P)]),
                   ('account.analytic.account', [('name', 'like', P)]), ('sipanel.scope.audit.event', [('res_model', '=', 'sale.order'), ('res_id', '=', o.id)])]:
    M = env[model].sudo().with_context(active_test=False)
    recs = M.search(dom)
    inv[model] = {'count': len(recs), 'ids': recs.ids[:40], 'active': (recs.mapped('active') if 'active' in M._fields else None)}
out['retained_inventory'] = inv
env.cr.commit()
print('CLEANUP_JSON=' + json.dumps(out, ensure_ascii=False, default=str))
