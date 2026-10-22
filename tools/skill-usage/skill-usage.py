"""Skill usage report from the skill-usage-log.sh JSONL log (stdlib only).

Usage: python3 skill-usage.py [--log FILE] [--skills-dir DIR ...] [--rare N] [--self-test]
Prints calls and last-used per skill, then installed skills never used / used <= N times,
with the size of their always-loaded listing entry (name + description chars, measured;
tokens are NOT estimated, divide chars by your own tokenizer ratio).
"""
import argparse, collections, glob, json, os, re, sys, tempfile


def load_log(path):
    calls = collections.defaultdict(lambda: [0, ""])
    for line in open(path, encoding="utf-8", errors="replace"):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        s = d.get("skill")
        if s:
            c = calls[s.split(":")[-1]]  # "plugin:skill" and "skill" count together
            c[0] += 1; c[1] = max(c[1], d.get("ts", ""))
    return calls


def installed(dirs):
    out = {}
    for d in dirs:
        for p in glob.glob(os.path.join(os.path.expanduser(d), "**", "SKILL.md"), recursive=True):
            m = re.match(r"---\n(.*?)\n---", open(p, encoding="utf-8", errors="replace").read(), re.S)
            fm = m.group(1) if m else ""
            n = re.search(r"^name:\s*(.+)$", fm, re.M)
            desc = re.search(r"^description:\s*(.+)$", fm, re.M)
            name = (n.group(1) if n else os.path.basename(os.path.dirname(p))).strip().strip("\"'")
            out[name] = len(name) + (len(desc.group(1)) if desc else 0)
    return out


def report(calls, inst, rare):
    print(f"{'skill':40} {'calls':>6}  last used")
    for s, (n, ts) in sorted(calls.items(), key=lambda x: -x[1][0]):
        print(f"{s:40} {n:6}  {ts[:10]}")
    unused = {s: c for s, c in inst.items() if calls.get(s, [0])[0] <= rare}
    tot = sum(inst.values())
    print(f"\ninstalled {len(inst)}, used {sum(1 for s in inst if s in calls)}, "
          f"never used {sum(1 for s in inst if s not in calls)}, <= {rare} calls {len(unused)}")
    print(f"listing chars: all {tot}, unused/rare {sum(unused.values())} ({100 * sum(unused.values()) // max(tot, 1)}%)")
    for s, c in sorted(unused.items(), key=lambda x: -x[1]):
        print(f"  {s:38} {calls.get(s, [0])[0]:3} calls  {c} chars")


def self_test():
    with tempfile.TemporaryDirectory() as t:
        log = os.path.join(t, "l.jsonl")
        open(log, "w").write('{"ts":"2026-01-02T00:00:00Z","skill":"a"}\n{"ts":"2026-01-03T00:00:00Z","skill":"p:a"}\nbad\n')
        for n in ("a", "b"):
            os.makedirs(os.path.join(t, "s", n))
            open(os.path.join(t, "s", n, "SKILL.md"), "w").write(f"---\nname: {n}\ndescription: hello\n---\n")
        c, i = load_log(log), installed([os.path.join(t, "s")])
        assert c["a"] == [2, "2026-01-03T00:00:00Z"] and i == {"a": 6, "b": 6}, (c, i)
        report(c, i, 0)
    print("self-test OK")


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--log", default=os.environ.get("SKILL_USAGE_LOG", "~/.claude/skill-usage.jsonl"))
    a.add_argument("--skills-dir", action="append", default=None)
    a.add_argument("--rare", type=int, default=0)
    a.add_argument("--self-test", action="store_true")
    o = a.parse_args()
    if o.self_test:
        self_test(); sys.exit()
    report(load_log(os.path.expanduser(o.log)), installed(o.skills_dir or ["~/.claude/skills"]), o.rare)
