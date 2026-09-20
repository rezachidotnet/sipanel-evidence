# STEP 1D - render every fixture PDF via the ORM report path and keep the exact
# HTML/args wkhtmltopdf was given, so geometry checks use the real boundaries.
import json, os, shutil, sys
from odoo.addons.base.models import ir_actions_report as M

TAG = RENDER_TAG                      # 'before' | 'after'
OUT = f'/tmp/sipanel_1d/{TAG}'
os.makedirs(OUT, exist_ok=True)
ids = json.load(open('/tmp/sipanel_1d/ids.json'))
docs = dict(ids['docs']); docs.update(ids['docs_E'])

rep = env.ref('sale.action_report_saleorder')
orig = M.subprocess.Popen
res = {}
for key, oid in sorted(docs.items()):
    order = env['sale.order'].browse(oid)
    cap = {}
    class P(orig):
        def __init__(self, args, *a, **kw):
            if isinstance(args, (list, tuple)) and 'wkhtmltopdf' in str(args[0]):
                cap['args'] = list(args)
                for i, x in enumerate(args):
                    if x == '--header-html':
                        shutil.copy(args[i + 1], f'{OUT}/{key}.header.html')
                    if x == '--footer-html':
                        shutil.copy(args[i + 1], f'{OUT}/{key}.footer.html')
                body = [f for f in args if isinstance(f, str) and '.body.' in f and f.endswith('.html')]
                if body:
                    shutil.copy(body[0], f'{OUT}/{key}.body.html')
            super().__init__(args, *a, **kw)
    M.subprocess.Popen = P
    try:
        pdf, _fmt = rep.sudo()._render_qweb_pdf('sale.action_report_saleorder', order.ids)
    finally:
        M.subprocess.Popen = orig
    open(f'{OUT}/{key}.pdf', 'wb').write(pdf)
    res[key] = {'order': order.name, 'id': oid, 'bytes': len(pdf), 'args': cap.get('args', [])}
    print('RENDERED', key, order.name, len(pdf))
json.dump(res, open(f'{OUT}/render.json', 'w'), indent=1)
print('DONE', TAG)
