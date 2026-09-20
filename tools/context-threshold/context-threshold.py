"""Cost per turn vs context size, from raw Claude Code transcripts (stdlib only).

Usage: python3 context-threshold.py [--dir ~/.claude/projects] [--model SUBSTR] [--self-test]
Prints a bucket table and the knee: first bucket >= 2x the cheapest well-populated
bucket with >= 30% of spend at or above it. Rate ratios are assumed, not real prices.
"""
import argparse, glob, json, os, sys, tempfile

EDGES = [0, 50, 75, 100, 150, 200, 250, 300, 400, 500, 700, float("inf")]  # k tokens
RATES = dict(input=1.0, read=0.1, write=1.25, out=5.0)  # x input rate; ponytail: assumed, calibrate vs ccusage
MIN_TURNS = 100  # "well-populated" bucket


def turns(paths, model):
    for p in paths:
        seen = {}
        for line in open(p, encoding="utf-8", errors="replace"):
            try:
                d = json.loads(line)
            except ValueError:
                continue
            m = d.get("message") or {}
            if d.get("type") != "assistant" or d.get("isSidechain") or not m.get("usage"):
                continue
            if model and model not in (m.get("model") or ""):
                continue
            seen[m.get("id") or line] = m["usage"]  # streamed messages repeat; last wins
        for u in seen.values():
            i, r, w, o = (u.get(k) or 0 for k in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens", "output_tokens"))
            yield i + r + w, i * RATES["input"] + r * RATES["read"] + w * RATES["write"] + o * RATES["out"]


def buckets(rows):
    b = [[0, 0.0] for _ in EDGES[:-1]]
    for ctx, cost in rows:
        k = ctx / 1000
        for j in range(len(b)):
            if EDGES[j] <= k < EDGES[j + 1]:
                b[j][0] += 1; b[j][1] += cost; break
    return b


def report(b):
    total = sum(c for _, c in b) or 1
    means = [c / n if n else 0 for n, c in b]
    base = min((m for (n, _), m in zip(b, means) if n >= MIN_TURNS and m), default=0)
    knee = None
    print(f"{'Context':<10}{'Turns':>8}{'Cost/turn':>11}{'Spend':>8}")
    for j, ((n, c), m) in enumerate(zip(b, means)):
        label = f"{EDGES[j]}k+" if EDGES[j + 1] == float("inf") else f"{EDGES[j]}-{EDGES[j + 1]}k"
        rel = m / base if base and n else 0
        tail = sum(x for _, x in b[j:]) / total
        if knee is None and n >= MIN_TURNS and rel >= 2 and tail >= 0.3:
            knee = EDGES[j]
        print(f"{label:<10}{n:>8}{rel:>10.2f}x{c / total:>8.1%}")
    print(f"knee: {str(knee) + 'k' if knee else 'none found'}")
    return knee


def self_test():
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "s.jsonl"), "w") as f:
        for ctx in [80_000] * 150 + [300_000] * 150:  # cost per turn grows with context
            f.write(json.dumps({"type": "assistant", "message": {"id": str(os.urandom(4)), "model": "m", "usage": {"input_tokens": 0, "cache_read_input_tokens": ctx, "cache_creation_input_tokens": 0, "output_tokens": 100}}}) + "\n")
        f.write(json.dumps({"type": "assistant", "isSidechain": True, "message": {"id": "x", "usage": {"input_tokens": 9}}}) + "\n")
    b = buckets(turns(glob.glob(d + "/*.jsonl"), None))
    assert sum(n for n, _ in b) == 300, "sidechain must be excluded"
    assert report(b) == 300, "knee should be the 300k bucket"
    print("self-test OK")


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--dir", default=os.path.expanduser("~/.claude/projects"))
    a.add_argument("--model")
    a.add_argument("--self-test", action="store_true")
    a = a.parse_args()
    if a.self_test:
        self_test()
    else:
        report(buckets(turns(glob.glob(os.path.join(a.dir, "*", "*.jsonl")), a.model)))
