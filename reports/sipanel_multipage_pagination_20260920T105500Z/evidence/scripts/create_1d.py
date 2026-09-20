# STEP 1D - synthetic fixtures for the multi-page pagination defect (L-02).
# Five document shapes, all DRAFT quotations, prefixed and synthetic. No email, no confirmation.
import json, os
TS = '20260920T105500Z'
P = f'SIPANEL-PAGINATION-CHECK-{TS}'
env = env(user=2, context={'lang': 'en_US', 'tz': 'Asia/Tehran', 'allowed_company_ids': [1]})
assert env.cr.dbname == 'sipanel', env.cr.dbname
ICP = env['ir.config_parameter'].sudo()
assert ICP.get_param('report.url') == 'http://127.0.0.1:8072', ICP.get_param('report.url')

v1 = env['sipanel.scope.version'].browse(115)
assert v1.state == 'released' and v1.recipe_line_ids, 'released version 115 missing'
tax = env['account.tax'].browse(287)
assert tax.exists(), 'tax 287 missing'
uom_m = env.ref('uom.product_uom_meter')
QS = env['sipanel.quote.scope']
SOL = env['sale.order.line']

LONG = ('این بند از یادداشت مشتری (داده آزمایشی) صرفاً برای اعتبارسنجی صفحه‌بندی سند چندصفحه‌ای ایجاد شده است. '
        'محدوده کار شامل تأمین، حمل و نصب متعلقات آبرو مطابق نقشه‌های تأییدشده است و هرگونه تغییر در نقشه‌ها باید کتباً اعلام شود. '
        'زمان‌بندی اجرا پس از تأیید نهایی مشتری و آماده بودن محل اعلام می‌گردد. ')

partner = env['res.partner'].create({
    'name': f'{P} مشتری آزمایشی پارسی', 'lang': 'fa_IR', 'email': False, 'phone': False,
    'street': 'خیابان آزمایشی، پلاک ۱۲', 'city': 'اصفهان'})

out = {'ts': TS, 'prefix': P, 'partner': partner.id, 'docs': {}}

def base_order(tag, note_html=False):
    return env['sale.order'].create({
        'partner_id': partner.id, 'user_id': env.uid,
        'client_order_ref': f'{P}-{tag}', 'origin': f'{P}-{tag}',
        'note': note_html or False})

def add_scope(order, qty, price, optional=False, section=None):
    s = QS._create_from_version(order, v1, qty, uom_m, optional=optional, section_line=section)
    s.anchor_line_id.write({'price_unit': price, 'tax_ids': [(6, 0, [tax.id])]})
    return s

def note_lines(order, rng, reps, seq0):
    for i in rng:
        SOL.create({'order_id': order.id, 'display_type': 'line_note', 'sequence': seq0 + i,
                    'name': f'یادداشت سطر {i} (داده آزمایشی): ' + LONG * reps})

# --- A: short quotation (single scope, no extra notes) -----------------------
a = base_order('A-SHORT')
sa = add_scope(a, 12.0, 2500000.0)
sa.anchor_line_id.write({'discount': 5.0})
sa.current_revision_id.action_generate_note(accept=True)
out['docs']['A_SHORT'] = a.id

# --- B: normal multi-page quotation ------------------------------------------
b = base_order('B-NORMAL', '<p>' + LONG + '</p>')
sb = add_scope(b, 12.0, 2500000.0)
sb.current_revision_id.action_generate_note(accept=True)
note_lines(b, range(1, 4), 2, 20)
out['docs']['B_NORMAL'] = b.id

# --- C: long Persian notes across several pages -------------------------------
c = base_order('C-LONGNOTES', '<p>' + LONG * 3 + '</p>')
sc = add_scope(c, 12.0, 2500000.0)
sc.current_revision_id.action_generate_note(accept=True)
note_lines(c, range(1, 9), 3, 20)
out['docs']['C_LONGNOTES'] = c.id

# --- D: optional + provisional + separately presented sections ----------------
d = base_order('D-SECTIONS', '<p>' + LONG * 2 + '</p>')
sd = add_scope(d, 12.0, 2500000.0)
sd.anchor_line_id.write({'discount': 5.0})
rd = sd.current_revision_id
prov = rd.component_ids.filtered(lambda x: x.uom_id == env.ref('uom.product_uom_unit') and x.basis == 'manual')
prov.write({'certainty': 'provisional',
            'provisional_basis': 'مقدار اولیه؛ پس از بازدید محل نهایی می‌شود (داده آزمایشی)'})
rd.action_generate_note(accept=True)
note_lines(d, range(1, 6), 2, 20)
sec = SOL.create({'order_id': d.id, 'display_type': 'line_section',
                  'name': 'گزینه‌های اختیاری (Optional – validation)', 'is_optional': True, 'sequence': 100})
sd2 = add_scope(d, 5.0, 2200000.0, optional=True, section=sec)
sd2.current_revision_id.action_generate_note(accept=True)
note_lines(d, range(6, 9), 2, 100)
out['docs']['D_SECTIONS'] = d.id

# --- E: totals / signature near a page boundary (sweep of filler lengths) ------
out['docs_E'] = {}
for k, reps in enumerate([1, 2, 3, 4, 5, 6], start=1):
    e = base_order(f'E-BOUNDARY{k}')
    se = add_scope(e, 12.0, 2500000.0)
    se.current_revision_id.action_generate_note(accept=True)
    SOL.create({'order_id': e.id, 'display_type': 'line_note', 'sequence': 30,
                'name': f'یادداشت مرزی {k} (داده آزمایشی): ' + LONG * reps})
    out['docs_E'][f'E{k}'] = e.id

env.cr.flush()
names = {}
for k, i in list(out['docs'].items()) + list(out['docs_E'].items()):
    o = env['sale.order'].browse(i)
    names[k] = {'id': i, 'name': o.name, 'state': o.state, 'lines': len(o.order_line),
                'untaxed': o.amount_untaxed, 'tax': o.amount_tax, 'total': o.amount_total}
out['orders'] = names
os.makedirs('/tmp/sipanel_1d', exist_ok=True)
json.dump(out, open('/tmp/sipanel_1d/ids.json', 'w'), ensure_ascii=False, indent=1, default=str)
env.cr.commit()
print('CREATED_1D=' + json.dumps(names, ensure_ascii=False))
