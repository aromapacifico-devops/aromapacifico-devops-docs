#!/usr/bin/env bash
# Builds the PDF of one or more reader documents in the visual identity of the platform,
# with a cover, the contents list of the first document on its own page and live links.
# With several documents each one starts on a new page, and links between them stay
# inside the PDF. Needs pandoc 3 or later, Python 3 and Chromium or Chrome. Fonts come
# from Google Fonts, so the build needs internet access.
# usage: tools/build-pdf.sh [-o out.pdf] [-k kicker] [-s subtitle] [-d date] docs/<path>.md [more.md ...]
# With one document and no -o, the PDF is written next to it with the same name.
set -euo pipefail

root=$(cd "$(dirname "$0")/.." && pwd)
kicker="Aroma Pacifico"
subtitle="Coffee traceability pilot for Cauca, Huila and Tolima"
date=$(LC_ALL=C date +"%B %Y")
pdf=""
while getopts "o:k:s:d:" opt; do
  case "$opt" in
    o) pdf=$(realpath -m "$OPTARG") ;;
    k) kicker=$OPTARG ;;
    s) subtitle=$OPTARG ;;
    d) date=$OPTARG ;;
    *) exit 2 ;;
  esac
done
shift $((OPTIND - 1))
[ $# -ge 1 ] || { echo "usage: tools/build-pdf.sh [-o out.pdf] [-k kicker] [-s subtitle] [-d date] docs/<path>.md [more.md ...]" >&2; exit 2; }
if [ -z "$pdf" ]; then
  [ $# -eq 1 ] || { echo "several documents need -o" >&2; exit 2; }
  pdf=$(realpath "$1")
  pdf=${pdf%.md}.pdf
fi

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

docs=()
for f in "$@"; do docs+=("$(realpath --relative-to="$root" "$f")"); done
included=$(IFS=:; echo "${docs[*]}")
title=$(grep -m1 '^# ' "$root/${docs[0]}" | sed 's/^# //')

parts=()
paths="$root"
for i in "${!docs[@]}"; do
  doc=${docs[$i]}
  anchor="doc-$(echo "${doc%.md}" | sed 's/[^[:alnum:]]/-/g')"
  DOC_DIR=$(dirname "$doc") DOC_PATH=$doc PDF_INCLUDED=$included pandoc "$root/$doc" \
    --from gfm --to json --lua-filter "$root/tools/pdf/links.lua" --output "$work/$i.json"
  parts+=("$anchor:$work/$i.json")
  paths="$paths:$root/$(dirname "$doc")"
done
python3 "$root/tools/pdf/join.py" "$work/joined.json" "${parts[@]}"

pandoc "$work/joined.json" \
  --from json \
  --to html5 \
  --standalone \
  --wrap=none \
  --template "$root/tools/pdf/template.html" \
  --lua-filter "$root/tools/pdf/cover.lua" \
  --css "$root/tools/pdf/style.css" \
  --metadata pagetitle="$title" \
  --metadata kicker="$kicker" \
  --metadata subtitle="$subtitle" \
  --metadata date="$date" \
  --metadata logo="$root/tools/pdf/logo.png" \
  --metadata waves="$root/tools/pdf/waves.png" \
  --embed-resources \
  --resource-path "$paths" \
  --output "$work/page.html"

browser=$(command -v chromium-browser || command -v chromium || command -v google-chrome)
"$browser" --headless=new --disable-gpu --no-pdf-header-footer \
  --virtual-time-budget=15000 \
  --print-to-pdf="$pdf" "file://$work/page.html" 2>/dev/null

echo "PDF written to ${pdf#"$root"/}"
