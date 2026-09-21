# STEP 2A: UI validation on the real view arch + a live end-to-end Persian quotation.
import json, re
from odoo.addons.sipanel_commercial_scope_core.models.sipanel_tools import stored_translations
TS = '20260921T013000Z'
P = f'SIPANEL-XLATE-CHECK-{TS}'
env = env(user=2, context={'lang': 'en_US', 'tz': 'Asia/Tehran', 'allowed_company_ids': [1]})
assert env.cr.dbname == 'sipanel'
out = {'ui': {}, 'e2e': {}}

# ---------------------------------------------------------------- UI validation
langs = [l[0] for l in env['res.lang'].get_installed()]
out['ui']['installed_langs'] = langs
out['ui']['translation_control_available'] = len(langs) > 1  # Odoo shows it when >1 lang
for model, view_xmlid in [('sipanel.scope.version', 'sipanel_commercial_scope_core.view_sipanel_scope_version_form'),
                          ('sipanel.scope.recipe.line', 'sipanel_commercial_scope_core.view_sipanel_recipe_line_form')]:
    M = env[model]
    try:
        view = M.get_view(env.ref(view_xmlid).id, 'form')
        arch = view['arch']
    except Exception as exc:
        out['ui'][model] = {'error': str(exc)[:200]}
        continue
    names = re.findall(r'<field[^>]*name="([^"]+)"', arch)
    out['ui'][model] = {
        'view': view_xmlid,
        'renders': True,
        'has_customer_label': 'customer_label' in names,
        'has_customer_description': 'customer_description' in names,
        'legacy_fields_in_view': sorted(n for n in names if n.endswith(('_fa', '_en'))),
        'customer_label_count': names.count('customer_label'),
        'customer_description_count': names.count('customer_description'),
        'field_is_translatable': bool(M._fields['customer_label'].translate),
        'field_label': M._fields['customer_label'].string,
        'fa_en_in_any_field_label': sorted(
            f'{n}:{M._fields[n].string}' for n in set(names)
            if n in M._fields and ('(FA)' in (M._fields[n].string or '') or '(EN)' in (M._fields[n].string or ''))),
    }
# list views too
for xmlid in ('sipanel_commercial_scope_core.view_sipanel_scope_version_list',):
    try:
        arch = env['sipanel.scope.version'].get_view(env.ref(xmlid).id, 'list')['arch']
        out['ui'][xmlid] = {'legacy_fields': sorted(set(re.findall(r'name="([a-z_]+_(?:fa|en))"', arch)))}
    except Exception as exc:
        out['ui'][xmlid] = {'error': str(exc)[:160]}
# groups / permissions unchanged
out['ui']['cost_group_still_guards_manual_cost'] = bool(
    env.ref('sipanel_commercial_scope_core.group_scope_cost_viewer', raise_if_not_found=False))

# ---------------------------------------------------------------- live E2E
v = env['sipanel.scope.version'].browse(115)
assert v.state == 'released'
out['e2e']['master_terms'] = {'label': stored_translations(v, 'customer_label'),
                              'description_langs': sorted(stored_translations(v, 'customer_description'))}
partner = env['res.partner'].create({'name': f'{P} مشتری', 'lang': 'fa_IR', 'email': False})
order = env['sale.order'].create({'partner_id': partner.id, 'client_order_ref': P, 'origin': P})
scope = env['sipanel.quote.scope']._create_from_version(order, v, 12.0, env.ref('uom.product_uom_meter'))
scope.anchor_line_id.write({'price_unit': 2500000.0})
rev = scope.current_revision_id
out['e2e']['revision'] = {
    'resolved_language': rev.resolved_language, 'label_resolved': rev.label_resolved,
    'label_fa': rev.label_fa, 'label_en': rev.label_en,
    'source_version_checksum': rev.source_version_checksum,
    'missing_translations': rev._missing_translation_keys(),
    'provenance_fallbacks': {k: p.get('fallback') for k, p in (rev.translation_provenance or {}).get('version', {}).items()},
    'component_resolved_sample': rev.component_ids[:3].mapped('customer_label_resolved'),
    'note_head': (rev.final_note or '').split('\n')[0],
}
pdf, _fmt = env['ir.actions.report'].sudo()._render_qweb_pdf('sale.action_report_saleorder', order.ids)
open('/tmp/xlate_e2e.pdf', 'wb').write(pdf)
out['e2e']['pdf_bytes'] = len(pdf)
out['e2e']['order'] = {'id': order.id, 'name': order.name, 'partner': partner.id,
                       'total': order.amount_total}
env.cr.commit()
print('RESULT=' + json.dumps(out, ensure_ascii=False, indent=1, default=str))
