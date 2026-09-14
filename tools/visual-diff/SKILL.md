---
name: visual-diff
description: Run this BEFORE viewing (Read-ing) any screenshot, slide export, or UI mockup image to check whether an AI-made edit worked — not after. This is default behavior, not opt-in: pipe the screenshot through visual-diff.js as part of the same step that produces or locates the image, rather than viewing it first and diffing later — a post-hoc PostToolUse rewrite doesn't reliably work for this in current Claude Code (see the still-open bug anthropics/claude-code#68951, where output-rewriting hooks silently no-op on built-in tools). Trigger on "check this looks right", "validate the slide/deck/mockup", "did that edit work", "does this match the design", "compare before and after", "take a screenshot and confirm", or any moment you're about to view an image specifically to judge whether it changed or changed correctly. Skip only when the user explicitly wants the raw/full image regardless of diff ("just show me", "I want the full screenshot"). Give it a stable --key for the artifact (file+slide/page, or a design-tool node id) so repeat checks compare against the right baseline — a fresh key every run silently defeats the whole cache.
---

# visual-diff

Pixel-diff pre-filter for screenshot validation. Compares a new screenshot against a cached
baseline of the same artifact: if nothing meaningfully changed, you never view the image at
all (near-zero vision tokens); if something did change, you view a small crop of just the
changed region instead of the full screenshot.

**Token rule (do not break):** on a `skip` decision, do not `Read` the screenshot — the JSON
result is the answer ("no visual change, X% diff"). On a `crop` decision, `Read` only
`cropPath`, never the original full screenshot. On a `full` decision (first time seeing this
artifact), there's no baseline yet to compare against — view the original if you need to,
that only happens once per artifact.

## Step 1 — Prereq gate

Needs `node` on PATH plus the global `pixelmatch`/`pngjs` packages (`npm install -g pixelmatch
pngjs`, one-time). If missing, install first — don't fall back to viewing the raw screenshot
just to avoid the install step, that's the exact token cost this skill exists to avoid.

## Step 2 — Run it

```
node visual-diff.js "<screenshot-path>" --key "<stable-artifact-key>"
```

Point the path at wherever this tool is installed. `<stable-artifact-key>` should identify
*this artifact*, not this invocation — e.g. `roadmap-deck/slide-04`, or a Figma node id.
Reuse the same key across repeat checks on the same thing so the cache actually compares
against the right prior state.

Optional flags: `--threshold <pct>` (default 0.5 — % of pixels differing to count as a real
change), `--pad <px>` (default 24 — padding around the changed-pixel bounding box before
crop), `--max-dim <px>` (default 768 — long-edge cap after crop, downsampled if exceeded).

## Step 3 — Act on the JSON result

The script always prints one JSON object to stdout:

- `"decision": "skip"` — nothing meaningfully changed (`diffPercent` below threshold). Report
  this directly to the user ("no visual change, 0.1% diff") without viewing anything.
- `"decision": "crop"` — something changed. `Read` only `cropPath` (a small PNG of just the
  changed region + padding), not the original screenshot.
- `"decision": "full"` — first time this artifact's been checked, nothing to compare against
  yet. View the original screenshot if you need to; it becomes the baseline for next time.

Every run also logs one line to `~/.claude/cache/visual-diff/gain.jsonl` (decision, pixel
counts, estimated tokens saved) — a real-usage ledger so the token-savings estimate below can
eventually be replaced with a measured number.

## Estimated token savings (Anthropic image-token approximation: tokens ≈ width_px × height_px / 750)

| Case | Resolution | Tokens |
|---|---|---|
| Full screenshot | 2560×1440 | ~4,915 |
| Cropped + downsampled | 768×432 | ~442 |
| Skipped | — | ~0 |

Worked example — 10-slide deck, 2 slides actually edited, validating the whole deck: naive
full-res view of all 10 = ~49,150 tokens; with visual-diff, 8 skip + 2 crop ≈ ~1,300 tokens —
roughly **97% fewer tokens** on that validation pass. Treat this as an estimate until
`gain.jsonl` has real usage to tally.
