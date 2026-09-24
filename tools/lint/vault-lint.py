#!/usr/bin/env python3
"""Deterministic hygiene checks for a folder of markdown wikis (stdlib only, never writes).

Checks that need no model judgment: required frontmatter fields, broken [[wikilinks]],
required top-level sections present and in order, and a `## Recap` on large files that sits
last. A model then only Reads the files this flags. See ../../examples/vault-lint-case-study.md.

Usage: vault-lint.py <wikis-dir> [--require-fields description] [--require-sections "Overview,Key Facts"]
                     [--recap-chars 15000] [--format json|tsv] [--self-test]
"""
import argparse
import re
import sys
import tempfile
from pathlib import Path

from findings import emit, parse_frontmatter, row

WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)")
TOP_HEADING_RE = re.compile(r"^## (.+)$", re.MULTILINE)


def find_wikilinks(text):
    return [m.group(1).split("|")[0].split("#")[0].strip() for m in WIKILINK_RE.finditer(text)]


def check_frontmatter(path, fields, required, findings):
    if fields is None:
        if required:
            findings.append(row(path, "frontmatter", "missing or malformed frontmatter block", "manual Read required"))
        return
    for key in required:
        # presence, not truthiness: an empty `topics: []` is a valid "nothing related yet"
        if key not in fields:
            findings.append(row(path, "frontmatter", f"missing required field: {key}", f"add {key}"))


def check_broken_links(path, fields, body, valid_targets, findings):
    targets = []
    for v in (fields or {}).values():
        targets += find_wikilinks(" ".join(v) if isinstance(v, list) else v)
    targets += find_wikilinks(body)
    for t in sorted(set(targets)):
        if t and t not in valid_targets:
            findings.append(row(path, "broken-link", f"[[{t}]] does not resolve", "QUESTION: typo, deleted page, or needs creating?"))


def check_sections(path, headings, required, findings):
    for req in required:
        if req not in headings:
            findings.append(row(path, "section-structure", f"missing required section: {req}", f"add ## {req}"))
    present = [h for h in headings if h in required]
    order = [required.index(h) for h in present]
    if order != sorted(order):
        findings.append(row(path, "section-structure", f"required sections out of order: {', '.join(present)}", f"reorder to: {', '.join(required)}"))


def check_recap(path, text, headings, recap_chars, findings):
    if not recap_chars:
        return
    if len(text) > recap_chars and "Recap" not in headings:
        findings.append(row(path, "recap-presence", f"{len(text)} chars, over {recap_chars}, no ## Recap", "QUESTION: draft a Recap from the key facts"))
    if "Recap" in headings and headings[-1] != "Recap":
        findings.append(row(path, "recap-position", "## Recap exists but is not the last ## heading", "AUTO-RESOLVE: move Recap to the end"))


def run(root, require_fields=("description",), require_sections=(), recap_chars=0):
    if not root.is_dir():
        raise FileNotFoundError(f"wikis dir not found: {root}")
    findings = []
    valid_targets = {p.stem for p in root.rglob("*.md")}
    for p in sorted(root.glob("*.md")):
        if p.name.startswith("_"):
            continue
        try:  # one bad file becomes a row; the scan continues
            text = p.read_text(encoding="utf-8", errors="replace")
            fields, body = parse_frontmatter(text)
            headings = [h.strip() for h in TOP_HEADING_RE.findall(body)]
            check_frontmatter(p, fields, require_fields, findings)
            check_broken_links(p, fields, body, valid_targets, findings)
            check_sections(p, headings, list(require_sections), findings)
            check_recap(p, text, headings, recap_chars, findings)
        except Exception as e:
            findings.append(row(p, "parse-error", str(e), "manual Read required"))
    return findings


def self_test():
    d = Path(tempfile.mkdtemp())
    ok = "---\ndescription: d\ntopics: []\n---\n## Overview\nx\n## Key Facts\ny\n## Recap\nz\n"  # empty topics is valid
    (d / "ok.md").write_text(ok)
    (d / "nofm.md").write_text("## Overview\n## Key Facts\n")
    (d / "nodesc.md").write_text("---\ntype: t\n---\n## Overview\n## Key Facts\n")
    (d / "link.md").write_text("---\ndescription: d\n---\n## Overview\nsee [[ok]] [[ok|alias]] [[missing]]\n## Key Facts\n")
    (d / "order.md").write_text("---\ndescription: d\n---\n## Key Facts\n## Overview\n")
    (d / "big.md").write_text("---\ndescription: d\n---\n## Overview\n## Key Facts\n" + "x" * 100)
    (d / "recap.md").write_text("---\ndescription: d\n---\n## Overview\n## Recap\n## Key Facts\n")
    (d / "_skip.md").write_text("no frontmatter, ignored")
    f = run(d, ("description",), ("Overview", "Key Facts"), recap_chars=50)
    got = sorted((Path(x["file"]).name, x["dimension"]) for x in f)
    want = sorted([
        ("nofm.md", "frontmatter"), ("nodesc.md", "frontmatter"), ("link.md", "broken-link"), ("link.md", "recap-presence"),
        ("order.md", "section-structure"), ("big.md", "recap-presence"),
        ("recap.md", "recap-position"),
    ])
    assert got == want, f"unexpected findings:\n{got}\n{want}"
    assert run(d) and not any(x["dimension"] in ("section-structure", "recap-presence") for x in run(d)), "structure checks are opt-in"
    print("self-test OK")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("wikis_dir", nargs="?")
    ap.add_argument("--require-fields", default="description", help="comma-separated frontmatter keys that must exist ('' to skip)")
    ap.add_argument("--require-sections", default="", help="comma-separated ## headings that must exist, in this order")
    ap.add_argument("--recap-chars", type=int, default=0, help="files over this many chars need a trailing ## Recap (0 = off)")
    ap.add_argument("--format", choices=("json", "tsv"), default="json")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.wikis_dir:
        ap.error("wikis_dir is required")
    split = lambda s: tuple(x.strip() for x in s.split(",") if x.strip())
    try:
        findings = run(Path(a.wikis_dir), split(a.require_fields), split(a.require_sections), a.recap_chars)
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    emit(findings, a.format)
    return 0


if __name__ == "__main__":
    sys.exit(main())
