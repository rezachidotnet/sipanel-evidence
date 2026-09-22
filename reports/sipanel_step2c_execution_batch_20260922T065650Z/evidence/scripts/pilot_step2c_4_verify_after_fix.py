# STEP 2C live pilot - stage 4: post-fix verification on FRESH synthetic orders + amendment/cancellation lineage.
import json, threading, traceback
from odoo import api
from odoo.exceptions import UserError
TS = '20260922T065650Z'
P = f'SIPANEL-STEP2C-{TS}'
env = env(user=2, context={'lang': 'en_US', 'tz': 'Asia/Tehran', 'allowed_company_ids': [1]})
assert env.cr.dbname == 'sipanel'
setup = json.load(open('/tmp/stage1_setup.json'))
ids = setup['ids']
exec_user = env['res.users'].browse(ids['exec_user'])
project = env['project.project'].browse(ids['project'])
system = env['account.analytic.account'].browse(ids['system'])
partner = env['res.partner'].browse(ids['customer'])
vA, vB = env['sipanel.scope.version'].browse(ids['version_A']), env['sipanel.scope.version'].browse(ids['version_B'])
uom_m = env.ref('uom.product_uom_meter')
Batch, Demand, Target = env['sipanel.execution.batch'], env['sipanel.execution.demand'], env['sipanel.execution.target']
out = {'ts': TS, 'prefix': P, 'stages': {}, 'new_orders': {}}

def quotation(tag, version, qty=10.0):
    order = env['sale.order'].create({'partner_id': partner.id, 'client_order_ref': f'{P}-{tag}', 'origin': f'{P}-{tag}'})
    scope = env['sipanel.quote.scope']._create_from_version(order, version, qty, uom_m)
    scope.write({'project_id': project.id, 'system_id': system.id})
    scope.anchor_line_id.write({'price_unit': 2500000.0, 'tax_ids': [(5, 0, 0)]})
    rev = scope.current_revision_id
    for c in rev.component_ids.filtered('separately_billable'):
        if c.sell_price_status == 'missing':
            c.action_set_manual_sell_price(450000.0)
    rev.action_generate_note(accept=True)
    order._sipanel_seal_current_revisions(actor='pilot')
    order.action_confirm()
    out['new_orders'][tag] = {'order': order.id, 'name': order.name, 'scope': scope.id, 'accepted_revision': scope.accepted_revision_id.id}
    return order, scope

def evidence(order):
    env.invalidate_all()
    batches = Batch.search([('order_id', '=', order.id)], order='id')
    demands = Demand.search([('order_id', '=', order.id)], order='id')
    gen = env['sale.order.line'].search([('order_id', '=', order.id), ('sipanel_is_generated', '=', True)], order='id')
    return {'order': order.name, 'order_state': order.state,
            'batches': [{'id': b.id, 'state': b.state, 'revision_set_hash': b.revision_set_hash[:16], 'released_by': b.released_by_id.login or None,
                         'error_summary': b.error_summary or None, 'demand_ids': b.demand_ids.ids, 'retry_count': b.retry_count} for b in batches],
            'demands': [{'id': d.id, 'batch': d.batch_id.id, 'component': d.component_id.id, 'revision': d.component_id.revision_id.id,
                         'occurrence_uid': d.component_id.occurrence_uid[:8], 'delta_uid': d.delta_uid, 'mode': d.execution_mode, 'owner': d.owner,
                         'key': d.demand_key[:12], 'qty': d.normalized_qty, 'signed_qty': d.signed_qty, 'state': d.state,
                         'project': d.project_id.id or None, 'system': d.system_id.id or None, 'activity': d.activity_id.id or None,
                         'reversal_of': d.reversal_of_id.id or None, 'reversal_required': d.reversal_required,
                         'targets': [(t.target_model, t.target_res_id, t.link_kind, t.allocated_qty, getattr(t.target_record().exists(), 'state', None)) for t in d.target_ids]}
                        for d in demands],
            'live_keys_unique': len({d.demand_key for d in demands if d.state != 'failed'}) == len([d for d in demands if d.state != 'failed']),
            'generated_lines': [{'id': l.id, 'component': l.sipanel_source_component_id.id, 'revision': l.sipanel_source_revision_id.id, 'qty': l.product_uom_qty,
                                 'state': l.state, 'moves': [(m.id, m.product_uom_qty, m.state) for m in l.move_ids], 'task': l.task_id.id or None,
                                 'invoice_lines': l.invoice_lines.ids} for l in gen],
            'pickings': [(p.id, p.picking_type_id.name, p.state, [(m.product_id.id, m.product_uom_qty, m.state) for m in p.move_ids]) for p in env['stock.picking'].search([('origin', '=', order.name)], order='id')],
            'purchase_orders': [(po.id, po.state, [(l.product_id.id, l.product_qty, l.analytic_distribution) for l in po.order_line]) for po in env['purchase.order'].search([('origin', '=', order.name)], order='id')],
            'mrp_productions': [(mo.id, mo.state, mo.product_qty, mo.project_id.id or None) for mo in env['mrp.production'].search([('origin', '=', order.name)], order='id')],
            'tasks': [(t.id, t.project_id.id, t.sale_line_id.id) for t in env['project.task'].search([('sale_line_id', 'in', order.order_line.ids)])],
            'audit_events': [(e.action, e.res_model, e.res_id) for e in env['sipanel.scope.audit.event'].sudo().search([('res_model', 'in', ('sipanel.execution.batch', 'sale.order')), ('res_id', 'in', batches.ids + [order.id])], order='id') if e.res_model == 'sale.order' and e.res_id == order.id or e.res_model == 'sipanel.execution.batch'],
            'mail_mail_total': env['mail.mail'].sudo().search_count([]), 'posted_account_moves': env['account.move'].sudo().search_count([('state', '=', 'posted')])}

def release(order):
    return Batch.browse(order.with_user(exec_user).action_sipanel_release_execution()['res_id'])

# ---------------------------------------------------------------- C3 partial failure + retry (post-fix) on fresh order A3
A3, sA3 = quotation('A3', vA)
env.cr.commit()
crane_tmpl = env['product.product'].browse(ids['products']['crane']).product_tmpl_id
sellers = env['product.supplierinfo'].search([('product_tmpl_id', '=', crane_tmpl.id)])
seller_vals = [{'partner_id': s.partner_id.id, 'product_tmpl_id': s.product_tmpl_id.id, 'price': s.price, 'min_qty': s.min_qty} for s in sellers]
sellers.unlink(); env.cr.commit()
counts = lambda: {m: env[m].search_count([]) for m in ('purchase.order', 'purchase.order.line', 'mrp.production', 'stock.picking', 'stock.move', 'sipanel.execution.target')}
c0 = counts()
f1 = release(A3)
f2 = release(A3)     # retry while the cause is still present
c1 = counts()
env.cr.commit()
for v in seller_vals:
    env['product.supplierinfo'].create(v)
env.cr.commit()
ok = release(A3)
ok2 = release(A3)
c2 = counts()
out['stages']['C3_A3_partial_failure_retry'] = {
    'failed_batch': (f1.id, f1.state, f1.error_summary, f1.demand_ids.mapped('state')),
    'retry_still_broken': (f2.id, f2.state, f2.error_summary, f2.demand_ids.mapped('state'), 'new batch' if f2.id != f1.id else 'same batch'),
    'global_counts_before': c0, 'global_counts_after_two_failures': c1,
    'retry_after_fix': (ok.id, ok.state, len(ok.demand_ids), ok.demand_ids.mapped('state'), len(ok.demand_ids.mapped('target_ids'))),
    'release_again_after_success': (ok2.id, ok2.id == ok.id),
    'global_counts_after_success': c2, 'evidence': evidence(A3)}
env.cr.commit()

# ---------------------------------------------------------------- C2 real concurrency on fresh order C (two transactions, two cursors)
C, sC = quotation('C', vA)
env.cr.commit()
results, reg = {}, env.registry
def worker(name):
    with reg.cursor() as cr:
        e = api.Environment(cr, exec_user.id, {'lang': 'en_US', 'allowed_company_ids': [1]})
        try:
            b = e['sipanel.execution.batch'].release_for_order(e['sale.order'].browse(C.id))
            cr.commit()
            results[name] = {'ok': True, 'batch': b.id, 'state': b.state, 'retry_count': b.retry_count, 'demands': len(b.demand_ids)}
        except Exception as exc:  # noqa
            cr.rollback()
            results[name] = {'ok': False, 'error': type(exc).__name__, 'message': str(exc)[:300]}
ts = [threading.Thread(target=worker, args=(f't{i}',)) for i in (1, 2)]
[t.start() for t in ts]; [t.join(timeout=600) for t in ts]
env.invalidate_all()
third = release(C)
out['stages']['C2_concurrency_C'] = {'threads': results, 'third_click': (third.id, third.state), 'evidence': evidence(C),
                                     'backoff_ms_param': env['ir.config_parameter'].sudo().get_param('sipanel_scope.release_backoff_ms'),
                                     'retry_count': env['sipanel.config'].release_retry_count()}
env.cr.commit()

# ---------------------------------------------------------------- Scenario B (post-fix) on fresh order B2
B2, sB2 = quotation('B2', vB)
env.cr.commit()
before = evidence(B2)
bb = release(B2)
bb2 = release(B2)
out['stages']['B2_native_after_fix'] = {'before_release': before, 'batch': (bb.id, bb.state), 'release_again_same': bb2.id == bb.id, 'after_release': evidence(B2)}
env.cr.commit()

# ---------------------------------------------------------------- C4 amendment on released orders: A (bridge, batch from stage 2) and B2 (native)
def amend_increase(order, scope, tag):
    rev = scope.accepted_revision_id
    bracket = rev.component_ids.filtered(lambda c: c.placement == 'own_line' and c.product_id.id == ids['products']['bracket'])
    before_lines = evidence(order)['generated_lines']
    res = {'before': {'revision': rev.id, 'bracket': bracket.id, 'qty': bracket.final_qty, 'generated_lines': before_lines}}
    try:
        with env.cr.savepoint():
            new = rev.action_amend()
            b2 = new.component_ids.filtered(lambda c: c.occurrence_uid == bracket.occurrence_uid)
            b2.write({'qty_override': True, 'override_qty': bracket.final_qty + 10.0, 'override_reason': f'{P} site survey'})
            scope.action_accept_change_order(f'{P}-CO-{tag}')
            created = order.with_user(exec_user).action_sipanel_release_amendment_delta()
            again = order.with_user(exec_user).action_sipanel_release_amendment_delta()
            res.update({'result': 'amended', 'new_revision': (new.id, new.state, new.prior_revision_id.id, new.acceptance_reference),
                        'accepted_revision_now': scope.accepted_revision_id.id,
                        'delta_demands': [(d.id, d.signed_qty, d.state, d.owner, d.delta_uid, [(t.target_model, t.target_res_id, t.link_kind, t.allocated_qty) for t in d.target_ids]) for d in created],
                        'delta_again_created': len(again),
                        'occurrence_signed_sum': sum(Demand.search([('component_id.occurrence_uid', '=', bracket.occurrence_uid), ('quote_scope_id', '=', scope.id), ('state', 'not in', ('cancelled', 'failed'))]).mapped('signed_qty')),
                        'reconciliation_problems': scope.accepted_revision_id.reconciliation_json.get('problems'),
                        'prior_revision_artifacts_intact': len(rev.artifact_ids), 'after': evidence(order)})
    except Exception as e:  # noqa
        res.update({'result': 'error', 'error': type(e).__name__, 'message': str(e)[:400], 'trace': traceback.format_exc()[-1200:]})
    return res
A = env['sale.order'].browse(setup['orders']['A']['order']); sA = env['sipanel.quote.scope'].browse(setup['orders']['A']['scope'])
out['stages']['C4_amend_A_bridge'] = amend_increase(A, sA, 'A')
env.cr.commit()
out['stages']['C4_amend_B2_native'] = amend_increase(B2, sB2, 'B2')
env.cr.commit()

# ---------------------------------------------------------------- C4 cancellation lineage on order C (bridge, released, untouched by amendment)
try:
    with env.cr.savepoint():
        Cx = C.with_user(exec_user)
        if Cx.locked:
            Cx.action_unlock()
        Cx.action_cancel()
        out['stages']['C4_cancel_C'] = {'result': 'cancelled', 'after': evidence(C)}
except Exception as e:  # noqa
    out['stages']['C4_cancel_C'] = {'result': 'error', 'error': type(e).__name__, 'message': str(e)[:400]}
env.cr.commit()
# Estimate-to-Actual: projection after amendment on A (measured, rolled back)
try:
    with env.cr.savepoint():
        touched = env['sipanel.actual.projection'].refresh_order(A)
        touched2 = env['sipanel.actual.projection'].refresh_order(A)
        out['stages']['actual_projection_A'] = {'events': [(e.source_model, e.source_res_id, e.component_type, e.layer, e.inclusion, e.amount, e.project_id.id, e.system_id.id, e.activity_id.id,
                                                            [(a.demand_id.id, a.allocation_basis, a.amount) for a in e.allocation_ids]) for e in touched],
                                                'idempotent': set(touched.ids) == set(touched2.ids), 'unique_source_keys': len(set(touched.mapped('source_key'))) == len(touched)}
        raise UserError('MEASURE_ONLY_ROLLBACK')
except UserError as e:
    if 'MEASURE_ONLY_ROLLBACK' not in str(e):
        out['stages']['actual_projection_A'] = {'error': str(e)[:300]}
out['stages']['final_counters'] = {'mail_mail_total': env['mail.mail'].sudo().search_count([]), 'posted_account_moves': env['account.move'].sudo().search_count([('state', '=', 'posted')]),
                                   'done_moves_total': env['stock.move'].sudo().search_count([('state', '=', 'done')]), 'quants_internal_qty': sum(env['stock.quant'].sudo().search([('location_id.usage', '=', 'internal')]).mapped('quantity'))}
env.cr.commit()
json.dump(out['new_orders'], open('/tmp/stage4_orders.json', 'w'))
print('VERIFY=' + json.dumps(out, ensure_ascii=False, default=str))
