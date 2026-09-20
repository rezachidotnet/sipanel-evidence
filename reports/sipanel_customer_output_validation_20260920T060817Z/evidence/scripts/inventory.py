import json
out = {}
S = env['sipanel.scope'].sudo().with_context(active_test=False)
V = env['sipanel.scope.version'].sudo().with_context(active_test=False)
out['scopes'] = [{'id': s.id, 'name': s.name, 'active': s.active} for s in S.search([])]
out['versions'] = [{'id': v.id, 'name': v.display_name, 'state': v.state, 'scope': v.scope_id.name, 'lines': len(v.recipe_line_ids), 'anchor': v.anchor_product_id.display_name, 'uom': v.base_uom_id.name, 'label_fa': v.label_fa} for v in V.search([])]
out['quote_scopes_total'] = env['sipanel.quote.scope'].sudo().with_context(active_test=False).search_count([])
out['orders_total'] = env['sale.order'].sudo().search_count([])
out['test_partners'] = [{'id': p.id, 'name': p.name, 'active': p.active, 'lang': p.lang} for p in env['res.partner'].sudo().with_context(active_test=False).search(['|', ('name', 'ilike', 'SIPANEL'), ('name', 'ilike', 'validation')])]
out['sale_report_actions'] = [{'xmlid': a.get_external_id().get(a.id), 'report_name': a.report_name, 'type': a.report_type, 'paperformat': a.paperformat_id.name, 'binding': bool(a.binding_model_id)} for a in env['ir.actions.report'].sudo().search([('model', '=', 'sale.order')])]
out['company_layout'] = {'external_report_layout': env.company.external_report_layout_id.key if env.company.external_report_layout_id else None, 'paperformat': env.company.paperformat_id.name, 'font': env.company.font, 'lang_company': env.company.partner_id.lang}
out['langs'] = [(l.code, l.active, l.direction) for l in env['res.lang'].sudo().with_context(active_test=False).search([('code', 'in', ['fa_IR', 'en_US'])])]
out['views_inheriting_saleorder_report'] = [(v.key, v.xml_id) for v in env['ir.ui.view'].sudo().search([('inherit_id.key', 'in', ['sale.report_saleorder_document', 'sale.report_saleorder']), ('active', '=', True)])]
out['views_inheriting_portal'] = [(v.key, v.xml_id) for v in env['ir.ui.view'].sudo().search([('inherit_id.key', 'in', ['sale.sale_order_portal_content', 'sale.sale_order_portal_template', 'sale_management.sale_order_portal_optional_product_quantity']), ('active', '=', True)])]
out['taxes'] = [{'id': t.id, 'name': t.name, 'amount': t.amount, 'type': t.type_tax_use, 'active': t.active} for t in env['account.tax'].sudo().search([('type_tax_use', '=', 'sale')], limit=10)]
out['icp'] = {k: env['ir.config_parameter'].sudo().get_param(k) for k in ['sipanel_scope.company_currency_only', 'sipanel_scope.min_margin_pct', 'sipanel_scope.system_plan_id', 'sipanel_scope.activity_plan_id', 'web.base.url']}
out['installed_relevant'] = [m.name for m in env['ir.module.module'].sudo().search([('state', '=', 'website')]) ] 
out['installed_relevant'] = sorted(m.name for m in env['ir.module.module'].sudo().search([('state', '=', 'installed'), ('name', 'in', ['website', 'sale_management', 'portal', 'sale_shamsi_report', 'sale_pdf_quote_builder', 'web_enterprise', 'l10n_ir', 'account', 'stock', 'mrp', 'project', 'purchase'])]))
out['modules_other_custom'] = sorted(m.name for m in env['ir.module.module'].sudo().search([('state', '=', 'installed'), ('author', 'not ilike', 'Odoo')]))
print('INV_JSON=' + json.dumps(out, ensure_ascii=False, default=str))
