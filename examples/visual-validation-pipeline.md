# Technique Guide: Pixel-Diff Pre-Filter for Screenshot Validation

**Problem:** Validating an AI-made edit to a rendered artifact (a slide, a deck export, a UI
mockup) usually means viewing a full-resolution screenshot through vision — every time, even
when nothing changed. That's thousands of image tokens spent confirming a no-op, and the cost
repeats on every check, not just the first one.

**Solution:** A deterministic pixel-diff runs before the model ever sees the image. It
compares the new screenshot against a cached baseline of the same artifact: no meaningful
change means the model never views the image at all; a real change means the model views only
a small crop of what changed, not the full frame.

> **Note on evidence:** unlike the numbered Case Studies in this repo, the numbers below are a
> worked *estimate* from Anthropic's published image-tokenization approximation, not yet
> measured production results — this technique is newly extracted and hasn't accumulated real
> usage. The tool logs every decision to a local ledger (`gain.jsonl`) specifically so the
> estimate can be replaced with a measured number once it has; this guide will move to the
> numbered Case Studies list when that happens, per [CONTRIBUTING.md](../CONTRIBUTING.md)'s
> bar for what counts as one.

---

## The Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│  Screenshot taken (slide export, UI capture, deck render)       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  visual-diff.js (local subprocess, pixelmatch + pngjs)          │
│  ─────────────────────────────────────                          │
│  • Diffs against cached baseline for this artifact key          │
│  • No baseline yet → decision "full" (first sight, cache it)    │
│  • Below threshold → decision "skip" (image never read)         │
│  • Above threshold → crop to changed-pixel bbox + padding,      │
│    downsample if still oversized → decision "crop"              │
│  • Always refreshes the baseline; logs one gain.jsonl line      │
└──────────────────────────┬──────────────────────────────────────┘
                           │ JSON decision (+ small crop path, if any)
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Model                                                           │
│  ─────────────────────────────────────                          │
│  • skip  → reports "no visual change" from the JSON alone        │
│  • crop  → Reads only the small crop, never the full screenshot  │
│  • full  → Reads the original once; it's now the baseline        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Tokenminning Principles Applied

| Principle | How This Technique Embodies It |
|-----------|-------------------------------|
| **Deterministic Pre-filter** | The diff itself needs no judgment — `pixelmatch` computes it mechanically in a subprocess. The model only sees the outcome (skip/crop/full), same shape as `vault-lint.py`'s mechanical-findings-first pattern. |
| **Compress don't repeat** | A `crop` decision sends only the changed region, not the unchanged 90%+ of the frame around it. |
| **Retrieve don't preload** | Nothing is speculatively pre-viewed — the model only ever looks at an image when the diff says there's something worth looking at. |
| **Stub Pattern** | The script's output is a JSON decision + (on `crop`) a file path to a small image — never the full image content pushed into context by default. |
| **Escalation ladder, implicit** | `skip` (0 tokens) → `crop` (partial) → `full` (whole image, first-sight only) — cost scales with how much actually needs judgment, not a flat per-check cost. |

---

## Estimated Impact (methodology, not yet measured — see note above)

Anthropic's published image-tokenization approximation: tokens ≈ width_px × height_px / 750.

| Case | Resolution | Pixels | Tokens |
|---|---|---|---|
| Full screenshot | 2560×1440 | 3,686,400 | ~4,915 |
| Cropped + downsampled | 768×432 | 331,776 | ~442 |
| Skipped | — | 0 | ~0 (small JSON only) |

**Worked scenario** — 10-slide deck, 2 slides actually edited, validating the whole deck to
confirm nothing else broke:
- **Naive** (view all 10 full-res): 10 × 4,915 = **49,150 tokens**.
- **With visual-diff**: 8 skipped (~400 tokens of JSON total) + 2 cropped (~884) ≈ **~1,300 tokens**.
- **Estimated savings: ~97%** on that validation pass.

---

## Try It Yourself

```bash
npm install -g pixelmatch pngjs

node tools/visual-diff/visual-diff.js <screenshot-path> --key <artifact-key>
```

See [tools/visual-diff](../tools/visual-diff) for the full CLI reference, flags, and the
`--self-test` check.

---

## When to Use This

| Scenario | Fits? |
|----------|-------|
| Repeat-checking the same artifact across an editing session (slide, mockup, deck) | Yes — this is the core case; the cache only pays off on repeat checks against a stable key |
| One-off screenshot with no prior baseline | Still runs (`decision: "full"`), but there's nothing to skip yet — value shows up on the *next* check |
| Comparing two genuinely different artifacts | No — a diff needs a meaningful baseline; pass a stable, artifact-specific `--key`, not a session-scoped one |
| Content the user explicitly wants viewed regardless of diff | No — skip the pre-filter, view it directly |

---

## Anti-Patterns This Replaces

| Anti-Pattern | Token Cost | Replaced By |
|--------------|------------|-------------|
| `Read` every screenshot on every validation pass, changed or not | ~5K tokens/image, every time | `visual-diff.js` → `skip` decision, 0 tokens, when nothing changed |
| View the full frame to check one small edit | Full-resolution tokens for a small fraction of relevant pixels | `crop` decision → only the changed region |
| Re-derive "did this change?" from memory/description each session | Inconsistent, no ground truth | Cached baseline + deterministic pixel diff, same answer every time |

---

## Related Examples

- [`vault-lint-case-study.md`](vault-lint-case-study.md) — the same Deterministic Pre-filter principle applied to text/markdown findings instead of pixels
- [`honey-eso-ccr-evaluation.md`](honey-eso-ccr-evaluation.md) — documents the same Claude Code hook limitation (`PostToolUse` output-rewriting silently no-ops, [#68951](https://github.com/anthropics/claude-code/issues/68951)) that shaped this technique's "pipe into the originating step, not a post-hoc hook" design

---

## Source Code

Open-sourced in this repo: [`tools/visual-diff/`](../tools/visual-diff) — `visual-diff.js`
(pure JS, no native dependencies) + `SKILL.md` (Claude Code skill contract) + install/usage
README.
