import sys
import anydoc

source, output = sys.argv[1], sys.argv[2]
open(output, "w", encoding="utf-8").write(anydoc.to_markdown(source))
print(f"WROTE {output}")
