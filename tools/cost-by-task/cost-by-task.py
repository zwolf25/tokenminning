"""Claude Code spend per task id, from raw transcripts, reconciled to ccusage (stdlib only).

Usage: python3 cost-by-task.py [--dir ~/.claude/projects] [--ccusage FILE.json] [--tool-prefix P] [--id-field F] [--top 15] [--self-test]
Join key: an id field in tool calls whose name starts with --tool-prefix (default: the author's aiwork MCP
server; point it at your own task tracker's MCP tools). Cost: per-message usage x assumed rates, scaled
per model so the total equals ccusage's dollars for that model. Sub-agent transcripts count toward
the parent session; a session touching N tasks splits its cost N ways.
"""
import argparse, collections, glob, json, os, subprocess, tempfile

RATES = dict(input=1.0, read=0.1, write=1.25, out=5.0)  # x input rate; ponytail: assumed, only per-model total is calibrated


def scan(root, prefix="mcp__aiwork__", field="task_id"):
    """-> {session: {"tasks": set, "w": {model: weighted tokens}}}"""
    ses = collections.defaultdict(lambda: {"tasks": set(), "w": collections.Counter()})
    for p in glob.glob(os.path.join(root, "*", "**", "*.jsonl"), recursive=True):
        rel = os.path.relpath(p, root).split(os.sep)
        s = ses[rel[0] + "/" + rel[1].removesuffix(".jsonl")]  # subagents/ files roll up to parent session
        seen = {}
        for line in open(p, encoding="utf-8", errors="replace"):
            try:
                d = json.loads(line)
            except ValueError:
                continue
            m = d.get("message") or {}
            if d.get("type") != "assistant" or not isinstance(m.get("content"), list):
                continue
            for c in m["content"]:
                if c.get("type") == "tool_use" and str(c.get("name", "")).startswith(prefix):
                    t = (c.get("input") or {}).get(field)
                    if isinstance(t, str) and t:
                        s["tasks"].add(t.lower())
            if m.get("usage") and m.get("model") and m["model"] != "<synthetic>":
                seen[m.get("id") or line] = (m["model"], m["usage"])  # streamed messages repeat; last wins
        for model, u in seen.values():
            i, r, w, o = (u.get(k) or 0 for k in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens", "output_tokens"))
            s["w"][model] += i * RATES["input"] + r * RATES["read"] + w * RATES["write"] + o * RATES["out"]
    return ses


def ccusage_by_model(path):
    if path:
        data = json.load(open(path))
    else:
        data = json.loads(subprocess.run(["ccusage", "daily", "--json", "--breakdown"], capture_output=True, text=True, check=True).stdout)
    tot = collections.Counter()
    for day in data["daily"]:
        for b in day["modelBreakdowns"]:
            tot[b["modelName"]] += b["cost"]
    return tot


def attribute(ses, real):
    """Scale weights per model to ccusage dollars, then split each session over its tasks."""
    raw = collections.Counter()
    for s in ses.values():
        raw.update(s["w"])
    scale = {m: real[m] / raw[m] for m in raw if raw[m]}
    per_task, unattr, sess_cost = collections.Counter(), 0.0, {}
    for k, s in ses.items():
        cost = sum(w * scale.get(m, 0) for m, w in s["w"].items())
        sess_cost[k] = cost
        if s["tasks"]:
            for t in s["tasks"]:
                per_task[t] += cost / len(s["tasks"])
        else:
            unattr += cost
    return per_task, unattr, sess_cost, scale


def report(ses, real, top):
    per_task, unattr, sess_cost, scale = attribute(ses, real)
    attributed = sum(per_task.values())
    total = attributed + unattr
    expected = sum(v for m, v in real.items() if m in scale)  # models never seen in transcripts can't be attributed
    assert abs(total - expected) < 0.01, f"reconcile failed: {total:.2f} vs ccusage {expected:.2f}"
    print(f"{'Task':<10}{'Spend':>10}{'Share':>8}")
    for t, c in per_task.most_common(top):
        print(f"{t:<10}{c:>10.2f}{c / total:>8.1%}")
    n_un = sum(1 for s in ses.values() if not s["tasks"])
    print(f"\nattributed {attributed:.2f} ({attributed / total:.0%}) + unattributed {unattr:.2f} ({unattr / total:.0%}, {n_un} sessions) = {total:.2f}; ccusage {expected:.2f}")
    return per_task, unattr


def self_test():
    d = tempfile.mkdtemp()
    os.makedirs(d + "/proj/sA/subagents")
    def msg(mid, tool=None, out=1000):
        c = [{"type": "tool_use", "name": "mcp__aiwork__get_task", "input": {"task_id": tool}}] if tool else []
        return json.dumps({"type": "assistant", "message": {"id": mid, "model": "m", "content": c, "usage": {"output_tokens": out}}}) + "\n"
    open(d + "/proj/sA.jsonl", "w").write(msg("1", "T1") + msg("1", "T1") + msg("2", "T2"))  # dup id counted once
    open(d + "/proj/sA/subagents/agent-x.jsonl", "w").write(msg("3"))  # rolls into sA
    open(d + "/proj/sB.jsonl", "w").write(msg("4"))  # no task
    per_task, unattr = report(scan(d), {"m": 10.0}, 5)
    assert abs(per_task["t1"] - 3.75) < 1e-9 and abs(per_task["t2"] - 3.75) < 1e-9, "sA (3 msgs) splits over 2 tasks"
    assert abs(unattr - 2.5) < 1e-9, "sB is unattributed"
    print("self-test OK")


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--dir", default=os.path.expanduser("~/.claude/projects"))
    a.add_argument("--ccusage", help="ccusage daily --json --breakdown output (default: run ccusage)")
    a.add_argument("--tool-prefix", default="mcp__aiwork__", help="tool-name prefix of your task tracker's MCP tools")
    a.add_argument("--id-field", default="task_id", help="tool-call input field holding the task id")
    a.add_argument("--top", type=int, default=15)
    a.add_argument("--self-test", action="store_true")
    a = a.parse_args()
    if a.self_test:
        self_test()
    else:
        report(scan(a.dir, a.tool_prefix, a.id_field), ccusage_by_model(a.ccusage), a.top)
