#!/bin/bash
# Claude Code status line: context size against the auto-compact window.
# Grey normally, amber at 60% of the window, red at or over it. Needs jq.
# Context = input + cache-read + cache-creation tokens of the last call, the same
# definition tools/context-threshold uses.
if [ "$1" = "--self-test" ]; then
  run() { printf '{"context_window":{"current_usage":{"input_tokens":%s,"cache_creation_input_tokens":0,"cache_read_input_tokens":0}}}' "$1" | CLAUDE_CODE_AUTO_COMPACT_WINDOW=250000 bash "$0"; }
  [ "$(run 50000)" = $'\033[38;5;245m50k/250k\033[0m' ] || { echo "FAIL grey"; exit 1; }
  [ "$(run 160000)" = $'\033[38;5;214m160k/250k\033[0m' ] || { echo "FAIL amber"; exit 1; }
  [ "$(run 250000)" = $'\033[38;5;196m250k/250k\033[0m' ] || { echo "FAIL red"; exit 1; }
  [ -z "$(echo '{}' | bash "$0")" ] || { echo "FAIL empty"; exit 1; }
  echo "self-test OK"; exit 0
fi
input=$(cat)
tokens=$(jq -r '.context_window.current_usage // empty
  | (.input_tokens + .cache_creation_input_tokens + .cache_read_input_tokens)' <<<"$input")
[ -z "$tokens" ] && exit 0
limit=${CLAUDE_CODE_AUTO_COMPACT_WINDOW:-250000}
color=245
[ $((tokens * 100 / limit)) -ge 60 ] && color=214
[ "$tokens" -ge "$limit" ] && color=196
printf '\033[38;5;%sm%sk/%sk\033[0m' "$color" $((tokens / 1000)) $((limit / 1000))
