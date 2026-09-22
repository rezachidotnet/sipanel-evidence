# STEP 2C live synthetic pilot on `sipanel` - stage 1: masters, quotations, seal, confirm.
# Everything created here is prefixed SIPANEL-STEP2C-<TS>. No email, no posting, no real records.
import json
from odoo.tests.common import new_test_user
TS = '20260922T065650Z'
P = f'SIPANEL-STEP2C-{TS}'
env = env(user=2, context={'lang': 'en_US', 'tz': 'Asia/Tehran', 'allowed_company_ids': [1]})
assert env.cr.dbname == 'sipanel'
ICP = env['ir.config_parameter'].sudo()
out = {'ts': TS, 'prefix': P, 'ids': {}, 'facts': {}}
uom_m, uom_unit, uom_hour = env.ref('uom.product_uom_meter'), env.ref('uom.product_uom_unit'), env.ref('uom.product_uom_hour')
mail_before = env['mail.mail'].sudo().search_count([])
out['facts']['mail_mail_before'] = mail_before

# --- synthetic dimensions (the installed plans 80/81 exist but hold no accounts)
plan_sys = env['account.analytic.plan'].sudo().browse(int(ICP.get_param('sipanel_scope.system_plan_id')))
plan_act = env['account.analytic.plan'].sudo().browse(int(ICP.get_param('sipanel_scope.activity_plan_id')))
AA = env['account.analytic.account'].sudo()
system = AA.create({'name': f'{P} System', 'plan_id': plan_sys.id})
act_ins = AA.create({'name': f'{P} Activity INS', 'plan_id': plan_act.id})
act_mfg = AA.create({'name': f'{P} Activity MFG', 'plan_id': plan_act.id})
project = env['project.project'].create({'name': f'{P} Project'})
out['ids'].update({'system': system.id, 'act_ins': act_ins.id, 'act_mfg': act_mfg.id, 'project': project.id,
                   'project_account': project.account_id.id or None, 'plan_system': plan_sys.id, 'plan_activity': plan_act.id})

# --- synthetic execution owner (the real group gate is exercised through this user)
exec_user = new_test_user(env, login=f'{P}-exec', name=f'{P} Execution Owner', email=False, password=False,
                          groups='base.group_user,sipanel_scope_execution.group_scope_execution_owner,stock.group_stock_user,'
                                 'purchase.group_purchase_user,mrp.group_mrp_user,project.group_project_user,'
                                 'sales_team.group_sale_manager,sipanel_sale_scope.group_scope_sales,'
                                 'sipanel_commercial_scope_core.group_scope_cost_viewer')
out['ids']['exec_user'] = exec_user.id

# --- synthetic products
Product = env['product.product']
def mk(tag, uom, price, cost, ptype='consu', storable=True, **extra):
    vals = {'name': f'{P} {tag}', 'type': ptype, 'uom_id': uom.id, 'list_price': price, 'standard_price': cost,
            'sale_ok': True, 'purchase_ok': True, 'invoice_policy': 'order'}
    if ptype == 'consu':
        vals['is_storable'] = storable
    vals.update(extra)
    return Product.create(vals)
pA_anchor = mk('A anchor (bridge, service)', uom_m, 0.0, 0.0, 'service', service_tracking='no')
pB_anchor = mk('B anchor (native, task service)', uom_m, 0.0, 0.0, 'service', service_tracking='task_global_project', project_id=project.id)
p_bracket = mk('Wall bracket', uom_unit, 450000.0, 90000.0)
p_gutter = mk('Galvanised gutter', uom_m, 0.0, 120000.0)
p_coil = mk('Coil (BoM component)', uom_m, 0.0, 60000.0)
p_crane = mk('Crane service', uom_unit, 1500000.0, 800000.0, 'service', service_tracking='no')
p_labour = mk('Installation labour', uom_hour, 0.0, 300000.0, 'service', service_tracking='no')
out['ids']['products'] = {'A_anchor': pA_anchor.id, 'B_anchor': pB_anchor.id, 'bracket': p_bracket.id, 'gutter': p_gutter.id,
                          'coil': p_coil.id, 'crane': p_crane.id, 'labour': p_labour.id}
out['facts']['owner_registry'] = {'A_anchor': env['sipanel.execution.owner.rule'].resolve(pA_anchor, env.company),
                                  'B_anchor': env['sipanel.execution.owner.rule'].resolve(pB_anchor, env.company)}
vendor = env['res.partner'].create({'name': f'{P} Synthetic Vendor', 'email': False, 'phone': False, 'supplier_rank': 1})
seller = env['product.supplierinfo'].create({'partner_id': vendor.id, 'product_tmpl_id': p_crane.product_tmpl_id.id, 'price': 800000.0, 'min_qty': 0})
bom = env['mrp.bom'].create({'product_tmpl_id': p_gutter.product_tmpl_id.id, 'product_qty': 1.0, 'type': 'normal',
                             'bom_line_ids': [(0, 0, {'product_id': p_coil.id, 'product_qty': 1.0})]})
out['ids'].update({'vendor': vendor.id, 'supplierinfo': seller.id, 'bom': bom.id})

# --- masters
def master(tag, anchor, owner_mode, lines):
    sm = env['sipanel.scope'].create({'code': f'{P}-{tag}', 'name': f'{P} {tag} master', 'owner_user_id': env.uid})
    v = env['sipanel.scope.version'].create({'scope_id': sm.id, 'customer_label': f'{tag} gutter accessories', 'base_uom_id': uom_m.id,
                                             'dimension_family': 'length', 'anchor_product_id': anchor.id, 'anchor_owner_mode': owner_mode, 'all_systems': True})
    v.update_field_translations('customer_label', {'en_US': f'{tag} gutter accessories', 'fa_IR': f'متعلقات آبرو {tag}'})
    L = env['sipanel.scope.recipe.line']
    made = {}
    for key, vals in lines.items():
        label = vals.pop('label')
        rec = L.create(dict(version_id=v.id, customer_eligible=True, customer_label=label, **vals))
        rec.update_field_translations('customer_label', {'en_US': label, 'fa_IR': label})
        made[key] = rec.id
    v.action_release()
    return sm, v, made
smA, vA, linesA = master('A', pA_anchor, 'component_bridge_owner', {
    'A1_bracket_own_line': dict(label='Wall bracket', sequence=10, product_id=p_bracket.id, uom_id=uom_unit.id, dimension_family='count',
                                basis='per_scope_qty', rate=2.0, activity_id=act_ins.id, execution_mode='stock_issue', placement='own_line'),
    'A2_crane_own_line': dict(label='Crane service', sequence=20, product_id=p_crane.id, uom_id=uom_unit.id, dimension_family='count',
                              basis='fixed', fixed_qty=1.0, activity_id=act_ins.id, execution_mode='equipment_service', placement='own_line'),
    'A3_gutter_included': dict(label='Galvanised gutter', sequence=30, product_id=p_gutter.id, uom_id=uom_m.id, dimension_family='length',
                               basis='per_scope_qty', rate=1.0, activity_id=act_mfg.id, execution_mode='manufacture', placement='included_parent'),
    'A4_labour_included': dict(label='Installation', sequence=40, product_id=p_labour.id, uom_id=uom_hour.id, dimension_family='time',
                               basis='fixed', fixed_qty=8.0, activity_id=act_ins.id, execution_mode='labour', placement='included_parent'),
})
smB, vB, linesB = master('B', pB_anchor, 'native_line_owner', {
    'B1_bracket_own_line': dict(label='Wall bracket', sequence=10, product_id=p_bracket.id, uom_id=uom_unit.id, dimension_family='count',
                                basis='per_scope_qty', rate=2.0, activity_id=act_ins.id, execution_mode='native_anchor_covered', placement='own_line'),
    'B2_labour_included': dict(label='Installation', sequence=20, product_id=p_labour.id, uom_id=uom_hour.id, dimension_family='time',
                               basis='fixed', fixed_qty=8.0, activity_id=act_ins.id, execution_mode='native_anchor_covered', placement='included_parent'),
})
out['ids'].update({'master_A': smA.id, 'version_A': vA.id, 'lines_A': linesA, 'master_B': smB.id, 'version_B': vB.id, 'lines_B': linesB})
out['facts']['versions'] = {'A': (vA.state, vA.anchor_owner_mode), 'B': (vB.state, vB.anchor_owner_mode)}

# --- quotations: A (clean bridge path), A2 (partial failure / retry), B (native path + concurrency)
partner = env['res.partner'].create({'name': f'{P} Synthetic Customer', 'lang': 'en_US', 'email': False, 'phone': False})
out['ids']['customer'] = partner.id
QS = env['sipanel.quote.scope']
def quotation(tag, version, qty):
    order = env['sale.order'].create({'partner_id': partner.id, 'client_order_ref': f'{P}-{tag}', 'origin': f'{P}-{tag}'})
    scope = QS._create_from_version(order, version, qty, uom_m)
    scope.write({'project_id': project.id, 'system_id': system.id})
    scope.anchor_line_id.write({'price_unit': 2500000.0, 'tax_ids': [(5, 0, 0)]})
    rev = scope.current_revision_id
    for c in rev.component_ids.filtered('separately_billable'):
        if c.sell_price_status == 'missing':
            c.action_set_manual_sell_price(450000.0)
    rev.action_generate_note(accept=True)
    order._sipanel_seal_current_revisions(actor='pilot')
    order.action_confirm()
    return order, scope
def lines(order):
    return [{'id': l.id, 'name': (l.name or '')[:50], 'product': l.product_id.id, 'qty': l.product_uom_qty, 'generated': l.sipanel_is_generated,
             'anchor': l.sipanel_is_anchor, 'origin_key': l.sipanel_origin_key or None, 'component': l.sipanel_source_component_id.id or None,
             'revision': l.sipanel_source_revision_id.id or None, 'moves': l.move_ids.ids, 'move_states': l.move_ids.mapped('state'),
             'purchase_lines': l.purchase_line_ids.ids, 'task': l.task_id.id or None, 'project': l.project_id.id or None}
            for l in order.order_line.sorted('sequence') if not l.display_type]
orders = {}
for tag, version, qty in (('A', vA, 10.0), ('A2', vA, 10.0), ('B', vB, 10.0)):
    order, scope = quotation(tag, version, qty)
    rev = scope.accepted_revision_id
    orders[tag] = {'order': order.id, 'name': order.name, 'state': order.state, 'scope': scope.id, 'accepted_revision': rev.id,
                   'revision_state': rev.state, 'acceptance_reference': rev.acceptance_reference,
                   'components': [{'id': c.id, 'name': c.name, 'occurrence_uid': c.occurrence_uid, 'placement': c.placement,
                                   'separately_billable': c.separately_billable, 'execution_mode': c.execution_mode,
                                   'execution_owner': c.execution_owner, 'final_qty': c.final_qty, 'uom': c.uom_id.name,
                                   'activity': c.activity_id.id, 'system': (c.system_id or scope.system_id).id,
                                   'sell_price_status': c.sell_price_status}
                                  for c in rev.component_ids.sorted('sequence')],
                   'lines': lines(order),
                   'generated_line_count': len(order.order_line.filtered('sipanel_is_generated')),
                   'stock_moves_from_generated_lines': env['stock.move'].search_count([('sale_line_id', 'in', order.order_line.filtered('sipanel_is_generated').ids)]),
                   'stock_moves_from_anchor_line': env['stock.move'].search_count([('sale_line_id', '=', scope.anchor_line_id.id)]),
                   'pickings_for_order': env['stock.picking'].search([('origin', '=', order.name)]).mapped(lambda p: (p.id, p.picking_type_id.name, p.state)),
                   'tasks_for_order': env['project.task'].search([('sale_order_id', '=', order.id)]).mapped(lambda t: (t.id, t.project_id.id, t.sale_line_id.id)),
                   'purchase_orders_for_order': env['purchase.order'].search_count([('origin', '=', order.name)]),
                   'mrp_for_order': env['mrp.production'].search_count([('origin', '=', order.name)]),
                   'demands': env['sipanel.execution.demand'].search_count([('order_id', '=', order.id)]),
                   'batches': env['sipanel.execution.batch'].search_count([('order_id', '=', order.id)])}
out['orders'] = orders
out['facts']['mail_mail_after_setup'] = env['mail.mail'].sudo().search_count([])
out['facts']['posted_moves'] = env['account.move'].sudo().search_count([('state', '=', 'posted')])
env.cr.commit()
print('SETUP=' + json.dumps(out, ensure_ascii=False, default=str))
