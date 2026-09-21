# STEP 2A post-migration verification.
import json
from odoo.addons.sipanel_commercial_scope_core.models.sipanel_tools import stored_translations
env = env(user=1, context={'active_test': False})
out = {}

V = env['sipanel.scope.version'].sudo().with_context(active_test=False)
versions = []
for v in V.search([]):
    versions.append({
        'id': v.id, 'name': v.display_name, 'state': v.state,
        'checksum_algo': v.checksum_algo,
        'customer_label': stored_translations(v, 'customer_label'),
        'customer_description': stored_translations(v, 'customer_description'),
        'v1_checksum_verifies': v.verify_release_checksum(),
    })
out['versions'] = versions

RL = env['sipanel.scope.recipe.line'].sudo()
out['recipe_lines'] = [{'id': l.id, 'label': stored_translations(l, 'customer_label')}
                       for l in RL.search([], order='id')]

# legacy columns still present but no longer ORM fields
Vf = env['sipanel.scope.version']._fields
out['legacy_fields_removed'] = {
    f: (f not in Vf) for f in ('label_fa', 'label_en', 'customer_description_fa', 'customer_description_en')}
out['legacy_fields_removed']['recipe.customer_label_fa'] = 'customer_label_fa' not in env['sipanel.scope.recipe.line']._fields
env.cr.execute("SELECT column_name FROM information_schema.columns WHERE table_name='sipanel_scope_version' AND column_name LIKE '%%_fa' OR table_name='sipanel_scope_version' AND column_name LIKE '%%_en'")
out['dormant_columns_still_in_db'] = sorted(r[0] for r in env.cr.fetchall())

# sealed snapshots must be byte-identical: recompute the seal payload
Rev = env['sipanel.quote.scope.revision'].sudo()
sealed = []
for r in Rev.search([('state', 'in', ('sent_sealed', 'accepted_sealed'))]):
    sealed.append({
        'id': r.id, 'ref': r.display_name, 'state': r.state,
        'stored_hash': r.sealed_hash,
        'recomputed_matches': r._current_seal_hash() == r.sealed_hash,
        'label_fa': r.label_fa, 'label_en': r.label_en,
        'label_resolved': r.label_resolved or None,
        'resolved_language': r.resolved_language or None,
    })
out['sealed_revisions'] = sealed
out['artifacts'] = [{'id': a.id, 'kind': a.kind, 'hash': a.content_hash, 'lang': a.language}
                    for a in env['sipanel.quote.scope.artifact'].sudo().search([], order='id')]
out['config_unchanged'] = {
    'report.url': env['ir.config_parameter'].sudo().get_param('report.url'),
    'website_langs': env['website'].sudo().browse(1).language_ids.mapped('code'),
    'paperformat_margins': [env.ref('sale.action_report_saleorder').get_paperformat().margin_top,
                            env.ref('sale.action_report_saleorder').get_paperformat().margin_bottom],
}
print('VERIFY=' + json.dumps(out, ensure_ascii=False, indent=1, default=str))
