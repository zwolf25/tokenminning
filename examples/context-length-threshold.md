# Case Study: Where Does Session Length Start Costing More?

**Question:** At what context size does cost per turn climb enough to justify `/compact` or `/clear`?
**Result:** Per-turn cost is ~2.1x at 250k tokens of context and ~4–5x at 500k+, versus the cheapest well-populated bucket. About 59% of this model's spend sits at or above 250k.
**Rule adopted:** `/compact` (or `/clear` between unrelated tasks) at ~250k.

---

## Method

`ccusage session` groups by project directory, so it cannot show cost per turn. The per-turn data is in the raw Claude Code transcripts (`~/.claude/projects/*/*.jsonl`): each assistant message carries a `usage` block (input, cache-read, cache-creation, output tokens).

- 311 sessions, ~20k main-thread turns (one model, sub-agent sidechains excluded).
- Messages deduplicated by message id (streamed messages repeat; last usage wins).
- Context size per turn = input + cache-read + cache-creation tokens.
- Cost per turn weighted by assumed rate ratios (cache-read 0.1x, cache-write 1.25x, output 5x input), not real prices.
- Turns bucketed by context size; compared mean cost per turn and share of total spend.

## Result

| Context size | Turns | Cost per turn (vs cheapest bucket) | Share of spend |
|:---|---:|:---:|:---:|
| 50–75k | 697 | 1.33x | 2.3% |
| 75–100k | 2,608 | 1.00x | 6.4% |
| 100–150k | 4,085 | 1.20x | 12.1% |
| 150–200k | 2,729 | 1.54x | 10.3% |
| 200–250k | 2,139 | 1.88x | 9.9% |
| 250–300k | 1,816 | 2.14x | 9.6% |
| 300–400k | 2,683 | 2.60x | 17.2% |
| 400–500k | 1,612 | 3.06x | 12.2% |
| 500–700k | 1,352 | 4.02x | 13.4% |
| 700k+ | 502 | 5.32x | 6.6% |

**Knee rule:** the first bucket where per-turn cost is at least 2x the baseline *and* at least 30% of spend sits at or above it. Here that is 250k.

**How the number moved:** the first pass merged 50–100k as the baseline and read the knee as ~300k. Using the cheapest well-populated bucket instead moves it to 250k. The baseline choice shifts the knee by a bucket or two, so treat the threshold as approximate and measure your own.

Context never drops below 50k in this setup: the always-loaded base (instructions, skills, tool schemas) is already large. That is the same lever as [Config Audit](second-brain-config-audit.md): a smaller base lowers the floor for every turn.

## Estimated saving

Capping sessions near 250k and resetting to ~100k would cut roughly 35% of spend on this model. That is an **upper bound**: it ignores the cost of compacting and the context lost when you do.

## Caveats

- Rate ratios are assumed. Calibrating against ccusage totals came out ~25% low on absolute dollars; the percentages and ratios are the usable part.
- Long sessions may contain heavier work, so not all of the rise is avoidable.
- One user, one setup. The threshold depends on your model and base context size; measure your own before copying 250k. The `context-length-threshold` skill in the `second-brain-skills` plugin does this per model from your own transcripts.

## Takeaway

Cost per turn grows with context, and most of the spend sits in the long tail of sessions. A one-line rule is a cheap test. Re-measure after a few weeks to see whether the >250k share of spend actually falls.
