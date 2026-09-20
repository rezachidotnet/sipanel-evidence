import sys, json, re, io
from PyPDF2 import PdfReader
from pdfminer.high_level import extract_text
MARK = sys.argv[1]; files = sys.argv[2:]
COSTS = ['731000', '731,000', '9876', '9,876', '55555', '55,555', '4321', '4,321', '8765000', '8,765,000', '18144382', '18,144,382', '10355618', '10,355,618', '36.34', '237024', '333330', '34568']
INTERNAL_WORDS = ['margin', 'cost', 'Cost', 'Margin', 'analytic', 'Analytic', 'sealed_hash', 'seal', 'recognition', 'supplier', 'Supplier', 'INTERNAL', 'access_token', '/opt/odoo', '/mnt/extra-addons', 'standard_price', 'unit_cost', 'occurrence_uid', 'scope_uid', 'audit']
for fn in files:
    r = PdfReader(fn)
    info = {'file': fn, 'pages': len(r.pages), 'metadata': {k: str(v) for k, v in (r.metadata or {}).items()}, 'encrypted': r.is_encrypted}
    fonts = set(); annots = []; js = False
    for i, p in enumerate(r.pages):
        res = p.get('/Resources'); res = res.get_object() if res is not None else {}
        fd = res.get('/Font'); fd = fd.get_object() if fd is not None else {}
        for k in fd:
            try: fonts.add(str(fd[k].get_object().get('/BaseFont')))
            except Exception as e: fonts.add('?' + str(e))
        an = p.get('/Annots'); an = an.get_object() if an is not None else []
        for a in an:
            try:
                a = a.get_object(); annots.append({'page': i + 1, 'subtype': str(a.get('/Subtype')), 'uri': str((a.get('/A') or {}).get('/URI', ''))[:120]})
            except Exception: pass
    root = r.trailer['/Root'].get_object()
    names = root.get('/Names'); names = names.get_object() if names is not None else {}
    info['fonts'] = sorted(fonts); info['annots'] = annots
    info['embedded_files'] = ('/EmbeddedFiles' in names)
    info['has_javascript'] = bool(root.get('/OpenAction')) or ('/JavaScript' in names)
    info['has_xmp_metadata'] = bool(root.get('/Metadata'))
    txt = extract_text(fn)
    pages_txt = [extract_text(fn, page_numbers=[i]) for i in range(len(r.pages))]
    info['text_len'] = len(txt)
    info['marker_hits'] = [m for m in re.findall(r'INTERNAL-MARKER-[A-Z\-]+-' + MARK, txt)]
    info['cost_hits'] = [c for c in COSTS if c in txt.replace('٬', ',').replace('،', ',')]
    info['internal_word_hits'] = {w: txt.count(w) for w in INTERNAL_WORDS if w in txt}
    info['token_like'] = re.findall(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', txt)
    info['sha_like'] = re.findall(r'\b[0-9a-f]{40,64}\b', txt)
    info['persian_chars'] = len(re.findall(r'[؀-ۿ]', txt))
    info['presentation_forms'] = len(re.findall(r'[ﭐ-﷿ﹰ-﻿]', txt))
    info['expect'] = {k: (k in txt) for k in ['SI-26/312', 'QUOTATION', '31,350,000', '28,500,000', '2,850,000', '2,500,000', '12.00', '5.00', '10%', 'm', 'Units', 'Hours']}
    with open(fn + '.txt', 'w') as f:
        for i, t in enumerate(pages_txt): f.write(f'===== PAGE {i+1} =====\n{t}\n')
    print('PDF_JSON=' + json.dumps(info, ensure_ascii=False))
