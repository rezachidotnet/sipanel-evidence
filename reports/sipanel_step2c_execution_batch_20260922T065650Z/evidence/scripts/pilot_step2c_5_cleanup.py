# STEP 2C cleanup. Sealed revisions, artifacts, audit events, batches, demands and target links are immutable lineage
# and are retained. Draft/cancelled synthetic operational documents are removed; masters, products, partners, user,
# project and analytic accounts are archived (they are referenced by retained records).
import json
TS = '20260922T065650Z'
P = f'SIPANEL-STEP2C-{TS}'
env = env(user=2, context={'lang': 'en_US', 'allowed_company_ids': [1]})
assert env.cr.dbname == 'sipanel'
out = {'prefix': P, 'deleted': {}, 'archived': {}, 'retained': {}, 'refused': {}}
orders = env['sale.order'].search([('client_order_ref', 'like', f'{P}-')], order='id')
out['orders'] = [(o.id, o.name, o.client_order_ref[-3:], o.state) for o in orders]
scopes = env['sipanel.quote.scope'].with_context(active_test=False).search([('order_id', 'in', orders.ids)])
revs = scopes.mapped('revision_ids')
# 0. safety: nothing posted, nothing done
assert not env['account.move'].search([('invoice_origin', 'in', orders.mapped('name'))]), 'no invoice expected'
assert not env['stock.move'].search([('origin', 'in', orders.mapped('name')), ('state', '=', 'done')]), 'no done move expected'
# 1. cancel every synthetic order (execution owner path: releases planned demand, keeps lineage)
exec_user = env['res.users'].with_context(active_test=False).search([('login', '=', f'{P}-exec')])
cancel_log = {}
for o in orders:
    if o.state == 'cancel':
        cancel_log[o.name] = 'already cancelled'; continue
    ox = o.with_user(exec_user)
    if ox.locked:
        ox.action_unlock()
    ox.action_cancel()
    cancel_log[o.name] = o.state
env.cr.flush()
out['cancel'] = cancel_log
# 2. draft/cancelled synthetic operational documents
names = orders.mapped('name')
pickings = env['stock.picking'].search([('origin', 'in', names)])
assert all(p.state in ('draft', 'cancel') for p in pickings), pickings.mapped('state')
out['deleted']['stock.picking'] = [(p.id, p.picking_type_id.name, p.state) for p in pickings]
out['deleted']['stock.move'] = env['stock.move'].search([('origin', 'in', names)]).ids
pickings.mapped('move_ids').filtered(lambda m: m.state != 'cancel')._action_cancel()
pickings.unlink()
mos = env['mrp.production'].search([('origin', 'in', names)])
assert all(m.state in ('draft', 'cancel') for m in mos), mos.mapped('state')
out['deleted']['mrp.production'] = [(m.id, m.state) for m in mos]
mos.filtered(lambda m: m.state == 'draft').action_cancel()
mos.unlink()
pos = env['purchase.order'].search([('origin', 'in', names)])
assert all(p.state in ('draft', 'cancel') for p in pos), pos.mapped('state')
out['deleted']['purchase.order'] = [(p.id, p.name, p.state) for p in pos]
pos.filtered(lambda p: p.state != 'cancel').button_cancel()
pos.unlink()
tasks = env['project.task'].search([('sale_line_id', 'in', orders.mapped('order_line').ids)])
assert not tasks.mapped('timesheet_ids'), 'no timesheets expected'
out['deleted']['project.task'] = tasks.ids
tasks.unlink()
bom = env['mrp.bom'].search([('product_tmpl_id.name', 'like', P)])
out['deleted']['mrp.bom'] = bom.ids
bom.unlink()
sellers = env['product.supplierinfo'].search([('partner_id.name', 'like', P)])
out['deleted']['product.supplierinfo'] = sellers.ids
sellers.unlink()
env.cr.flush()
# 3. retained lineage (immutable by design)
out['retained']['sale.order (cancelled, referenced by batches ondelete=restrict)'] = [(o.id, o.name) for o in orders]
out['retained']['sipanel.quote.scope (archived)'] = scopes.ids
out['retained']['sipanel.quote.scope.revision'] = [(r.id, r.state) for r in revs]
out['retained']['sipanel.quote.scope.artifact'] = revs.mapped('artifact_ids').ids
out['retained']['generated sale.order.line'] = env['sale.order.line'].search([('order_id', 'in', orders.ids), ('sipanel_is_generated', '=', True)]).ids
batches = env['sipanel.execution.batch'].search([('order_id', 'in', orders.ids)])
demands = env['sipanel.execution.demand'].search([('order_id', 'in', orders.ids)])
out['retained']['sipanel.execution.batch'] = [(b.id, b.state) for b in batches]
out['retained']['sipanel.execution.demand'] = {'count': len(demands), 'states': {s: len(demands.filtered(lambda d: d.state == s)) for s in set(demands.mapped('state'))}}
out['retained']['sipanel.execution.target'] = env['sipanel.execution.target'].search_count([('demand_id', 'in', demands.ids)])
out['retained']['stock.reference'] = env['stock.reference'].search([('name', 'like', 'SIPANEL/SI-26/')]).filtered(lambda r: any(n in r.name for n in names)).mapped('name')
out['retained']['sipanel.scope.audit.event (this pilot)'] = env['sipanel.scope.audit.event'].sudo().search_count([('create_date', '>=', '2026-09-22 07:08:00')])
scopes.write({'active': False})
out['archived']['sipanel.quote.scope'] = scopes.ids
# 4. masters, products, partners, user, project, analytic accounts: archive (referenced by retained lineage)
master = env['sipanel.scope'].with_context(active_test=False).search([('code', 'like', P)])
versions = env['sipanel.scope.version'].with_context(active_test=False).search([('scope_id', 'in', master.ids)])
master.write({'active': False}); out['archived']['sipanel.scope'] = master.ids; out['archived']['sipanel.scope.version'] = versions.ids
products = env['product.product'].with_context(active_test=False).search([('name', 'like', P)])
products.write({'active': False}); out['archived']['product.product'] = products.ids
tmpls = env['product.template'].with_context(active_test=False).search([('name', 'like', P)])
tmpls.write({'active': False}); out['archived']['product.template'] = tmpls.ids
if exec_user:
    exec_user.write({'active': False}); out['archived']['res.users'] = exec_user.ids   # before its partner: Odoo refuses to archive the contact of an active user
env.cr.flush(); env.invalidate_all()
partners = env['res.partner'].with_context(active_test=False).search([('name', 'like', P)])
user_partner = exec_user.partner_id
(partners - user_partner).write({'active': False}); out['archived']['res.partner'] = (partners - user_partner).ids
try:
    with env.cr.savepoint():
        user_partner.write({'active': False}); out['archived']['res.partner'] += user_partner.ids
except Exception as exc:  # noqa - the contact of the archived synthetic user: Odoo's guard still sees the user
    out['refused']['res.partner (user contact)'] = [user_partner.ids, str(exc)[:160]]
project = env['project.project'].with_context(active_test=False).search([('name', 'like', P)])
project.write({'active': False}); out['archived']['project.project'] = project.ids
accounts = env['account.analytic.account'].sudo().with_context(active_test=False).search([('name', 'like', P)])
accounts.write({'active': False}); out['archived']['account.analytic.account'] = accounts.ids
env.cr.flush()
# 5. nothing synthetic visible to an operator
out['active_leftovers'] = {
    'sale.order (not cancelled)': env['sale.order'].search_count([('client_order_ref', 'like', P), ('state', '!=', 'cancel')]),
    'sipanel.quote.scope': env['sipanel.quote.scope'].search_count([('order_id', 'in', orders.ids)]),
    'sipanel.scope': env['sipanel.scope'].search_count([('code', 'like', P)]),
    'sipanel.scope.version': env['sipanel.scope.version'].search_count([('scope_id.code', 'like', P)]),
    'product.product': env['product.product'].search_count([('name', 'like', P)]),
    'res.partner': env['res.partner'].search_count([('name', 'like', P)]),
    'res.users': env['res.users'].search_count([('login', 'like', P)]),
    'project.project': env['project.project'].search_count([('name', 'like', P)]),
    'project.task': env['project.task'].search_count([('project_id.name', 'like', P)]),
    'account.analytic.account': env['account.analytic.account'].sudo().search_count([('name', 'like', P)]),
    'stock.picking': env['stock.picking'].search_count([('origin', 'in', names)]),
    'purchase.order': env['purchase.order'].search_count([('origin', 'in', names)]),
    'mrp.production': env['mrp.production'].search_count([('origin', 'in', names)]),
    'mrp.bom': env['mrp.bom'].search_count([('product_tmpl_id.name', 'like', P)]),
    'account.move': env['account.move'].search_count([('invoice_origin', 'in', names)]),
    'sipanel.execution.demand (not cancelled/failed)': env['sipanel.execution.demand'].search_count([('order_id', 'in', orders.ids), ('state', 'not in', ('cancelled', 'failed'))]),
    'sipanel.execution.batch (not cancelled/failed)': env['sipanel.execution.batch'].search_count([('order_id', 'in', orders.ids), ('state', 'not in', ('cancelled', 'failed'))]),
}
out['side_effects'] = {
    'mail_mail_total': env['mail.mail'].sudo().search_count([]),
    'posted_account_moves': env['account.move'].sudo().search_count([('state', '=', 'posted')]),
    'done_stock_moves_total': env['stock.move'].sudo().search_count([('state', '=', 'done')]),
    'internal_quant_qty': sum(env['stock.quant'].sudo().search([('location_id.usage', '=', 'internal')]).mapped('quantity')),
    'purchase_orders_total': env['purchase.order'].sudo().search_count([]),
    'mrp_total': env['mrp.production'].sudo().search_count([]),
    'pickings_total': env['stock.picking'].sudo().search_count([]),
    'tasks_total': env['project.task'].sudo().search_count([]),
    'report_url': env['ir.config_parameter'].sudo().get_param('report.url'),
    'sipanel_params': {p.key: p.value for p in env['ir.config_parameter'].sudo().search([('key', 'like', 'sipanel_scope.%')])},
    'owner_rules': env['sipanel.execution.owner.rule'].search_count([]),
}
out['earlier_audit_records_intact'] = {
    'SI-26/312': env['sale.order'].sudo().search_count([('id', '=', 312)]),
    'version_115': env['sipanel.scope.version'].sudo().with_context(active_test=False).search_count([('id', '=', 115)]),
    'sepbill pilot revisions 886/887': env['sipanel.quote.scope.revision'].sudo().search_count([('id', 'in', (886, 887))]),
}
env.cr.commit()
print('CLEANUP=' + json.dumps(out, ensure_ascii=False, default=str))
