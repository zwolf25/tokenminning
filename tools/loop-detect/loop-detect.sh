#!/bin/bash
# PreToolUse hook (all tools): warn on the Nth consecutive identical tool call
# in a row (same tool_name + same tool_input). Escalates to a user permission
# prompt via permissionDecision:"ask" instead of silently blocking Claude —
# catches blind retry loops without breaking deliberate repeats.
# Requires: jq. Env: LOOP_DETECT_THRESHOLD (default 3), LOOP_DETECT_STATE_DIR.
# Self-test: loop-detect.sh --self-test
# ponytail: no per-tool allowlist, add one if a specific tool proves noisy.

command -v jq >/dev/null || exit 0

THRESHOLD="${LOOP_DETECT_THRESHOLD:-3}"
STATE_DIR="${LOOP_DETECT_STATE_DIR:-$HOME/.claude/hooks/.loop-state}"

hash() { if command -v md5sum >/dev/null; then md5sum | cut -d' ' -f1; elif command -v md5 >/dev/null; then md5 -q; else shasum | cut -d' ' -f1; fi; }

if [ "$1" = "--self-test" ]; then
  export LOOP_DETECT_STATE_DIR="$(mktemp -d)"
  call() { echo "{\"transcript_path\":\"/t\",\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"$1\"}}" | "$0"; }
  out=""; for i in 1 2 3; do out=$(call ls); done
  [ -n "$(call ls | head -c1)" ] && { echo "FAIL: 4th call should be silent"; exit 1; }
  echo "$out" | grep -q '"ask"' || { echo "FAIL: 3rd call should ask"; exit 1; }
  [ -z "$(call pwd)" ] || { echo "FAIL: different call should be silent"; exit 1; }
  rm -rf "$LOOP_DETECT_STATE_DIR"; echo "PASS"; exit 0
fi

mkdir -p "$STATE_DIR" 2>/dev/null
find "$STATE_DIR" -type f -mtime +1 -delete 2>/dev/null

INPUT=$(cat)

TRANSCRIPT=$(echo "$INPUT" | jq -r '.transcript_path // empty')
TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty')
SIG_INPUT=$(echo "$INPUT" | jq -Sc '.tool_input // {}')

[ -z "$TRANSCRIPT" ] && exit 0
[ -z "$TOOL" ] && exit 0

SIG=$(echo -n "${TOOL}:${SIG_INPUT}" | hash)
KEY=$(echo -n "$TRANSCRIPT" | hash)
STATE_FILE="$STATE_DIR/$KEY"

PREV=""
COUNT=0
if [ -f "$STATE_FILE" ]; then
  IFS='|' read -r PREV COUNT < "$STATE_FILE"
fi

if [ "$SIG" = "$PREV" ]; then
  COUNT=$((COUNT + 1))
else
  COUNT=1
fi

echo "${SIG}|${COUNT}" > "$STATE_FILE"

if [ "$COUNT" -eq "$THRESHOLD" ]; then
  jq -nc --arg tool "$TOOL" --arg n "$THRESHOLD" '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "ask",
      permissionDecisionReason: "Same \($tool) call repeated \($n)x in a row — possible retry loop, confirm to continue."
    }
  }'
fi

exit 0
