#!/usr/bin/env bash
# One-command report build: render mermaid diagrams -> embed -> generate docs/report.docx
#
# Rendering uses mermaid-cli (Python + Playwright/Chromium) — no Node.js. The first run
# downloads Chromium for Playwright (once, needs network); after that it works offline.
# Diagram text uses a Vietnamese-capable serif (Liberation Serif); drop a times.ttf into
# fonts/ if you want exact Times New Roman inside the diagrams.
#
# Usage:
#   bash scripts/build_report.sh
#   bash scripts/build_report.sh --no-render-mermaid

set -euo pipefail
cd "$(dirname "$0")/.."

# Ensure Playwright's Chromium is present (idempotent; downloads once, needs network).
uv run playwright install chromium >/dev/null 2>&1 || \
  echo "!! Could not ensure Chromium (needs network once); diagrams may be placeholders."

echo ">> Rendering diagrams and building docx…"
uv run python scripts/md_to_docx.py "$@"

echo
echo ">> Done: docs/report.docx"
echo "   - Footer page numbers: automatic."
echo "   - Mục lục / Danh mục bảng / Danh mục hình: open in LibreOffice/Word and update"
echo "     fields (Tools > Update > Update All, or F9) to fill them with page numbers."
