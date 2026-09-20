import json, base64
out = {}
ICP = env['ir.config_parameter'].sudo()
out['report_url'] = ICP.get_param('report.url'); out['web_base_url'] = ICP.get_param('web.base.url')
W = env['website'].sudo().search([])
out['websites'] = [{'id': w.id, 'name': w.name, 'domain': w.domain, 'default_lang': w.default_lang_id.code, 'langs': w.language_ids.mapped('code')} for w in W]
U = env['uom.uom'].sudo()
out['uom_fa'] = {u.id: (u.with_context(lang='en_US').name, u.with_context(lang='fa_IR').name) for u in U.search([('name', 'in', ['m', 'Units', 'Hours'])])}
out['fa_lang'] = [(l.code, l.active, l.direction, l.decimal_point, l.thousands_sep, l.date_format) for l in env['res.lang'].sudo().with_context(active_test=False).search([('code', '=', 'fa_IR')])]
o = env['sale.order'].sudo().browse(312)
out['order_state'] = o.state
out['messages'] = [{'id': m.id, 'type': m.message_type, 'subtype': m.subtype_id.name, 'internal': m.subtype_id.internal, 'body': (m.body or '')[:80]} for m in o.message_ids]
out['mails'] = env['mail.mail'].sudo().search_count([('model', '=', 'sale.order'), ('res_id', 'in', [312, 313])])
out['company'] = {'name': env.company.name, 'layout': env.company.external_report_layout_id.key, 'font': env.company.font, 'paper': env.company.paperformat_id.name}
for art in env['sipanel.quote.scope.artifact'].sudo().browse([256, 258]):
    att = art.attachment_id
    with open(f'/tmp/sipanel_val/artifact_{art.id}.pdf', 'wb') as f:
        f.write(att.raw)
    out[f'artifact_{art.id}'] = {'name': att.name, 'mimetype': att.mimetype, 'size': len(att.raw), 'hash_field': art.content_hash, 'res_model': att.res_model, 'res_id': att.res_id, 'public': att.public, 'access_token': bool(att.access_token)}
# fresh render through the same report path with explicit user 2 (as a salesperson would print)
pdf, fmt = env['ir.actions.report'].with_user(2)._render_qweb_pdf('sale.action_report_saleorder', [312])
with open('/tmp/sipanel_val/quotation_shell.pdf', 'wb') as f: f.write(pdf)
out['shell_render'] = {'fmt': fmt, 'size': len(pdf)}
html, _ = env['ir.actions.report'].with_user(2)._render_qweb_html('sale.action_report_saleorder', [312])
with open('/tmp/sipanel_val/quotation_shell.html', 'wb') as f: f.write(html)
out['shell_html_size'] = len(html)
print('RO2_JSON=' + json.dumps(out, ensure_ascii=False, default=str))
