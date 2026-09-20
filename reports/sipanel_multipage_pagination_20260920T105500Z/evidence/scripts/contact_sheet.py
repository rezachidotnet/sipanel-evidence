#!/usr/bin/env python3
"""Build before/after contact sheets from the rendered page PNGs (runs in the
odoo-sipanel container, which is where Pillow is available)."""
import glob, os, re, sys
from PIL import Image, ImageDraw

SRC, OUT = sys.argv[1], sys.argv[2]
THUMB_W, PAD, LABEL = 300, 12, 20
os.makedirs(OUT, exist_ok=True)


def pages(tag, key):
    files = glob.glob(os.path.join(SRC, tag, f'{key}-*.png'))
    return sorted(files, key=lambda f: int(re.search(r'-(\d+)\.png$', f).group(1)))


def strip(files):
    ims = []
    for f in files:
        im = Image.open(f).convert('RGB')
        im = im.resize((THUMB_W, round(im.height * THUMB_W / im.width)), Image.LANCZOS)
        ims.append((os.path.basename(f), im))
    return ims


keys = sorted({re.sub(r'-\d+\.png$', '', os.path.basename(f))
               for f in glob.glob(os.path.join(SRC, 'before', '*.png'))})
for key in keys:
    rows = [('BEFORE', strip(pages('before', key))), ('AFTER', strip(pages('after', key)))]
    height = sum(max((im.height for _n, im in r), default=0) + LABEL + PAD for _t, r in rows) + PAD
    width = max(sum(im.width + PAD for _n, im in r) + PAD for _t, r in rows)
    sheet = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(sheet)
    y = PAD
    for tag, row in rows:
        draw.text((PAD, y), f'{key}  {tag}  ({len(row)} pages)', fill='black')
        y += LABEL
        x = PAD
        for name, im in row:
            sheet.paste(im, (x, y))
            draw.rectangle([x, y, x + im.width, y + im.height], outline='#999999')
            draw.text((x + 3, y + 3), name.split('-')[-1].replace('.png', ''), fill='#cc0000')
            x += im.width + PAD
        y += max((im.height for _n, im in row), default=0) + PAD
    sheet.save(os.path.join(OUT, f'contact_{key}.png'))
    print('sheet', key, sheet.size)
