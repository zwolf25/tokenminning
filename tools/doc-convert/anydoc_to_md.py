import os
import sys
import anydoc

source, output = sys.argv[1], sys.argv[2]

base_dir = os.path.abspath(os.getcwd())
source_path = os.path.abspath(os.path.join(base_dir, source))
output_path = os.path.abspath(os.path.join(base_dir, output))
if os.path.commonpath([base_dir, source_path]) != base_dir or \
        os.path.commonpath([base_dir, output_path]) != base_dir:
    print("Error: source and output paths must stay within the current working directory")
    sys.exit(1)

open(output_path, "w", encoding="utf-8").write(anydoc.to_markdown(source_path))
print(f"WROTE {output_path}")
