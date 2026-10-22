# statusline

Claude Code status line that shows context size against the auto-compact window: grey normally, amber at 60% of the window, red at or over it. Bash plus `jq`, local, no model tokens. Extracted from the [Context-Length Threshold](../../examples/context-length-threshold.md) case study.

```bash
cp statusline.sh ~/.claude/statusline.sh && chmod +x ~/.claude/statusline.sh
# settings.json
{ "statusLine": { "type": "command", "command": "~/.claude/statusline.sh" } }
bash statusline.sh --self-test
```

- Reads `CLAUDE_CODE_AUTO_COMPACT_WINDOW` (default 250000), the same variable the cap uses, so the display and the cap cannot disagree. Set it to the knee [`tools/context-threshold`](../context-threshold) finds on your own history; do not copy 250k.
- Context is input + cache-read + cache-creation tokens of the last call, the definition the threshold analysis uses.
- The `context_window.current_usage` field name is from Claude Code 2.1.236; check it against your version. If the field is missing the script prints nothing.
- Prints only the context badge. To combine it with another status line, call that script first and append this output.
