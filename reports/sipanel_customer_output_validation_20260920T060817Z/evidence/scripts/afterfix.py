import json
env = env(user=2, context={'lang': 'en_US', 'allowed_company_ids': [1]})
out = {}
o = env['sale.order'].sudo().browse(312)
out['order312'] = {'state': o.state, 'signed_by': o.signed_by, 'signed_on': o.signed_on, 'signature_stored': bool(o.signature), 'scope2_state': env['sipanel.quote.scope'].sudo().browse(218).current_revision_id.state}
out['modules'] = {m.name: (m.state, m.latest_version, str(m.write_date)) for m in env['ir.module.module'].sudo().search([('name', 'like', 'sipanel_%')])}
ob = env['sale.order'].browse(313)
v1 = env['sipanel.scope.version'].browse(115)
uom_m = env.ref('uom.product_uom_meter')
scope_b = env['sipanel.quote.scope']._create_from_version(ob, v1, 3.0, uom_m)
rev = scope_b.current_revision_id
out['orderB_scope'] = {'scope_id': scope_b.id, 'rev_id': rev.id, 'language': rev.language, 'uom_snapshots': sorted(set(rev.component_ids.mapped('uom_name_snapshot'))), 'final_note': rev.final_note, 'anchor_line_name': scope_b.anchor_line_id.name}
env.cr.commit()
print('AFTERFIX_JSON=' + json.dumps(out, ensure_ascii=False, default=str))
