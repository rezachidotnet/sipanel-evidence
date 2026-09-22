# STEP 2C-CLOSEOUT minimal live pilot: a plain Sales user seals/sends their own synthetic quotation.
# Synthetic records only (prefix SIPANEL-STEP2CCO-<TS>); no release, no invoice, no email; cleanup at the end.
import json, re
from odoo.exceptions import AccessError, UserError
from odoo.addons.sipanel_commercial_scope_core.models.sipanel_tools import guard_ctx
from odoo.addons.sipanel_sale_scope.models.quote_scope_revision import SEAL_SERVICE_GUARD, SEAL_PROJECTION_FIELDS
TS = '20260922T105454Z'
P = f'SIPANEL-STEP2CCO-{TS}'
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
# the STEP 2C-HARDENING synthetic Sales user is re-activated (no new technical contact) and re-archived at the end
sales = env['res.users'].with_context(active_test=False).search([('login', '=', 'SIPANEL-STEP2CH-20260922T083014Z-sales')])
assert sales, 'synthetic Sales user expected'
sales.write({'active': True})
# make it a PLAIN Sales user: only internal user + Salesperson + SIPANEL Scope Sales (the STEP 2C-HARDENING pilot
# had also given it the Estimator group, which implies cost visibility)
sales.write({'group_ids': [(6, 0, [env.ref('base.group_user').id, env.ref('sales_team.group_sale_salesman').id, env.ref('sipanel_sale_scope.group_scope_sales').id])]})
env.cr.flush(); env.invalidate_all()
out['ids']['sales_user_groups'] = sorted(sales.group_ids.mapped('full_name'))
COST_GROUPS = ('sipanel_commercial_scope_core.group_scope_cost_viewer', 'sipanel_sale_scope.group_scope_waiver_finance',
               'sipanel_scope_execution.group_scope_execution_owner', 'account.group_account_manager', 'sales_team.group_sale_manager')
out['ids']['sales_user'] = (sales.id, sales.login, {g: sales.has_group(g) for g in COST_GROUPS})
assert not any(sales.has_group(g) for g in COST_GROUPS)
Product = env['product.product']
def mk(tag, uom, price, cost, ptype='consu', **extra):
    vals = {'name': f'{P} {tag}', 'type': ptype, 'uom_id': uom.id, 'list_price': price, 'standard_price': cost, 'sale_ok': True, 'purchase_ok': False, 'invoice_policy': 'order'}
    if ptype == 'consu':
        vals['is_storable'] = True
    vals.update(extra); return Product.create(vals)
p_anchor = mk('anchor (bridge)', uom_m, 0.0, 0.0, 'service', service_tracking='no')
p_bracket = mk('Wall bracket', uom_unit, 450000.0, 90000.0)
p_labour = mk('Installation labour', uom_hour, 0.0, 300000.0, 'service', service_tracking='no')
sm = env['sipanel.scope'].create({'code': f'{P}-A', 'name': f'{P} master', 'owner_user_id': env.uid})
v = env['sipanel.scope.version'].create({'scope_id': sm.id, 'customer_label': 'Gutter accessories (closeout pilot)', 'base_uom_id': uom_m.id, 'dimension_family': 'length',
                                         'anchor_product_id': p_anchor.id, 'anchor_owner_mode': 'component_bridge_owner', 'all_systems': True})
v.update_field_translations('customer_label', {'en_US': 'Gutter accessories (closeout pilot)', 'fa_IR': 'متعلقات آبرو'})
L = env['sipanel.scope.recipe.line']
for seq, prod, uom, fam, basis, extra, mode, placement, label in (
        (10, p_bracket, uom_unit, 'count', 'per_scope_qty', {'rate': 2.0}, 'stock_issue', 'own_line', 'Wall bracket'),
        (20, p_labour, uom_hour, 'time', 'fixed', {'fixed_qty': 8.0}, 'labour', 'included_parent', 'Installation')):
    rec = L.create(dict(version_id=v.id, customer_eligible=True, customer_label=label, sequence=seq, product_id=prod.id, uom_id=uom.id, dimension_family=fam,
                        basis=basis, activity_id=act.id, execution_mode=mode, placement=placement, **extra))
    rec.update_field_translations('customer_label', {'en_US': label, 'fa_IR': label})
v.action_release()
partner = env['res.partner'].create({'name': f'{P} Synthetic Customer', 'lang': 'en_US', 'email': False, 'phone': False})
out['ids'].update({'activity': act.id, 'products': {'anchor': p_anchor.id, 'bracket': p_bracket.id, 'labour': p_labour.id}, 'master': sm.id, 'version': v.id, 'customer': partner.id})
# quotation prepared by the administrator (adding a Scope writes cost snapshots), owned by the Sales user
order = env['sale.order'].create({'partner_id': partner.id, 'client_order_ref': f'{P}-A', 'origin': f'{P}-A'})
scope = env['sipanel.quote.scope']._create_from_version(order, v, 10.0, uom_m)
scope.anchor_line_id.write({'price_unit': 2500000.0, 'tax_ids': [(5, 0, 0)]})
rev = scope.current_revision_id
for c in rev.component_ids.filtered('separately_billable'):
    if c.sell_price_status == 'missing':
        c.action_set_manual_sell_price(450000.0)
rev.action_generate_note(accept=True)
order.write({'user_id': sales.id})
out['ids'].update({'order': (order.id, order.name), 'scope': scope.id, 'revision': rev.id})
out['stages']['permissions'] = {'sales_can_write_order': order.with_user(sales).has_access('write'), 'sales_can_write_revision': rev.with_user(sales).has_access('write'),
                                'revision_state_before': rev.state}
env.cr.commit()

# ---- the governed Seal/Send by the plain Sales user
try:
    order.with_user(sales).action_quotation_sent()
    seal = 'sealed by the Sales user'
except Exception as e:  # noqa
    seal = f'{type(e).__name__}: {str(e)[:200]}'
env.invalidate_all()
ev = env['sipanel.scope.audit.event'].sudo().search([('res_model', '=', rev._name), ('res_id', '=', rev.id), ('action', '=', 'seal')])
out['stages']['seal_send'] = {'result': seal, 'order_state': order.state, 'revision_state': rev.state, 'sealed_hash': rev.sealed_hash, 'sealed_by': rev.sealed_by_id.login,
                              'audit_seal_actor': ev.mapped('actor_user_id.login'), 'checksum_valid_now': rev._current_seal_hash() == rev.sealed_hash,
                              'net_revenue_projection_sudo': rev.sudo().net_revenue_projection, 'anchor_subtotal': scope.anchor_line_id.price_subtotal,
                              'artifacts': rev.artifact_ids.mapped('kind'), 'groups_after': {g: sales.has_group(g) for g in COST_GROUPS}}
env.cr.commit()

# ---- protected fields and spoof probes (each in a savepoint)
probes = []
def probe(label, fn):
    try:
        with env.cr.savepoint():
            fn(); probes.append((label, 'ALLOWED - UNEXPECTED'))
    except AccessError:
        probes.append((label, 'refused AccessError'))
    except Exception as e:  # noqa
        probes.append((label, f'refused {type(e).__name__}: {str(e)[:80]}'))
before = (rev.sudo().net_revenue_projection, rev.sudo().commercial_projection_json)
probe('sales reads net_revenue_projection', lambda: rev.with_user(sales).read(['net_revenue_projection']))
probe('sales search_read margin_amount', lambda: env['sipanel.quote.scope.revision'].with_user(sales).search_read([('id', '=', rev.id)], ['margin_amount']))
probe('sales export eligible_cost_total', lambda: rev.with_user(sales).export_data(['revision', 'eligible_cost_total']))
probe('sales writes net_revenue_projection', lambda: rev.with_user(sales).write({'net_revenue_projection': 1.0}))
probe('sales writes commercial_projection_json', lambda: rev.with_user(sales).write({'commercial_projection_json': {'price_subtotal': 1.0}}))
probe('sudo writes net_revenue_projection (no guard)', lambda: rev.sudo().write({'net_revenue_projection': 1.0}))
probe('sudo with seal_transaction flag only', lambda: rev.sudo().with_context(**guard_ctx('sipanel_seal_transaction')).write({'net_revenue_projection': 1.0}))
probe('raw context flags', lambda: rev.sudo().with_context(sipanel_seal_projection_service=True, sipanel_seal_transaction=True).write({'net_revenue_projection': 1.0}))
probe('guessed token', lambda: rev.sudo().with_context(sipanel_seal_projection_service=True, sipanel_seal_transaction=True, sipanel_guard_token='guess').write({'net_revenue_projection': 1.0}))
probe('import context', lambda: rev.sudo().with_context(import_file=True).write({'net_revenue_projection': 1.0}))
for f in SEAL_PROJECTION_FIELDS:
    probe(f'sudo same-value write of {f}', lambda f=f: rev.sudo().write({f: rev.sudo()[f].id if hasattr(rev.sudo()[f], 'id') else rev.sudo()[f]}))
env.invalidate_all()
out['stages']['probes'] = {'probes': probes, 'all_refused': all('refused' in r for _, r in probes),
                           'stored_unchanged': (rev.sudo().net_revenue_projection, rev.sudo().commercial_projection_json) == before,
                           'fields_visible_to_sales': sorted(f for f in rev.with_user(sales).fields_get() if 'cost' in f or 'margin' in f or 'net_revenue' in f)}
# another salesperson's order: the Sales user cannot seal it
other = env['sale.order'].create({'partner_id': partner.id, 'client_order_ref': f'{P}-B', 'origin': f'{P}-B'})
oscope = env['sipanel.quote.scope']._create_from_version(other, v, 10.0, uom_m)
oscope.anchor_line_id.write({'price_unit': 2500000.0, 'tax_ids': [(5, 0, 0)]})
for c in oscope.current_revision_id.component_ids.filtered('separately_billable'):
    if c.sell_price_status == 'missing':
        c.action_set_manual_sell_price(450000.0)
oscope.current_revision_id.action_generate_note(accept=True)
out['ids']['other_order'] = (other.id, other.name, other.user_id.login)
probe('sales seals another salesperson order', lambda: other.with_user(sales).action_quotation_sent())
env.invalidate_all()
out['stages']['other_order'] = {'probe': probes[-1], 'revision_state': oscope.current_revision_id.state}
env.cr.commit()

# ---- customer outputs as the Sales user: no cost / margin / net revenue
def visible(html):
    raw = html.decode() if isinstance(html, bytes) else html
    body = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', raw, flags=re.S | re.I)
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', body))
report = env.ref('sale.action_report_saleorder')
text = visible(report.with_user(sales)._render_qweb_html(report.report_name, order.ids)[0])
cost = rev.sudo().eligible_cost_total; net = rev.sudo().net_revenue_projection
leak = {tok: (tok in text) for tok in ('net_revenue', 'Net revenue', 'margin_amount', 'Margin', 'eligible_cost', 'unit_cost', 'Cost')}
leak['cost figure'] = bool(cost) and (f'{cost:,.2f}' in text or f'{cost:.2f}' in text)
pdf, fmt = env['ir.actions.report'].sudo()._render_qweb_pdf('sale.action_report_saleorder', order.ids)
out['stages']['customer_output'] = {'pdf_format': fmt, 'pdf_bytes': len(pdf), 'html_tokens_found': leak, 'any_leak': any(leak.values()),
                                    'portal_binding_keys': sorted(scope.anchor_line_id._sipanel_portal_binding().keys()),
                                    'artifact_text_has_cost_tokens': any(t in (a.content_text or '') for a in rev.artifact_ids for t in ('cost', 'margin', 'net_revenue'))}
env.cr.commit()
out['counters_after'] = counters()
out['no_release'] = {'batches_for_order': env['sipanel.execution.batch'].sudo().search_count([('order_id', 'in', [order.id, other.id])])}

# ---- cleanup: cancel, archive; keep sealed lineage
for o in (order, other):
    if o.state not in ('cancel',):
        o.action_cancel()
scopes = env['sipanel.quote.scope'].with_context(active_test=False).search([('order_id', 'in', [order.id, other.id])])
revs = scopes.mapped('revision_ids')
scopes.write({'active': False}); sm.write({'active': False})
for m, dom in (('product.product', [('name', 'like', P)]), ('product.template', [('name', 'like', P)]), ('res.partner', [('name', '=', f'{P} Synthetic Customer')])):
    env[m].with_context(active_test=False).search(dom).write({'active': False})
act.write({'active': False})
sales.write({'active': False})
out['cleanup'] = {'orders': [(o.id, o.name, o.state) for o in (order, other)], 'archived': {'quote scopes': scopes.ids, 'master': sm.id, 'version (released, retained)': v.id,
                  'products': env['product.product'].with_context(active_test=False).search([('name', 'like', P)]).ids, 'customer': partner.id, 'activity account': act.id,
                  'sales user re-archived': sales.id},
                  'retained': {'revisions': [(r.id, r.state) for r in revs], 'artifacts': revs.mapped('artifact_ids').ids,
                               'audit events (this pilot)': env['sipanel.scope.audit.event'].sudo().search_count([('create_date', '>=', '2026-09-22 11:20:00')])},
                  'active_leftovers': {'orders not cancelled': env['sale.order'].search_count([('client_order_ref', 'like', P), ('state', '!=', 'cancel')]),
                                       'quote scopes': env['sipanel.quote.scope'].search_count([('order_id', 'in', [order.id, other.id])]),
                                       'masters': env['sipanel.scope'].search_count([('code', 'like', P)]), 'products': env['product.product'].search_count([('name', 'like', P)]),
                                       'partners': env['res.partner'].search_count([('name', 'like', P)]), 'analytic accounts': env['account.analytic.account'].sudo().search_count([('name', 'like', P)]),
                                       'users active': env['res.users'].search_count([('login', 'like', 'SIPANEL-STEP2C')]),
                                       'invoices': env['account.move'].search_count([('invoice_origin', 'in', [order.name, other.name])]),
                                       'pickings': env['stock.picking'].search_count([('origin', 'in', [order.name, other.name])])},
                  'technical_contacts_active': env['res.partner'].search([('name', 'like', 'SIPANEL-STEP2C'), ('active', '=', True)]).mapped(lambda p: (p.id, p.name)),
                  'counters_final': counters()}
env.cr.commit()
print('PILOT=' + json.dumps(out, ensure_ascii=False, default=str))
