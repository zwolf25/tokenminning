# skill-usage

Which installed skills you actually call, and what the unused ones cost in the always-loaded skill listing. Zero dependencies (Python 3 stdlib + `jq` for the hook), local, no model tokens.

## 1. Log calls

Copy `skill-usage-log.sh` somewhere stable, `chmod +x` it, and add to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      { "matcher": "Skill", "hooks": [{ "type": "command", "command": "~/.claude/hooks/skill-usage-log.sh" }] }
    ]
  }
}
```

It appends one JSONL line (`ts`, `skill`, `cwd`) per call to `$SKILL_USAGE_LOG` (default `~/.claude/skill-usage.jsonl`). It prints nothing, so it adds zero tokens to the transcript.

## 2. Report

```bash
python3 skill-usage.py [--log FILE] [--skills-dir DIR ...] [--rare N]
python3 skill-usage.py --self-test
```

Prints calls and last-used date per skill, then installed skills never used or used <= N times (default 0), with their listing size.

- Installed = every `SKILL.md` found recursively under `--skills-dir` (default `~/.claude/skills`; repeat the flag to add plugin directories).
- `plugin:skill` and bare `skill` calls count together.
- Listing size is measured in characters (name + description). Tokens are not estimated; apply your own chars-per-token ratio.
- A skill with zero calls may just be new. Check the log's date range before deleting anything.
