# STEP 2A migration PREVIEW - runs BEFORE the upgrade, so the native columns do
# not exist yet and nothing can be written. Classifies every legacy value using
# the same plan_record() the real migration uses.
import json, sys
sys.path.insert(0, '/mnt/extra-addons')
env = env(user=1, context={'active_test': False})
assert env.cr.dbname == 'sipanel'

def clean(v):
    return v.strip() if isinstance(v, str) else ''

def plan_record(fa, en, existing):
    fa, en = clean(fa), clean(en)
    if not fa and not en:
        return {}, 'blank_both'
    terms = {'en_US': en, 'fa_IR': fa} if fa else {'en_US': en}
    terms = {l: v for l, v in terms.items() if v or not existing.get(l)}
    if not terms:
        return {}, 'nothing_to_write'
    if fa and en:
        klass = 'identical_both' if fa == en else 'distinct_per_language'
    else:
        klass = 'fa_only' if fa else 'en_only'
    return terms, klass

SPECS = [
    ('sipanel.scope.version', 'sipanel_scope_version',
     [('label_fa', 'label_en', 'customer_label'),
      ('customer_description_fa', 'customer_description_en', 'customer_description')]),
    ('sipanel.scope.recipe.line', 'sipanel_scope_recipe_line',
     [('customer_label_fa', 'customer_label_en', 'customer_label')]),
]
out = {'preview': True, 'models': {}, 'totals': {'scanned': 0, 'to_write': 0, 'terms_by_lang': {}}}
for model, table, pairs in SPECS:
    recs = env[model].sudo().with_context(active_test=False).search([])
    entry = {'table': table, 'records': len(recs), 'fields': {}}
    for fa_col, en_col, native in pairs:
        env.cr.execute(f'SELECT id, "{fa_col}", "{en_col}" FROM "{table}" ORDER BY id')
        rows = env.cr.fetchall()
        stats = {'native_field': native, 'classification': {}, 'records': []}
        for rid, fa, en in rows:
            terms, klass = plan_record(fa, en, {})
            stats['classification'][klass] = stats['classification'].get(klass, 0) + 1
            out['totals']['scanned'] += 1
            if terms:
                out['totals']['to_write'] += 1
                for l, v in terms.items():
                    if v:
                        out['totals']['terms_by_lang'][l] = out['totals']['terms_by_lang'].get(l, 0) + 1
            stats['records'].append({
                'id': rid, 'class': klass,
                'fa_len': len(clean(fa)), 'en_len': len(clean(en)),
                'target_langs': sorted(k for k, v in terms.items() if v),
                'writes_blank_en_US': bool(terms) and not terms.get('en_US'),
            })
        entry['fields'][f'{fa_col}|{en_col}'] = stats
    out['models'][model] = entry

V = env['sipanel.scope.version'].sudo().with_context(active_test=False)
released = V.search([('release_checksum', '!=', False)])
out['checksum_algo_v1_targets'] = {'count': len(released), 'ids': released.ids}
out['snapshot_models_untouched'] = {
    'sipanel.quote.scope.revision': env['sipanel.quote.scope.revision'].sudo().search_count([]),
    'sipanel.quote.scope.component': env['sipanel.quote.scope.component'].sudo().search_count([]),
    'sealed_revisions': env['sipanel.quote.scope.revision'].sudo().search_count([('state', 'in', ('sent_sealed', 'accepted_sealed'))]),
    'artifacts': env['sipanel.quote.scope.artifact'].sudo().search_count([]),
}
print('PREVIEW=' + json.dumps(out, ensure_ascii=False, indent=1))
