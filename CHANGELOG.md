# Changelog

One entry per release, newest first. Not a log of every commit — see git history for that.

## v0.2.5 — 2026-09-20

- Revised the [Context-Length Threshold](examples/context-length-threshold.md) case study from ~300k to ~250k using a more defensible baseline (cheapest well-populated bucket), documented how the baseline choice moves the knee, and linked the per-model `context-length-threshold` skill.

## v0.2.4 — 2026-09-20

- Added [Context-Length Threshold](examples/context-length-threshold.md) case study: per-turn cost from raw transcripts across 311 sessions shows ~2.4x cost at 300k context and ~4–5x at 500k+; turns above 300k are 30% of turns but ~49% of spend. Adopted a `/compact` at ~300k rule; includes caveats (assumed rate ratios, upper-bound saving).

## v0.2.3 — 2026-09-20

- Extended [Second Brain Config & Memory Audit](examples/second-brain-config-audit.md) with a follow-up on the `claude-md-audit` rubric (adapted from Alex Tong's MIT-licensed skill): noise taxonomy, tiers instead of scores, the no-precedence rule for cross-file contradictions, AUTO-vs-QUESTION fixes, and measured character reductions (-29% home file, -22% project file, -22% collaborator template) plus a triage-regression found during verification.

## v0.2.2 — 2026-09-20

- Extended [Second Brain Token Optimization](examples/second-brain-system.md) with a "Promotion" section (contributing local knowledge to the shared vault as a raw note, verify-then-trim, pointer wikis, owner/collaborator role split, measured local-size reduction with the caveat that it is not a per-session token saving) and a new anti-pattern: a derived-file sync that overwrites hand-curated fields.

## v0.2.1 — 2026-09-18

- Added [Stale Detection for Derived Documents](examples/derived-doc-staleness.md) case study: content-hash staleness with a size-materiality check, a guard against regenerating from a source thinner than the existing output, an output lint that catches skipped skill steps, and a peer-median thin-source check. Includes the measured cost of a plain refresh (about 86K tokens) versus rebuilding a thin source (about 400K), three dogfooding bugs, and the limits (no first-run saving, padding not detectable).
- Extended [Web Scraping Escalation](examples/web-scraping-escalation.md) with a "Delegation" section: the fallback ladder must be carried in every subagent prompt.

## v0.2.0 — 2026-09-14

- Added [`tools/visual-diff`](tools/visual-diff) — pixel-diff pre-filter for screenshot/slide/UI-mockup validation (pure JS via `pixelmatch`/`pngjs`, no native dependencies): skips vision entirely when a screenshot hasn't meaningfully changed against its cached baseline, crops to just the changed region otherwise. Extracted from the new [Pixel-Diff Screenshot Validation](examples/visual-validation-pipeline.md) case study (benchmarked on 30 synthetic cases; hit rates chosen, not observed in production).
- Cross-linked from README.md (Techniques table, Case Studies) and examples/index.md.

## v0.1.0 — 2026-09-07

First runnable code in the repo.

- Added [`tools/doc-convert`](tools/doc-convert) — zero-token document conversion (any doc → Markdown, Markdown → styled DOCX), extracted from the [Document Processing Pipeline](examples/document-processing.md) case study.
- Added [`tools/memory-template`](tools/memory-template) — a copy-pasteable agent memory pattern (typed frontmatter, self-shrinking index), extracted from the [Memory Systems](examples/memory.md) guide.
- Cross-linked both from README.md, examples/index.md, and their originating case studies.
