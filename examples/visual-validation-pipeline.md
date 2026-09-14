# Case Study: Pixel-Diff Pre-Filter for Screenshot Validation

**Problem:** Validating an AI-made edit to a rendered artifact (a slide, a deck export, a UI
mockup) usually means viewing a full-resolution screenshot through vision — every time, even
when nothing changed. That's thousands of image tokens spent confirming a no-op, and the cost
repeats on every check, not just the first one.

**Solution:** A deterministic pixel-diff runs before the model ever sees the image. It
compares the new screenshot against a cached baseline of the same artifact: no meaningful
change means the model never views the image at all; a real change means the model views only
a small crop of what changed, not the full frame.

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

## Results (pre-build estimate — not yet a live measurement)

Unlike case studies elsewhere in this repo with a real production run to measure against, this
tool is newly extracted and hasn't accumulated real usage yet. These numbers are computed from
Anthropic's published image-tokenization approximation (tokens ≈ width_px × height_px / 750)
applied to realistic resolutions, flagged as an estimate rather than rounded up to look more
certain than it is — same standard as this repo's [Wiki Lint stub-sync
extension](vault-lint-case-study.md#extending-the-pattern-stub-sync--manifest-upsert-v2).

| Case | Resolution | Basis | Tokens |
|---|---|---|---|
| Full screenshot | 2560×1440 | Anthropic's public approximation, common export resolution | ~4,915 |
| Cropped + downsampled | 768×432 | Same formula, `--max-dim 768` default | ~442 |
| Skipped | — | JSON decision only, no image sent | ~0 |

**Worked scenario** — 10-slide deck, 2 slides actually edited, validating the whole deck to
confirm nothing else broke:
- **Naive** (view all 10 full-res): 10 × 4,915 = **49,150 tokens**.
- **With visual-diff**: 8 skipped (~400 tokens of JSON total) + 2 cropped (~884) ≈ **~1,300 tokens**.
- **Estimated savings: ~97%** on that validation pass.

**What would need to happen before this graduates to a measured entry**: run the tool in
production for a real stretch, then tally `~/.claude/cache/visual-diff/gain.jsonl` (every
invocation logs its decision and estimated tokens saved) against actual reported token usage
on visual-validation-heavy sessions — the same standard every other measured row in this
repo's case studies already meets.

---

## Validation (correctness, not yet token measurement)

Separate from the token-savings estimate above — this is evidence the mechanism actually
works, checked before publishing rather than assumed:

- **Self-test** (`node visual-diff.js --self-test`): synthetic identical + changed-block PNGs
  produce the correct `skip`/`crop` decision and an exact bounding box.
- **Real rendered content, not synthetic test squares**: ran the full `full` → `skip` → `crop`
  cycle against an actual PowerPoint export (PPTX → PDF → PNG). The crop's bounding box matched
  the real edited region exactly, pixel for pixel. Also independently re-rendered the same
  source file a second time (not a file copy — a fresh export) and diffed it against the first
  render: **0% difference**, confirming the rendering pipeline itself doesn't introduce enough
  noise (font hinting, antialiasing jitter) to false-positive against the default 0.5%
  threshold — a real calibration risk for any pixel-diff tool, checked rather than assumed.
- **Fresh-session auto-invocation, unbiased**: had an agent with no memory of this tool's
  design run three natural-language requests ("does this look right?", "I re-exported, nothing
  changed", "I added a callout box") against real screenshots, never naming the skill. All
  three self-triggered correctly: `full` on first sight (and derived a sensible artifact key
  from file + slide number on its own, unprompted), `skip` on the unchanged re-export
  (confirmed it did not re-view the image, per the token rule), `crop` on the real edit
  (described only the changed region, not the full frame).

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
