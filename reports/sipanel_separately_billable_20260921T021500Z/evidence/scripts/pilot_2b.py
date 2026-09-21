# STEP 2B live synthetic pilot on `sipanel`: Quotation -> seal -> optional
# acceptance -> confirmation -> DRAFT invoice. No email, no posting.
import json
TS = '20260921T021500Z'
P = f'SIPANEL-SEPBILL-PILOT-{TS}'
env = env(user=2, context={'lang': 'en_US', 'tz': 'Asia/Tehran', 'allowed_company_ids': [1]})
assert env.cr.dbname == 'sipanel'
ICP = env['ir.config_parameter'].sudo()
assert ICP.get_param('report.url') == 'http://127.0.0.1:8072'
out = {'ts': TS, 'prefix': P}

src = env['sipanel.scope.version'].browse(115)
assert src.state == 'released', src.state
uom_m, uom_unit, uom_hour = (env.ref('uom.product_uom_meter'), env.ref('uom.product_uom_unit'),
                             env.ref('uom.product_uom_hour'))
out['reference_master'] = {'id': src.id, 'name': src.display_name,
                           'note': 'structure mirrored; its products were archived in STEP 1A, '
                                   'and a released master is never modified'}

# --- fresh synthetic products (the retained validation products are archived)
Product = env['product.product']
def mk(tag, uom, price, cost):
    return Product.create({'name': f'{P} {tag}', 'type': 'consu', 'uom_id': uom.id,
                           'list_price': price, 'standard_price': cost,
                           'sale_ok': True, 'purchase_ok': True, 'invoice_policy': 'order'})
p_anchor = mk('Gutter accessories (anchor)', uom_m, 0.0, 0.0)
p_gutter = mk('Galvanised gutter', uom_m, 0.0, 120000.0)
p_bracket = mk('Wall bracket', uom_unit, 450000.0, 90000.0)
p_crane = mk('Crane service', uom_unit, 1500000.0, 800000.0)
p_sealant = mk('Silicone sealant', uom_unit, 0.0, 20000.0)
p_screw = mk('Screws (internal)', uom_unit, 0.0, 5000.0)
out['pilot_products'] = {'anchor': p_anchor.id, 'gutter': p_gutter.id, 'bracket': p_bracket.id,
                         'crane': p_crane.id, 'sealant': p_sealant.id, 'screw': p_screw.id}
act = src.recipe_line_ids[:1].activity_id or env['account.analytic.account'].search(
    [('plan_id', '=', int(ICP.get_param('sipanel_scope.activity_plan_id')))], limit=1)

scope_m = env['sipanel.scope'].create({
    'code': f'{P}-MASTER', 'name': f'{P} gutter accessories (pilot)', 'owner_user_id': env.uid})
v = env['sipanel.scope.version'].create({
    'scope_id': scope_m.id, 'customer_label': 'Gutter accessories',
    'base_uom_id': uom_m.id, 'dimension_family': 'length', 'anchor_product_id': p_anchor.id,
    'anchor_owner_mode': 'component_bridge_owner', 'all_systems': True})
v.update_field_translations('customer_label', {'en_US': 'Gutter accessories', 'fa_IR': 'متعلقات آبرو'})
L = env['sipanel.scope.recipe.line']
base_vals = {'version_id': v.id, 'customer_eligible': True}
shapes = {}
l_inc = L.create(dict(base_vals, sequence=10, product_id=p_gutter.id, uom_id=uom_m.id,
                      dimension_family='length', basis='per_scope_qty', rate=1.0,
                      activity_id=act.id, execution_mode='stock_issue',
                      placement='included_parent', customer_label='Galvanised gutter'))
l_sep = L.create(dict(base_vals, sequence=20, product_id=p_bracket.id, uom_id=uom_unit.id,
                      dimension_family='count', basis='per_scope_qty', rate=2.0,
                      activity_id=act.id, execution_mode='stock_issue',
                      placement='own_line', customer_label='Wall bracket'))
l_prov = L.create(dict(base_vals, sequence=30, product_id=p_crane.id, uom_id=uom_unit.id,
                       dimension_family='count', basis='fixed', fixed_qty=1.0,
                       activity_id=act.id, execution_mode='equipment_service',
                       placement='own_line', customer_label='Crane service'))
l_cust = L.create(dict(base_vals, sequence=40, product_id=p_sealant.id, uom_id=uom_unit.id,
                       dimension_family='count', basis='fixed', fixed_qty=5.0,
                       execution_mode='no_action', no_action_reason='customer_responsibility',
                       responsibility='customer', placement='own_line',
                       customer_label='Customer-supplied sealant'))
l_int = L.create(dict(base_vals, sequence=50, product_id=p_screw.id, uom_id=uom_unit.id,
                      dimension_family='count', basis='fixed', fixed_qty=10.0,
                      activity_id=act.id, execution_mode='stock_issue',
                      customer_eligible=False, disclosure='internal_only', placement='own_line',
                      customer_label='Internal screws'))
for line, en, fa in ((l_inc, 'Galvanised gutter', 'ناودان گالوانیزه'),
                     (l_sep, 'Wall bracket', 'بست دیواری'),
                     (l_prov, 'Crane service', 'جرثقیل'),
                     (l_cust, 'Customer-supplied sealant', 'درزگیر کارفرما'),
                     (l_int, 'Internal screws', 'پیچ داخلی')):
    line.update_field_translations('customer_label', {'en_US': en, 'fa_IR': fa})
shapes = {'included': l_inc.id, 'separately_billable': l_sep.id, 'provisional_source': l_prov.id,
          'customer_scope': l_cust.id, 'internal_only': l_int.id}
out['shapes'] = shapes
out['pilot_master'] = {'scope': scope_m.id, 'version': v.id, 'lines': len(v.recipe_line_ids)}
v.action_release()
out['pilot_master']['released_checksum'] = v.release_checksum

# --- Persian quotation
partner = env['res.partner'].create({'name': f'{P} مشتری آزمایشی', 'lang': 'fa_IR', 'email': False})
order = env['sale.order'].create({'partner_id': partner.id, 'client_order_ref': P, 'origin': P})
QS = env['sipanel.quote.scope']
base = QS._create_from_version(order, v, 12.0, uom_m)
base.anchor_line_id.write({'price_unit': 2500000.0})
section = env['sale.order.line'].create({
    'order_id': order.id, 'display_type': 'line_section', 'name': 'گزینه‌های اختیاری',
    'is_optional': True, 'sequence': 100})
opt = QS._create_from_version(order, v, 5.0, uom_m, optional=True, section_line=section)

# one component becomes PROVISIONAL on the quotation (the master has no basis field)
prov = base.current_revision_id.component_ids.filtered(
    lambda c: c.source_line_id.id == shapes['provisional_source'])
prov.write({'certainty': 'provisional',
            'provisional_basis': 'مقدار اولیه؛ پس از بازدید محل نهایی می‌شود'})
for rev in (base.current_revision_id, opt.current_revision_id):
    for c in rev.component_ids.filtered('separately_billable'):
        if c.sell_price_status == 'missing':
            c.action_set_manual_sell_price(450000.0)
    rev.action_generate_note(accept=True)

def snapshot(tag):
    data = {'tag': tag, 'order': order.name, 'state': order.state,
            'amount_untaxed': order.amount_untaxed, 'amount_tax': order.amount_tax,
            'amount_total': order.amount_total, 'lines': []}
    for l in order.order_line.sorted('sequence'):
        data['lines'].append({
            'id': l.id, 'seq': l.sequence, 'display_type': l.display_type or 'product',
            'name': (l.name or '')[:60], 'qty': l.product_uom_qty, 'price_unit': l.price_unit,
            'subtotal': l.price_subtotal, 'taxes': l.tax_ids.mapped('name'),
            'generated': l.sipanel_is_generated, 'gate': l.sipanel_invoice_gate or '',
            'placement': l.sipanel_placement_snapshot or '', 'anchor': l.sipanel_is_anchor,
        })
    return data

out['before_seal'] = snapshot('draft')
pdf_before, _ = env['ir.actions.report'].sudo()._render_qweb_pdf('sale.action_report_saleorder', order.ids)
open('/tmp/pilot_before.pdf', 'wb').write(pdf_before)

order._sipanel_seal_current_revisions(actor='pilot')
out['after_seal'] = snapshot('sealed')
opt._transition_acceptance('accepted', actor='pilot')
out['after_accept'] = snapshot('optional accepted')
# Accepting an option changes the order total, which is part of the seal payload,
# so every sealed scope on the order legitimately drifts. The governed flow
# re-seals before confirmation (see test_pt21 in test_governance.py); this is
# pre-existing behaviour, not something the projection introduced.
out['drift_after_acceptance'] = {
    r.display_name: r._current_seal_hash() != r.sealed_hash
    for r in (base | opt).mapped('current_revision_id')}
order._sipanel_seal_current_revisions(actor='pilot_reseal')
out['after_reseal'] = snapshot('resealed')
order.action_confirm()
out['after_confirm'] = snapshot('confirmed')
pdf_after, _ = env['ir.actions.report'].sudo()._render_qweb_pdf('sale.action_report_saleorder', order.ids)
open('/tmp/pilot_after.pdf', 'wb').write(pdf_after)

invoice = order._create_invoices()
out['invoice'] = {
    'id': invoice.id, 'name': invoice.name, 'state': invoice.state,
    'amount_untaxed': invoice.amount_untaxed, 'amount_total': invoice.amount_total,
    'lines': [{
        'name': (l.name or '')[:60], 'qty': l.quantity, 'price_unit': l.price_unit,
        'taxes': l.tax_ids.mapped('name'),
        'scope': l.sipanel_source_scope_id.id or None,
        'revision': l.sipanel_source_revision_id.id or None,
        'component': l.sipanel_source_component_id.id or None,
        'origin_key': l.sipanel_origin_key or None,
        'sale_line': l.sipanel_source_line_id.id or None,
    } for l in invoice.invoice_line_ids],
}
# operational demand / double-counting evidence
gen = env['sale.order.line'].search([('order_id', '=', order.id), ('sipanel_is_generated', '=', True)])
out['operational'] = {
    'generated_lines': len(gen),
    'stock_moves_from_generated_lines': env['stock.move'].search_count([('sale_line_id', 'in', gen.ids)]),
    'execution_demands': env['sipanel.execution.demand'].search_count([('quote_scope_id', 'in', (base | opt).ids)]),
    'purchase_orders': env['purchase.order'].search_count([('origin', '=', order.name)]),
    'mrp_productions': env['mrp.production'].search_count([('origin', '=', order.name)]),
    'mail_mail': env['mail.mail'].sudo().search_count([('create_date', '>=', '2026-09-21 06:45:00')]),
}
out['reconciliation'] = {r.display_name: r.reconciliation_json
                         for r in (base | opt).mapped('current_revision_id')}
out['ids'] = {'order': order.id, 'partner': partner.id, 'base_scope': base.id, 'opt_scope': opt.id,
              'invoice': invoice.id, 'pilot_scope_master': scope_m.id, 'pilot_version': v.id}
env.cr.commit()
print('PILOT=' + json.dumps(out, ensure_ascii=False, default=str))
