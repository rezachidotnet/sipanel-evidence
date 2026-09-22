# STEP 2B-HARDENING: regenerate the pilot reconciliation evidence.
#
# The STEP 2B pilot keyed it by `display_name`, and both revisions of one order
# share that name, so one entry silently overwrote the other and only a single
# result survived. The evidence is now a LIST keyed by the immutable revision id.
import json
env = env(user=1, context={'active_test': False})
assert env.cr.dbname == 'sipanel'
TARGETS = [886, 887]
Rev = env['sipanel.quote.scope.revision'].sudo().with_context(active_test=False)
out = {'generated_utc': __import__('datetime').datetime.utcnow().isoformat() + 'Z',
       'source': 'retained STEP 2B pilot records (order cancelled, scopes archived)',
       'keyed_by': 'revision_id', 'revisions': []}
for rid in TARGETS:
    r = Rev.browse(rid)
    if not r.exists():
        out['revisions'].append({'revision_id': rid, 'error': 'record not found'})
        continue
    scope = r.quote_scope_id
    anchor = scope.anchor_line_id
    lines = env['sale.order.line'].sudo().with_context(active_test=False).search([
        ('sipanel_source_revision_id', '=', r.id), ('sipanel_is_generated', '=', True)])
    recon = r.reconciliation_json or {}
    out['revisions'].append({
        'revision_id': r.id,
        'revision_display_name': r.display_name,
        'revision_state': r.state,
        'revision_number': r.revision,
        'quote_scope_id': scope.id,
        'quote_scope_uid': scope.scope_uid,
        'quote_scope_is_optional': scope.is_optional,
        'quote_scope_acceptance_state': scope.acceptance_state,
        'order_id': r.order_id.id,
        'order_name': r.order_id.name,
        'order_state': r.order_id.state,
        'resolved_language': r.resolved_language,
        'sealed_hash': r.sealed_hash,
        'anchor_line_id': anchor.id or None,
        'anchor_amount': r.anchor_amount,
        'separate_amount': r.separate_amount,
        'projected_line_count': r.projected_line_count,
        'reconciliation_ok': r.reconciliation_ok,
        'component_rows': recon.get('rows', []),
        'separately_billable_components': recon.get('separately_billable_components'),
        'projected_sale_lines': [{
            'line_id': l.id,
            'origin_key': l.sipanel_origin_key,
            'component_id': l.sipanel_source_component_id.id,
            'name': l.name,
            'qty': l.product_uom_qty,
            'price_unit': l.price_unit,
            'price_subtotal': l.price_subtotal,
            'invoice_gate': l.sipanel_invoice_gate or '',
            'placement_snapshot': l.sipanel_placement_snapshot,
            'certainty_snapshot': l.sipanel_certainty_snapshot,
            'invoiced': bool(l.invoice_lines),
        } for l in lines.sorted('sequence')],
        'problems': recon.get('problems', []),
    })
ids = [r.get('revision_id') for r in out['revisions']]
out['distinct_revision_records_present'] = len(set(ids)) == len(TARGETS) and not any(
    'error' in r for r in out['revisions'])
out['all_problems_empty'] = all(not r.get('problems') for r in out['revisions'])
print('RECON=' + json.dumps(out, ensure_ascii=False, indent=1, default=str))
