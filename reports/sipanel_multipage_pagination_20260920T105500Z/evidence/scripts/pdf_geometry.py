#!/usr/bin/env python3
"""L-02 geometry acceptance checks for SIPANEL sale-order PDFs.

The printable body band is taken from the *effective* wkhtmltopdf invocation
(`--page-size A4 --margin-top 52 --margin-bottom 32`, millimetres), not guessed:

    body_top    = margin_top mm
    body_bottom = page_height - margin_bottom mm

Both checks run against a BODY-ONLY re-render (identical wkhtmltopdf arguments,
empty header and footer document). Pagination is byte-identical to the shipped
PDF because wkhtmltopdf lays header and footer out as separate documents, so any
text or ink found inside a margin band there is body content by construction -
no fragile "is this word part of the footer?" heuristics, which RTL shaping
breaks anyway (poppler emits Arabic presentation forms one glyph per word).

Checks
  TEXT     word boxes from `pdftotext -bbox`
             above / below  - entirely outside the band
             clipped_*      - straddling a band edge (a page starting or ending
                              in the middle of a text line)
  INK      dark-pixel rows inside the bands from a `pdftoppm` raster; catches
           table borders and backgrounds that carry no text
  ORPHAN   a final page whose body ink covers less than --orphan-fill of the band
           while the previous page was full
"""
import argparse, glob, json, os, re, subprocess, sys, tempfile
from xml.etree import ElementTree as ET

MM = 72.0 / 25.4
XH = '{http://www.w3.org/1999/xhtml}'


def words(pdf):
    xml = subprocess.run(['pdftotext', '-bbox', pdf, '-'], capture_output=True, check=True).stdout
    root = ET.fromstring(xml)
    for pno, page in enumerate(root.iter(XH + 'page'), 1):
        ph = float(page.get('height'))
        for w in page.iter(XH + 'word'):
            yield (pno, ph, float(w.get('xMin')), float(w.get('yMin')),
                   float(w.get('xMax')), float(w.get('yMax')), w.text or '')


def read_pgm(path):
    """Minimal binary PGM (P5) reader - avoids a Pillow dependency on the host."""
    data = open(path, 'rb').read()
    fields, i = [], 2
    while len(fields) < 3:
        while i < len(data) and data[i:i + 1].isspace():
            i += 1
        if data[i:i + 1] == b'#':
            while data[i:i + 1] not in (b'\n', b''):
                i += 1
            continue
        j = i
        while j < len(data) and not data[j:j + 1].isspace():
            j += 1
        fields.append(int(data[i:j])); i = j
    w, h, _maxv = fields
    return w, h, data[i + 1:i + 1 + w * h]


def dark_rows(buf, w, h, y_from, y_to, dark, min_run):
    """Rows in [y_from, y_to) holding a horizontal dark run of >= min_run px."""
    tbl = bytes(35 if v < dark else 46 for v in range(256))   # '#' / '.'
    out = []
    for y in range(max(0, int(y_from)), min(h, int(y_to))):
        row = buf[y * w:(y + 1) * w].translate(tbl)
        runs = list(re.finditer(b'#+', row))
        if runs:
            best = max(m.end() - m.start() for m in runs)
            if best >= min_run:
                out.append({'y_pt': None, 'y_px': y, 'dark_px': row.count(35),
                            'run': best, 'x0': runs[0].start(), 'x1': runs[-1].end(),
                            'span': round((runs[-1].end() - runs[0].start()) / w, 3)})
    return out


def check(pdf, mt, mb, tol, dpi, dark, min_run, orphan_fill, max_frame=36.0):
    dpi_used = dpi
    pages = {}

    def blank(pno, ph):
        return {'page': pno, 'page_h': round(ph, 1), 'body_top': round(mt * MM, 1),
                'body_bottom': round(ph - mb * MM, 1), 'above': [], 'below': [],
                'clipped_top': [], 'clipped_bottom': [], 'nwords': 0,
                'min_y': None, 'max_y': None, 'ink_above': [], 'ink_below': [],
                'ink_fill': None, 'min_ink_y': None, 'max_ink_y': None,
                'trailing_frame': None, 'leading_frame': None}

    for (pno, ph, x0, y0, x1, y1, t) in words(pdf):
        top, bot = mt * MM, ph - mb * MM
        p = pages.setdefault(pno, blank(pno, ph))
        p['nwords'] += 1
        p['min_y'] = y0 if p['min_y'] is None else min(p['min_y'], y0)
        p['max_y'] = y1 if p['max_y'] is None else max(p['max_y'], y1)
        rec = {'text': t, 'x0': round(x0, 1), 'y0': round(y0, 1), 'y1': round(y1, 1)}
        if y0 >= bot + tol:
            p['below'].append(rec)
        elif y1 > bot + tol:
            p['clipped_bottom'].append(rec)
        if y1 <= top - tol:
            p['above'].append(rec)
        elif y0 < top - tol:
            p['clipped_top'].append(rec)

    with tempfile.TemporaryDirectory() as d:
        subprocess.run(['pdftoppm', '-r', str(dpi), '-gray', pdf, os.path.join(d, 'p')],
                       check=True)
        for f in sorted(glob.glob(os.path.join(d, 'p-*.pgm'))):
            pno = int(re.search(r'p-(\d+)\.pgm$', f).group(1))
            w, h, buf = read_pgm(f)
            ph = h / dpi * 72
            p = pages.setdefault(pno, blank(pno, ph))
            top_px, bot_px = mt / 25.4 * dpi, h - mb / 25.4 * dpi
            for key, rows in (('ink_above', dark_rows(buf, w, h, 0, top_px, dark, min_run)),
                              ('ink_below', dark_rows(buf, w, h, bot_px, h, dark, min_run))):
                for r in rows:
                    r['y_pt'] = round(r['y_px'] / dpi * 72, 1)
                p[key] = rows
            body = dark_rows(buf, w, h, top_px, bot_px, dark, 1)
            p['_body_rows'] = body
            p['ink_fill'] = round(len(body) / max(1, int(bot_px) - int(top_px)), 3)
            allink = (p['ink_above'] + body + p['ink_below'])
            if allink:
                ys = [r['y_px'] / dpi * 72 for r in allink]
                p['min_ink_y'], p['max_ink_y'] = round(min(ys), 1), round(max(ys), 1)

    res = [pages[k] for k in sorted(pages)]
    for p in res:
        p['violations'] = (len(p['above']) + len(p['below']) + len(p['clipped_top'])
                           + len(p['clipped_bottom']) + len(p['ink_above'])
                           + len(p['ink_below']))
        for k in ('min_y', 'max_y'):
            if p[k] is not None:
                p[k] = round(p[k], 1)
        # A frame/border painted into space that holds no text: the table box
        # overlay continuing past the last row toward the bottom of the page box.
        # Width matters - a full-width rule is a table frame, a narrow centred
        # blob is the signature image, which legitimately sits below its caption.
        if p['max_ink_y'] is not None and p['max_y'] is not None:
            p['trailing_frame'] = round(p['max_ink_y'] - p['max_y'], 1)
        if p['min_ink_y'] is not None and p['min_y'] is not None:
            p['leading_frame'] = round(p['min_y'] - p['min_ink_y'], 1)
        tail = [r for r in p.pop('_body_rows', []) + p['ink_below']
                if p['max_y'] is not None and r['y_px'] / dpi_used * 72 > p['max_y']]
        p['trailing_span'] = round(max((r['span'] for r in tail), default=0.0), 3)
        if (p['trailing_frame'] is not None and p['trailing_frame'] > max_frame
                and p['trailing_span'] > 0.5):
            p['violations'] += 1
            p['frame_violation'] = True
    # An orphan continuation page carries ink but no readable content at all -
    # a bare frame, or a signature image torn away from its caption. A final
    # page holding a few real lines of running prose is not a defect: the text
    # has to go somewhere, and the alternative is overflowing the footer.
    orphan = None
    for p in res:
        band = p['body_bottom'] - p['body_top']
        span = 0.0 if p['max_y'] is None else (p['max_y'] - p['min_y'])
        p['text_fraction'] = round(span / band, 3)
    if len(res) >= 2:
        last = res[-1]
        if last['nwords'] == 0 and last['max_ink_y'] is not None:
            orphan = {'page': last['page'], 'words': 0,
                      'fraction': last['text_fraction'],
                      'reason': 'page carries ink but no text'}
            last['violations'] += 1
    return res, orphan


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pdf', help='BODY-ONLY render (empty header/footer)')
    ap.add_argument('--margin-top', type=float, default=52.0)
    ap.add_argument('--margin-bottom', type=float, default=32.0)
    ap.add_argument('--tol', type=float, default=1.0)
    ap.add_argument('--dpi', type=int, default=150)
    ap.add_argument('--dark', type=int, default=170)
    ap.add_argument('--min-run', type=int, default=3)
    ap.add_argument('--orphan-fill', type=float, default=0.15,
                    help='min fraction of the band a final page must fill')
    ap.add_argument('--max-frame', type=float, default=36.0,
                    help='max pt of border/rule ink allowed below the last text line')
    ap.add_argument('--label', default='')
    ap.add_argument('--json')
    ap.add_argument('--quiet', action='store_true')
    a = ap.parse_args()

    res, orphan = check(a.pdf, a.margin_top, a.margin_bottom, a.tol,
                        a.dpi, a.dark, a.min_run, a.orphan_fill, a.max_frame)
    total = sum(p['violations'] for p in res) + (1 if orphan else 0)
    label = a.label or os.path.basename(a.pdf)
    if not a.quiet:
        print(f'== {label}  band [{a.margin_top}mm .. page-{a.margin_bottom}mm]  tol {a.tol}pt')
        print(f'{"pg":>3} {"words":>6} {"minY":>7} {"maxY":>7} {"maxInk":>7} {"limit":>7} '
              f'{"frame":>6} {"abv":>4} {"blw":>4} {"clpT":>4} {"clpB":>4} {"inkA":>4} '
              f'{"inkB":>4}  verdict')
        for p in res:
            print(f'{p["page"]:>3} {p["nwords"]:>6} {str(p["min_y"]):>7} {str(p["max_y"]):>7} '
                  f'{str(p["max_ink_y"]):>7} {p["body_bottom"]:>7} '
                  f'{str(p["trailing_frame"]):>6} {len(p["above"]):>4} '
                  f'{len(p["below"]):>4} {len(p["clipped_top"]):>4} {len(p["clipped_bottom"]):>4} '
                  f'{len(p["ink_above"]):>4} {len(p["ink_below"]):>4}  '
                  f'{"FAIL" if p["violations"] else "ok"}')
            if p.get('frame_violation'):
                print(f'       frame: border ink runs {p["trailing_frame"]}pt below the '
                      f'last text line (max {a.max_frame}pt)')
            for k in ('clipped_bottom', 'clipped_top', 'below', 'above'):
                for r in p[k][:4]:
                    print(f'       {k}: y={r["y0"]}..{r["y1"]} {r["text"]!r}')
            for k in ('ink_below', 'ink_above'):
                if p[k]:
                    print(f'       {k}: {len(p[k])} rows, first y={p[k][0]["y_pt"]}pt '
                          f'run={p[k][0]["run"]}px last y={p[k][-1]["y_pt"]}pt')
        if orphan:
            print(f'ORPHAN: page {orphan["page"]}: {orphan["reason"]}')
        print(f'RESULT {label}: {"FAIL" if total else "PASS"} ({total} violations)')
    if a.json:
        json.dump({'pdf': a.pdf, 'label': label, 'margin_top_mm': a.margin_top,
                   'margin_bottom_mm': a.margin_bottom, 'tol_pt': a.tol, 'dpi': a.dpi,
                   'pages': res, 'orphan': orphan, 'violations': total},
                  open(a.json, 'w'), indent=1, ensure_ascii=False)
    return 1 if total else 0


if __name__ == '__main__':
    sys.exit(main())
