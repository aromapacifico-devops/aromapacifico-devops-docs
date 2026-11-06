#!/bin/sh
# Exports each page of the diagram source to an editable PNG. Run from this folder.
set -eu
cd ../diagrams
i=1
for name in 01-end-to-end 02-cloud-deployment 03-connectivity-and-centers 04-pest-to-fumigation 05-landing-zone; do
  flatpak run com.jgraph.drawio.desktop --disable-gpu -x -f png -e -b 20 -p "$i" -o "$name.drawio.png" platform-architecture.drawio 2>/dev/null
  i=$((i + 1))
done
