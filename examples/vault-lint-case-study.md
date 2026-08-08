# Case Study: Eliminating 85% of Mechanical Wiki-Cleanup Overhead

## The Problem
Four wiki-maintenance skills (`wiki-builder`, `wiki-cleanup`, `sc-wiki-builder`, `sc-wiki-cleanup`) each re-read every wiki file to check 5 mechanical hygiene dimensions. On a 98-file personal vault + 97-wiki shared vault, this meant **~91 model `Read` calls per run**, re-ingested every turn — the single largest token sink in the Second Brain pipeline.

## The Solution
A deterministic, dependency-free Python script (`vault-lint.py`) that:
1. Scans all wikis + raw manifest in ~2 seconds
2. Emits one structured row per finding (no model calls)
3. Skills now **only Read what vault-lint flags** — 90 → 13 findings (85.6% reduction)

## Key Implementation Details
- **Two identical copies**: `skills-repo/scripts/vault-lint.py` (personal skills) + `zacai-skills/scripts/vault-lint.py` (shared SC skills)
- **Fallback design**: single-file parse errors → flagged row, scan continues; whole-script failure → skill falls back to old manual check
- **Bash carve-out**: Skills explicitly permit one scripted `Bash` pass to auto-fix batches of mechanical findings (e.g., 50 legacy `last-indexed` → `source-updated` renames in one command)

## Results
| Metric | Before | After |
|--------|--------|-------|
| Mechanical findings | 90 | 13 |
| Stub freshness issues | 73 | 0 |
| `wiki-cleanup` token cost (monthly) | 8.5M tokens | ~1.2M est. |
| Dollar cost | $8.12 | ~$1.15 est. |
| Runtime | 64 turns | 1 turn (lint) + judgment only |

## Two Bugs Caught by Dogfooding
1. **Comma-in-filename Source-files miscount** — split on bare commas; fixed to split only on `, <date>`
2. **Empty `topics: []` flagged as missing field** — truthiness check; fixed to check key presence

Both now covered by regression assertions in `test_vault_lint.py`.

## Reusable Pattern
Model-heavy audit → deterministic pre-filter → model only judges
Applies to any pipeline where mechanical checks dominate token spend.
