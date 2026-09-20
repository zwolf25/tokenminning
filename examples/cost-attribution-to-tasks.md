# Case Study: Attributing Claude Code Cost to Task IDs

**Question:** Which tasks are expensive, and how much spend is invisible to task tracking?
**Result:** 44% of spend (about $700 of $1,590) sat in 198 sessions that never touched a task ID. Attributed spend was broad: the top task was $55 (about 3.5% of total), with no single expensive task.
**Rule adopted:** open each work session with `/todos <id>` so the cost has an owner.

---

## Method

`ccusage session` groups by project directory, not by session, and `ccusage session --id` returned null for real session ids. So the join is done from raw transcripts (`~/.claude/projects/**/*.jsonl`).

- **Join key:** task ids in `mcp__aiwork__*` tool calls inside each transcript. The task store has no session column, so the transcript is the only link.
- **Cost:** per-message `usage` (deduplicated by message id) times a rough rate table, then scaled per model so the total equals ccusage's dollars for that model. Subagent transcripts count toward the parent session.
- **Split:** a session that touches several tasks divides its cost evenly across them.
- **Check:** an assert requires attributed + unattributed to match ccusage's total (1590.60 vs 1590.58).

## Result

| | Sessions | Spend |
|:---|---:|---:|
| Attributed to a task | many, 1-3 per task | ~$890 (56%) |
| No task touched | 198 | ~$700 (44%) |
| Top 10 unattributed | 10 | ~$283 (40% of the unattributed) |

The unattributed median is $0.81 a session, so the tail is cheap and a few long sessions in the home and vault directories carry most of it. Cost mix is cache-read dominated (5.45B cache-read tokens vs 17M output), which is the same lever as [Context-Length Threshold](context-length-threshold.md).

## Caveats

- Even split across tasks in one session is crude; a session that starts on task A and drifts to B is charged to both.
- Rate weights are assumed and calibrated only in total per model, so per-session dollars are approximate.
- Sessions that never call a task tool cannot be attributed by construction. The 44% measures tracking discipline as much as spend.
- One user, one setup, and no saving is claimed here. This is measurement to aim the next fix.

## Takeaway

Attribution shows that per-task cost is not the problem here; long, untracked sessions are. Start sessions from a task id to make spend attributable, then aim `/compact` at the biggest unattributed sessions.
