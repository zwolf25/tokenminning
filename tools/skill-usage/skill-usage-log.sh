#!/bin/bash
# PostToolUse hook (Skill): append one JSONL line per skill call. Silent: no stdout, so zero transcript tokens.
# Log path: $SKILL_USAGE_LOG, default ~/.claude/skill-usage.jsonl. Needs jq.
LOG="${SKILL_USAGE_LOG:-$HOME/.claude/skill-usage.jsonl}"
skill=$(jq -r '.tool_input.skill // empty')
[ -z "$skill" ] && exit 0
jq -nc --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --arg skill "$skill" --arg cwd "$PWD" \
  '{ts:$ts, skill:$skill, cwd:$cwd}' >> "$LOG"
exit 0
