# Case Study: Where Does Session Length Start Costing More?

**Question:** At what context size does cost per turn climb enough to justify `/compact` or `/clear`?
**Result:** Per-turn cost is ~2.4x at 300k tokens of context and ~4–5x at 500k+, versus 50–100k. Turns above 300k are 30% of turns but ~49% of spend.
**Rule adopted:** `/compact` (or `/clear` between unrelated tasks) at ~300k.

---

## Method

`ccusage session` groups by project directory, so it cannot show cost per turn. The per-turn data is in the raw Claude Code transcripts (`~/.claude/projects/*/*.jsonl`): each assistant message carries a `usage` block (input, cache-read, cache-creation, output tokens).

- 311 sessions, ~20k main-thread turns (one model, sub-agent sidechains excluded).
- Messages deduplicated by message id (streamed messages repeat; last usage wins).
- Context size per turn = input + cache-read + cache-creation tokens.
- Cost per turn weighted by assumed rate ratios (cache-read 0.1x, cache-write 1.25x, output 5x input), not real prices.
- Turns bucketed by context size; compared mean cost per turn and share of total spend.

## Result

| Context size | Cost per turn (vs 50–100k) | Share of spend |
|:---|:---:|:---:|
| 50–100k | 1.0x | 8.7% |
| 100–150k | 1.1x | 12.1% |
| 150–200k | 1.4x | 10.3% |
| 200–250k | 1.75x | 9.9% |
| 250–300k | 2.0x | 9.6% |
| 300–400k | 2.4x | 17.2% |
| 400–500k | 2.9x | 12.2% |
| 500–700k | 3.75x | 13.4% |
| 700k+ | ~5x | 6.6% |

Context never drops below 50k in this setup: the always-loaded base (instructions, skills, tool schemas) is already large. That is the same lever as [Config Audit](second-brain-config-audit.md): a smaller base lowers the floor for every turn.

## Estimated saving

Capping sessions near 300k and resetting to ~100k would cut roughly 30% of spend on this model. That is an **upper bound**: it ignores the cost of compacting and the context lost when you do.

## Caveats

- Rate ratios are assumed. Calibrating against ccusage totals came out ~25% low on absolute dollars; the percentages and ratios are the usable part.
- Long sessions may contain heavier work, so not all of the rise is avoidable.
- One user, one setup. The threshold depends on your base context size; measure your own before copying 300k.

## Takeaway

Cost per turn grows with context, and most of the spend sits in the long tail of sessions. A one-line rule is a cheap test. Re-measure after a few weeks to see whether the >300k share of spend actually falls.
