# STEP 2C-HARDENING minimal live pilot on `sipanel`. Synthetic records only (prefix SIPANEL-STEP2CH-<TS>).
# One Bridge Owner order (created by a synthetic Sales user), one Native Owner order; release; provenance
# spoof probes; one amendment; cancellation by the Sales user; repeated cancellation; native boundary; duplicates.
import json, traceback
from odoo.tests.common import new_test_user
from odoo.exceptions import AccessError, UserError
from odoo.addons.sipanel_commercial_scope_core.models.sipanel_tools import guard_ctx
from odoo.addons.sipanel_scope_execution.models.execution_demand import DEMAND_ENGINE_GUARD, DEMAND_IMMUTABLE_FIELDS
TS = '20260922T083014Z'
P = f'SIPANEL-STEP2CH-{TS}'
env = env(user=2, context={'lang': 'en_US', 'tz': 'Asia/Tehran', 'allowed_company_ids': [1]})
assert env.cr.dbname == 'sipanel'
ICP = env['ir.config_parameter'].sudo()
out = {'ts': TS, 'prefix': P, 'ids': {}, 'stages': {}}
counters = lambda: {'mail_mail': env['mail.mail'].sudo().search_count([]), 'posted_moves': env['account.move'].sudo().search_count([('state', '=', 'posted')]),
                    'done_stock_moves': env['stock.move'].sudo().search_count([('state', '=', 'done')]), 'purchase_orders': env['purchase.order'].sudo().search_count([]),
                    'mrp': env['mrp.production'].sudo().search_count([]), 'pickings': env['stock.picking'].sudo().search_count([]),
                    'internal_quant_qty': sum(env['stock.quant'].sudo().search([('location_id.usage', '=', 'internal')]).mapped('quantity'))}
out['counters_before'] = counters()
uom_m, uom_unit, uom_hour = env.ref('uom.product_uom_meter'), env.ref('uom.product_uom_unit'), env.ref('uom.product_uom_hour')

# --- dimensions, project, users
plan_sys = env['account.analytic.plan'].sudo().browse(int(ICP.get_param('sipanel_scope.system_plan_id')))
plan_act = env['account.analytic.plan'].sudo().browse(int(ICP.get_param('sipanel_scope.activity_plan_id')))
AA = env['account.analytic.account'].sudo()
system = AA.create({'name': f'{P} System', 'plan_id': plan_sys.id}); act = AA.create({'name': f'{P} Activity', 'plan_id': plan_act.id})
project = env['project.project'].create({'name': f'{P} Project'})
# the STEP 2C synthetic execution owner is re-activated for this pilot (no second technical contact) and re-archived at cleanup
exec_user = env['res.users'].with_context(active_test=False).search([('login', '=', 'SIPANEL-STEP2C-20260922T065650Z-exec')])
assert exec_user, 'STEP 2C synthetic owner expected'
exec_user.write({'active': True})
sales = new_test_user(env, login=f'{P}-sales', name=f'{P} Sales User', email=False, password=False,
                      groups='sales_team.group_sale_salesman,sipanel_sale_scope.group_scope_sales,sipanel_commercial_scope_core.group_scope_estimator')
out['ids'].update({'system': system.id, 'activity': act.id, 'project': project.id, 'exec_user': exec_user.id, 'sales_user': sales.id,
                   'exec_is_owner': exec_user.has_group('sipanel_scope_execution.group_scope_execution_owner'),
                   'sales_is_owner': sales.has_group('sipanel_scope_execution.group_scope_execution_owner')})

# --- products and masters (no vendor, no BoM: no supplier commitment, no MO)
Product = env['product.product']
def mk(tag, uom, price, cost, ptype='consu', **extra):
    vals = {'name': f'{P} {tag}', 'type': ptype, 'uom_id': uom.id, 'list_price': price, 'standard_price': cost, 'sale_ok': True, 'purchase_ok': False, 'invoice_policy': 'order'}
    if ptype == 'consu':
        vals['is_storable'] = True
    vals.update(extra); return Product.create(vals)
pA = mk('A anchor (bridge)', uom_m, 0.0, 0.0, 'service', service_tracking='no')
pB = mk('B anchor (native task)', uom_m, 0.0, 0.0, 'service', service_tracking='task_global_project', project_id=project.id)
p_bracket = mk('Wall bracket', uom_unit, 450000.0, 90000.0)
p_labour = mk('Installation labour', uom_hour, 0.0, 300000.0, 'service', service_tracking='no')
out['ids']['products'] = {'A_anchor': pA.id, 'B_anchor': pB.id, 'bracket': p_bracket.id, 'labour': p_labour.id}
def master(tag, anchor, owner_mode, mode_bracket, mode_labour):
    sm = env['sipanel.scope'].create({'code': f'{P}-{tag}', 'name': f'{P} {tag} master', 'owner_user_id': env.uid})
    v = env['sipanel.scope.version'].create({'scope_id': sm.id, 'customer_label': f'{tag} gutter accessories', 'base_uom_id': uom_m.id, 'dimension_family': 'length',
                                             'anchor_product_id': anchor.id, 'anchor_owner_mode': owner_mode, 'all_systems': True})
    v.update_field_translations('customer_label', {'en_US': f'{tag} gutter accessories', 'fa_IR': f'متعلقات آبرو {tag}'})
    L = env['sipanel.scope.recipe.line']
    for seq, prod, uom, fam, basis, extra, mode, placement, label in (
            (10, p_bracket, uom_unit, 'count', 'per_scope_qty', {'rate': 2.0}, mode_bracket, 'own_line', 'Wall bracket'),
            (20, p_labour, uom_hour, 'time', 'fixed', {'fixed_qty': 8.0}, mode_labour, 'included_parent', 'Installation')):
        rec = L.create(dict(version_id=v.id, customer_eligible=True, customer_label=label, sequence=seq, product_id=prod.id, uom_id=uom.id, dimension_family=fam,
                            basis=basis, activity_id=act.id, execution_mode=mode, placement=placement, **extra))
        rec.update_field_translations('customer_label', {'en_US': label, 'fa_IR': label})
    v.action_release(); return sm, v
smA, vA = master('A', pA, 'component_bridge_owner', 'stock_issue', 'labour')
smB, vB = master('B', pB, 'native_line_owner', 'native_anchor_covered', 'native_anchor_covered')
out['ids'].update({'master_A': smA.id, 'version_A': vA.id, 'master_B': smB.id, 'version_B': vB.id})
partner = env['res.partner'].create({'name': f'{P} Synthetic Customer', 'lang': 'en_US', 'email': False, 'phone': False})
out['ids']['customer'] = partner.id

def quotation(tag, version, user):
    e = env(user=user.id)
    order = e['sale.order'].create({'partner_id': partner.id, 'client_order_ref': f'{P}-{tag}', 'origin': f'{P}-{tag}'})
    scope = e['sipanel.quote.scope']._create_from_version(order, version, 10.0, uom_m)
    scope.write({'project_id': project.id, 'system_id': system.id})
    scope.anchor_line_id.write({'price_unit': 2500000.0, 'tax_ids': [(5, 0, 0)]})
    rev = scope.current_revision_id
    for c in rev.component_ids.filtered('separately_billable'):
        if c.sell_price_status == 'missing':
            c.action_set_manual_sell_price(450000.0)
    rev.action_generate_note(accept=True)
    order._sipanel_seal_current_revisions(actor='pilot')
    order.action_confirm()
    return env['sale.order'].browse(order.id), env['sipanel.quote.scope'].browse(scope.id)
A, sA = quotation('A', vA, env['res.users'].browse(2))
A.write({'user_id': sales.id})         # the Sales user's own document (sealing needs cost-viewer fields: OBS-2CH-01)
B, sB = quotation('B', vB, env['res.users'].browse(2))
out['ids'].update({'order_A': (A.id, A.name, A.user_id.login), 'order_B': (B.id, B.name), 'scope_A': sA.id, 'scope_B': sB.id})

Batch, Demand = env['sipanel.execution.batch'], env['sipanel.execution.demand']
def evidence(order):
    env.invalidate_all()
    batches = Batch.search([('order_id', '=', order.id)], order='id'); demands = Demand.search([('order_id', '=', order.id)], order='id')
    gen = env['sale.order.line'].search([('order_id', '=', order.id), ('sipanel_is_generated', '=', True)], order='id')
    return {'order': order.name, 'state': order.state,
            'batches': [(b.id, b.state, len(b.demand_ids)) for b in batches],
            'demands': [{'id': d.id, 'mode': d.execution_mode, 'owner': d.owner, 'qty': d.signed_qty, 'state': d.state, 'reversal_required': d.reversal_required,
                         'delta_uid': d.delta_uid, 'reversal_of': d.reversal_of_id.id or None, 'key': d.demand_key[:12],
                         'targets': [(t.target_model, t.target_res_id, t.link_kind, getattr(t.target_record().exists(), 'state', None)) for t in d.target_ids]} for d in demands],
            'generated_lines': [(l.id, l.sipanel_source_revision_id.id, l.product_uom_qty, [(m.id, m.product_uom_qty, m.state) for m in l.move_ids]) for l in gen],
            'pickings': [(p.id, p.picking_type_id.name, p.state) for p in env['stock.picking'].search([('origin', '=', order.name)], order='id')],
            'tasks': [(t.id, t.state) for t in env['project.task'].search([('sale_line_id', 'in', order.order_line.ids)])],
            'purchase_orders': env['purchase.order'].search_count([('origin', '=', order.name)]), 'mrp': env['mrp.production'].search_count([('origin', '=', order.name)]),
            'audit': [(e.action, e.res_id, e.actor_user_id.login) for e in env['sipanel.scope.audit.event'].sudo().search(
                [('res_model', '=', 'sipanel.execution.batch'), ('res_id', 'in', batches.ids)], order='id')]}
def release(order):
    return Batch.browse(order.with_user(exec_user).action_sipanel_release_execution()['res_id'])

# --- release both
bA, bB = release(A), release(B)
out['stages']['release'] = {'A': evidence(A), 'B': evidence(B), 'A_again_same': release(A).id == bA.id, 'B_again_same': release(B).id == bB.id}
env.cr.commit()

# --- provenance spoof probes on a live demand (each attempt in a savepoint; stored values compared afterwards)
d = bA.demand_ids.filtered(lambda x: x.execution_mode == 'stock_issue')[:1]
snap = {f: (d[f].id if hasattr(d[f], 'id') else d[f]) for f in DEMAND_IMMUTABLE_FIELDS}; snap['state'] = d.state
probes = []
def probe(label, fn):
    try:
        with env.cr.savepoint():
            fn(); probes.append((label, 'ALLOWED - UNEXPECTED'))
    except AccessError as e:
        probes.append((label, 'refused AccessError'))
    except Exception as e:  # noqa
        probes.append((label, f'refused {type(e).__name__}: {str(e)[:80]}'))
probe('exec owner writes demand_key', lambda: d.with_user(exec_user).write({'demand_key': 'x'}))
probe('exec owner writes state', lambda: d.with_user(exec_user).write({'state': 'cancelled'}))
probe('sudo writes demand_key', lambda: d.sudo().write({'demand_key': 'x'}))
probe('sudo writes state', lambda: d.sudo().write({'state': 'cancelled'}))
probe('raw context flag', lambda: d.with_user(exec_user).with_context(sipanel_demand_engine=True).write({'state': 'cancelled'}))
probe('guessed token', lambda: d.sudo().with_context(sipanel_demand_engine=True, sipanel_guard_token='guess').write({'state': 'cancelled'}))
probe('import context', lambda: d.sudo().with_context(import_file=True).write({'state': 'cancelled'}))
probe('engine token but immutable field', lambda: d.sudo().with_context(**guard_ctx(DEMAND_ENGINE_GUARD)).write({'signed_qty': 99.0}))
for f in DEMAND_IMMUTABLE_FIELDS:
    probe(f'same-value write of {f}', lambda f=f: d.with_user(exec_user).write({f: snap[f]}))
vals = Demand._prepare_from_component(bA, d.component_id, sA, 'forged:1')
n = Demand.search_count([])
probe('forged create (exec owner)', lambda: Demand.with_user(exec_user).create(dict(vals)))
probe('forged create (sudo + raw flag)', lambda: Demand.sudo().with_context(sipanel_demand_engine=True).create(dict(vals)))
probe('forged create (import)', lambda: Demand.sudo().with_context(import_file=True).create(dict(vals)))
probe('unlink (sudo)', lambda: d.sudo().unlink())
probe('sales user writes demand', lambda: d.with_user(sales).write({'state': 'cancelled'}))
probe('sales user cancels B batch via RPC-equivalent call', lambda: bB.with_user(sales).action_cancel_planned())
probe('sales user cancels B batch with forged engine context', lambda: bB.with_user(sales).with_context(**guard_ctx(DEMAND_ENGINE_GUARD)).action_cancel_planned())
probe('sales user cancels order B (not theirs)', lambda: B.with_user(sales).action_cancel())
env.invalidate_all()
after = {f: (d[f].id if hasattr(d[f], 'id') else d[f]) for f in DEMAND_IMMUTABLE_FIELDS}; after['state'] = d.state
out['stages']['provenance_probes'] = {'probes': probes, 'all_refused': all('refused' in r for _, r in probes), 'stored_values_unchanged': after == snap,
                                      'demand_count_unchanged': Demand.search_count([]) == n, 'B_batch_state': bB.state}
env.cr.commit()

# --- one amendment on A (+10 bracket) through the engine
rev = sA.accepted_revision_id
bracket = rev.component_ids.filtered(lambda c: c.placement == 'own_line')
new = rev.action_amend()
b2 = new.component_ids.filtered(lambda c: c.occurrence_uid == bracket.occurrence_uid)
b2.write({'qty_override': True, 'override_qty': bracket.final_qty + 10.0, 'override_reason': f'{P} survey'})
sA.action_accept_change_order(f'{P}-CO-A')
delta = A.with_user(exec_user).action_sipanel_release_amendment_delta()
again = A.with_user(exec_user).action_sipanel_release_amendment_delta()
out['stages']['amendment_A'] = {'new_revision': (new.id, new.state), 'delta': [(x.id, x.signed_qty, x.state, x.delta_uid, [(t.target_model, t.target_res_id) for t in x.target_ids]) for x in delta],
                                'delta_again': len(again), 'evidence': evidence(A)}
env.cr.commit()

# --- cancellation of A by the Sales user (authorised: their own order), then repeated cancellation
docs_before = {'pickings': env['stock.picking'].search_count([('origin', '=', A.name)]), 'moves': env['stock.move'].search_count([('origin', '=', A.name)])}
try:
    Ax = A.with_user(sales)
    if Ax.locked:
        Ax.action_unlock()
    Ax.action_cancel()
    res = 'cancelled by sales user'
except Exception as e:  # noqa
    res = f'{type(e).__name__}: {str(e)[:200]}'
env.invalidate_all()
ev1 = evidence(A)
# repeated cancellation: batch action twice more (exec owner) and the order again (sales user)
for b in Batch.search([('order_id', '=', A.id)]):
    b.with_user(exec_user).action_cancel_planned(); b.with_user(exec_user).action_cancel_planned()
A.with_user(sales).action_cancel()
ev2 = evidence(A)
out['stages']['cancel_A_by_sales'] = {'result': res, 'after_first': ev1, 'after_repeats_identical': ev1 == ev2, 'after_repeats': ev2,
                                      'docs_created_by_cancel': {'pickings': env['stock.picking'].search_count([('origin', '=', A.name)]) - docs_before['pickings'],
                                                                 'moves': env['stock.move'].search_count([('origin', '=', A.name)]) - docs_before['moves']},
                                      'sales_demand_access': {'write': Demand.with_user(sales).has_access('write'), 'create': Demand.with_user(sales).has_access('create'), 'unlink': Demand.with_user(sales).has_access('unlink')}}
env.cr.commit()

# --- native boundary on B: batch cancellation must not touch the native delivery move / task
genB = env['sale.order.line'].search([('order_id', '=', B.id), ('sipanel_is_generated', '=', True)])
mv = genB.move_ids; task = sB.anchor_line_id.task_id
before = (mv.state, mv.product_uom_qty, task.exists() and task.state)
bB.with_user(exec_user).action_cancel_planned(); bB.with_user(exec_user).action_cancel_planned()
env.invalidate_all()
after_batch = (mv.state, mv.product_uom_qty, task.exists() and task.state)
Bx = B.with_user(exec_user)
if Bx.locked:
    Bx.action_unlock()
Bx.action_cancel()
env.invalidate_all()
out['stages']['native_boundary_B'] = {'native_move_before': before, 'native_move_after_batch_cancel': after_batch, 'untouched_by_sipanel': before == after_batch,
                                      'after_order_cancel_by_odoo': (mv.state, mv.product_uom_qty), 'evidence': evidence(B)}
env.cr.commit()
out['counters_after'] = counters()
out['duplicates'] = {'purchase_orders_for_pilot': env['purchase.order'].search_count([('origin', 'in', [A.name, B.name])]), 'mrp_for_pilot': env['mrp.production'].search_count([('origin', 'in', [A.name, B.name])]),
                     'sipanel_pickings_A': [(p.id, p.state) for p in env['stock.picking'].search([('origin', '=', A.name)])],
                     'native_moves_from_bridge_generated_lines': env['stock.move'].search_count([('sale_line_id', 'in', env['sale.order.line'].search([('order_id', '=', A.id), ('sipanel_is_generated', '=', True)]).ids)]),
                     'live_demand_keys_unique': len({x.demand_key for x in Demand.search([('order_id', 'in', [A.id, B.id]), ('state', '!=', 'failed')])}) == Demand.search_count([('order_id', 'in', [A.id, B.id]), ('state', '!=', 'failed')])}
env.cr.commit()
print('PILOT=' + json.dumps(out, ensure_ascii=False, default=str))
