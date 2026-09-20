#!/usr/bin/env python3
"""Root-cause probe: re-render a captured report body with injected CSS variants.

Each variant is rendered with the exact wkhtmltopdf arguments Odoo used, header
and footer emptied, so differences come only from the injected rule.
"""
import argparse, os, re, subprocess, sys

WK = ['/usr/local/bin/wkhtmltopdf', '--disable-local-file-access', '--quiet',
      '--page-size', 'A4', '--margin-top', '52.0', '--dpi', '90',
      '--zoom', '1.0666666666666667', '--header-spacing', '52',
      '--margin-left', '0.0', '--margin-bottom', '32.0', '--margin-right', '0.0',
      '--orientation', 'Portrait', '--javascript-delay', '1000',
      '--header-html', '/tmp/l02_empty.html', '--footer-html', '/tmp/l02_empty.html']

VARIANTS = {
 'V0_baseline': '',
 'V1_no_overlay': '.o_table_boxed-rounded table:not(.o_ignore_layout_styling)::before{display:none !important;}',
 'V2_real_borders': """
.o_table_boxed-rounded table:not(.o_ignore_layout_styling)::before{display:none !important;}
.o_table_boxed-rounded table.o_main_table:not(.o_ignore_layout_styling){border:1px solid #495057 !important;}
""",
 'V3_tr_avoid': 'tbody tr{page-break-inside:avoid !important;}',
 'V4_sig_avoid': '.signature_container,.signature_title{page-break-inside:avoid !important;}',
 'V5_static_table': '.o_table_boxed-rounded table:not(.o_ignore_layout_styling){position:static !important;}',
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('body_html', help='path INSIDE the container')
    ap.add_argument('outdir', help='path INSIDE the container')
    ap.add_argument('--container', default='odoo-sipanel')
    a = ap.parse_args()
    script = r'''
set -e
mkdir -p %(out)s
printf "<html><head><meta charset=\"utf-8\"/></head><body></body></html>" > /tmp/l02_empty.html
''' % {'out': a.outdir}
    for name, css in VARIANTS.items():
        script += f'''
python3 - <<'EOF'
src = open({a.body_html!r}, encoding='utf-8').read()
css = {css!r}
inj = '<style type="text/css">' + css + '</style>' if css else ''
i = src.lower().rfind('</head>')
out = src[:i] + inj + src[i:] if i > 0 else inj + src
open({a.outdir!r} + '/{name}.html', 'w', encoding='utf-8').write(out)
EOF
{' '.join(WK)} {a.outdir}/{name}.html {a.outdir}/{name}.pdf >/dev/null 2>&1 || true
echo "VARIANT {name} $(stat -c%s {a.outdir}/{name}.pdf 2>/dev/null || echo MISSING)"
'''
    subprocess.run(['docker', 'exec', a.container, 'bash', '-c', script], check=True)


if __name__ == '__main__':
    sys.exit(main())
