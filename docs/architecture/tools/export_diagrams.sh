#!/bin/sh
# Exports each page of the diagram source to an editable PNG. Run from this folder.
set -eu
cd ../diagrams
i=1
for name in 00-platform-overview 01-end-to-end 02-implementation-scope 03-connectivity-and-centers 04-pest-to-fumigation 05-landing-zone 06-environments 07-farm-connection-sequence 08-sack-state-model 09-center-wlan 10-drone-mission-link 11-audit-evidence-path 12-lot-geometry-lifecycle 13-center-operation 14-crop-case-states 15-alert-delivery-sequence; do
  flatpak run com.jgraph.drawio.desktop --disable-gpu -x -f png -e -b 20 -p "$i" -o "$name.drawio.png" platform-architecture.drawio 2>/dev/null
  i=$((i + 1))
done
