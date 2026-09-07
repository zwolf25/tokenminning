# doc-convert

Zero-token document conversion. Runs as a local subprocess — no API calls, no model tokens spent on the conversion itself. See [Zero-Token Content Processing](../../examples/document-processing.md) for the case study this was extracted from.

Two directions:
- Any document → Markdown (`anydoc_to_md.py`)
- Markdown → styled DOCX (`convert.js`)

## Install

**For → Markdown:**
```bash
# uv (runs the AnyDoc converter, auto-fetched on first use)
curl -LsSf https://astral.sh/uv/install.sh | sh

# optional fallback, for scanned/image-heavy PDFs, HTML, images
uv tool install 'markitdown[all]'
```

**For Markdown → DOCX:**
```bash
# Node.js, then the docx package
npm install -g docx
```

## Usage

### Convert any document to Markdown

```bash
uv run --with firecrawl-anydoc --no-project anydoc_to_md.py <source> <output>.md
```

Handles DOCX, XLSX, PPTX, RTF, ODT, ODS, ODP, EPUB, CSV, and text-based PDF. Falls back to `markitdown` (if installed) for scanned/image-heavy PDFs, HTML, and images — or if AnyDoc errors on a file:

```bash
markitdown <source> -o <output>.md
```

Complex-layout PDFs (diagrams, whiteboard exports) come through garbled in both tools — that's a shared weakness of text-extraction approaches, not something either engine fixes.

### Convert Markdown to a styled DOCX

```bash
node convert.js <source>.md <output>.docx [--style <name>]
```

- No `--style` → `styles/default.json` (Arial, navy/blue palette, styled tables — see [docx-style-guide.md](docx-style-guide.md)).
- `--style report` → `styles/report.json`, a tighter-spacing variant.
- Add your own: drop a new JSON file in `styles/` following the same shape, then pass `--style <filename-without-extension>`.

Supports headings (H1–H3), tables, bold/italic, bullets (nested), ordered lists, inline code, fenced code blocks, links, images (sized from the file, relative to the source .md), blockquotes, and HTML entities in table cells.

## Why this exists

Reading a large document into an LLM's context just to write it back out in another format burns thousands of tokens for zero reasoning value — the conversion is mechanical, not something that needs a model. This tool does the mechanical part in a subprocess so tokens go to the parts of a task that actually need judgment. See the case study for measured before/after numbers: [examples/document-processing.md](../../examples/document-processing.md).

## Claude Code users

[`SKILL.md`](SKILL.md) packages this as a Claude Code skill, so Claude routes to it automatically on requests like "convert this to markdown" or "turn this into a Word doc." Drop this folder into your skills directory to use it that way; the CLI scripts work standalone regardless of what agent or editor you're using.
