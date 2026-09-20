# Case Study: Honey/eso CCR Evaluation

**Scope:** Evaluated `green-pt/honey-for-devs` (Honey) — a 4-piece token-saving skill — against an existing Claude Code setup (RTK proxy + caveman/ponytail modes)
**Result:** Kept only CCR, vendored standalone as `eso`; rejected `honey-usage` (redundant/less accurate than `ccusage`); dropped a planned Windows shared-vault addendum
**Unexpected discovery:** Two reversals in one investigation, plus a live-confirmed Claude Code bug that changed how the surviving piece gets used

---

## Context

Existing setup:
- **RTK** — Rust CLI proxy rewriting recognized commands (`git status` → `rtk git status`), 92.2% lifetime token savings on the commands it covers
- **Caveman mode** — terse prose, drops filler
- **Ponytail mode** — blocks over-engineered code, YAGNI/stdlib-first

Honey (`green-pt/honey-for-devs`, 295★, MIT) merges the same two ideas as caveman+ponytail into
one skill, plus three novel pieces: **ESON** (a compact lossless handoff format), **CCR**
(Compress-Cache-Retrieve — lossy-but-recoverable compression of large uniform JSON arrays from
tool output), **PX** (renders large read-only text as PNG pages, useful only to a
Fable-class reader), and **honey-usage** (cross-agent token/cost/CO2 reporting).

Question: *does any of this add something the existing setup doesn't already cover?*

Did not install Honey wholesale — its ponytail/caveman merge collides with the already-installed
originals (same upstream authors it credits). Did not pursue PX — it only pays off for a
Fable-class reader, which this setup doesn't run day-to-day.

---

## Track 1 — CCR: kept, vendored standalone

RTK rewrites *recognized commands* (`git`, `grep`, `find`, …) — it has no mechanism for
compressing arbitrary uniform JSON-array output (an API response, a custom script's output, an
MCP tool result) that isn't one of those commands in the first place. CCR is additive on that
long tail, not a replacement for RTK's already-covered surface.

Tested for real, not just cited: built a synthetic 200-row log array (mostly `info` rows, with a
real anomaly cluster — 5 `error` rows and 3 `warn` rows) and ran the actual `eso crush` /
`eso retrieve` CLI.

**Result:** `crush` kept 15 of 200 rows — head/tail anchors plus *both* real anomaly windows,
correctly identified as change-points rather than evenly downsampled past them — plus one
sentinel row. **13,696 → 1,082 bytes, a 92.1% reduction.** `eso retrieve <hash>` restored the
original file byte-for-byte identical (verified with `diff`, zero differences) — the round-trip
is genuinely lossless, as documented.

**Verdict:** adopt standalone as a CLI (`eso crush` / `eso retrieve`), for uniform JSON-array
output outside RTK's recognized command set.

---

## Track 2 — honey-usage: rejected

Ran `honey-usage` against this account's actual `~/.claude/projects/**/*.jsonl` history. Real
lifetime numbers: **$2,452.08** total cost, 25.69kg CO2, 32.98M input / 17.04M output / 5.46B
cache-read / 122.23M cache-write tokens across 10 model rows — the single biggest line item was
5.43 **billion** cache-read tokens on one model row, dwarfing raw input/output by three orders of
magnitude.

Two problems surfaced:

1. **Redundant** — `ccusage`, an already-installed, actively-maintained tool, covers the same
   daily/weekly/monthly/session reporting with current-model pricing.
2. **Less accurate** — honey-usage's cost math measured roughly **47% off** on identical token
   counts, from stale pricing for newer models.

**Open question, not a resolved finding:** the same history also surfaced several non-Anthropic
model rows inside Claude Code's own session logs (names resembling third-party open-weight
models), each with real token/cost numbers computed via honey-usage's fallback pricing. The
source of these rows wasn't determined in this investigation — could be a proxy/gateway, an
eval harness, leftover test fixtures, or something else. Reporting it as an open question rather
than asserting a cause.

**Verdict:** rejected. `ccusage` already does this, more accurately.

---

## Track 3 — Windows gap: reversed

The highest-leverage angle going in: RTK is Homebrew-only (Windows explicitly unsupported, WSL
blocked by a real virtualization issue), so every Windows collaborator on the shared team setup
gets 0% of the ~92% savings this setup gets from RTK. Honey's install mechanics turned out to be
genuinely cross-platform by construction — its installer delegates straight to Node, and its
Claude Code plugin hooks are OS-agnostic (`node -e` invocations with explicit path-separator
normalization, no bash/sh dependency anywhere).

That made a Honey-plugin Windows addendum look like the fix — until checking upstream directly:
**`rtk-ai/rtk` (the RTK family itself, 79,324★) already ships a native Windows build**
(`rtk-x86_64-pc-windows-msvc.zip`, confirmed via the GitHub releases API). That's a better fix
than a substitute tool — same mechanism, not an approximation of it — so the shared team vault
was updated with the native RTK Windows build instead, and the planned Honey-plugin addendum was
dropped entirely.

**Verdict:** moot. The real fix already existed upstream; it just hadn't been checked yet.

---

## Track 4 — a live bug, reproduced

Honey's own optional `PostToolUse` hook auto-compresses every Bash result. Before wiring it in:
reproduced [`anthropics/claude-code#68951`](https://github.com/anthropics/claude-code/issues/68951)
against the actual installed build (2.1.236, 2026-09-09) using the issue's own minimal repro —
confirming the hook fires and reports success, but the model still receives the original,
uncompressed output. This isn't a stale report from an older version; it reproduces on a current
build. Re-checked 2026-09-20: the issue is still open (last updated 2026-09-07).

**Resolution:** skipped the hook. Instead, made "pipe through `eso crush` yourself, as part of
the same command, when output is likely to be a large uniform array" the default instruction —
that sidesteps the bug entirely, since the crushed output *is* the tool result from the start,
never a post-hoc rewrite.

---

## Token Savings

| Category | Amount | Notes |
|---|---|---|
| **RTK (existing, unrelated to this evaluation)** | 92.2% lifetime | 19,576 commands, 176.0M of 190.9M+ tokens saved — the baseline this evaluation checked against |
| **CCR, synthetic test** | 92.1% | 13,696 → 1,082 bytes, byte-identical retrieve |
| **honey-usage** | 0% (rejected) | Redundant with `ccusage`, and ~47% less accurate |
| **Windows-gap fix** | N/A (reversed) | Solved upstream by RTK's own native Windows build, not by this evaluation |

---

## Mapping to Tokenminning Principles

| Principle | Applied Here |
|---|---|
| **Retrieve, don't preload** | CCR keeps a sampled view and retrieves dropped rows only on demand, by hash |
| **Compress, don't repeat** | CCR compresses tool output once at the source, matching RTK's own approach to a different surface |
| **Structure, don't narrate** | A sentinel marker (`_ccr` + hash) replaces prose explanation of what was dropped |
| **Design systems, not prompts** | The fix for the hook bug is a documented default-behavior instruction, not a one-off ask each time |
| **Optimize context, not complexity** | Rejected `honey-usage` and the Windows addendum once each was shown to duplicate something simpler that already existed |
| **Eliminate context debt continuously** | Checking `rtk-ai/rtk`'s own releases before building a substitute closed a gap that would otherwise have shipped as unnecessary new tooling |
| **Spend tokens where reasoning matters** | Live-reproducing the hook bug spent effort confirming a workaround was necessary, not skipped as "probably fine" |

---

## Key Insights

1. **Paired-delta beats ratio-of-totals** — Honey's own README benchmarks per-task deltas against
   a baseline and reports the median with a significance test, explicitly to avoid the failure
   mode where "a tool's published number is dominated by its one longest test case." Worth
   applying whenever evaluating *any* token-saving tool's claims, not just this one.

2. **Check upstream before building a substitute** — the Windows gap looked like it needed a new
   piece of tooling until a five-minute check of `rtk-ai/rtk`'s own releases showed the real fix
   already existed. The investigation's most valuable output was *not* building something.

3. **Redundancy checks are still work** — `honey-usage` looked like a clean addition until it was
   run against real history and compared to what was already installed. It lost on both
   uniqueness and accuracy.

4. **Reproduce, don't cite** — the hook bug was confirmed against this machine's actual current
   build, not accepted on the strength of the upstream issue report alone. A workaround built on
   an unverified report is a workaround for a maybe-problem.

5. **A one-machine test can become team infrastructure in the same session** — CCR started as
   "test this standalone" and, once it held up, was vendored to the shared team setup with the
   same onboarding and audit hooks RTK already has — without ever growing beyond three plain
   files and a wrapper script.

---

## Files / Artifacts

- **Raw notes:** dated investigation notes covering both reversals and the live bug repro
- **Config:** a short usage note added to the personal setup, documenting when to reach for CCR
  and why the auto-hook is deliberately not wired in
- **Team rollout:** the same standalone tool and usage note mirrored into the shared team setup,
  with an onboarding step and an audit-check addition — the same distribution path RTK took
- **Upstream:** [`anthropics/claude-code#68951`](https://github.com/anthropics/claude-code/issues/68951) (reproduced, not filed)
