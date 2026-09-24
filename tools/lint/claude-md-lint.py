#!/usr/bin/env python3
"""Deterministic slice of a CLAUDE.md audit (stdlib only, never writes).

Claude Code concatenates every CLAUDE.md it finds into context and nothing overrides anything,
so lines that repeat or dangle are paid for every session. This flags what needs no judgment:
size incl. @imports, missing @imports, missing explicit paths, 3+ line cross-file duplicates,
settings.json pasted as prose. Tiers, not scores. Wishlist, Railroader and contradictions need
a model; run the claude-md-audit skill for those (see ../../examples/second-brain-config-audit.md).

Usage: claude-md-lint.py [FILE ...] [--format json|tsv] [--self-test]
No files = ~/.claude/CLAUDE.md, ~/.claude/rules/*.md, and CLAUDE.md / CLAUDE.local.md from cwd up to /.
"""
import argparse
import re
import sys
import tempfile
from pathlib import Path

from findings import emit, row

WARN_LINES, FLAG_LINES = 200, 300  # Anthropic's target is under 200 per file
DUP_RUN = 3  # a single repeated line is a deliberate pointer/default; 3+ is dead weight
MAX_HOPS = 5  # Claude Code follows imports at most 5 deep
IMPORT_RE = re.compile(r"(?:^|\s)@(\S+)")
CODE_SPAN_RE = re.compile(r"`[^`]*`")
PATH_RE = re.compile(r"(?<![\w/.~])(~/[\w./-]*[\w/]|/(?:Users|home|etc|opt|usr|var|tmp)/[\w./-]*[\w/])")
LEAK_RE = re.compile(r'"(hooks|permissions|env)"\s*:')


def load(path):
    """-> [(lineno, text, in_fence)] with block <!-- comments --> dropped (Claude strips them)."""
    out, in_comment, in_fence = [], False, False
    for n, raw in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        line = raw
        if in_comment:
            if "-->" not in line:
                continue
            line, in_comment = line.split("-->", 1)[1], False
        line = re.sub(r"<!--.*?-->", "", line)
        if "<!--" in line:
            line, in_comment = line.split("<!--", 1)[0], True
        if raw.strip() and not line.strip():
            continue  # line was only a comment
        if line.lstrip().startswith(("```", "~~~")):
            out.append((n, line, True))
            in_fence = not in_fence
            continue
        out.append((n, line, in_fence))
    return out


def imports(path, lines):
    for n, text, fenced in lines:
        if fenced:
            continue
        for m in IMPORT_RE.finditer(CODE_SPAN_RE.sub("", text)):
            target = m.group(1).rstrip(".,;:)")
            if "/" in target or "." in target:
                p = Path(target).expanduser()
                yield n, target, (p if p.is_absolute() else path.parent / p)


def stack(files):
    """Resolve imports -> (ordered unique files, {file: lines}, {file: total lines incl. imports}, missing rows)."""
    data, totals, missing, order = {}, {}, [], []

    def visit(p, hop, chain):
        p = p.resolve()
        if p not in data:
            data[p] = load(p)
            order.append(p)
        total = len(data[p])
        for n, target, imp in imports(p, data[p]):
            if not imp.is_file():
                missing.append(row(p, "stale-import", f"@{target} does not exist", "QUESTION: fix the path or delete the import", n))
            elif hop < MAX_HOPS and imp.resolve() not in chain:
                total += visit(imp, hop + 1, chain | {p})
        totals[p] = max(totals.get(p, 0), total)
        return total

    for f in files:
        visit(Path(f), 0, frozenset())
    return order, data, totals, missing


def check_size(p, total, findings):
    if total > FLAG_LINES:
        findings.append(row(p, "size", f"{total} lines including imports (over {FLAG_LINES})", "QUESTION: move procedures into skills, drop duplicates"))
    elif total > WARN_LINES:
        findings.append(row(p, "size", f"{total} lines including imports (over {WARN_LINES}, adherence drops)", "warning: trim before it grows"))


def exists(raw):
    """Paths with spaces get cut at the space by PATH_RE, so also accept a sibling whose name starts with the cut leaf."""
    p = Path(raw).expanduser()
    return p.exists() or (p.parent.is_dir() and any(c.name.startswith(p.name) for c in p.parent.iterdir()))


def check_stale_paths(p, lines, findings):
    for n, text, fenced in lines:
        if fenced:
            continue
        for m in PATH_RE.finditer(text):
            if "*" not in m.group(1) and not exists(m.group(1)):
                findings.append(row(p, "stale-path", f"`{m.group(1)}` does not exist", "QUESTION: renamed, moved, or deliberately hypothetical?", n))


def check_settings_leak(p, lines, findings):
    fence, start = [], None
    for n, text, fenced in lines:
        if fenced and text.lstrip().startswith(("```", "~~~")):
            if start is None:
                start, fence = n, []
            else:
                if LEAK_RE.search("\n".join(fence)):
                    findings.append(row(p, "settings-leak", "settings.json content (hooks/permissions/env) pasted as prose", "belongs in settings.json, not CLAUDE.md", start))
                start = None
        elif fenced and start is not None:
            fence.append(text)


def norm_lines(lines):
    out = []
    for n, text, _ in lines:
        t = " ".join(text.lower().split())
        if len(t) >= 12 and not re.fullmatch(r"[-|:=# *_>]+", t):
            out.append((n, t))
    return out


def check_duplicates(order, data, findings):
    norm = {p: norm_lines(data[p]) for p in order}
    for ai, a in enumerate(order):
        for b in order[ai + 1:]:
            where = {}
            for j, (_, t) in enumerate(norm[b]):
                where.setdefault(t, []).append(j)
            A, B = norm[a], norm[b]
            for i in range(len(A)):
                for j in where.get(A[i][1], []):
                    if i and j and A[i - 1][1] == B[j - 1][1]:
                        continue  # not the start of a run
                    k = 0
                    while i + k < len(A) and j + k < len(B) and A[i + k][1] == B[j + k][1]:
                        k += 1
                    if k >= DUP_RUN:
                        findings.append(row(a, "duplicate", f"lines {A[i][0]}-{A[i + k - 1][0]} repeat in {b} lines {B[j][0]}-{B[j + k - 1][0]}: \"{A[i][1][:60]}\"", "QUESTION: both copies load; keep one and point to it", A[i][0]))


def tier(n):
    return "Strong" if n == 0 else "Functional" if n <= 2 else "Needs work"


def lint(files):
    order, data, totals, findings = stack(files)
    for p in order:
        check_size(p, totals[p], findings)
        check_stale_paths(p, data[p], findings)
        check_settings_leak(p, data[p], findings)
    check_duplicates(order, data, findings)
    # ponytail: contradictions (A says X, B says not-X) need judgment; left to the claude-md-audit skill
    for p in order:
        n = sum(1 for f in findings if f["dimension"] != "tier" and (f["file"] == str(p) or (f["dimension"] == "duplicate" and f"in {p} " in f["detail"])))
        findings.append(row(p, "tier", f"{tier(n)} ({n} flags, {totals[p]} lines incl. imports)", "tiers, not scores"))
    return findings


def discover():
    home, cwd = Path.home(), Path.cwd()
    cand = [home / ".claude" / "CLAUDE.md", *sorted((home / ".claude" / "rules").glob("*.md"))]
    for d in [*cwd.parents][::-1] + [cwd]:
        cand += [d / "CLAUDE.md", d / "CLAUDE.local.md"]
    seen, out = set(), []
    for c in cand:
        if c.is_file() and c.resolve() not in seen:
            seen.add(c.resolve())
            out.append(c)
    return out


def self_test():
    d = Path(tempfile.mkdtemp())
    (d / "imp.md").write_text("imported line one is here\n" * 2)
    dup = "\n".join(f"shared rule number {i} is stated here" for i in range(3))
    (d / "a.md").write_text(
        f"# A\n@imp.md and `@notimport.md` and mail me@x.com\n@gone.md\n<!-- block\ncomment -->\n{dup}\n"
        "one repeated single line stays exempt\nSee `/Users/nobody-here/x` and ~/definitely-missing-dir/f.md\n"
        '```json\n{"hooks": {}}\n```\n'
    )
    (d / "My Notes Dir").mkdir()  # path with spaces: `d/My` is cut at the space but must not be flagged
    (d / "spaced.md").write_text(f"see `{d}/My Notes Dir/x`\n")
    assert not [x for x in lint([d / "spaced.md"]) if x["dimension"] == "stale-path"], "spaced path is a false positive"
    (d / "b.md").write_text(f"# B\n{dup}\none repeated single line stays exempt\n")
    (d / "big.md").write_text("filler line number x\n" * 250)
    f = lint([d / "a.md", d / "b.md"])
    dims = sorted(x["dimension"] for x in f)
    assert dims.count("stale-import") == 1 and "notimport" not in str(f), "@ in backticks/emails is not an import; only @gone.md is missing"
    assert dims.count("stale-path") == 2, "both missing explicit paths flagged"
    assert dims.count("settings-leak") == 1
    assert dims.count("duplicate") == 1, "3-line run flagged once; 1-line repeat exempt"
    tiers = {Path(x["file"]).name: x["detail"].split(" (")[0] for x in f if x["dimension"] == "tier"}
    assert tiers["a.md"] == "Needs work" and tiers["b.md"] == "Functional" and tiers["imp.md"] == "Strong", tiers
    a_total = next(x for x in f if x["dimension"] == "tier" and x["file"].endswith("a.md"))["detail"]
    assert "13 lines" in a_total, f"comment lines dropped, 2 imported lines counted: {a_total}"
    big = lint([d / "big.md"])
    assert [x["dimension"] for x in big if x["dimension"] == "size"] == ["size"] and big[-1]["detail"].startswith("Functional")
    print("self-test OK")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*")
    ap.add_argument("--format", choices=("json", "tsv"), default="json")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    files = [Path(f) for f in a.files] or discover()
    missing = [f for f in files if not f.is_file()]
    if missing or not files:
        print(f"error: {'missing ' + str(missing[0]) if missing else 'no CLAUDE.md files found'}", file=sys.stderr)
        return 2
    emit(lint(files), a.format)
    return 0


if __name__ == "__main__":
    sys.exit(main())
