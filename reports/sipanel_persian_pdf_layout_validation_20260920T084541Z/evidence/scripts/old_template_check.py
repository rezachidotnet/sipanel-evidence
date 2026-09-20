"""Run the new structural assertions against a template file (old HEAD version vs corrected) with lxml — 'fails before, passes after' evidence."""
import sys, re
from lxml import etree
for fn in sys.argv[1:]:
    document = etree.parse(fn)
    cover = document.xpath("//div[contains(@class, 'custom-full-page-cover')]")
    style = " ".join(cover[0].get("style").split())
    markup = etree.tostring(cover[0], encoding="unicode")
    spacers = [int(px) for px in re.findall(r'style="height: (\d+)px;"', markup)]
    checks = {'one_cover': len(cover) == 1, 'height_20cm': 'height: 20cm;' in style, 'overflow_hidden': 'overflow: hidden;' in style,
              'page_break': 'page-break-after: always;' in style, 'max_spacer_le_100': max(spacers) <= 100, 'sum_spacers_le_320': sum(spacers) <= 320,
              'date_once': len(cover[0].xpath(".//*[@t-field='doc.date_order_shamsi']")) == 1}
    print(fn.split('/')[-1], 'spacers', spacers, 'RESULT', 'PASS' if all(checks.values()) else 'FAIL', {k: v for k, v in checks.items() if not v})
