# Windows counterpart of export_diagrams.sh. Exports each page of the diagram source to an editable PNG. Run from this folder.
$ErrorActionPreference = "Stop"
$drawio = Join-Path $env:LOCALAPPDATA "Programs\draw.io\draw.io.exe"
if (-not (Test-Path $drawio)) { $drawio = "draw.io" }
$names = "00-platform-overview", "01-end-to-end", "02-implementation-scope", "03-connectivity-and-centers", "04-pest-to-fumigation", "05-landing-zone", "06-environments", "07-farm-connection-sequence", "08-sack-state-model", "09-center-wlan", "10-drone-mission-link", "11-audit-evidence-path", "12-lot-geometry-lifecycle", "13-center-operation"
Set-Location (Join-Path $PSScriptRoot "..\diagrams")
for ($i = 0; $i -lt $names.Count; $i++) {
  & $drawio --disable-gpu -x -f png -e -b 20 -p ($i + 1) -o "$($names[$i]).drawio.png" platform-architecture.drawio
}
