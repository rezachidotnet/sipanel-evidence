import re, json
COSTS = ['731000', '731,000', '9876', '9,876', '55555', '55,555', '4321', '4,321', '8765000', '8,765,000', '18144382', '18,144,382', '10355618', '10,355,618', '36.34', '237024', '333330', '34568']
INTERNAL = ['margin', 'Margin', 'cost', 'Cost', 'analytic', 'Analytic', 'sealed_hash', 'recognition', 'supplier', 'Supplier', 'INTERNAL', '/opt/odoo', '/mnt/extra-addons', 'unit_cost', 'occurrence_uid', 'scope_uid', 'audit', 'sipanel_', 'password', 'session_id']
tok = json.load(open('val/token_1b.json'))['order']
FA_CHROME = ['پیش فاکتور', 'شماره', 'تاریخ', 'مبلغ', 'مالیات', 'جمع', 'کل', 'مشتری', 'فروشنده', 'خانه', 'حساب', 'خروج', 'ورود', 'تأیید', 'امضا', 'رد', 'دانلود', 'چاپ', 'سفارش']
for fn in ['val/live/portal_fa.html', 'val/live/portal_en_after_fa.html', 'val/live/report_html_fa_route.html']:
    s = open(fn, encoding='utf-8').read()
    i = {'file': fn, 'len': len(s)}
    i['html_tag'] = re.findall(r'<html[^>]*>', s)[:1]
    i['dir_rtl_count'] = len(re.findall(r'dir="rtl"', s)); i['rtl_css'] = bool(re.search(r'\.rtl\.', s))
    i['lang_switcher'] = sorted(set(re.findall(r'/(fa|en)/my/orders/312', s)))
    i['fa_chrome_hits'] = {w: s.count(w) for w in FA_CHROME if w in s}
    i['en_chrome_hits'] = {w: s.count(w) for w in ['Sign', 'Accept', 'Reject', 'Quotation Date', 'Expiration', 'Salesperson', 'Download', 'Print', 'Home', 'Sign out', 'Untaxed Amount', 'Total', 'Taxes'] if w in s}
    i['totals'] = {k: (k in s) for k in ['39,500,000', '3,950,000', '43,450,000', '2,500,000', '2,200,000']}
    i['markers'] = re.findall(r'INTERNAL-MARKER-[A-Z\-]+', s); i['costs'] = [c for c in COSTS if c in s]
    i['internal_words'] = {w: len(re.findall(re.escape(w), s)) for w in INTERNAL if w in s}
    i['comments'] = [c.strip()[:60] for c in re.findall(r'<!--(.*?)-->', s, re.S)]
    i['token_count'] = s.count(tok); i['session_cookie_like'] = bool(re.search(r'session_id=[0-9a-f]{20,}', s))
    i['sipanel_attrs'] = sorted(set(re.findall(r'data-sipanel-[a-z\-]+', s)))
    i['persian_content'] = {k: (k in s) for k in ['ناودان گالوانیزه', 'بست دیواری', 'درزگیر سیلیکونی', 'داربست', 'جرثقیل', 'گزینه‌های اختیاری', 'یادداشت مشتری', 'یادداشت سطر']}
    i['qty_widget_value'] = re.findall(r'js_quantity form-control"[^>]*value="([^"]*)"', s)
    i['shamsi_date'] = re.findall(r'1405/0[0-9]/[0-9]{2}', s)[:3]
    print(json.dumps(i, ensure_ascii=False))
