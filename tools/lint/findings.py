"""Shared findings framework for vault-lint and claude-md-lint (stdlib only).

One finding = {file, dimension, detail, proposed_fix} (+ optional line). Linters only report;
callers decide what to apply. `proposed_fix` starts with AUTO-RESOLVE (fix fully determined) or
QUESTION (needs a human/model judgment); anything else is a plain direction.
"""
import json
import re


def parse_frontmatter(text):
    """Hand-rolled frontmatter parse (no YAML dep). Returns (fields dict or None, body_text).
    A field's value is a str, or a list[str] for either array style (`key: [a, b]`) or
    block style (`key:\\n  - a\\n  - b`)."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, text
    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return None, text
    fm_lines = lines[1:end_idx]
    body = "\n".join(lines[end_idx + 1:])

    fields = {}
    i = 0
    while i < len(fm_lines):
        line = fm_lines[i]
        if not line.strip() or line.strip().startswith("#"):
            i += 1
            continue
        m = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if not m:
            i += 1
            continue
        key, value = m.group(1), m.group(2).strip()
        if value == "":
            items = []
            i += 1
            while i < len(fm_lines) and fm_lines[i].strip().startswith("- "):
                items.append(fm_lines[i].strip()[2:].strip().strip('"').strip("'"))
                i += 1
            fields[key] = items if items else ""
            continue
        elif value.startswith("[") and value.endswith("]"):
            inner = value[1:-1]
            fields[key] = [v.strip().strip('"').strip("'") for v in inner.split(",") if v.strip()]
        else:
            fields[key] = value.strip('"').strip("'")
        i += 1
    return fields, body


def row(path, dimension, detail, proposed_fix, line=None):
    r = {"file": str(path), "dimension": dimension, "detail": detail, "proposed_fix": proposed_fix}
    if line is not None:
        r["line"] = line
    return r


def emit(findings, fmt="json"):
    if fmt == "json":
        print(json.dumps(findings, indent=2))
    else:
        for f in findings:
            loc = f["file"] + (f":{f['line']}" if "line" in f else "")
            print("\t".join([loc, f["dimension"], f["detail"], f["proposed_fix"]]))
