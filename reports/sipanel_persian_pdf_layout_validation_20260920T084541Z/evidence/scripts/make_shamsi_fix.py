"""Produce the corrected Shamsi report template + test in the scratch area (source stays untouched until applied with sudo)."""
import os, re
SRC = '/opt/odoo/addons/sale_shamsi_report'
OUT = os.path.join(os.path.dirname(__file__), 'shamsi_edit')
os.makedirs(OUT, exist_ok=True)
t = open(f'{SRC}/views/sale_report_templates.xml', encoding='utf-8').read()
n0 = t.count('overflow: hidden')
assert n0 == 0
t2 = t.replace('                height: 20cm; \n', '                height: 20cm; \n                overflow: hidden; /* cover content must never spill past the page break onto page 2 */\n', 1)
assert t2 != t, 'height line not found'
t3 = t2.replace('                <div style="height: 100px;"></div>\n                <div style="font-size: 26px; line-height: 2.2; color: #000;">',
                '                <div style="height: 60px;"></div>\n                <div style="font-size: 26px; line-height: 2.2; color: #000;">', 1)
assert t3 != t2, 'spacer 100 not found'
t4 = t3.replace('                    <div style="height: 300px;"></div>\n', '                    <div style="height: 80px;"></div>\n', 1)
assert t4 != t3, 'spacer 300 not found'
open(f'{OUT}/sale_report_templates.xml', 'w', encoding='utf-8').write(t4)
s = open(f'{SRC}/tests/test_sale_order_shamsi.py', encoding='utf-8').read()
assert s.startswith('from datetime import datetime\n')
s2 = 'import re\n' + s
NEW = '''    def test_sale_report_cover_page_is_bounded(self):
        """Regression (2026-09-20): the cover block is a fixed 20cm box with page-break-after; its content
        (title, number, customer, date) must stay inside that box, otherwise the large date line spills past
        the page break and overlaps the document-information block at the top of page 2."""
        document = self._parse("views/sale_report_templates.xml")
        cover = document.xpath("//div[contains(@class, 'custom-full-page-cover')]")
        self.assertEqual(len(cover), 1)
        style = " ".join(cover[0].get("style").split())
        self.assertIn("height: 20cm;", style)
        self.assertIn("overflow: hidden;", style)
        self.assertIn("page-break-after: always;", style)
        markup = etree.tostring(cover[0], encoding="unicode")
        spacers = [int(px) for px in re.findall(r'style="height: (\\d+)px;"', markup)]
        self.assertTrue(spacers)
        self.assertLessEqual(max(spacers), 100, "a single spacer must not push the cover date out of the 20cm box")
        self.assertLessEqual(sum(spacers), 320, "total spacer height must leave room for the cover text inside 20cm")
        # the document date is rendered exactly once on the cover; page 2 keeps the native informations block
        self.assertEqual(len(cover[0].xpath(".//*[@t-field='doc.date_order_shamsi']")), 1)

    def test_sale_portal_template_language_branches(self):
'''
assert s2.count('    def test_sale_portal_template_language_branches(self):\n') == 1
s3 = s2.replace('    def test_sale_portal_template_language_branches(self):\n', NEW, 1)
open(f'{OUT}/test_sale_order_shamsi.py', 'w', encoding='utf-8').write(s3)
print('OK', len(t), len(t4), len(s), len(s3))
