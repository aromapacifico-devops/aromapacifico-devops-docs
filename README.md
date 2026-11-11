# Aroma Pacifico platform documentation

Architecture and technical documentation for the update of the coffee traceability pilot in Cauca, Huila and Tolima.

The platform follows each 60 kg sack from the farm to the port of Buenaventura, monitors crops and drying, and supports a drone service for pest confirmation, fumigation and harvest estimation.

Documents live under `docs/`, grouped by subject.

## PDF of a document

Documents delivered to the Federation carry a PDF next to the Markdown file, in the visual identity of the platform, with a cover, the contents list on its own page and live links. Links to other files of this repository point to their page on GitHub. The PDF is rebuilt in the same pull request that changes the document.

```bash
tools/build-pdf.sh -k "Cost document" -d "Prices of November 2026" docs/governance/pilot-cost.md
```

The script needs pandoc 3 or later and Chromium or Chrome, and it reads the Outfit and Roboto Mono fonts from Google Fonts, so it needs internet access. The logo and the waves of the cover in `tools/pdf/` are cut from `docs/design/aroma-pacifico-branding.pdf`.
