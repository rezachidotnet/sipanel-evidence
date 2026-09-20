# STEP 1B Action B — enable fa_IR as an additional language of website "sipanel" (id 1); default language unchanged. Explicit commit.
import json
assert env.cr.dbname == 'sipanel'
W = env['website'].sudo().browse(1)
assert W.name == 'sipanel' and W.company_id.name == 'Sipanel'
fa = env['res.lang'].sudo().with_context(active_test=False).search([('code', '=', 'fa_IR')])
before = {'default_lang': W.default_lang_id.code, 'langs': W.language_ids.mapped('code'), 'fa_active': fa.active, 'fa_url_code': fa.url_code, 'write_date': str(W.write_date)}
if not fa.active:
    env['res.lang'].sudo()._activate_lang('fa_IR')  # native path; would also load translations (not needed: already active)
if fa not in W.language_ids:
    W.write({'language_ids': [(4, fa.id)]})
env.cr.commit()
W.invalidate_recordset()
after = {'default_lang': W.default_lang_id.code, 'langs': W.language_ids.mapped('code'), 'fa_active': fa.active, 'fa_url_code': fa.url_code, 'write_date': str(W.write_date)}
others = [{'id': w.id, 'name': w.name, 'langs': w.language_ids.mapped('code')} for w in env['website'].sudo().search([('id', '!=', 1)])]
print('FA_JSON=' + json.dumps({'before': before, 'after': after, 'other_websites': others, 'translation_load_triggered': False}))
