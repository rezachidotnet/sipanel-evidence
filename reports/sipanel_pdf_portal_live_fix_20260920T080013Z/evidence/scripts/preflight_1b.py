# read-only preflight for STEP 1B (no commit)
import json
out = {'db': env.cr.dbname}
ICP = env['ir.config_parameter'].sudo()
ru = ICP.get_param('report.url')
out['report_url'] = {'repr': repr(ru), 'len': len(ru or ''), 'record_id': ICP.search([('key', '=', 'report.url')]).id}
out['web_base_url'] = ICP.get_param('web.base.url')
out['websites'] = [{'id': w.id, 'name': w.name, 'domain': w.domain, 'company': w.company_id.name, 'default_lang': w.default_lang_id.code,
                    'langs': w.language_ids.mapped('code'), 'specific_user': w.specific_user_account} for w in env['website'].sudo().search([])]
L = env['res.lang'].sudo().with_context(active_test=False)
out['langs'] = [{'code': l.code, 'name': l.name, 'active': l.active, 'direction': l.direction, 'url_code': l.url_code} for l in L.search([('code', 'in', ['fa_IR', 'en_US'])])]
out['fa_translations_sample'] = {
    'website_portal_terms': env['ir.translation'].sudo().search_count([]) if 'ir.translation' in env else 'n/a (jsonb translations)',
    'uom_units_fa': env.ref('uom.product_uom_unit').with_context(lang='fa_IR').name,
    'sale_order_type_name_fa': env['sale.order'].sudo().browse(312).with_context(lang='fa_IR').type_name,
}
out['modules_with_fa_po'] = 'checked in shell separately'
o = env['sale.order'].sudo().browse(312)
out['order_312'] = {'state': o.state, 'partner_lang': o.partner_id.lang, 'partner_active': o.partner_id.active, 'has_token': bool(o.access_token), 'total': o.amount_total}
out['recent_hostnotfound_lines_hint'] = 'see docker logs grep'
print('PRE1B_JSON=' + json.dumps(out, ensure_ascii=False, default=str))
