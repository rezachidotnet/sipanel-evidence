# STEP 2A cleanup: remove the synthetic end-to-end quotation. The migrated
# master translations are NOT temporary data and stay.
import json
TS = '20260921T013000Z'
P = f'SIPANEL-XLATE-CHECK-{TS}'
env = env(user=2, context={'lang': 'en_US', 'allowed_company_ids': [1]})
assert env.cr.dbname == 'sipanel'
out = {'prefix': P, 'deleted': {}, 'leftovers': {}, 'side_effects': {}}

orders = env['sale.order'].search([('client_order_ref', '=', P)])
for o in orders:
    assert o.state == 'draft', (o.name, o.state)
scopes = env['sipanel.quote.scope'].search([('order_id', 'in', orders.ids)])
revs = scopes.mapped('revision_ids')
comps = revs.mapped('component_ids')
assert all(r.state == 'working' for r in revs), 'a revision is sealed'
assert not revs.mapped('artifact_ids'), 'artifacts exist'
counts = {'orders': len(orders), 'order_lines': sum(len(o.order_line) for o in orders),
          'scopes': len(scopes), 'revisions': len(revs), 'components': len(comps)}
lines = scopes.mapped('anchor_line_id')
scopes.write({'current_revision_id': False}); env.cr.flush()   # D-04 workaround
comps.sudo().unlink(); env.cr.flush()
revs.unlink(); env.cr.flush()
scopes.unlink(); env.cr.flush()
lines.unlink(); env.cr.flush()
names = orders.mapped('name'); orders.unlink(); env.cr.flush()
out['deleted'] = dict(counts, order_names=names)
partners = env['res.partner'].search([('name', 'like', P)])
try:
    pids = partners.ids; partners.unlink(); env.cr.flush(); out['deleted']['partners'] = pids
except Exception as exc:
    partners.write({'active': False}); out['deleted']['partners_archived'] = [partners.ids, str(exc)[:120]]

for model, dom in [('sale.order', [('client_order_ref', '=', P)]),
                   ('sipanel.quote.scope', [('order_id.client_order_ref', '=', P)]),
                   ('res.partner', [('name', 'like', P)])]:
    out['leftovers'][model] = env[model].sudo().with_context(active_test=False).search_count(dom)

since = '2026-09-21 01:25:00'
out['side_effects'] = {
    'mail_mail': env['mail.mail'].sudo().search_count([('create_date', '>=', since)]),
    'stock_picking': env['stock.picking'].sudo().search_count([('origin', 'in', names)]),
    'account_move': env['account.move'].sudo().search_count([('invoice_origin', 'in', names)]),
    'mrp_production': env['mrp.production'].sudo().search_count([('origin', 'in', names)]),
    'purchase_order': env['purchase.order'].sudo().search_count([('origin', 'in', names)]),
    'execution_demand': env['sipanel.execution.demand'].sudo().search_count([]),
}
V = env['sipanel.scope.version'].sudo().with_context(active_test=False)
out['retained_master_translations'] = {
    v.id: {'algo': v.checksum_algo,
           'label_langs': sorted((v.customer_label and
                                  v._fields['customer_label']._get_stored_translations(v) or {}))}
    for v in V.search([])}
out['config'] = {'report.url': env['ir.config_parameter'].sudo().get_param('report.url'),
                 'website_langs': env['website'].sudo().browse(1).language_ids.mapped('code')}
out['retained_audit_records'] = {
    'SI-26/312': env['sale.order'].sudo().with_context(active_test=False).search_count([('id', '=', 312)]),
    'sealed_revisions': env['sipanel.quote.scope.revision'].sudo().search_count([('state', 'in', ('sent_sealed', 'accepted_sealed'))]),
    'artifacts': env['sipanel.quote.scope.artifact'].sudo().search_count([])}
env.cr.commit()
print('CLEANUP=' + json.dumps(out, ensure_ascii=False, default=str))
