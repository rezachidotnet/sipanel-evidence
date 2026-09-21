# STEP 2A read-only inventory of the legacy FA/EN customer-text fields.
import json
env = env(user=1, context={'active_test': False})
assert env.cr.dbname == 'sipanel'
SPECS = [
    ('sipanel.scope.version', [('label_fa', 'label_en', 'customer_label'),
                               ('customer_description_fa', 'customer_description_en', 'customer_description')]),
    ('sipanel.scope.recipe.line', [('customer_label_fa', 'customer_label_en', 'customer_label')]),
    ('sipanel.quote.scope.revision', [('label_fa', 'label_en', None),
                                      ('customer_description_fa', 'customer_description_en', None)]),
    ('sipanel.quote.scope.component', [('customer_label_fa', 'customer_label_en', None)]),
]
out = {}
def clean(v):
    return (v or '').strip()
for model, pairs in SPECS:
    M = env[model].sudo().with_context(active_test=False)
    total = M.search_count([])
    info = {'total_records': total, 'fields': {}}
    for fa, en, new in pairs:
        recs = M.search([])
        blank = both = fa_only = en_only = equal = conflict = 0
        malformed = []
        for r in recs:
            a, b = clean(r[fa]), clean(r[en])
            if not a and not b:
                blank += 1
            elif a and not b:
                fa_only += 1
            elif b and not a:
                en_only += 1
            else:
                both += 1
                if a == b:
                    equal += 1
                else:
                    conflict += 1
            for val, tag in ((r[fa], fa), (r[en], en)):
                if val is not None and not isinstance(val, str):
                    malformed.append([r.id, tag, type(val).__name__])
                elif val and val != val.strip():
                    malformed.append([r.id, tag, 'leading/trailing whitespace'])
        info['fields'][f'{fa}|{en}'] = {
            'new_field': new, 'blank_both': blank, 'fa_only': fa_only, 'en_only': en_only,
            'both_populated': both, 'both_equal': equal, 'both_conflicting': conflict,
            'malformed': malformed[:20], 'malformed_count': len(malformed),
        }
    out[model] = info
# released vs draft breakdown for the master version
V = env['sipanel.scope.version'].sudo().with_context(active_test=False)
out['sipanel.scope.version']['by_state'] = {
    s: V.search_count([('state', '=', s)]) for s in ('draft', 'released', 'superseded')}
out['sipanel.scope.version']['released_with_checksum'] = V.search_count([('state', 'in', ('released', 'superseded')), ('release_checksum', '!=', False)])
RL = env['sipanel.scope.recipe.line'].sudo()
out['sipanel.scope.recipe.line']['by_version_state'] = {
    s: RL.search_count([('version_id.state', '=', s)]) for s in ('draft', 'released', 'superseded')}
out['sipanel.scope.recipe.line']['internal_only'] = RL.search_count([('disclosure', '=', 'internal_only')])
out['installed_langs'] = [l[0] for l in env['res.lang'].get_installed()]
out['sealed_revisions'] = env['sipanel.quote.scope.revision'].sudo().search_count([('state', 'in', ('sent_sealed', 'accepted_sealed'))])
out['artifacts'] = env['sipanel.quote.scope.artifact'].sudo().search_count([])
print('INVENTORY=' + json.dumps(out, ensure_ascii=False, indent=1))
