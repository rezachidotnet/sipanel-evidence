# STEP 2C live pilot - stage 3a: MEASURE amendment on a confirmed+released order (A) and the actual-cost projection. No fixes yet.
import json, traceback
from odoo.exceptions import UserError
TS = '20260922T065650Z'
env = env(user=2, context={'lang': 'en_US', 'tz': 'Asia/Tehran', 'allowed_company_ids': [1]})
assert env.cr.dbname == 'sipanel'
setup = json.load(open('/tmp/stage1_setup.json'))
out = {'ts': TS, 'stages': {}}
A = env['sale.order'].browse(setup['orders']['A']['order'])
scope = env['sipanel.quote.scope'].browse(setup['orders']['A']['scope'])
rev = scope.accepted_revision_id
bracket = rev.component_ids.filtered(lambda c: c.placement == 'own_line' and c.execution_mode == 'stock_issue')
gen_before = env['sale.order.line'].search([('order_id', '=', A.id), ('sipanel_is_generated', '=', True)])
out['stages']['before'] = {'revision': rev.id, 'state': rev.state, 'bracket': bracket.id, 'qty': bracket.final_qty,
                           'generated_lines': [(l.id, l.sipanel_source_revision_id.id, l.product_uom_qty, l.state) for l in gen_before]}
# C4: amendment on a confirmed order that has generated (separately billable) lines
try:
    with env.cr.savepoint():
        new = rev.action_amend()
        out['stages']['amend'] = {'result': 'created', 'new_revision': new.id, 'state': new.state, 'prior': new.prior_revision_id.id,
                                  'generated_lines_after_amend': [(l.id, l.sipanel_source_revision_id.id, l.product_uom_qty, l.state) for l in
                                                                  env['sale.order.line'].search([('order_id', '=', A.id), ('sipanel_is_generated', '=', True)])]}
        raise UserError('MEASURE_ONLY_ROLLBACK')
except UserError as e:
    if 'MEASURE_ONLY_ROLLBACK' not in str(e):
        out['stages']['amend'] = {'result': 'refused', 'error': type(e).__name__, 'message': str(e)[:400]}
except Exception as e:  # noqa
    out['stages']['amend'] = {'result': 'error', 'error': type(e).__name__, 'message': str(e)[:400], 'trace': traceback.format_exc()[-1500:]}
# where does the refusal come from? try the projection retire step in isolation on a copy of the facts
try:
    with env.cr.savepoint():
        line = gen_before[0]
        line.with_context(sipanel_guard_token='x').unlink()
        out['stages']['unlink_generated_line_on_confirmed_order'] = 'allowed'
        raise UserError('MEASURE_ONLY_ROLLBACK')
except UserError as e:
    if 'MEASURE_ONLY_ROLLBACK' not in str(e):
        out['stages']['unlink_generated_line_on_confirmed_order'] = f'refused: {str(e)[:200]}'
except Exception as e:  # noqa
    out['stages']['unlink_generated_line_on_confirmed_order'] = f'{type(e).__name__}: {str(e)[:200]}'
# Estimate-to-Actual lineage: what the costing projection sees for A and B (measured, then rolled back)
res = {}
for tag in ('A', 'B'):
    order = env['sale.order'].browse(setup['orders'][tag]['order'])
    try:
        with env.cr.savepoint():
            touched = env['sipanel.actual.projection'].refresh_order(order)
            res[tag] = {'events': [{'source': (e.source_model, e.source_res_id), 'type': e.component_type, 'layer': e.layer, 'inclusion': e.inclusion,
                                    'amount': e.amount, 'qty': e.qty, 'project': e.project_id.id or None, 'system': e.system_id.id or None,
                                    'activity': e.activity_id.id or None,
                                    'allocations': [(a.demand_id.id or None, a.component_id.id or None, a.allocation_basis, a.amount) for a in e.allocation_ids]}
                                   for e in touched],
                        'policies_approved': env['sipanel.cost.recognition.policy'].sudo().search_count([('state', '=', 'approved')]) if 'state' in env['sipanel.cost.recognition.policy']._fields else None}
            raise UserError('MEASURE_ONLY_ROLLBACK')
    except UserError as e:
        if 'MEASURE_ONLY_ROLLBACK' not in str(e):
            res[tag] = {'error': str(e)[:300]}
    except Exception as e:  # noqa
        res[tag] = {'error': f'{type(e).__name__}: {str(e)[:300]}'}
out['stages']['actual_cost_projection'] = res
out['stages']['policy_fields'] = list(env['sipanel.cost.recognition.policy']._fields.keys())[:40]
env.cr.rollback()
print('MEASURE=' + json.dumps(out, ensure_ascii=False, default=str, indent=1))
