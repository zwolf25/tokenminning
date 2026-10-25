# retrieval-gaps

Finds the times you had to tell Claude "it's in the X wiki" or "you missed that", by mining your own Claude Code transcripts. Zero dependencies (Python 3 stdlib), local, no model tokens.

Use it before adding retrieval infrastructure (vector search, embeddings, a new MCP server). If the count is near zero, the infrastructure has nothing to fix. Extracted from the [Evaluate Before Adopting](../../examples/evaluate-before-adopting.md) case study.

```bash
python3 retrieval-gaps.py [DAYS]        # default 90
python3 retrieval-gaps.py --self-test
```

Reads `~/.claude/projects/*/*.jsonl` (override with `CLAUDE_PROJECTS_DIR`). A hit is a real user message, not a tool result and not a scheduled-task or system message, that matches phrases like "check the ... wiki", "it's in the ... vault", "you missed", "didn't you check", "should have found". Each hit prints its date, project, the matched phrase, the first 200 characters, and the last four search or read tool calls before it.

## Read the output by hand

The regex over-matches. In our run, every candidate hit from two passes was a false positive (a routing test, a deck-edit complaint, a question about Jira fields). Count only hits where the answer existed in your knowledge base and Claude did not surface it.

## Limits

It only sees misses you said out loud. A silent miss, where Claude answered without the right file and you never noticed, is invisible. Treat a zero as "no voiced misses", not "no misses". Add a one-line `retrieval-gaps.md` log to your CLAUDE.md rules so future misses are recorded at the moment they happen.
