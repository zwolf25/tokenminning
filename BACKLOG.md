# Backlog

Living list of planned updates and improvements. Newest review first in the log at the bottom.

**How to maintain**
- One row per item. Give each a stable ID (`B-NNN`); never reuse IDs.
- Status: `todo` · `doing` · `done` · `dropped`. When an item ships, set `done` and name the release (for example `done v0.10.0`). Do not delete rows; move them to "Done" at release time.
- Priority: `P1` fixes something wrong or blocks adoption · `P2` improves quality · `P3` nice to have.
- Add the date and source of each new item in the review log. Re-review at every minor release.
- Large items become a GitHub issue; put the issue number in the Notes column.

## Open

### Correctness and reproducibility

| ID | Pri | Item | Notes | Status |
|----|-----|------|-------|--------|
| B-002 | P1 | Case studies cite measured numbers (87%, 99.4%, 59% above the knee) that nobody can re-check; the data is private. | Add a `Method / Reproduce` box per case study: data source, sample size, date, what is estimated. Mirror the caveats already used in CS10 and CS12. | todo |
| B-003 | P2 | README "Real-World Results" and "Tooling Measured Results" mix measured and estimated values in one column (for example "~1.2M est."). | Add an `Evidence` column: measured / estimated / single run. | todo |
| B-004 | P2 | "100+ versioned skills", "100% tool consistency", "100x faster" are unsourced. | Cite a count and method, or reword. Claims like these cut against the repo's own "measured results" bar. | todo |
| B-005 | P2 | `loop-detect` ships with zero measured savings (0 loops in 13,753 calls) and keys state on `transcript_path`. Behavior in headless or subagent sessions is untested. | Test in a non-interactive run (`ask` has no prompt there). Decide: ship, or move it to examples as "not worth it" evidence. | todo |
| B-006 | P2 | `loop-detect` requires `jq` but exits 0 silently without it. | Print one warning to stderr on first use. | todo |

### Tools and CI

| ID | Pri | Item | Notes | Status |
|----|-----|------|-------|--------|
| B-011 | P2 | No pinned Python version in CI; tools claim "stdlib only". | Pin `actions/setup-python` (3.9 and latest) so the stdlib claim is tested. | todo |
| B-012 | P2 | `check-links.py` checks relative links only. External links (shields, medium, upstream repos, issue #68951) can rot. | Add a scheduled (weekly) external-link check, non-blocking. | todo |
| B-013 | P2 | `check-links.py` does not check `#anchor` targets. README nav (`#case-studies`, `#principles`) can break silently. | Validate heading anchors for local `.md` targets. | todo |
| B-014 | P2 | No shared test layout: each tool has its own inline `--self-test`. | Fine at this size. Revisit when a tool passes ~300 lines (`claude-md-lint.py` is 241). | todo |
| B-015 | P3 | No `requirements`/version note per tool; Node 22 only in CI. | Add `engines` to the two `package.json` files. | todo |
| B-016 | P3 | `tools/lint` has `findings.py` shared by two linters; no check that the two stay in sync. | Add one cross-tool self-test. | todo |

### Docs and structure

| ID | Pri | Item | Notes | Status |
|----|-----|------|-------|--------|
| B-020 | P1 | README is 27 KB and puts 15 case-study blurbs in `<details>` blocks that repeat the case-study files. The repo preaches "retrieve, don't preload" yet loads everything on the landing page. | Cut each case study in the README to one row (title, result, link). Keep detail in `examples/`. | todo |
| B-021 | P2 | "Quick Start" shows a `grep` of private paths and two numbered steps that are comments, not commands. | Replace with a runnable 3-step path: `claude-md-lint.py` on your CLAUDE.md, read result, apply one trim. | todo |
| B-022 | P2 | Several pages name an employer and internal skills (README note, `skill-tooling-pattern`, `rtk-llmlingua-evaluation`, `web-scraping-escalation`). Readers cannot map them to their own setup. | Add a short "How to adapt" section per case study; confirm that every named item is cleared for public use. | todo |
| B-023 | P2 | No counterexamples page, although CONTRIBUTING calls them "valuable" and routes them to Discussions. | Write `examples/counterexamples.md` from the author's own cases (`loop-detect` no-gain, `retrieval-gaps` 0 misses, rejected LLMLingua). | todo |
| B-024 | P2 | Only Claude Code is covered. CONTRIBUTING asks for Cursor, Codex, Continue patterns. | Add one non-Claude tool pattern, or narrow the stated scope. | todo |
| B-025 | P3 | Link-checked but not spell/format-checked. Mixed styles in tables (bold, emoji). | Add `markdownlint` with a small config. | todo |
| B-026 | P3 | "Origin" says tokenminning was coined July 2026; no source. | Link the first public use. | todo |

### Process

| ID | Pri | Item | Notes | Status |
|----|-----|------|-------|--------|
| B-030 | P2 | No issue templates, no PR template, no Discussions categories documented. | Add `.github/ISSUE_TEMPLATE/` (case study proposal, tool bug) and a PR checklist from CONTRIBUTING steps 1-5. | todo |
| B-031 | P2 | Release steps are manual (PR, tag, release). Last two commits are `release:` PRs. | Document in CONTRIBUTING, or add a `release` workflow that drafts notes from CHANGELOG. | todo |
| B-032 | P3 | Roadmap is invisible to visitors. | Link this file from README and CONTRIBUTING. | todo |
| B-033 | P3 | No CODEOWNERS or security note. Tools read `~/.claude/projects` transcripts, which hold sensitive data. | Add a README note: tools are local-only and print aggregates; state it explicitly. | todo |

## Done

| ID | Item | Release |
|----|------|---------|
| B-001 | AnyDoc path: clear `uv run` error and self-test (real conversion still untested) | v0.9.2 |
| B-010 | CI matrix adds `macos-latest` | v0.9.2 |

## Review log

| Date | Source | Items added |
|------|--------|-------------|
| 2026-11-02 | Full repo review at v0.9.0 (README, CONTRIBUTING, CHANGELOG, CI, all tools skimmed; `check-links.py` passes) | B-001 to B-033 |

Not checked in the first review: the 22 `examples/*.md` bodies were not read line by line, and no tool was run beyond `check-links.py`. Treat B-001 and B-005 as read-from-source, not reproduced.
