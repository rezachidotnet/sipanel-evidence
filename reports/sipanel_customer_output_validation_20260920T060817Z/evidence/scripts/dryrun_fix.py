# DRY RUN: set report.url inside the transaction, render, then ROLLBACK (no commit).
import json, subprocess, os, re
ICP = env['ir.config_parameter'].sudo()
before = ICP.get_param('report.url')
ICP.set_param('report.url', 'http://127.0.0.1:8069')
pdf, fmt = env['ir.actions.report'].with_user(2)._render_qweb_pdf('sale.action_report_saleorder', [312])
open('/tmp/sipanel_val/quotation_dryrun_fixed.pdf', 'wb').write(pdf)
# PNG evidence: same body HTML rendered by wkhtmltoimage with the same base url
html, _ = env['ir.actions.report'].with_user(2)._render_qweb_html('sale.action_report_saleorder', [312])
html = html.decode('utf-8').replace('<head>', '<head><base href="http://127.0.0.1:8069/"/>', 1)
open('/tmp/sipanel_val/quotation_dryrun_fixed.html', 'w').write(html)
r = subprocess.run(['wkhtmltoimage', '--quiet', '--encoding', 'utf-8', '--width', '1000', '--javascript-delay', '1500',
                    '/tmp/sipanel_val/quotation_dryrun_fixed.html', '/tmp/sipanel_val/quotation_dryrun_fixed.png'], capture_output=True, text=True)
env.cr.rollback()
after = env['ir.config_parameter'].sudo().get_param('report.url')
print('DRYRUN_JSON=' + json.dumps({'before': before, 'after_rollback': after, 'fmt': fmt, 'size': len(pdf), 'wkhtmltoimage_rc': r.returncode, 'err': r.stderr[-300:], 'png': os.path.getsize('/tmp/sipanel_val/quotation_dryrun_fixed.png') if os.path.exists('/tmp/sipanel_val/quotation_dryrun_fixed.png') else None}))
