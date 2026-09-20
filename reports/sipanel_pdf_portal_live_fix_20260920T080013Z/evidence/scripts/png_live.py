import subprocess, os
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
D = '/tmp/sipanel_val'
html = open(f'{D}/report_html_fa_route.html', encoding='utf-8').read().replace('<head>', '<head><base href="http://127.0.0.1:8072/"/>', 1)
open(f'{D}/report_live.html', 'w', encoding='utf-8').write(html)
r = subprocess.run(['wkhtmltoimage', '--quiet', '--encoding', 'utf-8', '--width', '1000', '--javascript-delay', '1500', f'{D}/report_live.html', f'{D}/report_live.png'], capture_output=True, text=True)
im = Image.open(f'{D}/report_live.png').convert('RGB')
w, h = im.size; im = im.resize((900, int(h * 900 / w))); w, h = im.size
bbox = Image.eval(im.convert('L'), lambda p: 255 - p).getbbox()
if bbox: im = im.crop((0, 0, w, min(h, bbox[3] + 40)))
w, h = im.size; n = 0
for y in range(0, h, 1300):
    n += 1; im.crop((0, y, w, min(h, y + 1300))).save(f'{D}/report_live_part{n:02d}.png', optimize=True)
print('rc', r.returncode, 'size', im.size, 'parts', n)
