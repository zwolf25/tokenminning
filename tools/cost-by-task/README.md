# cost-by-task

Claude Code spend per task id, joined from your own raw transcripts and reconciled to `ccusage`. Zero dependencies (Python 3 stdlib) plus the `ccusage` CLI, local, no model tokens. Extracted from the [Attributing Claude Code Cost to Task IDs](../../examples/cost-attribution-to-tasks.md) case study.

```bash
python3 cost-by-task.py [--dir ~/.claude/projects] [--tool-prefix mcp__aiwork__] [--id-field task_id] [--ccusage FILE.json] [--top 15]
python3 cost-by-task.py --self-test
```

Prints spend and share for the top tasks, then attributed vs unattributed spend and the ccusage total it reconciles to.

- **Requires a task tracker exposed as MCP tools** whose calls carry a task id. The defaults match the author's `aiwork` server; set `--tool-prefix` and `--id-field` for yours (e.g. `mcp__linear__`, `issueId`). With no such tracker there is nothing to join on and all spend lands as unattributed.
- **Join key:** the id field in those tool calls, per transcript. The task store has no session column, so the transcript is the only link.
- **Cost:** per-message usage (deduplicated by message id) times assumed rate ratios, then scaled per model so the total equals ccusage's dollars for that model. Sub-agent transcripts count toward the parent session.
- **Split:** a session touching several tasks divides its cost evenly across them.
- **Check:** an assert fails if attributed + unattributed differs from ccusage by more than a cent. Pass `--ccusage` a saved `ccusage daily --json --breakdown` file to skip the live call.
- Per-session dollars are approximate; only the per-model total is calibrated. Sessions that never call a task tool are unattributable by construction.
