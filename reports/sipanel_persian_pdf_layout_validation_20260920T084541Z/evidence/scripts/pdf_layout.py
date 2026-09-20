"""Page-level layout analysis of a real PDF with pdfminer (no rasteriser): text boxes, font sizes, overlaps, page map PNGs."""
import sys, json, re
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTTextLine, LAParams
from PIL import Image, ImageDraw
fn = sys.argv[1]; out_prefix = sys.argv[2] if len(sys.argv) > 2 else fn
res = []
for pno, page in enumerate(extract_pages(fn, laparams=LAParams(line_margin=0.2)), 1):
    W, H = page.width, page.height
    lines = []
    for el in page:
        if isinstance(el, LTTextContainer):
            for ln in el:
                if isinstance(ln, LTTextLine):
                    txt = ln.get_text().strip()
                    if not txt: continue
                    sizes = [c.size for c in ln if isinstance(c, LTChar)]
                    lines.append({'x0': round(ln.x0, 1), 'y0': round(ln.y0, 1), 'x1': round(ln.x1, 1), 'y1': round(ln.y1, 1),
                                  'size': round(max(sizes), 1) if sizes else 0, 'text': txt[:60]})
    # overlaps: pairs of lines whose boxes intersect by more than 3pt in both axes
    overlaps = []
    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            a, b = lines[i], lines[j]
            ix = min(a['x1'], b['x1']) - max(a['x0'], b['x0']); iy = min(a['y1'], b['y1']) - max(a['y0'], b['y0'])
            if ix > 3 and iy > 3:
                overlaps.append({'a': a['text'], 'a_size': a['size'], 'b': b['text'], 'b_size': b['size'], 'ix': round(ix, 1), 'iy': round(iy, 1), 'y_top_from_page_top': round(H - max(a['y1'], b['y1']), 1)})
    big = [l for l in lines if l['size'] >= 18]
    res.append({'page': pno, 'w': round(W), 'h': round(H), 'lines': len(lines), 'big_text': big, 'overlaps': overlaps,
                'top_lines': sorted(lines, key=lambda l: -l['y1'])[:8]})
    # page map image: boxes only (text not drawn: no Arabic shaping in PIL)
    S = 1.5
    im = Image.new('RGB', (int(W * S), int(H * S)), 'white'); d = ImageDraw.Draw(im)
    for l in lines:
        col = 'red' if l['size'] >= 18 else ('blue' if l['size'] >= 12 else 'gray')
        d.rectangle([l['x0'] * S, (H - l['y1']) * S, l['x1'] * S, (H - l['y0']) * S], outline=col, width=2 if l['size'] >= 18 else 1)
    for o in overlaps:
        pass
    d.text((10, 10), f'page {pno} text boxes: red>=18pt blue>=12pt gray<12pt; overlaps={len(overlaps)}', fill='black')
    im.save(f'{out_prefix}.page{pno}.map.png', optimize=True)
print('LAYOUT_JSON=' + json.dumps(res, ensure_ascii=False))
