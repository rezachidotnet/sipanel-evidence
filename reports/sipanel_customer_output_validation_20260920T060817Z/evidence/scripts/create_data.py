# SIPANEL customer-output validation data (temporary, prefixed). Runs as approved user id 2. Commits at end.
import json, os
TS = '20260920T060817Z'
P = f'SIPANEL-CUSTOMER-OUTPUT-CHECK-{TS}'
MK = lambda k: f'INTERNAL-MARKER-{k}-{TS}'
env = env(user=2, context={'lang': 'en_US', 'tz': 'Asia/Tehran', 'allowed_company_ids': [1]})
assert env.cr.dbname == 'sipanel'
assert env.user.login == 'amirmousa1983@gmail.com'
ids = {'ts': TS, 'prefix': P}
company = env.company
Plan = env['account.analytic.plan']
plan_sys = Plan.browse(int(env['ir.config_parameter'].sudo().get_param('sipanel_scope.system_plan_id')))
plan_act = Plan.browse(int(env['ir.config_parameter'].sudo().get_param('sipanel_scope.activity_plan_id')))
AA = env['account.analytic.account']
system = AA.create({'name': f'{P} SYSTEM {MK("ANALYTIC")}', 'plan_id': plan_sys.id})
act_mfg = AA.create({'name': f'{P} ACT-MFG {MK("ANALYTIC")}', 'plan_id': plan_act.id})
act_ins = AA.create({'name': f'{P} ACT-INS {MK("ANALYTIC")}', 'plan_id': plan_act.id})
ids['analytic_accounts'] = [system.id, act_mfg.id, act_ins.id]
uom_m = env.ref('uom.product_uom_meter'); uom_unit = env.ref('uom.product_uom_unit'); uom_hour = env.ref('uom.product_uom_hour')
Product = env['product.product']
def mk(name, uom, cost, ptype='consu', code=None):
    vals = {'name': f'{P} {name}', 'type': ptype, 'uom_id': uom.id, 'standard_price': cost, 'sale_ok': True, 'purchase_ok': False,
            'list_price': 0.0, 'default_code': code or f'VAL-{name[:6].upper().replace(" ", "")}-{TS[-6:]}',
            'description': f'{MK("PRODUCTDESC")} (validation data, not a real cost)'}
    if ptype == 'consu':
        vals['is_storable'] = True
    return Product.create(vals)
p_anchor = mk('Gutter run anchor (validation)', uom_m, 0.0, 'service', code=f'VAL-ANCHOR-{TS[-6:]}')
p_gutter = mk('Gutter validation', uom_m, 731000.0)
p_bracket = mk('Bracket validation', uom_unit, 9876.0)
p_sealant = mk('Sealant validation', uom_unit, 55555.0)
p_labour = mk('Labour validation', uom_hour, 4321.0, 'service')
p_crane = mk('Crane validation', uom_unit, 8765000.0, 'service')
p_screw = mk('Screw validation', uom_unit, 123.0)
p_scaff = mk('Scaffolding validation (customer)', uom_unit, 0.0, 'service')
ids['products'] = [p.id for p in (p_anchor, p_gutter, p_bracket, p_sealant, p_labour, p_crane, p_screw, p_scaff)]
scope = env['sipanel.scope'].create({'code': P, 'name': f'{P} {MK("SCOPENAME")}', 'owner_user_id': env.uid})
v1 = env['sipanel.scope.version'].create({
    'scope_id': scope.id, 'label_fa': 'متعلقات آبرو (داده آزمایشی)', 'label_en': 'Gutter accessories (validation data)',
    'customer_description_fa': 'شرح مشتری: تأمین و نصب متعلقات آبرو مطابق نقشه — این پیش‌فاکتور صرفاً برای اعتبارسنجی خروجی است.',
    'customer_description_en': 'Customer description: supply and installation of gutter accessories per drawing (validation only).',
    'internal_description': f'{MK("VERSIONDESC")} internal engineering notes must never reach the customer',
    'base_uom_id': uom_m.id, 'dimension_family': 'length', 'anchor_product_id': p_anchor.id,
    'anchor_owner_mode': 'component_bridge_owner', 'all_systems': True})
L = env['sipanel.scope.recipe.line']
common = {'version_id': v1.id, 'customer_eligible': True}
l_gutter = L.create(dict(common, sequence=10, product_id=p_gutter.id, uom_id=uom_m.id, dimension_family='length', basis='per_scope_qty', rate=1.0,
                         activity_id=act_mfg.id, execution_mode='manufacture', customer_label_fa='ناودان گالوانیزه', customer_label_en='Galvanised gutter',
                         placement='included_parent', certainty='firm', internal_description=f'{MK("COMP-GUTTER")}'))
l_bracket = L.create(dict(common, sequence=20, product_id=p_bracket.id, uom_id=uom_unit.id, dimension_family='count', basis='per_scope_qty', rate=2.0,
                          activity_id=act_ins.id, execution_mode='stock_issue', customer_label_fa='بست دیواری (صورت‌حساب جداگانه)', customer_label_en='Wall bracket (billed separately)',
                          placement='own_line', certainty='firm'))
l_sealant = L.create(dict(common, sequence=30, product_id=p_sealant.id, uom_id=uom_unit.id, dimension_family='count', basis='manual', manual_qty_default=6.0,
                          activity_id=act_ins.id, execution_mode='stock_issue', customer_label_fa='درزگیر سیلیکونی', customer_label_en='Silicone sealant',
                          placement='included_parent', certainty='firm'))  # provisional is set on the quote component (requires customer-visible basis)
l_labour = L.create(dict(common, sequence=40, product_id=p_labour.id, uom_id=uom_hour.id, dimension_family='time', basis='fixed', fixed_qty=8.0,
                         activity_id=act_ins.id, execution_mode='labour', cost_policy='manual_estimate', manual_cost_default=4321.0,
                         customer_label_fa='نصب و راه‌اندازی', customer_label_en='Installation', placement='included_parent'))
l_scaff = L.create(dict(common, sequence=50, product_id=p_scaff.id, uom_id=uom_unit.id, dimension_family='count', basis='fixed', fixed_qty=1.0, responsibility='customer',
                        execution_mode='no_action', no_action_reason='customer_responsibility', placement='no_customer_line',
                        customer_label_fa='داربست و دسترسی به محل به عهده کارفرما است (خارج از محدوده)', customer_label_en='Scaffolding and site access are the customer’s responsibility (excluded)'))
l_internal = L.create(dict(common, sequence=60, product_id=p_screw.id, uom_id=uom_unit.id, dimension_family='count', basis='fixed', fixed_qty=20.0,
                           activity_id=act_ins.id, execution_mode='stock_issue', customer_eligible=False, disclosure='internal_only',
                           customer_label_fa=MK('LABEL-FA'), customer_label_en=MK('LABEL-EN'), internal_description=MK('COMP-INTERNAL')))
l_crane = L.create(dict(common, sequence=70, product_id=p_crane.id, uom_id=uom_unit.id, dimension_family='count', basis='fixed', fixed_qty=1.0,
                        activity_id=act_ins.id, execution_mode='equipment_service', cost_policy='manual_estimate', manual_cost_default=8765000.0,
                        customer_label_fa='جرثقیل', customer_label_en='Crane'))
ids['scope'] = scope.id; ids['version'] = v1.id; ids['recipe_lines'] = v1.recipe_line_ids.ids
v1.action_release()
assert v1.state == 'released', v1.state
partner = env['res.partner'].create({'name': f'{P} مشتری آزمایشی (Synthetic Validation Customer)', 'lang': 'fa_IR', 'email': False, 'phone': False,
                                     'comment': f'{MK("PARTNERNOTE")} synthetic customer, no real person', 'street': 'نشانی آزمایشی', 'city': 'تهران'})
ids['partner'] = partner.id
tax = env['account.tax'].browse(287)
assert tax.exists() and tax.type_tax_use == 'sale'
SO = env['sale.order']
order = SO.create({'partner_id': partner.id, 'user_id': env.uid, 'client_order_ref': P, 'origin': P,
                   'note': '<p>یادداشت مشتری (داده آزمایشی): این پیش‌فاکتور صرفاً برای اعتبارسنجی خروجی ایجاد شده و فاقد اعتبار تجاری است. اقلام اختیاری تنها پس از تأیید مشتری در محدوده قرار می‌گیرند.</p>'})
ids['order'] = order.id; ids['order_name'] = order.name
QS = env['sipanel.quote.scope']
scope1 = QS._create_from_version(order, v1, 12.0, uom_m)
a1 = scope1.anchor_line_id
a1.write({'price_unit': 2500000.0, 'discount': 5.0, 'tax_ids': [(6, 0, [tax.id])]})
r1 = scope1.current_revision_id
c_seal = r1.component_ids.filtered(lambda c: c.product_id == p_sealant)
c_seal.write({'certainty': 'provisional', 'provisional_basis': 'مقدار اولیه؛ پس از بازدید محل نهایی می‌شود (داده آزمایشی)'})
c_int = r1.component_ids.filtered(lambda c: c.product_id == p_screw)
c_int.sudo().write({'manual_cost_reason': MK('COSTREASON')}) if 'manual_cost_reason' in c_int._fields else None
r1.action_generate_note(accept=True)
note_line = env['sale.order.line'].create({'order_id': order.id, 'display_type': 'line_note', 'sequence': 50,
    'name': 'یادداشت سطر (داده آزمایشی): قیمت‌ها بر اساس ریال و شامل مالیات بر ارزش افزوده طبق ردیف است.'})
section = env['sale.order.line'].create({'order_id': order.id, 'display_type': 'line_section', 'name': 'گزینه‌های اختیاری (Optional – validation)', 'is_optional': True, 'sequence': 100})
scope2 = QS._create_from_version(order, v1, 5.0, uom_m, optional=True, section_line=section)
a2 = scope2.anchor_line_id
a2.write({'price_unit': 2200000.0, 'tax_ids': [(6, 0, [tax.id])]})
ids.update({'scope1': scope1.id, 'scope2': scope2.id, 'rev1': r1.id, 'rev2': scope2.current_revision_id.id, 'anchor1': a1.id, 'anchor2': a2.id,
            'section': section.id, 'note_line': note_line.id})
order.message_post(body=f'{MK("CHATTER")} internal note: margin discussion must not reach the portal', message_type='comment', subtype_xmlid='mail.mt_note')
order_b = SO.create({'partner_id': partner.id, 'user_id': env.uid, 'client_order_ref': P + '-B', 'origin': P + '-B',
                     'order_line': [(0, 0, {'product_id': p_anchor.id, 'product_uom_qty': 1.0, 'price_unit': 1.0})]})
ids['order_b'] = order_b.id; ids['order_b_name'] = order_b.name
print('READINESS:', order.sipanel_readiness_state, '|', order.sipanel_readiness_text)
rs = r1.sudo()
ids['backoffice'] = {'rev1_eligible_cost_total': rs.eligible_cost_total, 'rev1_margin_amount': rs.margin_amount, 'rev1_margin_percent': rs.margin_percent,
                     'order_total_cost': order.sudo().sipanel_total_cost, 'order_total_margin': order.sudo().sipanel_total_margin,
                     'components': [{'id': c.id, 'label_fa': c.customer_label_fa, 'disclosure': c.disclosure, 'placement': c.placement, 'certainty': c.certainty,
                                     'responsibility': c.responsibility, 'final_qty': c.final_qty, 'unit_cost': c.sudo().unit_cost, 'cost_amount': c.sudo().cost_amount,
                                     'cost_source': c.cost_source} for c in r1.component_ids]}
# mark as sent WITHOUT email: seals revisions (SIPANEL hook) and sets state=sent (native), no mail.
order.action_quotation_sent()
env.cr.flush()
assert order.state == 'sent'
assert scope1.current_revision_id.state == 'sent_sealed' and scope2.current_revision_id.state == 'sent_sealed'
ids['seal'] = {'rev1_hash': scope1.current_revision_id.sealed_hash, 'rev2_hash': scope2.current_revision_id.sealed_hash, 'order_hash': order.sipanel_current_seal_hash,
               'artifacts': [{'id': a.id, 'kind': a.kind, 'hash': a.content_hash, 'att': a.attachment_id.id} for a in (scope1.current_revision_id.artifact_ids | scope2.current_revision_id.artifact_ids).sudo()]}
tokens = {'order': order._portal_ensure_token(), 'order_b': order_b._portal_ensure_token()}
ids['final_note_rev1'] = scope1.current_revision_id.final_note
ids['final_note_rev2'] = scope2.current_revision_id.final_note
ids['amounts'] = {'untaxed': order.amount_untaxed, 'tax': order.amount_tax, 'total': order.amount_total, 'currency': order.currency_id.name,
                  'lines': [{'id': l.id, 'name': l.name, 'display_type': l.display_type, 'qty': l.product_uom_qty, 'uom': l.product_uom_id.name, 'price_unit': l.price_unit,
                             'discount': l.discount, 'taxes': l.tax_ids.mapped('name'), 'subtotal': l.price_subtotal, 'total': l.price_total, 'is_optional': l.is_optional, 'optional_line': (l._is_line_optional() if not l.display_type else None)} for l in order.order_line]}
ids['mail_count_before'] = env['mail.mail'].sudo().search_count([('model', '=', 'sale.order'), ('res_id', 'in', [order.id, order_b.id])])
os.makedirs('/tmp/sipanel_val', exist_ok=True)
with open('/tmp/sipanel_val/ids.json', 'w') as f: json.dump(ids, f, ensure_ascii=False, indent=1, default=str)
with open('/tmp/sipanel_val/tokens.json', 'w') as f: json.dump(tokens, f)
os.chmod('/tmp/sipanel_val/tokens.json', 0o600)
env.cr.commit()
print('CREATED_OK', json.dumps({k: ids[k] for k in ('order', 'order_name', 'order_b', 'scope1', 'scope2', 'rev1', 'rev2', 'partner', 'version')}))
