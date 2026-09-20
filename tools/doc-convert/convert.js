// Markdown -> styled .docx generator. Single engine for general doc conversion.
// Style is loaded from styles/<name>.json (default: "default"); pass --style <name> to switch.
// Supersedes generate-docx.js (same rendering core; adds preset selection + links/images/blockquotes).
// The MR report pipeline keeps its own docx-generator.js (charts + Council gates) — not this file.
//
// Usage (identical on macOS/Windows/Linux — no shell-specific env-var syntax):
//   node convert.js <input>.md <output>.docx [--style <name>]
//   node convert.js --self-test

const fs = require('fs');
const path = require('path');

// `docx` is installed globally (`npm install -g docx`, see this tool's README) — resolve via the
// global node_modules root if a plain require() can't find it, so no NODE_PATH prefix is needed.
let docxLib;
try {
  docxLib = require('docx');
} catch (e) {
  if (e.code !== 'MODULE_NOT_FOUND') throw e;
  const { execSync } = require('child_process');
  const globalRoot = execSync('npm root -g', { encoding: 'utf8' }).trim();
  docxLib = require(path.join(globalRoot, 'docx'));
}
const { Document, Packer, Paragraph, TextRun, ExternalHyperlink, ImageRun, HeadingLevel,
        Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType, AlignmentType } = docxLib;

// ---- self-test: convert a tiny inline markdown file, assert a valid .docx (zip) comes out ----
if (process.argv.includes('--self-test')) {
  const os = require('os');
  const { execFileSync } = require('child_process');
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'doc-convert-'));
  const md = path.join(dir, 't.md'), out = path.join(dir, 't.docx');
  fs.writeFileSync(md, '# Title\n\nBody **bold**.\n\n| a | b |\n|---|---|\n| 1 | 2 |\n\n- item\n');
  execFileSync(process.execPath, [__filename, md, out], { stdio: 'inherit' });
  const head = fs.readFileSync(out).subarray(0, 2).toString();
  if (head !== 'PK') { console.error('self-test FAILED: output is not a docx (zip)'); process.exit(1); }
  console.log('self-test OK');
  process.exit(0);
}

// ---- args: two positionals (in, out) + optional --style <name> ----
const argv = process.argv.slice(2);
let STYLE = 'default';
const positional = [];
for (let a = 0; a < argv.length; a++) {
  if (argv[a] === '--style') { STYLE = argv[++a]; continue; }
  positional.push(argv[a]);
}
const [SRC, OUT] = positional;
if (!SRC || !OUT) { console.error('Usage: node convert.js <input>.md <output>.docx [--style <name>]'); process.exit(1); }

// ---- style preset ----
const stylesDir = path.join(__dirname, 'styles');
function loadStyle(name) {
  const p = path.join(stylesDir, name + '.json');
  if (!fs.existsSync(p)) {
    if (name !== 'default') { console.error(`Style '${name}' not found, using 'default'.`); return loadStyle('default'); }
    return { font: 'Arial', colors: { dark: '1F2A44', accent: '2E5A88', grey: 'E7ECF3', muted: '5A6472', borderOuter: 'B0B8C4', borderInner: 'D5DCE5', headerText: 'FFFFFF' },
             size: { h1: 30, h2: 24, h3: 21, h4: 19, h5: 18, h6: 18, body: 20, bullet: 20, table: 18, muted: 18 },
             page: { width: 12240, height: 15840, margin: 1080 }, table: { width: 9360 } };
  }
  return JSON.parse(fs.readFileSync(p, 'utf8'));
}
const S = loadStyle(STYLE);
const C = S.colors, SZ = S.size, FONT = S.font, TW = S.table.width;

// Spacing — read from preset or fall back to legacy hardcoded values
const SP = S.spacing || {
  line: 240,             // single spacing
  bodyBefore: 0, bodyAfter: 80,
  bulletBefore: 0, bulletAfter: 40,
  heading1Before: 240, heading1After: 120,
  heading2Before: 220, heading2After: 100,
  heading3Before: 160, heading3After: 80,
  heading4Before: 140, heading4After: 60,
  heading5Before: 120, heading5After: 40,
  heading6Before: 100, heading6After: 20,
  tableBefore: 0, tableAfter: 120
};

// ---- HTML entity decode (5 most common) ----
function decodeEntities(str) {
  return str.replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<').replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"').replace(/&#39;/g, "'");
}

// ---- reflow soft-wrapped lines into one logical line per paragraph/bullet ----
const rawLines = fs.readFileSync(SRC, "utf8").split("\n");
const isBoundary = (l) => { const t = l.trim(); return t === "" || t === "---" || t.startsWith("|") || t.startsWith("#") || t.startsWith(">") || /^!\[.*\]\(.*\)\s*$/.test(t) || t.startsWith("```"); };
const startsBlock = (l) => { const t = l.trim(); return /^[-*]\s/.test(t) || /^\d+\.\s/.test(t); };
const md = [];
let buf = null;
let inFence = false;
const flush = () => { if (buf !== null) { md.push(buf); buf = null; } };
for (const line of rawLines) {
  if (line.trim().startsWith("```")) { flush(); md.push(line); inFence = !inFence; continue; }
  if (inFence) { md.push(line); continue; }
  if (isBoundary(line)) { flush(); md.push(line); continue; }
  if (startsBlock(line)) { flush(); buf = line.trim(); continue; }
  if (buf === null) buf = line.trim(); else buf += " " + line.trim();
}
flush();

// ---- inline markdown -> span objects {text, bold, italics, link, code} ----
function spans(text) {
  const out = []; const re = /(\[[^\]]+\]\([^)]+\)|\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g; let last = 0, m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) out.push({ text: text.slice(last, m.index) });
    const t = m[0];
    if (t.startsWith("[")) {
      const mm = /^\[([^\]]+)\]\(([^)]+)\)$/.exec(t);
      out.push({ text: mm[1], link: mm[2] });
    } else if (t.startsWith("**")) {
      // Recurse to find nested links/code inside bold
      const inner = spans(t.slice(2, -2));
      out.push(...inner.map(s => ({ ...s, bold: true })));
    } else if (t.startsWith("`")) {
      out.push({ text: t.slice(1, -1), code: true });
    } else {
      // Italic — recurse for nested links/code too
      const inner = spans(t.slice(1, -1));
      out.push(...inner.map(s => ({ ...s, italics: true })));
    }
    last = re.lastIndex;
  }
  if (last < text.length) out.push({ text: text.slice(last) });
  return out.length ? out : [{ text }];
}

// span -> TextRun (or ExternalHyperlink wrapping one)
function spanToRun(sp, size, baseColor) {
  const fontName = sp.code ? "Courier New" : FONT;
  const color = sp.code ? C.muted : (sp.link ? C.accent : baseColor);
  const tr = new TextRun({ text: sp.text, bold: sp.bold, italics: sp.italics,
    color, underline: sp.link ? {} : undefined, font: fontName, size: sp.code ? SZ.table : size });
  return sp.link ? new ExternalHyperlink({ children: [tr], link: sp.link }) : tr;
}

const runs = (text, size = SZ.body) => spans(decodeEntities(text)).map(s => spanToRun(s, size));

function splitRow(line) { let s = line.trim(); if (s.startsWith("|")) s = s.slice(1); if (s.endsWith("|")) s = s.slice(0, -1); return s.split("|").map(c => decodeEntities(c.trim())); }
const isSep = (line) => /^\|?[\s:|-]+\|?$/.test(line) && line.includes("-");

function makeTable(rows) {
  const ncol = Math.max(...rows.map(r => r.length));
  const widths = Array(ncol).fill(Math.floor(TW / ncol));
  const trows = rows.map((cells, ri) => new TableRow({
    tableHeader: ri === 0,
    children: Array.from({ length: ncol }, (_, ci) => new TableCell({
      width: { size: widths[ci], type: WidthType.DXA },
      shading: ri === 0 ? { fill: C.accent, type: ShadingType.CLEAR } : (ri % 2 === 0 ? { fill: C.grey, type: ShadingType.CLEAR } : undefined),
      margins: { top: 40, bottom: 40, left: 80, right: 80 },
      children: [new Paragraph({ children: spans(decodeEntities(cells[ci] || "")).map(sp => {
        const color = ri === 0 ? C.headerText : (sp.link ? C.accent : "000000");
        const tr = new TextRun({ text: sp.text, bold: ri === 0 ? true : sp.bold, italics: sp.italics,
          color, underline: sp.link ? {} : undefined, font: FONT, size: SZ.table });
        return sp.link ? new ExternalHyperlink({ children: [tr], link: sp.link }) : tr;
      }) })]
    }))
  }));
  return new Table({
    columnWidths: widths, width: { size: TW, type: WidthType.DXA }, rows: trows,
    borders: {
      top: { style: BorderStyle.SINGLE, size: 4, color: C.borderOuter }, bottom: { style: BorderStyle.SINGLE, size: 4, color: C.borderOuter },
      left: { style: BorderStyle.SINGLE, size: 4, color: C.borderOuter }, right: { style: BorderStyle.SINGLE, size: 4, color: C.borderOuter },
      insideHorizontal: { style: BorderStyle.SINGLE, size: 2, color: C.borderInner }, insideVertical: { style: BorderStyle.SINGLE, size: 2, color: C.borderInner }
    }
  });
}

// ---- image dimensions from PNG/JPEG headers (no dependency); scale to fit content width ----
const MAX_W = 624; // px, ~ content width at 96dpi within 0.75" margins on US Letter
function imageDims(buf) {
  if (buf.length > 24 && buf.readUInt32BE(0) === 0x89504e47) { // PNG
    return { type: "png", w: buf.readUInt32BE(16), h: buf.readUInt32BE(20) };
  }
  if (buf.length > 4 && buf[0] === 0xff && buf[1] === 0xd8) { // JPEG: scan SOF markers
    let o = 2;
    while (o + 9 < buf.length) {
      if (buf[o] !== 0xff) { o++; continue; }
      const mk = buf[o + 1];
      if (mk >= 0xc0 && mk <= 0xcf && mk !== 0xc4 && mk !== 0xc8 && mk !== 0xcc) {
        return { type: "jpg", h: buf.readUInt16BE(o + 5), w: buf.readUInt16BE(o + 7) };
      }
      o += 2 + buf.readUInt16BE(o + 2);
    }
  }
  return null;
}
function imageParagraph(altAndPath) {
  const mm = /^!\[([^\]]*)\]\(([^)]+)\)/.exec(altAndPath.trim());
  const alt = mm[1], rel = mm[2];
  const imgPath = path.isAbsolute(rel) ? rel : path.join(path.dirname(SRC), rel);
  if (!fs.existsSync(imgPath)) return new Paragraph({ spacing: { line: SP.line, after: 80 }, children: [new TextRun({ text: `[image not found: ${rel}]`, italics: true, color: C.muted, font: FONT, size: SZ.muted })] });
  const data = fs.readFileSync(imgPath);
  const dim = imageDims(data);
  if (!dim) return new Paragraph({ spacing: { line: SP.line, after: 80 }, children: [new TextRun({ text: alt || rel, italics: true, color: C.muted, font: FONT, size: SZ.muted })] });
  const scale = dim.w > MAX_W ? MAX_W / dim.w : 1;
  return new Paragraph({ alignment: AlignmentType.CENTER, spacing: { line: SP.line, after: 120 }, children: [new ImageRun({ type: dim.type, data, transformation: { width: Math.round(dim.w * scale), height: Math.round(dim.h * scale) } })] });
}

// ---- main parse loop ----
// figure captions: an italic line directly under an image (blank lines allowed between) centers with it
const captionIdx = new Set();
for (let k = 0; k < md.length; k++) {
  if (!/^!\[.*\]\(.*\)\s*$/.test(md[k].trim())) continue;
  let j = k + 1;
  while (j < md.length && md[j].trim() === "") j++;
  const tt = j < md.length ? md[j].trim() : "";
  if (tt.length > 2 && tt[0] === "*" && tt[1] !== "*" && tt[tt.length - 1] === "*" && tt[tt.length - 2] !== "*") captionIdx.add(j);
}

const children = [];
let i = 0;
while (i < md.length) {
  const line = md[i];
  const t = line.trim();

  // Fenced code block — monospace, light grey background, preserve line breaks
  if (t.startsWith("```")) {
    i++; const codeLines = [];
    while (i < md.length && !md[i].trim().startsWith("```")) {
      const cl = md[i];
      const leading = cl.match(/^(\s*)/)[1];
      codeLines.push(' '.repeat(leading.length) + cl.slice(leading.length).trimEnd() || " ");
      i++;
    }
    if (i < md.length) i++; // skip closing ```
    children.push(new Paragraph({ text: "", spacing: { before: SP.bodyBefore } }));
    for (const cl of codeLines) {
      children.push(new Paragraph({
        spacing: { line: SP.line, after: 0 },
        shading: { fill: C.grey, type: ShadingType.CLEAR },
        children: [new TextRun({ text: cl, font: "Courier New", size: SZ.table, color: "000000" })]
      }));
    }
    children.push(new Paragraph({ text: "", spacing: { after: SP.bodyAfter } }));
    continue;
  }

  // Table
  if (t.startsWith("|") && i + 1 < md.length && isSep(md[i + 1])) {
    const rows = [splitRow(line)]; i += 2;
    while (i < md.length && md[i].trim().startsWith("|")) { rows.push(splitRow(md[i])); i++; }
    children.push(new Paragraph({ text: "", spacing: { before: SP.tableBefore } }));
    children.push(makeTable(rows));
    children.push(new Paragraph({ text: "", spacing: { after: SP.tableAfter } }));
    continue;
  }

  // Blank / horizontal rule
  if (t === "" || t === "---") { i++; continue; }

  // Image
  if (/^!\[.*\]\(.*\)\s*$/.test(t)) { children.push(imageParagraph(t)); i++; continue; }

  // Blockquote
  if (t.startsWith("> ") || t === ">") {
    children.push(new Paragraph({ indent: { left: 360 }, spacing: { line: SP.line, after: SP.bodyAfter },
      children: runs(t.replace(/^>\s?/, ""), SZ.body) }));
    i++; continue;
  }

  // Headings
  if (t.startsWith("# ")) {
    children.push(new Paragraph({ heading: HeadingLevel.HEADING_1,
      spacing: { line: SP.line, before: SP.heading1Before, after: SP.heading1After },
      children: [new TextRun({ text: t.slice(2), bold: true, color: C.dark, font: FONT, size: SZ.h1 })] }));
    i++; continue;
  }
  if (t.startsWith("## ")) {
    children.push(new Paragraph({ heading: HeadingLevel.HEADING_2,
      spacing: { line: SP.line, before: SP.heading2Before, after: SP.heading2After },
      children: [new TextRun({ text: t.slice(3), bold: true, color: C.accent, font: FONT, size: SZ.h2 })] }));
    i++; continue;
  }
  if (t.startsWith("### ")) {
    children.push(new Paragraph({ heading: HeadingLevel.HEADING_3,
      spacing: { line: SP.line, before: SP.heading3Before, after: SP.heading3After },
      children: [new TextRun({ text: t.slice(4), bold: true, color: C.dark, font: FONT, size: SZ.h3 })] }));
    i++; continue;
  }

  // H4–H6
  if (t.startsWith("#### ")) {
    children.push(new Paragraph({ heading: HeadingLevel.HEADING_4,
      spacing: { line: SP.line, before: SP.heading4Before, after: SP.heading4After },
      children: [new TextRun({ text: t.slice(5), bold: true, color: C.dark, font: FONT, size: SZ.h4 })] }));
    i++; continue;
  }
  if (t.startsWith("##### ")) {
    children.push(new Paragraph({ heading: HeadingLevel.HEADING_5,
      spacing: { line: SP.line, before: SP.heading5Before, after: SP.heading5After },
      children: [new TextRun({ text: t.slice(6), bold: true, color: C.muted, font: FONT, size: SZ.h5 })] }));
    i++; continue;
  }
  if (t.startsWith("###### ")) {
    children.push(new Paragraph({ heading: HeadingLevel.HEADING_6,
      spacing: { line: SP.line, before: SP.heading6Before, after: SP.heading6After },
      children: [new TextRun({ text: t.slice(7), bold: true, italics: true, color: C.muted, font: FONT, size: SZ.h6 })] }));
    i++; continue;
  }

  // Bullets — detect nesting from leading whitespace
  if (t.startsWith("- ") || t.startsWith("* ")) {
    const indent = line.match(/^(\s*)[-*]\s/)[1].length;
    const level = Math.floor(indent / 2); // 0 spaces → 0, 2 → 1, 4 → 2
    children.push(new Paragraph({ bullet: { level },
      spacing: { line: SP.line, before: SP.bulletBefore, after: SP.bulletAfter },
      children: runs(t.replace(/^\s*[-*]\s/, ""), SZ.bullet) }));
    i++; continue;
  }

  // Numbered list
  if (/^\d+\.\s/.test(t)) {
    children.push(new Paragraph({ spacing: { line: SP.line, after: SP.bulletAfter },
      children: runs(t.replace(/^\d+\.\s/, ""), SZ.bullet) }));
    i++; continue;
  }

  // Italic subtitle line (centered if it's a figure caption directly under an image)
  if (t.length > 2 && t[0] === "*" && t[1] !== "*" && t[t.length - 1] === "*" && t[t.length - 2] !== "*") {
    children.push(new Paragraph({ alignment: captionIdx.has(i) ? AlignmentType.CENTER : undefined, spacing: { line: SP.line, after: SP.bodyAfter },
      children: [new TextRun({ text: t.slice(1, -1), italics: true, color: C.muted, font: FONT, size: SZ.muted })] }));
    i++; continue;
  }

  // Body paragraph
  children.push(new Paragraph({ spacing: { line: SP.line, before: SP.bodyBefore, after: SP.bodyAfter },
    children: runs(t, SZ.body) }));
  i++;
}

const doc = new Document({ sections: [{
  properties: { page: { size: { width: S.page.width, height: S.page.height }, margin: { top: S.page.margin, bottom: S.page.margin, left: S.page.margin, right: S.page.margin } } },
  children }] });
Packer.toBuffer(doc).then(buf => { fs.writeFileSync(OUT, buf); console.log("WROTE " + OUT + " (" + buf.length + " bytes, style=" + STYLE + ")"); });