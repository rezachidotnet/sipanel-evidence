#!/usr/bin/env python3
"""Replay the five L-02 regression rules (the ones in
sale_shamsi_report/tests/test_sale_order_shamsi.py::TestSaleOrderPdfPagination)
over already captured body-only renders, so the before/after verdict per
document shape is reproducible without re-running Odoo. Runs in the
odoo-sipanel container, which has pdfminer.six."""
import glob, os, re, sys
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTChar, LTCurve, LTFigure, LTImage, LTLine, LTRect
import unicodedata

MM = 72.0 / 25.4
MARGIN_TOP, MARGIN_BOTTOM, TOL = 52.0, 32.0, 1.0


def read(path):
    out = []
    for layout in extract_pages(path):
        h = layout.height
        chars, graphics, images = [], [], []

        def walk(node):
            for e in node:
                if isinstance(e, LTChar):
                    chars.append((h - e.y1, h - e.y0, e.get_text()))
                elif isinstance(e, (LTRect, LTLine, LTCurve)):
                    graphics.append((h - e.y1, h - e.y0))
                elif isinstance(e, (LTImage, LTFigure)):
                    images.append((h - e.y1, h - e.y0))
                if hasattr(e, '__iter__'):
                    walk(e)

        walk(layout)
        raw = ''.join(c[2] for c in chars)
        flat = re.sub(r'\s+', '', unicodedata.normalize('NFKC', raw)).lower()
        out.append({'h': h, 'chars': chars, 'graphics': graphics, 'images': images,
                    'text': flat})
    return out


def rules(pages):
    res = {}
    outside, split, stretched, blank = [], [], [], []
    for n, p in enumerate(pages, 1):
        top, bottom = MARGIN_TOP * MM, p['h'] - MARGIN_BOTTOM * MM
        for y0, y1, t in p['chars']:
            if y1 > bottom + TOL or y0 < top - TOL:
                outside.append((n, round(y0, 1), round(y1, 1), t))
            for edge in (top, bottom):
                if y0 < edge - TOL and y1 > edge + TOL:
                    split.append((n, round(y0, 1), round(y1, 1), t))
        for y0, y1 in p['graphics']:
            if y1 > p['h'] + TOL or y0 < -TOL:
                stretched.append((n, round(y0, 1), round(y1, 1)))
        if (p['graphics'] or p['images']) and not p['chars']:
            blank.append(n)
    res['R1_text_outside_printable_body'] = outside
    res['R2_text_line_split_by_page_edge'] = split
    res['R3_table_frame_not_paginated'] = stretched
    res['R4_page_with_marks_but_no_text'] = blank
    # R5 (column header repeats on continuation pages) is deliberately NOT
    # replayed here. These fixtures are Persian, and both poppler and pdfminer
    # emit Arabic presentation forms glyph by glyph with layout-driven spacing,
    # so substring matching on the extracted text is not trustworthy. R5 is
    # covered by the in-Odoo test, which renders a Latin fixture, and by the
    # page-by-page visual review.
    return res


base = sys.argv[1] if len(sys.argv) > 1 else '/tmp/sipanel_1d'
print(f'{"fixture":<13}{"tag":<8}{"pg":>3}  R1  R2  R3  R4  verdict')
totals = {}
for tag in ('before', 'after'):
    for path in sorted(glob.glob(os.path.join(base, tag, '*.bodyonly.pdf'))):
        key = os.path.basename(path).replace('.bodyonly.pdf', '')
        pages = read(path)
        r = rules(pages)
        counts = [len(r[k]) for k in sorted(r)]
        bad = sum(counts)
        totals[(key, tag)] = (counts, bad)
        print(f'{key:<13}{tag:<8}{len(pages):>3}  ' +
              '  '.join(f'{c:<2}' for c in counts) +
              f'  {"FAIL" if bad else "PASS"}')
        for k in sorted(r):
            if r[k]:
                print(f'      {k}: {r[k][:4]}{" ..." if len(r[k]) > 4 else ""}')
nb = sum(1 for (k, t), (_c, b) in totals.items() if t == 'before' and b)
na = sum(1 for (k, t), (_c, b) in totals.items() if t == 'after' and b)
print(f'\nSUMMARY: {nb} of 10 shapes FAIL before the fix, {na} of 10 FAIL after')
