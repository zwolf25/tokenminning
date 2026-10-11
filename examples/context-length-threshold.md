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
- One user, one setup. The threshold depends on your model and base context size; measure your own before copying 250k. The [`tools/context-threshold`](../tools/context-threshold) script in this repo (and the `context-length-threshold` skill in the `second-brain-skills` plugin) does this per model from your own transcripts.

## Follow-up: enforce it with `CLAUDE_CODE_AUTO_COMPACT_WINDOW`

A habit rule drifts. Claude Code reads the `CLAUDE_CODE_AUTO_COMPACT_WINDOW` environment variable (token count) to set the context size at which it auto-compacts; without it the window defaults large, so sessions can grow past the knee. Set it in `~/.claude/settings.json` to your own knee (here 250000):

```json
{ "env": { "CLAUDE_CODE_AUTO_COMPACT_WINDOW": "250000" } }
```

It applies to new sessions only. Check the variable name against your Claude Code version before relying on it.

**Result after two weeks (one user, one setup):** turns at or above 250k context went from 7.3% (the day before the change) to 0.0% over 14 days, so the cap holds. Cost per day (`ccusage`, 7-day average) fell from $46.95 to $23.47 over the last week, but treat that as suggestive: daily cost varied about 10x with workload, and the model mix also changed in the window. The mechanism (no turns over the knee) is the solid claim; the dollar drop is not attributable to the cap alone.

Do not copy 250k. Run the threshold tool on your own history first and set the variable to the knee it finds.

## Make it visible: context on the status line

A cap you cannot see is easy to forget. This status line script (Claude Code pipes session JSON to it on stdin) prints context size against the window: grey normally, amber at 60% of the window, red at or over it. It reads the same `CLAUDE_CODE_AUTO_COMPACT_WINDOW` variable the cap uses, so the two cannot disagree. Needs `jq`.

```bash
#!/bin/bash
input=$(cat)
tokens=$(jq -r '.context_window.current_usage // empty
  | (.input_tokens + .cache_creation_input_tokens + .cache_read_input_tokens)' <<<"$input")
[ -z "$tokens" ] && exit 0
limit=${CLAUDE_CODE_AUTO_COMPACT_WINDOW:-250000}
color=245
[ $((tokens * 100 / limit)) -ge 60 ] && color=214
[ "$tokens" -ge "$limit" ] && color=196
printf '\033[38;5;%sm%sk/%sk\033[0m' "$color" $((tokens / 1000)) $((limit / 1000))
```

Save it as `~/.claude/statusline.sh`, make it executable, and point the `statusLine` setting at it (`{ "statusLine": { "type": "command", "command": "~/.claude/statusline.sh" } }`). The `current_usage` field name is from the Claude Code build used here (2.1.236); check it against your version. The context definition (input + cache read + cache creation) is the same one the threshold analysis uses.

## Audit recipe: before and after with `ccusage`

1. **Baseline first.** Before changing anything, record a week of daily cost and cache-read share:
   ```bash
   ccusage daily --since YYYYMMDD --until YYYYMMDD --json \
     | jq '{days:(.daily|length), avg_per_day:(([.daily[].totalCost]|add)/(.daily|length)), cache_read_share:(([.daily[].cacheReadTokens]|add)/([.daily[].totalTokens]|add))}'
   ```
2. **Find your knee** with [`tools/context-threshold`](../tools/context-threshold) on your own transcripts. If it reports no knee, stop; there is nothing to cap.
3. **Set the window** to that number, and run for at least a week of new sessions.
4. **Re-measure both windows on the same day** with the same command. `ccusage` reprices history when its pricing table updates: re-running the baseline week above, written up in this case study, gave $48.51 a day against the $46.95 recorded at the time.
5. **Compare 7-day averages, not days.** Daily cost here ranged from $6.57 to $64.51, so a single day says nothing.
6. **Check the mechanism separately from the dollars.** The share of turns at or above your window is the thing the cap controls. The cost per day is also moved by workload and model mix. One session in this setup cost $47.46 across 1,276 requests and peaked at 219k context, never touching the cap: long sessions are a turn-count problem the cap does not address.
7. **Use one cost source.** OpenTelemetry's cost metric ran about 30% above `ccusage` on the same days here (cause not verified). Do not mix them in one comparison.

## Takeaway

Cost per turn grows with context, and most of the spend sits in the long tail of sessions. A one-line rule is a cheap test. Re-measure after a few weeks to see whether the >250k share of spend actually falls.
