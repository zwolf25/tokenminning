# Changelog

One entry per release, newest first. Not a log of every commit — see git history for that.

## v0.2.0 — 2026-09-14

- Added [`tools/visual-diff`](tools/visual-diff) — pixel-diff pre-filter for screenshot/slide/UI-mockup validation (pure JS via `pixelmatch`/`pngjs`, no native dependencies): skips vision entirely when a screenshot hasn't meaningfully changed against its cached baseline, crops to just the changed region otherwise. Extracted from the new [Pixel-Diff Screenshot Validation](examples/visual-validation-pipeline.md) case study (pre-build estimate, not yet a live measurement — same convention as the Wiki Lint case study's stub-sync extension).
- Cross-linked from README.md (Techniques table, Case Studies) and examples/index.md.

## v0.1.0 — 2026-09-07

First runnable code in the repo.

- Added [`tools/doc-convert`](tools/doc-convert) — zero-token document conversion (any doc → Markdown, Markdown → styled DOCX), extracted from the [Document Processing Pipeline](examples/document-processing.md) case study.
- Added [`tools/memory-template`](tools/memory-template) — a copy-pasteable agent memory pattern (typed frontmatter, self-shrinking index), extracted from the [Memory Systems](examples/memory.md) guide.
- Cross-linked both from README.md, examples/index.md, and their originating case studies.
