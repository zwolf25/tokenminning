# context-threshold

Cost per turn versus context size, computed from your own raw Claude Code transcripts. Zero dependencies (Python 3 stdlib), local, no model tokens. Extracted from the [Context-Length Threshold](../../examples/context-length-threshold.md) case study.

```bash
python3 context-threshold.py [--dir ~/.claude/projects] [--model sonnet-5]
python3 context-threshold.py --self-test
```

Prints turns, cost per turn (relative to the cheapest well-populated bucket), and share of spend for each context-size bucket, then the **knee**: the first bucket at least 2x the baseline with at least 30% of spend at or above it. Use it to pick your own `/compact` point instead of copying 250k.

- Main-thread turns only (sub-agent sidechains excluded); streamed messages deduplicated by id.
- Context per turn = input + cache-read + cache-creation tokens.
- Rate ratios are assumed (cache-read 0.1x, cache-write 1.25x, output 5x input), not real prices. Trust the ratios and percentages, not absolute dollars. Edit `RATES` to calibrate against `ccusage`.
- Filter with `--model` (substring match) since the knee differs per model.

On the author's data with `--model sonnet-5` it reproduces the case study table and a 250k knee.
