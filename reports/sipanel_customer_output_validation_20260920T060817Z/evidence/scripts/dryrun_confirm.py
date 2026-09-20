# DRY RUN of the customer-signature path (action_confirm) — everything rolled back, nothing committed.
import json
from odoo.exceptions import UserError
out = {}
o = env['sale.order'].sudo().browse(312); s2 = env['sipanel.quote.scope'].sudo().browse(218); s1 = env['sipanel.quote.scope'].sudo().browse(217)
out['after_portal'] = {'line558_qty': s2.anchor_line_id.product_uom_qty, 'acceptance_state': s2.acceptance_state, 'acceptance_reference': s2.acceptance_reference,
                       'rev2_state': s2.current_revision_id.state, 'rev2_hash_now_matches_seal': s2.current_revision_id._current_seal_hash() == s2.current_revision_id.sealed_hash,
                       'rev1_hash_now_matches_seal': s1.current_revision_id._current_seal_hash() == s1.current_revision_id.sealed_hash,
                       'order_total': o.amount_total}
A = env['sipanel.scope.audit.event'].sudo()
out['audit_scope2'] = [{'action': a.action, 'revision_ref': a.revision_ref, 'summary': (a.summary or '')[:60], 'after': (a.after_json if 'after_json' in a._fields else getattr(a, 'after', ''))} for a in A.search([('res_model', '=', 'sipanel.quote.scope'), ('res_id', '=', 218)], order='id')]
counts = lambda: {m: env[m].sudo().search_count(d) for m, d in [('stock.picking', [('origin', 'ilike', 'SI-26/312')]), ('mrp.production', [('origin', 'ilike', 'SI-26/312')]), ('account.move', [('invoice_origin', 'ilike', 'SI-26/312')]), ('project.task', [('sale_order_id', '=', 312)]), ('sipanel.execution.demand', [('order_id', '=', 312)]), ('sipanel.execution.batch', [('order_id', '=', 312)]), ('mail.mail', [('model', '=', 'sale.order'), ('res_id', '=', 312)])]}
out['downstream_before'] = counts()
ou = o.with_user(1)  # portal accept path runs sudo (SUPERUSER)
try:
    ou.action_confirm()
    out['confirm_direct'] = 'CONFIRMED (unexpected)'
except UserError as e:
    out['confirm_direct'] = 'UserError: ' + str(e)[:220]
env.cr.rollback()
env.invalidate_all()
# operator re-send (seals a new revision carrying the accepted qty), then customer signature path
if True:
    o.with_user(2)._sipanel_seal_current_revisions(actor='send')
    r2b = s2.current_revision_id
    out['after_resend'] = {'rev2_current': r2b.name, 'state': r2b.state, 'prior': r2b.prior_revision_id.name, 'hash': r2b.sealed_hash[:16], 'scope_qty': r2b.scope_qty, 'acceptance_state': s2.acceptance_state, 'acceptance_reference': s2.acceptance_reference}
    try:
        ou.action_confirm()
        out['confirm_after_resend'] = {'order_state': o.state, 'scope1': (s1.state, s1.accepted_revision_id.name, s1.accepted_revision_id.acceptance_reference, s1.accepted_revision_id.accepted_by_id.name),
                                       'scope2': (s2.state, s2.accepted_revision_id.name, s2.accepted_revision_id.acceptance_reference, s2.accepted_revision_id.accepted_by_id.name, s2.acceptance_reference),
                                       'downstream_after_confirm': counts(),
                                       'audit_accept': [(a.action, a.revision_ref) for a in A.search([('action', '=', 'accept'), ('res_model', '=', 'sipanel.quote.scope.revision'), ('res_id', 'in', [s1.accepted_revision_id.id, s2.accepted_revision_id.id])])]}
    except UserError as e:
        out['confirm_after_resend'] = 'UserError: ' + str(e)[:220]
    env.cr.rollback()
    env.invalidate_all()
out['after_rollback'] = {'order_state': o.state, 'scope2_current': s2.current_revision_id.name, 'scope2_state': s2.state, 'downstream': counts(), 'revisions_of_scope2': s2.revision_ids.mapped('name')}
print('DRYRUN_CONFIRM=' + json.dumps(out, ensure_ascii=False, default=str))
