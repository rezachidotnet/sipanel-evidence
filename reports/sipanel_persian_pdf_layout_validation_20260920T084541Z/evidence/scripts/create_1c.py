# STEP 1C — fresh post-D-02 draft validation quotation (prefixed, synthetic). Commits at end. Renders the BEFORE-fix PDF via the ORM report path.
import json, os
TS = '20260920T084541Z'
P = f'SIPANEL-PDF-LAYOUT-CHECK-{TS}'
MK = lambda k: f'INTERNAL-MARKER-{k}-{TS}'
env = env(user=2, context={'lang': 'en_US', 'tz': 'Asia/Tehran', 'allowed_company_ids': [1]})
assert env.cr.dbname == 'sipanel'
ICP = env['ir.config_parameter'].sudo()
assert ICP.get_param('report.url') == 'http://127.0.0.1:8072', ICP.get_param('report.url')
ids = {'ts': TS, 'prefix': P, 'report_url': ICP.get_param('report.url'), 'website_langs': env['website'].sudo().browse(1).language_ids.mapped('code')}
v1 = env['sipanel.scope.version'].browse(115)
assert v1.state == 'released' and v1.recipe_line_ids
ids['reused_version'] = {'id': v1.id, 'scope_master': v1.scope_id.id, 'scope_active': v1.scope_id.active, 'lines': len(v1.recipe_line_ids),
                        'internal_only_lines': v1.recipe_line_ids.filtered(lambda l: l.disclosure == 'internal_only').ids,
                        'own_line_lines': v1.recipe_line_ids.filtered(lambda l: l.placement == 'own_line').ids}
partner = env['res.partner'].create({'name': f'{P} مشتری آزمایشی پارسی (Synthetic Persian Customer)', 'lang': 'fa_IR', 'email': False, 'phone': False,
                                     'comment': f'{MK("PARTNERNOTE")} synthetic', 'street': 'خیابان آزمایشی، پلاک ۱۲', 'city': 'اصفهان'})
ids['partner'] = partner.id
tax = env['account.tax'].browse(287)
LONG = ('این بند از یادداشت مشتری (داده آزمایشی) صرفاً برای اعتبارسنجی صفحه‌بندی سند چندصفحه‌ای ایجاد شده است. '
        'محدوده کار شامل تأمین، حمل و نصب متعلقات آبرو مطابق نقشه‌های تأییدشده است و هرگونه تغییر در نقشه‌ها باید کتباً اعلام شود. '
        'زمان‌بندی اجرا پس از تأیید نهایی مشتری و آماده بودن محل اعلام می‌گردد. ')
order = env['sale.order'].create({'partner_id': partner.id, 'user_id': env.uid, 'client_order_ref': P, 'origin': P,
                                  'note': '<p>' + (LONG * 3) + '</p>'})
ids['order'] = order.id; ids['order_name'] = order.name
uom_m = env.ref('uom.product_uom_meter')
QS = env['sipanel.quote.scope']
s1 = QS._create_from_version(order, v1, 12.0, uom_m)
s1.anchor_line_id.write({'price_unit': 2500000.0, 'discount': 5.0, 'tax_ids': [(6, 0, [tax.id])]})
r1 = s1.current_revision_id
c_seal = r1.component_ids.filtered(lambda c: c.uom_id == env.ref('uom.product_uom_unit') and c.basis == 'manual')
c_seal.write({'certainty': 'provisional', 'provisional_basis': 'مقدار اولیه؛ پس از بازدید محل نهایی می‌شود (داده آزمایشی)'})
r1.action_generate_note(accept=True)
SOL = env['sale.order.line']
for i in range(1, 6):
    SOL.create({'order_id': order.id, 'display_type': 'line_note', 'sequence': 20 + i,
                'name': f'یادداشت سطر {i} (داده آزمایشی): ' + LONG * 2})
section = SOL.create({'order_id': order.id, 'display_type': 'line_section', 'name': 'گزینه‌های اختیاری (Optional – validation)', 'is_optional': True, 'sequence': 100})
s2 = QS._create_from_version(order, v1, 5.0, uom_m, optional=True, section_line=section)
s2.anchor_line_id.write({'price_unit': 2200000.0, 'tax_ids': [(6, 0, [tax.id])]})
for i in range(6, 9):
    SOL.create({'order_id': order.id, 'display_type': 'line_note', 'sequence': 100 + i,
                'name': f'یادداشت سطر {i} (داده آزمایشی): ' + LONG * 2})
order.message_post(body=f'{MK("CHATTER")} internal note', message_type='comment', subtype_xmlid='mail.mt_note')
env.cr.flush()
ids.update({'scope1': s1.id, 'scope2': s2.id, 'rev1': r1.id, 'rev2': s2.current_revision_id.id, 'lines': order.order_line.ids, 'state': order.state,
            'final_note_rev1': r1.final_note, 'uom_snapshots': sorted(set(r1.component_ids.mapped('uom_name_snapshot'))),
            'amounts': {'untaxed': order.amount_untaxed, 'tax': order.amount_tax, 'total': order.amount_total},
            'backoffice': {'cost': r1.sudo().eligible_cost_total, 'margin': r1.sudo().margin_amount, 'internal_only_components': r1.component_ids.filtered(lambda c: c.disclosure == 'internal_only').ids}})
pdf, fmt = env['ir.actions.report']._render_qweb_pdf('sale.action_report_saleorder', [order.id])
os.makedirs('/tmp/sipanel_val', exist_ok=True)
open('/tmp/sipanel_val/fresh_before_fix.pdf', 'wb').write(pdf); ids['pdf_before'] = {'fmt': fmt, 'size': len(pdf)}
with open('/tmp/sipanel_val/ids_1c.json', 'w') as f: json.dump(ids, f, ensure_ascii=False, indent=1, default=str)
env.cr.commit()
print('CREATED_1C=' + json.dumps({k: ids[k] for k in ('order', 'order_name', 'state', 'partner', 'scope1', 'scope2', 'uom_snapshots', 'amounts', 'pdf_before')}, ensure_ascii=False))
print('NOTE_1C=' + json.dumps(ids['final_note_rev1'], ensure_ascii=False))
