# lint

Two zero-dependency (Python 3 stdlib) linters on one findings format. They run locally, never write files, and use no model tokens: a model then only reads what they flag. Extracted from the [Wiki Lint](../../examples/vault-lint-case-study.md) and [Config Audit](../../examples/second-brain-config-audit.md) case studies.

Every finding is `{file, dimension, detail, proposed_fix}` (plus `line` where it applies). `proposed_fix` starts with `AUTO-RESOLVE` when the fix is fully determined, `QUESTION` when it needs a judgment, or a plain direction. Output is `--format json` (default) or `tsv`. Shared code lives in [findings.py](findings.py).

## vault-lint

Mechanical hygiene for a folder of markdown wikis.

```bash
python3 vault-lint.py <wikis-dir> [--require-fields description,type] [--require-sections "Overview,Key Facts"] [--recap-chars 15000] [--format tsv]
python3 vault-lint.py --self-test
```

| Dimension | Flags |
|:---|:---|
| `frontmatter` | A `--require-fields` key is absent. Checks presence, not truthiness, so `topics: []` is valid |
| `broken-link` | A `[[wikilink]]` (frontmatter or body) matches no `*.md` file under the folder |
| `section-structure` | A `--require-sections` heading is missing or out of the given order |
| `recap-presence` / `recap-position` | With `--recap-chars N`: a file over N chars has no `## Recap`, or the Recap is not the last `##` heading |
| `parse-error` | One file failed to parse; the scan continues |

Files starting with `_` are skipped. Section and Recap checks are off unless you pass the flags, since they encode one vault's template. Thin pointer pages that lack your required sections will be flagged; that is a signal to exempt them by convention in your own wrapper.

## claude-md-lint

The deterministic slice of a CLAUDE.md audit. Claude Code concatenates every CLAUDE.md it finds and nothing overrides anything, so lines that repeat or dangle are paid for every session.

```bash
python3 claude-md-lint.py [FILE ...] [--format tsv]     # no files = your whole stack
python3 claude-md-lint.py --self-test
```

With no files it audits `~/.claude/CLAUDE.md`, `~/.claude/rules/*.md`, and each `CLAUDE.md` / `CLAUDE.local.md` from the working directory up to `/`.

| Dimension | Flags |
|:---|:---|
| `size` | Lines including `@imports` above 200 (warning) or 300 (flag) |
| `stale-import` | An `@path` import whose target does not exist |
| `stale-path` | An explicit `~/...` or `/Users/...` path that does not exist |
| `duplicate` | 3+ consecutive lines repeated across two files in the stack; a single repeated line is exempt |
| `settings-leak` | A fenced block with `hooks`, `permissions` or `env` keys, which belongs in `settings.json` |
| `tier` | Per file: Strong (0 flags), Functional (1-2), Needs work (3+). Tiers, not scores |

`@x` inside backticks or code fences is not an import, block `<!-- comments -->` are not counted (Claude strips them), and imports are followed up to 5 hops.

**Not deterministic, so not here:** vague advice, procedures that belong in a skill, and contradictions between files. Because nothing overrides anything, every contradiction is a coin flip each session, but spotting one takes judgment; use the `claude-md-audit` skill (rubric in [Config Audit](../../examples/second-brain-config-audit.md)) for those.

Paths containing spaces are matched by prefix (the lint cuts at the space), so a missing path is only flagged when no sibling starts with the same name. That fix came from running it on a real stack, where the first version flagged three false positives.
