# STEP 2C-CLOSEOUT-HARDENING minimal live pilot: plain Sales user seals/sends their own synthetic quotation,
# plus one live refused pre-sudo probe (rev.with_user(sales).sudo().action_seal() on another salesperson's order)
# inside a savepoint. Synthetic records only (prefix SIPANEL-STEP2CCOH-<TS>); no release, no invoice, no email; cleanup at the end.
import json, re
from odoo.exceptions import AccessError
from odoo.addons.sipanel_commercial_scope_core.models.sipanel_tools import guard_ctx
TS = '20260923T051626Z'
P = f'SIPANEL-STEP2CCOH-{TS}'
env = env(user=2, context={'lang': 'en_US', 'tz': 'Asia/Tehran', 'allowed_company_ids': [1]})
assert env.cr.dbname == 'sipanel'
out = {'ts': TS, 'prefix': P, 'ids': {}, 'stages': {}}
counters = lambda: {'mail_mail': env['mail.mail'].sudo().search_count([]), 'posted_moves': env['account.move'].sudo().search_count([('state', '=', 'posted')]),
                    'done_stock_moves': env['stock.move'].sudo().search_count([('state', '=', 'done')]), 'purchase_orders': env['purchase.order'].sudo().search_count([]),
                    'batches': env['sipanel.execution.batch'].sudo().search_count([]), 'demands': env['sipanel.execution.demand'].sudo().search_count([]),
                    'analytic_lines': env['account.analytic.line'].sudo().search_count([])}
out['counters_before'] = counters()
uom_m, uom_unit, uom_hour = env.ref('uom.product_uom_meter'), env.ref('uom.product_uom_unit'), env.ref('uom.product_uom_hour')
ICP = env['ir.config_parameter'].sudo()
plan_act = env['account.analytic.plan'].sudo().browse(int(ICP.get_param('sipanel_scope.activity_plan_id')))
act = env['account.analytic.account'].sudo().create({'name': f'{P} Activity', 'plan_id': plan_act.id})
sales = env['res.users'].with_context(active_test=False).search([('login', '=', 'SIPANEL-STEP2CH-20260922T083014Z-sales')])
assert sales
sales.write({'active': True, 'group_ids': [(6, 0, [env.ref('base.group_user').id, env.ref('sales_team.group_sale_salesman').id, env.ref('sipanel_sale_scope.group_scope_sales').id])]})
env.cr.flush(); env.invalidate_all()
plain = env['res.users'].with_context(active_test=False).search([('login', '=', 'SIPANEL-STEP2C-20260922T065650Z-exec')])   # reused as an "unauthorised" plain internal user
assert plain
plain.write({'active': True, 'group_ids': [(6, 0, [env.ref('base.group_user').id])]})
env.cr.flush(); env.invalidate_all()
out['ids'].update({'sales_user': (sales.id, sales.login, sorted(sales.group_ids.mapped('full_name'))), 'plain_user': (plain.id, plain.login, sorted(plain.group_ids.mapped('full_name')))})
Product = env['product.product']
def mk(tag, uom, price, cost, ptype='consu', **extra):
    vals = {'name': f'{P} {tag}', 'type': ptype, 'uom_id': uom.id, 'list_price': price, 'standard_price': cost, 'sale_ok': True, 'purchase_ok': False, 'invoice_policy': 'order'}
    if ptype == 'consu': vals['is_storable'] = True
    vals.update(extra); return Product.create(vals)
p_anchor = mk('anchor (bridge)', uom_m, 0.0, 0.0, 'service', service_tracking='no')
p_bracket = mk('Wall bracket', uom_unit, 450000.0, 90000.0)
p_labour = mk('Installation labour', uom_hour, 0.0, 300000.0, 'service', service_tracking='no')
sm = env['sipanel.scope'].create({'code': f'{P}-A', 'name': f'{P} master', 'owner_user_id': env.uid})
v = env['sipanel.scope.version'].create({'scope_id': sm.id, 'customer_label': 'Gutter accessories (closeout-hardening pilot)', 'base_uom_id': uom_m.id, 'dimension_family': 'length',
                                         'anchor_product_id': p_anchor.id, 'anchor_owner_mode': 'component_bridge_owner', 'all_systems': True})
v.update_field_translations('customer_label', {'en_US': 'Gutter accessories (closeout-hardening pilot)', 'fa_IR': 'متعلقات آبرو'})
L = env['sipanel.scope.recipe.line']
for seq, prod, uom, fam, basis, extra, mode, placement, label in (
        (10, p_bracket, uom_unit, 'count', 'per_scope_qty', {'rate': 2.0}, 'stock_issue', 'own_line', 'Wall bracket'),
        (20, p_labour, uom_hour, 'time', 'fixed', {'fixed_qty': 8.0}, 'labour', 'included_parent', 'Installation')):
    rec = L.create(dict(version_id=v.id, customer_eligible=True, customer_label=label, sequence=seq, product_id=prod.id, uom_id=uom.id, dimension_family=fam,
                        basis=basis, activity_id=act.id, execution_mode=mode, placement=placement, **extra))
    rec.update_field_translations('customer_label', {'en_US': label, 'fa_IR': label})
v.action_release()
partner = env['res.partner'].create({'name': f'{P} Synthetic Customer', 'lang': 'en_US', 'email': False, 'phone': False})
def quotation(tag, owner):
    order = env['sale.order'].create({'partner_id': partner.id, 'client_order_ref': f'{P}-{tag}', 'origin': f'{P}-{tag}'})
    scope = env['sipanel.quote.scope']._create_from_version(order, v, 10.0, uom_m)
    scope.anchor_line_id.write({'price_unit': 2500000.0, 'tax_ids': [(5, 0, 0)]})
    rev = scope.current_revision_id
    for c in rev.component_ids.filtered('separately_billable'):
        if c.sell_price_status == 'missing': c.action_set_manual_sell_price(450000.0)
    rev.action_generate_note(accept=True)
    if owner is not None: order.write({'user_id': owner.id})
    return order, scope, rev
A, sA, rA = quotation('A', sales)                       # the Sales user's own
B, sB, rB = quotation('B', None)                        # the administrator's (inaccessible to the Sales user)
out['ids'].update({'activity': act.id, 'products': {'anchor': p_anchor.id, 'bracket': p_bracket.id, 'labour': p_labour.id}, 'master': sm.id, 'version': v.id, 'customer': partner.id,
                   'order_A': (A.id, A.name, A.user_id.login), 'order_B': (B.id, B.name, B.user_id.login), 'revision_A': rA.id, 'revision_B': rB.id})
env.cr.commit()

def snap(rev):
    rs = rev.sudo(); return (rs.state, rs.sealed_hash, rs.sealed_by_id.id, len(rs.artifact_ids), rs.net_revenue_projection, rs.order_id.state)
# ---- live refused pre-sudo probes on B (each in a savepoint)
probes = []
def probe(label, fn):
    before = snap(rB)
    try:
        with env.cr.savepoint():
            fn(); probes.append((label, 'ALLOWED - UNEXPECTED'))
    except AccessError:
        probes.append((label, 'refused AccessError'))
    except Exception as e:  # noqa
        probes.append((label, f'refused {type(e).__name__}: {str(e)[:80]}'))
    env.invalidate_all()
    probes[-1] = probes[-1] + (('state unchanged' if snap(rB) == before else 'STATE CHANGED'),)
probe('B.with_user(sales).sudo().action_seal()', lambda: rB.with_user(sales).sudo().action_seal())
probe('B order.with_user(sales).sudo().action_quotation_sent()', lambda: B.with_user(sales).sudo().action_quotation_sent())
probe('B.with_user(plain).sudo().action_seal()', lambda: rB.with_user(plain).sudo().action_seal())
probe('B.with_user(sales).sudo() + raw flags', lambda: rB.with_user(sales).sudo().with_context(sipanel_seal_projection_service=True, sipanel_seal_transaction=True).action_seal())
probe('B.with_user(sales).sudo() + guessed token', lambda: rB.with_user(sales).sudo().with_context(sipanel_seal_projection_service=True, sipanel_seal_transaction=True, sipanel_guard_token='guess').action_seal())
probe('B.with_user(sales).sudo() + import_file', lambda: rB.with_user(sales).sudo().with_context(import_file=True).action_seal())
probe('B.with_user(sales).sudo() + genuine seal_transaction flag', lambda: rB.with_user(sales).sudo().with_context(**guard_ctx('sipanel_seal_transaction')).action_seal())
probe('B plain (no sudo) sales action_seal', lambda: rB.with_user(sales).action_seal())
out['stages']['refused_pre_sudo_probes'] = {'probes': probes, 'all_refused_and_unchanged': all('refused' in r and u == 'state unchanged' for _, r, u in probes), 'B_revision_state': rB.state}
env.cr.commit()

# ---- the governed Seal/Send by the plain Sales user on their own order A
try:
    A.with_user(sales).action_quotation_sent(); seal = 'sealed by the Sales user'
except Exception as e:  # noqa
    seal = f'{type(e).__name__}: {str(e)[:200]}'
env.invalidate_all()
ev = env['sipanel.scope.audit.event'].sudo().search([('res_model', '=', rA._name), ('res_id', '=', rA.id), ('action', '=', 'seal')])
out['stages']['seal_send_A'] = {'result': seal, 'order_state': A.state, 'revision_state': rA.state, 'sealed_hash': rA.sealed_hash, 'sealed_by': rA.sealed_by_id.login,
                                'audit_seal_actor': ev.mapped('actor_user_id.login'), 'checksum_valid_now': rA._current_seal_hash() == rA.sealed_hash,
                                'net_revenue_projection_sudo': rA.sudo().net_revenue_projection, 'anchor_subtotal': sA.anchor_line_id.price_subtotal, 'artifacts': rA.artifact_ids.mapped('kind')}
# leakage after the seal
def visible(html):
    raw = html.decode() if isinstance(html, bytes) else html
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', raw, flags=re.S | re.I)))
leaks = []
for f in ('net_revenue_projection', 'margin_amount', 'eligible_cost_total'):
    try:
        with env.cr.savepoint():
            rA.with_user(sales).read([f]); leaks.append((f, 'READABLE - UNEXPECTED'))
    except AccessError:
        leaks.append((f, 'refused'))
report = env.ref('sale.action_report_saleorder')
text = visible(report.with_user(sales)._render_qweb_html(report.report_name, A.ids)[0])
tokens = {t: (t in text) for t in ('net_revenue', 'Net revenue', 'margin_amount', 'Margin', 'eligible_cost', 'unit_cost', 'Cost')}
out['stages']['leakage'] = {'field_reads': leaks, 'pdf_html_tokens': tokens, 'any_leak': any(tokens.values()) or any('UNEXPECTED' in r for _, r in leaks),
                            'portal_binding_keys': sorted(sA.anchor_line_id._sipanel_portal_binding().keys()),
                            'artifact_text_has_cost_tokens': any(t in (a.content_text or '') for a in rA.artifact_ids for t in ('cost', 'margin', 'net_revenue'))}
out['no_release'] = env['sipanel.execution.batch'].sudo().search_count([('order_id', 'in', [A.id, B.id])])
out['counters_after'] = counters()
env.cr.commit()
# ---- cleanup
for o in (A, B):
    if o.state != 'cancel': o.action_cancel()
scopes = env['sipanel.quote.scope'].with_context(active_test=False).search([('order_id', 'in', [A.id, B.id])]); revs = scopes.mapped('revision_ids')
scopes.write({'active': False}); sm.write({'active': False})
for m, dom in (('product.product', [('name', 'like', P)]), ('product.template', [('name', 'like', P)]), ('res.partner', [('name', '=', f'{P} Synthetic Customer')])):
    env[m].with_context(active_test=False).search(dom).write({'active': False})
act.write({'active': False})
sales.write({'active': False}); plain.write({'active': False})
out['cleanup'] = {'orders': [(o.id, o.name, o.state) for o in (A, B)], 'archived': {'quote scopes': scopes.ids, 'master': sm.id, 'version (released, retained)': v.id,
                  'products': env['product.product'].with_context(active_test=False).search([('name', 'like', P)]).ids, 'customer': partner.id, 'activity account': act.id,
                  'users re-archived': [sales.id, plain.id]},
                  'retained': {'revisions': [(r.id, r.state) for r in revs], 'artifacts': revs.mapped('artifact_ids').ids,
                               'audit events (this pilot)': env['sipanel.scope.audit.event'].sudo().search_count([('create_date', '>=', '2026-09-23 05:00:00')])},
                  'active_leftovers': {'orders not cancelled': env['sale.order'].search_count([('client_order_ref', 'like', P), ('state', '!=', 'cancel')]),
                                       'quote scopes': env['sipanel.quote.scope'].search_count([('order_id', 'in', [A.id, B.id])]), 'masters': env['sipanel.scope'].search_count([('code', 'like', P)]),
                                       'products': env['product.product'].search_count([('name', 'like', P)]), 'partners': env['res.partner'].search_count([('name', 'like', P)]),
                                       'analytic accounts': env['account.analytic.account'].sudo().search_count([('name', 'like', P)]), 'users active': env['res.users'].search_count([('login', 'like', 'SIPANEL-STEP2C')]),
                                       'invoices': env['account.move'].search_count([('invoice_origin', 'in', [A.name, B.name])]), 'pickings': env['stock.picking'].search_count([('origin', 'in', [A.name, B.name])])},
                  'technical_contacts_active': env['res.partner'].search([('name', 'like', 'SIPANEL-STEP2C'), ('active', '=', True)]).mapped(lambda p: (p.id, p.name)),
                  'counters_final': counters()}
env.cr.commit()
print('PILOT=' + json.dumps(out, ensure_ascii=False, default=str))
