# STEP 2B cleanup. Sealed revisions and their artifacts cannot be deleted by
# design - that immutability is exactly what this step tested - so whatever
# cannot be deleted is cancelled and archived, and listed explicitly.
import json
TS = '20260921T021500Z'
P = f'SIPANEL-SEPBILL-PILOT-{TS}'
env = env(user=2, context={'lang': 'en_US', 'allowed_company_ids': [1]})
assert env.cr.dbname == 'sipanel'
out = {'prefix': P, 'deleted': {}, 'archived': {}, 'retained': {}, 'side_effects': {}}

order = env['sale.order'].search([('client_order_ref', '=', P)])
scopes = env['sipanel.quote.scope'].search([('order_id', 'in', order.ids)])
revs = scopes.mapped('revision_ids')

# 1. the draft invoice: never posted, so it can simply go
invoices = env['account.move'].search([('invoice_origin', 'in', order.mapped('name'))])
out['invoice_states'] = invoices.mapped('state')
assert all(m.state == 'draft' for m in invoices), 'refusing to touch a posted invoice'
out['deleted']['invoices'] = len(invoices)
invoices.unlink()
env.cr.flush()

# 2. cancel the order (keeps the audit trail, releases downstream demand)
if order and order.state not in ('cancel', 'draft'):
    order._action_cancel()
env.cr.flush()
out['order_state_after_cancel'] = order.mapped('state')

# 3. sealed revisions cannot be deleted; archive the scopes instead
sealed = revs.filtered(lambda r: r.state != 'working')
out['retained']['sealed_revisions'] = sealed.ids
out['retained']['artifacts'] = revs.mapped('artifact_ids').ids
generated = env['sale.order.line'].search([('order_id', 'in', order.ids), ('sipanel_is_generated', '=', True)])
out['retained']['generated_lines'] = generated.ids
if sealed:
    scopes.write({'active': False})
    out['archived']['quote_scopes'] = scopes.ids
    out['archived']['order'] = order.ids
else:
    out['deleted']['order'] = order.mapped('name')

# 4. the pilot master: a released version can never be deleted, so archive it
master = env['sipanel.scope'].with_context(active_test=False).search([('code', 'like', P)])
versions = env['sipanel.scope.version'].with_context(active_test=False).search([('scope_id', 'in', master.ids)])
master.write({'active': False})
out['archived']['master_scope'] = master.ids
out['archived']['master_versions'] = versions.ids
products = env['product.product'].with_context(active_test=False).search([('name', 'like', P)])
products.write({'active': False})
out['archived']['products'] = products.ids
partners = env['res.partner'].with_context(active_test=False).search([('name', 'like', P)])
# The order is retained (its revisions are sealed and sealed content is never
# deleted), so the customer it points at is retained with it - archived, not
# deleted. A savepoint keeps a foreign-key refusal from poisoning the whole
# cleanup transaction.
if out.get('deleted', {}).get('order'):
    try:
        with env.cr.savepoint():
            pids = partners.ids
            partners.unlink()
            out['deleted']['partners'] = pids
    except Exception as exc:                      # noqa: BLE001
        partners.write({'active': False})
        out['archived']['partners'] = [partners.ids, str(exc)[:100]]
else:
    partners.write({'active': False})
    out['archived']['partners'] = partners.ids
env.cr.flush()

# 5. what is still visible to an operator (nothing should be)
out['active_leftovers'] = {
    'sale.order': env['sale.order'].search_count([('client_order_ref', '=', P)]),
    'sipanel.quote.scope': env['sipanel.quote.scope'].search_count([('order_id.client_order_ref', '=', P)]),
    'sipanel.scope': env['sipanel.scope'].search_count([('code', 'like', P)]),
    'product.product': env['product.product'].search_count([('name', 'like', P)]),
    'res.partner': env['res.partner'].search_count([('name', 'like', P)]),
    'account.move': env['account.move'].search_count([('invoice_origin', 'in', order.mapped('name'))]),
}
since = '2026-09-21 06:15:00'
out['side_effects'] = {
    'mail_mail': env['mail.mail'].sudo().search_count([('create_date', '>=', since)]),
    'stock_picking': env['stock.picking'].sudo().search_count([('origin', 'in', order.mapped('name'))]),
    'purchase_order': env['purchase.order'].sudo().search_count([('origin', 'in', order.mapped('name'))]),
    'mrp_production': env['mrp.production'].sudo().search_count([('origin', 'in', order.mapped('name'))]),
    'posted_moves': env['account.move'].sudo().search_count([('state', '=', 'posted'), ('create_date', '>=', since)]),
}
out['config'] = {
    'report.url': env['ir.config_parameter'].sudo().get_param('report.url'),
    'website_langs': env['website'].sudo().browse(1).language_ids.mapped('code'),
    'installed_langs': [l[0] for l in env['res.lang'].get_installed()],
}
out['earlier_audit_records_intact'] = {
    'SI-26/312': env['sale.order'].sudo().with_context(active_test=False).search_count([('id', '=', 312)]),
    'version_115': env['sipanel.scope.version'].sudo().with_context(active_test=False).search_count([('id', '=', 115)]),
    'artifacts_total': env['sipanel.quote.scope.artifact'].sudo().search_count([]),
}
env.cr.commit()
print('CLEANUP=' + json.dumps(out, ensure_ascii=False, default=str))
