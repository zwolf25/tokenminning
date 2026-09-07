---
name: doc-convert
description: Convert documents locally, without spending model tokens — PDF/DOCX/PPTX/XLSX → Markdown, and Markdown → styled DOCX (using a named style preset, e.g. `default` or `report`). Local, CloudConvert-style tool; runs as a subprocess, so it costs no model tokens. Use when the user says "convert this to markdown", "pdf to md", "docx to markdown", "pptx to markdown", "what's in this deck", "read this presentation", "turn this markdown into a Word doc", "convert to docx", "md to docx", or gives a source file and wants it in the other format. Give it a source path and output path (optionally a style name); it writes the output file and reports only the path — never dumps content into the conversation.
---

# doc-convert

Local, token-free document conversion. Two directions, routed by the **input** file extension:

- **DOCX/XLSX/PPTX/RTF/ODT/ODS/ODP/EPUB/CSV/text-based PDF → Markdown** — via `anydoc_to_md.py` (Firecrawl's AnyDoc library), run through `uv run`. Falls back to `markitdown` for anything AnyDoc doesn't cover (scanned/image-heavy PDFs, HTML, images) or if AnyDoc errors.
- **Markdown → styled DOCX** — via `convert.js`, applying a style preset (default = `styles/default.json`).

**Token rule (do not break):** the conversion happens in a subprocess. Run it, then report the output path + the one-line status the tool prints. **Never read the converted file back into context** — a large document echoed into the chat is thousands of wasted tokens. The user asked for a file on disk, not the content in the conversation.

## Step 1 — Prereq gate (offer the fallback ladder, don't dead-end)

Check what's installed before running:

- **→ Markdown** needs `uv` on PATH (runs AnyDoc via `uv run --with firecrawl-anydoc`, auto-fetched on first use — no separate install step). Test: `uv --version`. For the markitdown fallback path specifically, also needs `markitdown` on PATH. Test: `markitdown --version` (or `which markitdown`).
- **Markdown → DOCX** needs `node` on PATH (plus the global `docx` package). Test: `node --version`.

If a tool is missing, present the ladder — most-preferred first — instead of failing:

1. **Install (primary, token-free going forward):** see this tool's [README.md](README.md) for install commands (`node`/`npm install -g docx`, `uv`, `uv tool install 'markitdown[all]'`).
2. **Fallback (no install, costs tokens):** for **→MD**, `Read` the source file yourself and write the markdown out. For **MD→DOCX** without Node, produce a visually-equivalent reproduction using whatever docx-writing library is available in your environment. Note to the user that this path spends tokens.

## Step 2 — Run the conversion

**Inputs you need:** source path, output path, and (for MD→DOCX) an optional style name.

### DOCX / XLSX / PPTX / RTF / ODT / ODS / ODP / EPUB / CSV / text-based PDF → Markdown
```
uv run --with firecrawl-anydoc --no-project anydoc_to_md.py "<source>" "<output>.md"
```
First run fetches the small `firecrawl-anydoc` package (cached by `uv` after that — no separate install step). If it errors (encrypted/malformed file, or a format it doesn't cover), fall back to markitdown:
```
markitdown "<source>" -o "<output>.md"
```
Also use the markitdown fallback directly for **HTML, images, and scanned/image-heavy PDFs** — AnyDoc doesn't OCR, it only extracts native text. **Complex-layout PDFs (diagrams, whiteboard/Miro exports) come through garbled in both tools** — that's a shared weakness, not fixable by switching engines; say so rather than presenting either output as reliable.

### Markdown → styled DOCX
```
node convert.js "<source>.md" "<output>.docx" [--style <name>]
```
- No `--style` → **default** preset (Arial, the bundled palette, styled tables).
- `--style report` → the `report` preset (available presets live in `styles/*.json`).
- Add a new style by dropping another JSON in `styles/` — see [README.md](README.md).

Handles headings (H1–H3), tables, bold/italic, bullets (nested ≥2 levels), ordered lists, inline `code`, fenced code blocks, links (incl. nested inside bold/italic), images (relative to the .md), blockquotes, and HTML entities in cells. Not yet: H4+.

## Step 3 — Report

State the output path and the tool's one-line result (e.g. `WROTE …docx (10112 bytes, style=default)`). Confirm success. Do not paste the document body.
