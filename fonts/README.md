# Fonts for diagram rendering

Place a **Times New Roman** `.ttf` here (e.g. `times.ttf`) so mermaid diagrams render
with the correct font. `scripts/md_to_docx.py` points fontconfig at this folder at render
time — **nothing is installed on the machine**, which suits a server.

- Only used to draw text inside the mermaid diagram images.
- The `.docx` itself just stores the font name "Times New Roman"; Word / Google Docs
  render it with their own copy, so this file is not needed for the document text.
- The font file is **not committed** (Times New Roman is proprietary — supply your own
  licensed copy, e.g. from a Windows/Office install at `C:\Windows\Fonts\times.ttf`).

Any filename ending in `.ttf`/`.otf` in this folder is picked up.
