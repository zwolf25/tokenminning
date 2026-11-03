import sys

HINT = "run via: uv run --with firecrawl-anydoc --no-project anydoc_to_md.py <source> <output>.md"


def load_anydoc():
    try:
        import anydoc
    except ImportError:
        sys.exit(f"anydoc is not installed; {HINT}")
    return anydoc


if sys.argv[1:] == ["--self-test"]:
    sys.modules["anydoc"] = None  # makes `import anydoc` raise ImportError
    try:
        load_anydoc()
    except SystemExit as e:
        assert HINT in str(e), "missing-module message must carry the uv command"
        print("self-test OK")
        sys.exit(0)
    sys.exit("self-test FAILED: no exit on missing anydoc")

if len(sys.argv) != 3:
    sys.exit("usage: anydoc_to_md.py <source> <output>.md")
source, output = sys.argv[1], sys.argv[2]
try:
    text = load_anydoc().to_markdown(source)
except Exception as e:
    sys.exit(f"anydoc failed on {source}: {e} (try: markitdown {source} -o {output})")
open(output, "w", encoding="utf-8").write(text)
print(f"WROTE {output}")
