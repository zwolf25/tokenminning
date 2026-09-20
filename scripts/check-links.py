"""Fail on broken relative links/images in *.md and on unused files in resources/."""
import glob, os, re, sys

md = [f for f in glob.glob("**/*.md", recursive=True) if "node_modules" not in f]
bad, used = [], set()
for f in md:
    text = re.sub(r"<!--.*?-->", "", open(f, encoding="utf-8").read(), flags=re.S)
    text = re.sub(r"```.*?```", "", text, flags=re.S)  # ignore code blocks
    for t in re.findall(r"\]\(([^)\s#]+)", text) + re.findall(r'src="([^"#]+)"', text):
        if re.match(r"(https?:|mailto:)", t):
            continue
        p = os.path.normpath(os.path.join(os.path.dirname(f), t))
        used.add(p)
        if not os.path.exists(p):
            bad.append(f"{f}: broken link {t}")
for r in glob.glob("resources/*"):
    if os.path.normpath(r) not in used:
        bad.append(f"{r}: unused resource")
print("\n".join(bad) or "links OK")
sys.exit(1 if bad else 0)
