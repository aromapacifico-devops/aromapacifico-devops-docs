#!/usr/bin/env bash
# Builds the PDF of a reader document in the visual identity of the platform, with
# a cover, the contents list of the document as its first page and live links.
# Needs pandoc 3 or later and Chromium or Chrome. Fonts come from Google Fonts, so
# the build needs internet access.
# usage: tools/build-pdf.sh [-k kicker] [-s subtitle] [-d date] docs/<path>.md
# The PDF is written next to the Markdown file with the same name.
set -euo pipefail

root=$(cd "$(dirname "$0")/.." && pwd)
kicker="Aroma Pacifico"
subtitle="Coffee traceability pilot for Cauca, Huila and Tolima"
date=$(LC_ALL=C date +"%B %Y")
while getopts "k:s:d:" opt; do
  case "$opt" in
    k) kicker=$OPTARG ;;
    s) subtitle=$OPTARG ;;
    d) date=$OPTARG ;;
    *) exit 2 ;;
  esac
done
shift $((OPTIND - 1))
[ $# -eq 1 ] || { echo "usage: tools/build-pdf.sh [-k kicker] [-s subtitle] [-d date] docs/<path>.md" >&2; exit 2; }

src=$(realpath "$1")
pdf=${src%.md}.pdf
title=$(grep -m1 '^# ' "$src" | sed 's/^# //')
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT; [ -n "${KEEP_HTML:-}" ] && trap 'cp "$work/page.html" "$KEEP_HTML"; rm -rf "$work"' EXIT

DOC_DIR=$(realpath --relative-to="$root" "$(dirname "$src")") pandoc "$src" \
  --from gfm \
  --to html5 \
  --standalone \
  --wrap=none \
  --template "$root/tools/pdf/template.html" \
  --lua-filter "$root/tools/pdf/filter.lua" \
  --css "$root/tools/pdf/style.css" \
  --metadata pagetitle="$title" \
  --metadata kicker="$kicker" \
  --metadata subtitle="$subtitle" \
  --metadata date="$date" \
  --metadata logo="$root/tools/pdf/logo.png" \
  --metadata waves="$root/tools/pdf/waves.png" \
  --embed-resources \
  --resource-path "$(dirname "$src"):$root" \
  --output "$work/page.html"

browser=$(command -v chromium-browser || command -v chromium || command -v google-chrome)
"$browser" --headless=new --disable-gpu --no-pdf-header-footer \
  --virtual-time-budget=15000 \
  --print-to-pdf="$pdf" "file://$work/page.html" 2>/dev/null

echo "PDF written to ${pdf#"$root"/}"
