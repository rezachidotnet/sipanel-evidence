import sys, json
from PyPDF2 import PdfReader
for fn in sys.argv[1:]:
    r = PdfReader(fn); root = r.trailer['/Root'].get_object(); names = root.get('/Names'); names = names.get_object() if names is not None else {}
    out = {'file': fn, 'embedded': []}
    ef = names.get('/EmbeddedFiles')
    if ef is not None:
        ef = ef.get_object()
        arr = ef.get('/Names')
        arr = arr.get_object() if arr is not None else []
        for i in range(0, len(arr), 2):
            name = str(arr[i]); spec = arr[i + 1].get_object(); f = spec.get('/EF').get_object().get('/F').get_object()
            data = f.get_data()
            out['embedded'].append({'name': name, 'size': len(data), 'head': data[:200].decode('utf-8', 'replace')})
    print('EMB_JSON=' + json.dumps(out, ensure_ascii=False))
