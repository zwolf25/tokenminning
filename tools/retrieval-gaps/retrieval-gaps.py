#!/usr/bin/env python3
"""Mine Claude Code transcripts for retrieval-miss corrections. Stdlib only.

A candidate = a real user message (not tool_result, not scheduled-task/system text)
that matches a "you should have looked there" pattern. Prints one line per hit
with date, project dir, and the preceding assistant search tools, for hand review.
"""
import glob, json, os, re, sys
from datetime import datetime, timedelta, timezone

PAT = re.compile(
    r"(check (the )?[\w\-\. ]{0,40}\bwiki|it'?s in (the |my )?[\w\-\. ]{0,40}(wiki|vault|file|folder|note)|"
    r"look (in|at) (the )?[\w\-\. ]{0,40}(wiki|vault|folder)|you (missed|didn'?t (find|see|check|look))|"
    r"didn'?t you (see|check|find|read)|(should|could) have (found|checked|looked|read)|"
    r"we (already )?(have|wrote|documented) (this|that|it)|already (in|documented in) (the |my )?[\w\-\. ]{0,40}(wiki|vault)|"
    r"search (the |my )?(wiki|vault|second brain))", re.I)
SKIP = re.compile(r"^(<scheduled-task|<system-reminder|<command-|<local-command|\[Request interrupted|Caveat:)", re.I)
SEARCH_TOOLS = {"Grep", "Glob", "Read"}


def user_text(d):
    m = d.get("message", {}).get("content")
    if isinstance(m, str):
        return m
    if isinstance(m, list):
        if any(b.get("type") == "tool_result" for b in m):
            return ""
        return "\n".join(b.get("text", "") for b in m if b.get("type") == "text")
    return ""


def mine(root, days):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    hits = []
    for f in glob.glob(os.path.join(root, "*", "*.jsonl")):
        proj = os.path.basename(os.path.dirname(f))
        last_tools = []
        for line in open(f, errors="replace"):
            try:
                d = json.loads(line)
            except ValueError:
                continue
            ts = d.get("timestamp")
            if d.get("type") == "assistant":
                for b in d.get("message", {}).get("content", []) or []:
                    if isinstance(b, dict) and b.get("type") == "tool_use":
                        inp = b.get("input", {})
                        arg = inp.get("pattern") or inp.get("file_path") or inp.get("command", "")[:60]
                        last_tools = (last_tools + [f"{b['name']}:{str(arg)[:50]}"])[-4:]
            elif d.get("type") == "user" and ts:
                t = user_text(d).strip()
                if not t or SKIP.match(t) or len(t) > 1500:
                    continue
                try:
                    when = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                except ValueError:
                    continue
                if when < cutoff:
                    continue
                m = PAT.search(t)
                if m:
                    hits.append((when.date().isoformat(), proj[-30:], m.group(0), t[:200].replace("\n", " "), last_tools))
    return sorted(hits)


def self_test():
    import tempfile
    assert PAT.search("you missed the pricing wiki")
    assert PAT.search("it's in the competitors wiki")
    assert not PAT.search("write a haiku")
    assert SKIP.match("<scheduled-task name=x>")
    now = datetime.now(timezone.utc).isoformat()
    old = (datetime.now(timezone.utc) - timedelta(days=400)).isoformat()
    rows = [
        {"type": "assistant", "timestamp": now, "message": {"content": [
            {"type": "tool_use", "name": "Grep", "input": {"pattern": "pricing"}}]}},
        {"type": "user", "timestamp": now, "message": {"content": "it's in the pricing wiki, check the wiki"}},
        {"type": "user", "timestamp": now, "message": {"content": [{"type": "tool_result", "content": "you missed it"}]}},
        {"type": "user", "timestamp": old, "message": {"content": "you missed the wiki"}},
        {"type": "user", "timestamp": now, "message": {"content": "<scheduled-task> you missed the wiki"}},
    ]
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "proj"))
        with open(os.path.join(d, "proj", "s.jsonl"), "w") as f:
            f.write("\n".join(json.dumps(r) for r in rows))
        hits = mine(d, 90)
    assert len(hits) == 1, hits  # tool_result, old, and scheduled-task rows are ignored
    assert hits[0][4] == ["Grep:pricing"], hits
    print("ok")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
        sys.exit()
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 90
    root = os.path.expanduser(os.environ.get("CLAUDE_PROJECTS_DIR", "~/.claude/projects"))
    hits = mine(root, days)
    print(f"{len(hits)} candidate hits in last {days} days")
    for h in hits:
        print(f"{h[0]} | {h[1]} | {h[2]!r}\n   {h[3]}\n   prior: {h[4]}")
