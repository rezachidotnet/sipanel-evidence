# STEP 2C-HARDENING cleanup + finding 7 investigation (supported Odoo behaviour only, no SQL).
import json
TS = '20260922T083014Z'
P = f'SIPANEL-STEP2CH-{TS}'
P2C = 'SIPANEL-STEP2C-20260922T065650Z'
env = env(user=2, context={'lang': 'en_US', 'allowed_company_ids': [1]})
assert env.cr.dbname == 'sipanel'
out = {'prefix': P, 'deleted': {}, 'archived': {}, 'retained': {}, 'refused': {}, 'finding7': {}}
orders = env['sale.order'].search([('client_order_ref', 'like', f'{P}-')], order='id')
names = orders.mapped('name')
assert not env['account.move'].search([('invoice_origin', 'in', names)]) and not env['stock.move'].search([('origin', 'in', names), ('state', '=', 'done')])
exec_user = env['res.users'].with_context(active_test=False).search([('login', '=', f'{P2C}-exec')])
sales = env['res.users'].with_context(active_test=False).search([('login', '=', f'{P}-sales')])
for o in orders:
    if o.state != 'cancel':
        ox = o.with_user(exec_user)
        if ox.locked: ox.action_unlock()
        ox.action_cancel()
out['orders'] = [(o.id, o.name, o.state) for o in orders]
pickings = env['stock.picking'].search([('origin', 'in', names)])
assert all(p.state in ('draft', 'cancel') for p in pickings)
out['deleted']['stock.picking'] = [(p.id, p.picking_type_id.name, p.state) for p in pickings]; out['deleted']['stock.move'] = pickings.mapped('move_ids').ids
pickings.unlink()
tasks = env['project.task'].sudo().with_context(active_test=False).search(['|', ('sale_line_id', 'in', orders.mapped('order_line').ids), '&', ('create_date', '>=', '2026-09-22 08:30:00'), ('name', 'like', P)])
assert not tasks.mapped('timesheet_ids')
out['deleted']['project.task'] = [(t.id, t.name[:50]) for t in tasks]; tasks.unlink()
assert not env['purchase.order'].search([('origin', 'in', names)]) and not env['mrp.production'].search([('origin', 'in', names)])
scopes = env['sipanel.quote.scope'].with_context(active_test=False).search([('order_id', 'in', orders.ids)])
revs = scopes.mapped('revision_ids')
batches = env['sipanel.execution.batch'].search([('order_id', 'in', orders.ids)]); demands = env['sipanel.execution.demand'].search([('order_id', 'in', orders.ids)])
out['retained'] = {'sale.order (cancelled)': [(o.id, o.name) for o in orders], 'quote scopes (archived)': scopes.ids, 'revisions': [(r.id, r.state) for r in revs],
                   'artifacts': revs.mapped('artifact_ids').ids, 'generated lines': env['sale.order.line'].search([('order_id', 'in', orders.ids), ('sipanel_is_generated', '=', True)]).ids,
                   'batches': [(b.id, b.state) for b in batches], 'demands': {'count': len(demands), 'states': {s: len(demands.filtered(lambda d: d.state == s)) for s in set(demands.mapped('state'))}},
                   'targets': env['sipanel.execution.target'].search_count([('demand_id', 'in', demands.ids)]),
                   'audit events (this pilot)': env['sipanel.scope.audit.event'].sudo().search_count([('create_date', '>=', '2026-09-22 08:30:00')])}
scopes.write({'active': False}); out['archived']['quote scopes'] = scopes.ids
master = env['sipanel.scope'].with_context(active_test=False).search([('code', 'like', P)]); master.write({'active': False}); out['archived']['masters'] = master.ids
out['retained']['master versions (released, no archive flag)'] = env['sipanel.scope.version'].with_context(active_test=False).search([('scope_id', 'in', master.ids)]).ids
for model in ('product.product', 'product.template', 'project.project'):
    recs = env[model].with_context(active_test=False).search([('name', 'like', P)]); recs.write({'active': False}); out['archived'][model] = recs.ids
accounts = env['account.analytic.account'].sudo().with_context(active_test=False).search([('name', 'like', P)]); accounts.write({'active': False}); out['archived']['analytic accounts'] = accounts.ids
customer = env['res.partner'].with_context(active_test=False).search([('name', '=', f'{P} Synthetic Customer')]); customer.write({'active': False}); out['archived']['customer partner'] = customer.ids

# ---- finding 7: synthetic users and their contacts, supported lifecycle only
def contact_facts(user):
    p = user.partner_id
    return {'user': (user.id, user.login, user.active, user.share), 'partner': (p.id, p.name, p.active), 'email': p.email or None, 'phone': p.phone or None,
            'portal_or_login': bool(user.active) or user.has_group('base.group_portal'), 'groups_count': len(user.group_ids),
            'referenced_by': {'audit actor rows': env['sipanel.scope.audit.event'].sudo().search_count([('actor_user_id', '=', user.id)]),
                              'batches released/requested': env['sipanel.execution.batch'].sudo().search_count(['|', ('released_by_id', '=', user.id), ('requested_by_id', '=', user.id)]),
                              'mail.message author': env['mail.message'].sudo().search_count([('author_id', '=', p.id)]),
                              'mail.followers': env['mail.followers'].sudo().search_count([('partner_id', '=', p.id)])}}
f7 = {}
for u in (exec_user, sales):
    u.write({'active': False})
    facts = contact_facts(u)
    # (a) supported archive of the contact after the user is archived
    try:
        with env.cr.savepoint():
            u.partner_id.write({'active': False})
        facts['partner_archive'] = 'archived'
    except Exception as e:  # noqa
        facts['partner_archive'] = f'refused by Odoo guard: {type(e).__name__}'
    # (b) could the USER be deleted safely? only if no lineage references it (batches / audit actor)
    facts['user_unlink_safe'] = facts['referenced_by']['audit actor rows'] == 0 and facts['referenced_by']['batches released/requested'] == 0
    if not facts['user_unlink_safe']:
        facts['user_unlink'] = 'NOT attempted: user is the actor of immutable audit rows / released batches (ondelete set-null would rewrite lineage)'
    else:
        try:
            with env.cr.savepoint():
                pid = u.partner_id.id; u.unlink(); facts['user_unlink'] = f'user deleted (partner {pid} left for lifecycle)'
        except Exception as e:  # noqa
            facts['user_unlink'] = f'refused: {type(e).__name__}: {str(e)[:120]}'
    # (c) unmistakable display name, only if the audit trail does not store names (it stores actor_user_id)
    if u.exists() and u.partner_id.active and not u.partner_id.name.startswith('[ARCHIVED SYNTHETIC USER]'):
        u.partner_id.write({'name': f'[ARCHIVED SYNTHETIC USER] {u.partner_id.name}'})
        facts['renamed'] = u.partner_id.name
    f7[u.login if u.exists() else 'deleted'] = facts
out['finding7'] = f7
out['active_synthetic_technical_contacts'] = env['res.partner'].search([('name', 'like', 'SIPANEL-STEP2C'), ('active', '=', True)]).mapped(lambda p: (p.id, p.name))
out['active_leftovers'] = {
    'sale.order not cancelled': env['sale.order'].search_count([('client_order_ref', 'like', P), ('state', '!=', 'cancel')]),
    'quote scopes': env['sipanel.quote.scope'].search_count([('order_id', 'in', orders.ids)]), 'masters': env['sipanel.scope'].search_count([('code', 'like', P)]),
    'products': env['product.product'].search_count([('name', 'like', P)]), 'projects': env['project.project'].search_count([('name', 'like', P)]),
    'tasks': env['project.task'].sudo().search_count([('name', 'like', P)]), 'analytic accounts': env['account.analytic.account'].sudo().search_count([('name', 'like', P)]),
    'users active': env['res.users'].search_count([('login', 'like', 'SIPANEL-STEP2C')]), 'partners active (all STEP 2C prefixes)': len(out['active_synthetic_technical_contacts']),
    'pickings': env['stock.picking'].search_count([('origin', 'in', names)]), 'purchase orders': env['purchase.order'].search_count([('origin', 'in', names)]),
    'mrp': env['mrp.production'].search_count([('origin', 'in', names)]), 'invoices': env['account.move'].search_count([('invoice_origin', 'in', names)]),
    'live demands': env['sipanel.execution.demand'].search_count([('order_id', 'in', orders.ids), ('state', 'not in', ('cancelled', 'failed'))]),
    'live batches': env['sipanel.execution.batch'].search_count([('order_id', 'in', orders.ids), ('state', 'not in', ('cancelled', 'failed'))])}
out['side_effects'] = {'mail_mail': env['mail.mail'].sudo().search_count([]), 'posted_moves': env['account.move'].sudo().search_count([('state', '=', 'posted')]),
                       'done_stock_moves': env['stock.move'].sudo().search_count([('state', '=', 'done')]), 'purchase_orders_total': env['purchase.order'].sudo().search_count([]),
                       'mrp_total': env['mrp.production'].sudo().search_count([]), 'pickings_total': env['stock.picking'].sudo().search_count([]),
                       'internal_quant_qty': sum(env['stock.quant'].sudo().search([('location_id.usage', '=', 'internal')]).mapped('quantity')),
                       'sipanel_params': {p.key: p.value for p in env['ir.config_parameter'].sudo().search([('key', 'like', 'sipanel_scope.%')])}}
out['earlier_records_intact'] = {'SI-26/312': env['sale.order'].sudo().search_count([('id', '=', 312)]), 'version_115': env['sipanel.scope.version'].sudo().search_count([('id', '=', 115)]),
                                 'step2c batches 195-265 present': env['sipanel.execution.batch'].sudo().search_count([('id', 'in', [195, 196, 197, 198, 259, 260, 261, 262, 263, 264, 265])])}
env.cr.commit()
print('CLEANUP=' + json.dumps(out, ensure_ascii=False, default=str))
