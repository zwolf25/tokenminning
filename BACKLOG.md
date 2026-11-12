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
| B-005 | P2 | `loop-detect` ships with zero measured savings (0 loops in 13,753 calls) and keys state on `transcript_path`. Behavior in headless or subagent sessions is untested. | Test in a non-interactive run (`ask` has no prompt there). Decide: ship, or move it to examples as "not worth it" evidence. | todo |
| B-006 | P2 | `loop-detect` requires `jq` but exits 0 silently without it. | Print one warning to stderr on first use. | todo |
| B-007 | P2 | Tools only run on the author's private `~/.claude` data. A reader cannot try `cost-by-task`, `skill-usage`, `retrieval-gaps` or `context-threshold` without their own transcripts, and self-tests use synthetic inline data. | Add a small `fixtures/` set of fake transcripts and a one-line demo command per tool README. Also gives B-002 a public reproducible path. | todo |
| B-008 | P2 | `anydoc_to_md.py` (B-001) has an error path and self-test, but no real conversion has been run in CI. | Add one tiny PDF or DOCX fixture and a CI step that converts it. | todo |

### Tools and CI

| ID | Pri | Item | Notes | Status |
|----|-----|------|-------|--------|
| B-011 | P2 | No pinned Python version in CI; tools claim "stdlib only". | Pin `actions/setup-python` (3.9 and latest) so the stdlib claim is tested. | todo |
| B-012 | P2 | `check-links.py` checks relative links only. External links (shields, medium, upstream repos, issue #68951) can rot. | Add a scheduled (weekly) external-link check, non-blocking. | todo |
| B-013 | P2 | `check-links.py` does not check `#anchor` targets. README nav (`#case-studies`, `#principles`) can break silently. | Validate heading anchors for local `.md` targets. | todo |
| B-014 | P2 | No shared test layout: each tool has its own inline `--self-test`. | Fine at this size. Revisit when a tool passes ~300 lines (`claude-md-lint.py` is 241). | todo |
| B-015 | P3 | No `requirements`/version note per tool; Node 22 only in CI. | Add `engines` to the two `package.json` files. | todo |
| B-016 | P3 | `tools/lint` has `findings.py` shared by two linters; no check that the two stay in sync. | Add one cross-tool self-test. | todo |
| B-017 | P2 | No Dependabot. `actions/*@v4` and the two npm lockfiles (`doc-convert`, `visual-diff`) get no update PRs. | Add `.github/dependabot.yml` for `github-actions` and `npm`, monthly. | todo |
| B-018 | P3 | CI runs only on push and PR. A stale-but-green repo never re-tests against new Node, Python or runner images. | Add a weekly `schedule` trigger to `lint.yml`. | todo |

### Docs and structure

| ID | Pri | Item | Notes | Status |
|----|-----|------|-------|--------|
| B-029 | P3 | `examples/index.md` still lists only some case studies, and the README Technique Guides table repeats it. Split out of B-020. | Make `examples/index.md` the single full case-study list; README keeps its one-row table. | todo |
| B-022 | P2 | Several pages name an employer and internal skills (README note, `skill-tooling-pattern`, `rtk-llmlingua-evaluation`, `web-scraping-escalation`). Readers cannot map them to their own setup. | Add a short "How to adapt" section per case study; confirm that every named item is cleared for public use. | todo |
| B-023 | P2 | No counterexamples page, although CONTRIBUTING calls them "valuable" and routes them to Discussions. | Write `examples/counterexamples.md` from the author's own cases (`loop-detect` no-gain, `retrieval-gaps` 0 misses, rejected LLMLingua). | todo |
| B-024 | P2 | Only Claude Code is covered. CONTRIBUTING asks for Cursor, Codex, Continue patterns. | Add one non-Claude tool pattern, or narrow the stated scope. | todo |
| B-028 | P2 | Discussions is enabled but CONTRIBUTING routes counterexamples there and nothing is seeded. Zero open issues suggests visitors do not engage. | Seed 2 pinned Discussions: "Counterexamples: where did this not work for you?" and "Share your own measured result". Pair with B-023. | todo |
| B-025 | P3 | Link-checked but not spell/format-checked. Mixed styles in tables (bold, emoji). | Add `markdownlint` with a small config. | todo |
| B-026 | P3 | "Origin" says tokenminning was coined July 2026; no source. | Link the first public use. | todo |

### Process

| ID | Pri | Item | Notes | Status |
|----|-----|------|-------|--------|
| B-030 | P2 | No issue templates, no PR template, no Discussions categories documented. (2026-11-12: GitHub's community profile lists both templates as present, yet `.github/` holds only `workflows/`. Likely inherited from an account-level `.github` repo. Verify before building.) | Add `.github/ISSUE_TEMPLATE/` (case study proposal, tool bug) and a PR checklist from CONTRIBUTING steps 1-5. | todo |
| B-031 | P2 | Release steps are manual (PR, tag, release). Last two commits are `release:` PRs. | Document in CONTRIBUTING, or add a `release` workflow that drafts notes from CHANGELOG. | todo |
| B-032 | P3 | Roadmap is invisible to visitors. | Link this file from README and CONTRIBUTING. | todo |
| B-033 | P2 | No CODEOWNERS or security note. Tools read `~/.claude/projects` transcripts, which hold sensitive data. | Add a README note: tools are local-only and print aggregates; state it explicitly. | todo |

## Done

| ID | Item | Release |
|----|------|---------|
| B-001 | AnyDoc path: clear `uv run` error and self-test (real conversion still untested) | v0.9.2 |
| B-010 | CI matrix adds `macos-latest` | v0.9.2 |
| B-003 | README results tables gain an Evidence column | v0.9.3 |
| B-004 | unsourced "100+", "100% consistency" and "100x faster" claims reworded | v0.9.3 |
| B-020 | README case studies cut to one row each (27 KB → 21 KB) | v0.9.3 |
| B-021 | Quick Start replaced with a runnable 3-step `claude-md-lint.py` path | v0.9.3 |
| B-027 | GitHub topics and homepage set (repo settings, not a file change) | v0.9.3 |

## Review log

| Date | Source | Items added |
|------|--------|-------------|
| 2026-11-12 | Re-review at v0.9.2 against GitHub (0 open issues, 0 open PRs, 36 stars, 5 forks, no topics, community health 57%). Added B-007, B-008, B-017, B-018, B-027, B-028 (B-029 split from B-020 during v0.9.3). Promoted B-004 and B-021 to P1, B-033 from P3 to P2. Shipped B-003, B-004, B-020, B-021, B-027 in v0.9.3. | B-007, B-008, B-017, B-018, B-027, B-028, B-029 |
| 2026-11-02 | Full repo review at v0.9.0 (README, CONTRIBUTING, CHANGELOG, CI, all tools skimmed; `check-links.py` passes) | B-001 to B-033 |

Not checked in the first review: the 22 `examples/*.md` bodies were not read line by line, and no tool was run beyond `check-links.py`. Treat B-001 and B-005 as read-from-source, not reproduced.
