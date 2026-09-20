# STEP 1D - Persian portal regression: the fa route must still render and its
# totals must equal the quotation (and the PDF) totals.
import json
ids = json.load(open('/tmp/sipanel_1d/ids.json'))
docs = dict(ids['docs']); docs.update(ids['docs_E'])
out = {}
for key, oid in sorted(docs.items()):
    o = env['sale.order'].browse(oid)
    out[key] = {'id': oid, 'name': o.name, 'state': o.state,
                'untaxed': o.amount_untaxed, 'tax': o.amount_tax, 'total': o.amount_total,
                'access_url': o.get_portal_url(), 'token': bool(o._portal_ensure_token())}
env.cr.flush()
env.cr.commit()
json.dump(out, open('/tmp/sipanel_1d/portal_targets.json', 'w'), indent=1, default=str)
print('PORTAL_TARGETS=' + json.dumps({k: {'name': v['name'], 'total': v['total'],
      'url': v['access_url']} for k, v in out.items()}, ensure_ascii=False))
