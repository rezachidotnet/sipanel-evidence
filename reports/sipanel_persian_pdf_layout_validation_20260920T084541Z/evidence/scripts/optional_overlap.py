from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTTextLine, LTChar
import sys
for pno, page in enumerate(extract_pages(sys.argv[1]), 1):
    if pno != 3: continue
    for el in page:
        if isinstance(el, LTTextContainer):
            for ln in el:
                if isinstance(ln, LTTextLine) and 'Optional' in ln.get_text():
                    chars = [c for c in ln if isinstance(c, LTChar)]
                    print('page3 line bbox', [round(v, 1) for v in ln.bbox], 'font', chars[0].fontname if chars else None, 'size', round(chars[0].size, 1) if chars else None, 'text', repr(ln.get_text().strip()[:60]))
