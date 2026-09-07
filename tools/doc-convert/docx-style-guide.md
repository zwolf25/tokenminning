# Global .docx Style Guide

Default visual identity for every `.docx` file this tool produces — unless you explicitly ask for different styling in a given request (e.g. a client template, a letterhead-driven brand doc). Adapted from a real production style guide, kept generic here as a starting point to fork. This file carries only the visually-generic parts forward: palette, typography, table styling — swap the values below for your own brand and drop a new preset in `styles/` (see [README.md](README.md)).

---

## Color Palette

| Token | Hex | Used for |
|---|---|---|
| `DARK` | `#1F2A44` | H1 text, H3 text |
| `ACCENT` | `#2E5A88` | H2 text, table header background |
| `GREY` | `#E7ECF3` | Table even-row background (alternating) |
| `MUTED` | `#5A6472` | Italic subtitle lines, footer text |
| Table border outer | `#B0B8C4` | Outer table borders (4 DXA) |
| Table border inner | `#D5DCE5` | Inner cell borders (2 DXA) |
| Table header text | `#FFFFFF` | White on `ACCENT` header rows |

---

## Word Document Typography

| Element | Size | Weight | Color | Spacing (before / after DXA) |
|---------|------|--------|-------|-------------------------------|
| Page | US Letter 12240×15840 DXA | — | — | Margins: 1080 DXA (0.75") all sides |
| Font | Arial | — | — | Used throughout |
| H1 | 15pt | Bold | `#1F2A44` | 240 / 120 |
| H2 | 12pt | Bold | `#2E5A88` | 220 / 100 |
| H3 | 10.5pt | Bold | `#1F2A44` | 160 / 80 |
| H4 | 9.5pt | Bold | `#1F2A44` | 140 / 60 |
| H5 | 9pt | Bold | `#5A6472` | 120 / 40 |
| H6 | 9pt | Bold Italic | `#5A6472` | 100 / 20 |
| Body | 10pt | Normal | `#000000` | 0 / 120 |
| Bullet | 10pt | Normal | `#000000` | 0 / 60 |
| Italic line (subtitle/footer) | 9pt | Italic | `#5A6472` | 0 / 80 |

Sizes above are effective points. The style preset (`styles/default.json`) stores docx half-points (2× the values shown here, e.g. 30 = 15pt).

---

## Table Styling

| Element | Spec |
|---------|------|
| Header row background | `#2E5A88` |
| Header text | White (`#FFFFFF`), 9pt bold |
| Even data rows | `#E7ECF3` background |
| Odd data rows | White (no shading) |
| Data cell text | 10pt, `#000000` |
| Cell margins | 40 DXA top/bottom, 80 DXA left/right |
| Outer borders | SINGLE, 4 DXA, `#B0B8C4` |
| Inner borders | SINGLE, 2 DXA, `#D5DCE5` |
| Table width | 9360 DXA (full text width within margins) |
| Column widths | Evenly distributed (9360 ÷ N columns) unless overridden |

**No prose-heavy cells:** cells with >20 words produce unreadable columns in Word. Convert to bullet lists outside the table.

---

## How to apply

- **Markdown → docx conversions:** use `convert.js` (this same folder): `node convert.js <input>.md <output>.docx [--style <name>]`. Implements every value above.
- **Escape hatch:** this guide is a default, not a hard constraint — fork it, or add a new JSON preset to `styles/` for a different look, per-project.
