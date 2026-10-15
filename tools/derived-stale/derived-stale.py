"""Content-hash staleness for derived documents (stdlib only).

Usage: python3 derived-stale.py check|stamp SOURCE OUTDIR
       python3 derived-stale.py guard SOURCE REPORT
       python3 derived-stale.py peers SOURCE...
       python3 derived-stale.py --self-test
check: STALE only if body hash changed AND (dated entries newer than the sidecar date OR size moved >= 5%).
stamp: write OUTDIR/.source-hash = "<12-hex sha256> <date> <bytes>" (call after a refresh).
guard: exit 1 if source < 0.9x REPORT size; else copy REPORT to REPORT.prev.
peers: flag sources under 0.5x the median source size.
"""
import datetime, hashlib, os, re, shutil, statistics, sys, tempfile

SIDECAR, MATERIAL, GUARD, PEER = ".source-hash", 0.05, 0.9, 0.5  # ponytail: thresholds fit to one corpus, re-measure on yours


def body(path):
    t = open(path, encoding="utf-8").read().replace("\r\n", "\n")
    t = re.sub(r"\A---\n.*?\n---\n", "", t, flags=re.S)  # strip frontmatter
    return "\n".join(l.rstrip() for l in t.split("\n")).encode()


def read_sidecar(outdir):
    h, d, n = open(os.path.join(outdir, SIDECAR)).read().split()
    return h, d, int(n)


def stamp(src, outdir):
    b = body(src)
    open(os.path.join(outdir, SIDECAR), "w").write(f"{hashlib.sha256(b).hexdigest()[:12]} {datetime.date.today()} {len(b)}\n")


def check(src, outdir):
    b = body(src)
    try:
        h, d, n = read_sidecar(outdir)
    except FileNotFoundError:
        return "STALE: no sidecar (never stamped)"
    if hashlib.sha256(b).hexdigest()[:12] == h:
        return None
    newer = [x for x in re.findall(r"\b\d{4}-\d{2}-\d{2}\b", b.decode()) if x > d]
    moved = abs(len(b) - n) / max(n, 1)
    if newer or moved >= MATERIAL:
        return f"STALE: hash changed, {len(newer)} newer dated entries, size moved {moved:.0%}"
    return None  # hash changed but immaterial


def guard(src, report):
    ratio = len(body(src)) / max(os.path.getsize(report), 1)
    if ratio < GUARD:
        return f"BLOCKED: source is {ratio:.2f}x report (< {GUARD}); rebuild the source first"
    shutil.copy(report, report + ".prev")
    return None


def peers(srcs):
    sizes = {s: len(body(s)) for s in srcs}
    med = statistics.median(sizes.values())
    return [f"THIN: {s} is {n / med:.2f}x median" for s, n in sizes.items() if n < PEER * med]


def self_test():
    with tempfile.TemporaryDirectory() as t:
        src, out = os.path.join(t, "s.md"), os.path.join(t, "o")
        os.mkdir(out)
        rep = os.path.join(out, "r.md")
        text = "---\nupdated: 2026-01-01\n---\n" + "line\n" * 200
        open(src, "w").write(text)
        open(rep, "w").write("x" * 900)
        assert check(src, out).startswith("STALE")  # never stamped
        stamp(src, out)
        assert check(src, out) is None
        open(src, "w").write(text.replace("2026-01-01", "2026-09-09"))  # frontmatter-only bump
        assert check(src, out) is None
        open(src, "w").write(text + "note\n")  # immaterial edit
        assert check(src, out) is None
        open(src, "w").write(text + "2999-01-01 new entry\n")  # dated entry
        assert check(src, out).startswith("STALE")
        open(src, "w").write(text + "line\n" * 20)  # >=5% growth
        assert check(src, out).startswith("STALE")
        assert guard(src, rep) is None and os.path.exists(rep + ".prev")
        open(rep, "w").write("x" * 5000)
        assert guard(src, rep).startswith("BLOCKED")
        small = os.path.join(t, "small.md")
        open(small, "w").write("x\n" * 10)
        assert len(peers([src, src + "", small, src])) == 1
    print("ok")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--self-test"]:
        self_test()
    elif len(a) == 3 and a[0] in ("check", "guard"):
        r = (check if a[0] == "check" else guard)(a[1], a[2])
        print(r or "ok")
        sys.exit(1 if r else 0)
    elif len(a) == 3 and a[0] == "stamp":
        stamp(a[1], a[2])
    elif len(a) >= 2 and a[0] == "peers":
        r = peers(a[1:])
        print("\n".join(r) or "ok")
        sys.exit(1 if r else 0)
    else:
        sys.exit(__doc__)
