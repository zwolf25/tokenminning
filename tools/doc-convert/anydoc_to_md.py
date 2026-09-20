import sys
import anydoc

if len(sys.argv) != 3:
    sys.exit("usage: anydoc_to_md.py <source> <output>.md")
source, output = sys.argv[1], sys.argv[2]
try:
    text = anydoc.to_markdown(source)
except Exception as e:
    sys.exit(f"anydoc failed on {source}: {e} (try: markitdown {source} -o {output})")
open(output, "w", encoding="utf-8").write(text)
print(f"WROTE {output}")
