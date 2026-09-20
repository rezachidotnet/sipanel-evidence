import subprocess, os
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
D = '/tmp/sipanel_val'
# "before" rendering: same HTML, base href on the currently configured (unresolvable) report.url host
html = open(f'{D}/quotation_dryrun_fixed.html', encoding='utf-8').read().replace('<base href="http://127.0.0.1:8069/"/>', '<base href="http://odoo:8069/"/>', 1)
open(f'{D}/quotation_before_unstyled.html', 'w', encoding='utf-8').write(html)
subprocess.run(['wkhtmltoimage', '--quiet', '--encoding', 'utf-8', '--width', '1000', '--javascript-delay', '1500', f'{D}/quotation_before_unstyled.html', f'{D}/quotation_before_unstyled.png'], capture_output=True)
for tag in ('quotation_dryrun_fixed', 'quotation_before_unstyled'):
    im = Image.open(f'{D}/{tag}.png').convert('RGB')
    w, h = im.size
    scale = 900 / w
    im = im.resize((900, int(h * scale)))
    w, h = im.size
    # crop away trailing blank space
    bbox = Image.eval(im.convert('L'), lambda p: 255 - p).getbbox()
    if bbox: im = im.crop((0, 0, w, min(h, bbox[3] + 40)))
    w, h = im.size
    step = 1300; n = 0
    for y in range(0, h, step):
        part = im.crop((0, y, w, min(h, y + step)))
        n += 1
        part.save(f'{D}/{tag}_part{n:02d}.png', optimize=True)
    print(tag, 'size', im.size, 'parts', n)
