#!/usr/bin/env bash
# Re-render a captured report body with the EXACT wkhtmltopdf arguments Odoo used,
# but with an empty header and footer. Pagination is unchanged (header/footer are
# separate documents), so every mark left inside the margin bands is body ink.
set -euo pipefail
TAG=$1   # before | after
docker exec odoo-sipanel bash -c '
set -e
printf "<html><head><meta charset=\"utf-8\"/></head><body></body></html>" > /tmp/l02_empty.html
cd /tmp/sipanel_1d/'"$TAG"'
for b in *.body.html; do
  k=${b%.body.html}
  /usr/local/bin/wkhtmltopdf --disable-local-file-access --quiet --page-size A4 \
    --margin-top 52.0 --dpi 90 --zoom 1.0666666666666667 --header-spacing 52 \
    --margin-left 0.0 --margin-bottom 32.0 --margin-right 0.0 --orientation Portrait \
    --javascript-delay 1000 --header-html /tmp/l02_empty.html --footer-html /tmp/l02_empty.html \
    "$b" "$k.bodyonly.pdf" >/dev/null 2>&1 || true
  echo "bodyonly $k $(stat -c%s "$k.bodyonly.pdf" 2>/dev/null || echo MISSING)"
done'
