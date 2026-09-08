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

---

## Extending the Pattern: Stub Sync & Manifest Upsert (v2)

The same four skills had two more fully-mechanical steps still done by the model: syncing local
"pointer stub" files from a shared manifest (`wiki-builder` Step 7), and upserting rows into that
manifest (`sc-wiki-builder` Step 5.6). Both are 100% deterministic once the underlying data
(`name`, `updated`, `description`) is known — the model was spending tokens reading a markdown
table into context and hand-writing boilerplate file content, work with zero judgment in it.

**The fix**: two small scripts, `sync-stubs.py` and `manifest-upsert.py`, both reusing
`vault-lint.py`'s existing `parse_manifest_full()` / `parse_frontmatter()` helpers rather than
re-deriving a pipe-table parser a third time (ponytail: reuse before you write). `sync-stubs.py`
diffs the manifest against local stub files and writes any missing/stale ones directly from the
manifest's own `updated`/`description` columns; `manifest-upsert.py` does the mirror-image
operation, upserting a `(name, updated, description)` row into the manifest table, alphabetically
sorted, idempotent on rerun. In both cases the one genuinely non-mechanical step — linking a stub
to 2-5 relevant local wikis by topic — stays with the model; only the file I/O and table mechanics
moved to code.

**Three more bugs caught by dogfooding** (same discipline as the two above — write the script,
then run it against real production data before trusting it):

1. **A phantom manifest row, live in production.** `parse_manifest`'s original line-parsing check
   was `if "|" not in line`, meant to skip prose — but the manifest's own header blockquote
   contained a backticked example (`` `name | updated | description` ``) that itself has pipe
   characters. Every run of the existing `stub-source-updated` check had been silently carrying one
   bogus row keyed on that prose fragment. Fixed by requiring the line to actually *start with* `|`
   (real markdown table syntax), not merely contain one — caught only because a new caller
   (`manifest-upsert.py`) needed the same parser and a test asserted the exact row count.
2. **A distance heuristic that broke on its own success case.** The new "orphaned raw note"
   detector (ported from hand-specified skill-text logic into the script as a 6th dimension) first
   required the processed-marker to sit within the last ~10 lines of the file. Real notes that
   updated more than ~8 wikis in one run legitimately have a longer backlink list than that — a
   file that had genuinely and correctly updated 10 wikis got flagged as orphaned. First pass
   against real vault data: 32 false positives out of 299 real files. Root cause: the distance
   check was redundant once heading-immediacy is already required, and actively wrong for anything
   past a fixed line count. Fix: drop the distance heuristic entirely.
3. **A required-wikilink check that broke on a valid empty case.** Same detector also required at
   least one `[[wikilink]]` after the `## Wikis Updated` heading — but a legitimate "no update
   needed" outcome (an automated capture that found nothing new to add) writes that heading
   followed by a `(none — already covered)` explanation instead, with no wikilink at all. Second
   pass against real data: down to 4 false positives, all this exact pattern. Fix: accept any real
   content after the heading, not specifically a link.

After both fixes: **0 false positives across all 299 real raw files** in the shared vault, plus 0
in the parallel personal-vault pass. Both bugs are now locked in as regression fixtures in
`test_vault_lint.py` — a heading followed by a `(none — ...)` explanation, and a manifest with a
pipe character inside its own header prose, are permanent test cases now, not things to
rediscover next time someone touches this file.

### Results (pre-build estimate — not yet a live measurement)

Unlike the numbers above (measured from a real production run), these are estimated from real
per-operation costs observed in the session that built this extension, before the scripts had run
enough times in production to measure directly — flagged as such rather than rounded up to look
more certain than it is.

| Operation | Before (model-driven) | After (script) | Basis |
|---|---|---|---|
| Manifest read for stub diff | ~2,325 tokens/run (real: 115-line/~9.3KB manifest, chars/4) | 0 (Python file I/O) | Measured file size, this session |
| Manifest read for row upsert | ~2,325 tokens/run (same file, separate consumer) | 0 | Same |
| Per-stub authorship | ~200-500 tokens/stub touched | 0 (templated) | This session's real 2-stub touch |
| **Per-run estimate** | — | **~2,500-3,000 tokens/run avoided** | Conservative; scales up on multi-wiki batch runs |
| **Aggregate over one measured invocation-frequency sample** | — | **~40,000-48,000 tokens** | 16 of 232 sessions invoke this skill family (separately measured, real transcript scan); every invocation runs the stub-sync step unconditionally |

**What would need to happen before this graduates to a measured entry**: run both scripts in
production for a real stretch, then diff actual token spend against a prior comparable window —
the same standard every other row in this file's Results table already meets.
