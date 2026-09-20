import json, os
env = env(user=2, context={'lang': 'en_US', 'tz': 'Asia/Tehran', 'allowed_company_ids': [1]})
o = env['sale.order'].browse(368)
assert o.state == 'draft' and o.client_order_ref.startswith('SIPANEL-PDF-LAYOUT-CHECK-')
view = env['ir.ui.view'].sudo().search([('key', '=', 'sale_shamsi_report.report_saleorder_document_shamsi')], limit=1)
arch = view.arch_db or ''
pdf, fmt = env['ir.actions.report']._render_qweb_pdf('sale.action_report_saleorder', [o.id])
open('/tmp/sipanel_val/fresh_after_fix.pdf', 'wb').write(pdf)
tok = o._portal_ensure_token()
with open('/tmp/sipanel_val/token_1c.json', 'w') as f: json.dump({'order': tok}, f)
os.chmod('/tmp/sipanel_val/token_1c.json', 0o600)
env.cr.commit()
print('AFTER_JSON=' + json.dumps({'fmt': fmt, 'size': len(pdf), 'view_id': view.id, 'view_has_overflow_hidden': 'overflow: hidden' in arch, 'view_spacer_300': 'height: 300px' in arch,
                                  'module_state': env['ir.module.module'].sudo().search([('name', '=', 'sale_shamsi_report')]).state, 'report_url': env['ir.config_parameter'].sudo().get_param('report.url')}))
