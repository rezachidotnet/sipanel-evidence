#!/usr/bin/env python3
"""Render a captured report body with arbitrary injected CSS variants (in-container)."""
import json, subprocess, sys

WK = ('/usr/local/bin/wkhtmltopdf --disable-local-file-access --quiet --page-size A4 '
      '--margin-top 52.0 --dpi 90 --zoom 1.0666666666666667 --header-spacing 52 '
      '--margin-left 0.0 --margin-bottom 32.0 --margin-right 0.0 --orientation Portrait '
      '--javascript-delay 1000 --header-html /tmp/l02_empty.html --footer-html /tmp/l02_empty.html')

body, outdir, spec = sys.argv[1], sys.argv[2], json.load(open(sys.argv[3]))
sh = (f'set -e; mkdir -p {outdir}; printf "<html><head><meta charset=\\"utf-8\\"/>'
      f'</head><body></body></html>" > /tmp/l02_empty.html\n')
for name, css in spec.items():
    sh += f'''python3 - <<'EOF'
src = open({body!r}, encoding='utf-8').read()
inj = {('<style type="text/css">' + css + '</style>') if css else ''!r}
i = src.lower().rfind('</head>')
open({outdir!r} + '/{name}.html', 'w', encoding='utf-8').write(src[:i] + inj + src[i:])
EOF
{WK} {outdir}/{name}.html {outdir}/{name}.pdf >/dev/null 2>&1 || true
echo "VARIANT {name} $(stat -c%s {outdir}/{name}.pdf 2>/dev/null || echo MISSING)"
'''
subprocess.run(['docker', 'exec', 'odoo-sipanel', 'bash', '-c', sh], check=True)
