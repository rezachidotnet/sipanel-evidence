# read-only post-change state
import json
out = {}
ICP = env['ir.config_parameter'].sudo()
out['report_url'] = repr(ICP.get_param('report.url')); out['web_base_url'] = ICP.get_param('web.base.url')
W = env['website'].sudo().browse(1)
out['website'] = {'default_lang': W.default_lang_id.code, 'langs': W.language_ids.mapped('code'), 'homepage_url': W.homepage_url, 'write_date': str(W.write_date)}
out['homepage_pages'] = [(p.url, p.is_published, p.website_id.id) for p in env['website.page'].sudo().search([('url', 'in', ['/', '/home'])])]
out['menus_root'] = env['website.menu'].sudo().search_count([('website_id', '=', 1)])
o = env['sale.order'].sudo().browse(312)
out['order_312'] = {'state': o.state, 'write_date': str(o.write_date), 'signed_by': o.signed_by, 'amount_total': o.amount_total, 'msg_count': len(o.message_ids)}
out['mail_since_0800'] = env['mail.mail'].sudo().search_count([('create_date', '>=', '2026-09-20 08:00:00')])
out['partner_426_active'] = env['res.partner'].sudo().with_context(active_test=False).browse(426).active
out['portal_users_new'] = env['res.users'].sudo().search_count([('create_date', '>=', '2026-09-20 08:00:00')])
out['lang_fa'] = [(l.code, l.active, l.url_code, l.direction) for l in env['res.lang'].sudo().search([('code', '=', 'fa_IR')])]
print('POST_JSON=' + json.dumps(out, ensure_ascii=False, default=str))
