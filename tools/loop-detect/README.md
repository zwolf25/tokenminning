# loop-detect

Claude Code `PreToolUse` hook that asks for confirmation on the 3rd identical tool call in a row (same tool name and same input), to catch blind retry loops. It returns `permissionDecision: "ask"` instead of blocking, so deliberate repeats still go through. Bash plus `jq`, local, no model tokens.

```bash
cp loop-detect.sh ~/.claude/hooks/loop-detect.sh && chmod +x ~/.claude/hooks/loop-detect.sh
# settings.json
{ "hooks": { "PreToolUse": [{ "hooks": [{ "type": "command", "command": "~/.claude/hooks/loop-detect.sh" }] }] } }
bash loop-detect.sh --self-test
```

- `LOOP_DETECT_THRESHOLD` sets how many identical calls in a row trigger the prompt (default 3). `LOOP_DETECT_STATE_DIR` moves the per-transcript counter files (default `~/.claude/hooks/.loop-state`, pruned after a day).
- Needs `jq`. If it is missing the hook does nothing.
- No measured savings. On the author's own history (300 transcripts, 13,753 tool calls) there were zero runs of 3 or more identical consecutive calls. Count yours before relying on it; it is a cheap guard, not a proven saver.
