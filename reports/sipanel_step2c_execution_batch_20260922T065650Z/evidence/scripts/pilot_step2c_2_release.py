# STEP 2C live pilot - stage 2: release, idempotency, concurrency, partial failure and retry.
import json, threading, traceback
import odoo
from odoo import api
from odoo.exceptions import UserError
TS = '20260922T065650Z'
P = f'SIPANEL-STEP2C-{TS}'
env = env(user=2, context={'lang': 'en_US', 'tz': 'Asia/Tehran', 'allowed_company_ids': [1]})
assert env.cr.dbname == 'sipanel'
setup = json.load(open('/tmp/stage1_setup.json'))
ids = setup['ids']
exec_user = env['res.users'].browse(ids['exec_user'])
out = {'ts': TS, 'prefix': P, 'stages': {}}
Batch, Demand, Target = env['sipanel.execution.batch'], env['sipanel.execution.demand'], env['sipanel.execution.target']

def order_of(tag):
    return env['sale.order'].browse(setup['orders'][tag]['order'])

def evidence(order):
    env.invalidate_all()
    batches = Batch.search([('order_id', '=', order.id)], order='id')
    demands = Demand.search([('order_id', '=', order.id)], order='id')
    gen = order.order_line.filtered('sipanel_is_generated')
    ev = {'order': order.name, 'order_state': order.state,
          'batches': [{'id': b.id, 'name': b.name, 'state': b.state, 'action_uid': b.action_uid, 'revision_set_hash': b.revision_set_hash,
                       'retry_count': b.retry_count, 'released_by': b.released_by_id.login or None, 'error_summary': b.error_summary or None,
                       'demand_ids': b.demand_ids.ids, 'accepted_revisions': b.accepted_revision_ids.ids} for b in batches],
          'demands': [{'id': d.id, 'batch': d.batch_id.id, 'component': d.component_id.id, 'component_name': d.component_id.name[-24:],
                       'occurrence_uid': d.component_id.occurrence_uid, 'revision': d.component_id.revision_id.id,
                       'quote_scope': d.quote_scope_id.id, 'delta_uid': d.delta_uid, 'mode': d.execution_mode, 'owner': d.owner,
                       'demand_key': d.demand_key, 'qty': d.normalized_qty, 'signed_qty': d.signed_qty, 'uom': d.uom_id.name, 'state': d.state,
                       'project': d.project_id.id or None, 'system': d.system_id.id or None, 'activity': d.activity_id.id or None,
                       'reversal_of': d.reversal_of_id.id or None, 'reversal_required': d.reversal_required,
                       'targets': [{'id': t.id, 'model': t.target_model, 'res_id': t.target_res_id, 'link_kind': t.link_kind,
                                    'qty': t.allocated_qty, 'display': t.target_display, 'reference': t.stock_reference_id.name or None,
                                    'state': getattr(t.target_record().exists(), 'state', None)} for t in d.target_ids]}
                      for d in demands],
          'unique_demand_keys': len(set(demands.mapped('demand_key'))), 'demand_count': len(demands),
          'generated_lines': [{'id': l.id, 'component': l.sipanel_source_component_id.id, 'qty': l.product_uom_qty,
                               'moves': l.move_ids.ids, 'move_states': l.move_ids.mapped('state'), 'purchase_lines': l.purchase_line_ids.ids,
                               'task': l.task_id.id or None} for l in gen],
          'stock_moves_from_generated_lines': env['stock.move'].search_count([('sale_line_id', 'in', gen.ids)]),
          'pickings': [(p.id, p.picking_type_id.name, p.state, p.move_ids.mapped(lambda m: (m.product_id.id, m.product_uom_qty, m.state)))
                       for p in env['stock.picking'].search([('origin', '=', order.name)], order='id')],
          'purchase_orders': [(po.id, po.name, po.state, po.partner_id.id, [(l.product_id.id, l.product_qty, l.analytic_distribution) for l in po.order_line])
                              for po in env['purchase.order'].search([('origin', '=', order.name)], order='id')],
          'mrp_productions': [(mo.id, mo.name, mo.state, mo.product_id.id, mo.product_qty, mo.project_id.id or None)
                              for mo in env['mrp.production'].search([('origin', '=', order.name)], order='id')],
          'tasks': [(t.id, t.project_id.id, t.sale_line_id.id) for t in env['project.task'].search([('sale_line_id', 'in', order.order_line.ids)])],
          'analytic_lines_project': env['account.analytic.line'].sudo().search_count([('account_id', '=', env['project.project'].browse(ids['project']).account_id.id)]) if env['project.project'].browse(ids['project']).account_id else None,
          'stock_references': order.stock_reference_ids.mapped('name') if 'stock_reference_ids' in order._fields else None,
          'audit_events': [(e.action, e.res_model, e.res_id, e.correlation_uid) for e in env['sipanel.scope.audit.event'].sudo().search(
              [('res_model', '=', 'sipanel.execution.batch'), ('res_id', 'in', batches.ids)], order='id')],
          'mail_mail_total': env['mail.mail'].sudo().search_count([]), 'posted_account_moves': env['account.move'].sudo().search_count([('state', '=', 'posted')])}
    return ev

def release(order, user=None):
    res = order.with_user(user or exec_user).action_sipanel_release_execution()
    return Batch.browse(res['res_id'])

# ---------------------------------------------------------------- C2 concurrency on B (before anything touches B)
env.cr.commit()
B = order_of('B')
results = {}
def worker(name):
    reg = odoo.registry('sipanel')
    with reg.cursor() as cr:
        e = api.Environment(cr, exec_user.id, {'lang': 'en_US', 'allowed_company_ids': [1]})
        try:
            b = e['sipanel.execution.batch'].release_for_order(e['sale.order'].browse(B.id))
            cr.commit()
            results[name] = {'ok': True, 'batch': b.id, 'state': b.state, 'retry_count': b.retry_count}
        except Exception as exc:  # noqa
            cr.rollback()
            results[name] = {'ok': False, 'error': type(exc).__name__, 'message': str(exc)[:300]}
ts = [threading.Thread(target=worker, args=(f't{i}',)) for i in (1, 2)]
[t.start() for t in ts]; [t.join(timeout=300) for t in ts]
env.invalidate_all()
after_threads = evidence(B)
b_again = release(B)                      # a third click after the winner committed
out['stages']['C2_concurrency_B'] = {'threads': results, 'batches_after_threads': [(b['id'], b['state']) for b in after_threads['batches']],
                                     'third_click_batch': b_again.id, 'third_click_state': b_again.state,
                                     'backoff_ms_param': env['ir.config_parameter'].sudo().get_param('sipanel_scope.release_backoff_ms'),
                                     'retry_count_param': env['sipanel.config'].release_retry_count()}
out['stages']['B_after_release'] = evidence(B)
env.cr.commit()

# ---------------------------------------------------------------- Scenario A: release once / twice / retry after completion
A = order_of('A')
with env.cr.savepoint():
    try:
        A.with_user(2).action_sipanel_release_execution()
        out['stages']['A_release_by_non_owner'] = 'UNEXPECTED: allowed'
    except UserError as e:
        out['stages']['A_release_by_non_owner'] = f'refused: {str(e)[:120]}'
        raise  # roll back the savepoint
    except Exception:
        pass
b1 = release(A)
out['stages']['A_release_1'] = evidence(A)
b2 = release(A)
b3 = Batch.with_user(exec_user).release_for_order(A)
b4 = release(A)
out['stages']['A_release_2_3_4'] = {'batch_ids': [b1.id, b2.id, b3.id, b4.id], 'same': len({b1.id, b2.id, b3.id, b4.id}) == 1,
                                    'evidence_after': evidence(A)}
env.cr.commit()

# ---------------------------------------------------------------- C3 partial failure on A2: remove the vendor => BUY_DIRECT adapter fails
A2 = order_of('A2')
seller = env['product.supplierinfo'].browse(ids['supplierinfo'])
seller_vals = {'partner_id': seller.partner_id.id, 'product_tmpl_id': seller.product_tmpl_id.id, 'price': seller.price, 'min_qty': seller.min_qty}
seller.unlink()
env.cr.commit()
counts_before = {m: env[m].search_count([]) for m in ('purchase.order', 'purchase.order.line', 'mrp.production', 'stock.picking', 'stock.move', 'sipanel.execution.target')}
fb = release(A2)
env.invalidate_all()
counts_after = {m: env[m].search_count([]) for m in ('purchase.order', 'purchase.order.line', 'mrp.production', 'stock.picking', 'stock.move', 'sipanel.execution.target')}
out['stages']['A2_failed_release'] = {'batch': fb.id, 'state': fb.state, 'error_summary': fb.error_summary, 'demand_states': fb.demand_ids.mapped('state'),
                                      'demand_keys': fb.demand_ids.mapped('demand_key'), 'targets': len(fb.demand_ids.mapped('target_ids')),
                                      'global_counts_before': counts_before, 'global_counts_after': counts_after,
                                      'evidence': evidence(A2)}
env.cr.commit()
# retry the failed release without fixing => same failure or new batch?
fb2 = release(A2)
out['stages']['A2_retry_still_broken'] = {'batch': fb2.id, 'state': fb2.state, 'same_as_first': fb2.id == fb.id, 'error_summary': fb2.error_summary,
                                          'demand_count': len(fb2.demand_ids), 'batches_now': Batch.search_count([('order_id', '=', A2.id)])}
env.cr.commit()
# fix the cause and retry
new_seller = env['product.supplierinfo'].create(seller_vals)
ids['supplierinfo'] = new_seller.id
env.cr.commit()
rb = release(A2)
env.invalidate_all()
out['stages']['A2_retry_after_fix'] = {'batch': rb.id, 'state': rb.state, 'new_batch': rb.id != fb.id, 'demand_count': len(rb.demand_ids),
                                       'demand_states': rb.demand_ids.mapped('state'), 'target_count': len(rb.demand_ids.mapped('target_ids')),
                                       'evidence': evidence(A2)}
env.cr.commit()
json.dump(ids, open('/tmp/stage2_ids.json', 'w'))
print('RELEASE=' + json.dumps(out, ensure_ascii=False, default=str))
