# visual-diff

Pixel-diff pre-filter for screenshot validation. Runs as a local subprocess — no API calls,
no model tokens spent deciding whether an image is worth looking at. See [Visual Validation
Pipeline](../../examples/visual-validation-pipeline.md) for the case study this was extracted
from.

Compares a new screenshot against a cached baseline of the same artifact:
- Nothing meaningfully changed → the model never views the image at all.
- Something changed → the model views only a small crop of the changed region, not the full screenshot.

## Install

```bash
# from this folder (or `npm install -g pixelmatch pngjs`, also resolved)
npm install
```

Pure JS, no native bindings — deliberately not `sharp` or another native-compiled image lib,
so this runs identically on any collaborator's machine with zero build tooling.

## Usage

```bash
node visual-diff.js <screenshot-path> --key <artifact-key> [--threshold 0.5] [--pad 24] [--max-dim 768]
```

`--key` should identify the artifact, not the invocation (e.g. `deck/slide-04`, a Figma node
id) — reused across repeat checks so the cache compares against the right prior state. A
fresh key every run defeats the cache entirely.

Prints one JSON object to stdout:

```json
{"decision": "skip", "diffPercent": 0.08, "key": "deck/slide-04", "estimatedTokensSaved": 4915}
```

- `"decision": "skip"` — below `--threshold`% pixels changed. Report this directly; don't view anything.
- `"decision": "crop"` — real change. View only `cropPath` (a small PNG of the changed region + padding), never the original.
- `"decision": "full"` — first time this artifact's been checked, nothing to diff against yet. Becomes the baseline for next time.

Every run also appends one line to `~/.claude/cache/visual-diff/gain.jsonl` (override the directory with `VISUAL_DIFF_CACHE_DIR` or `--cache-dir`) (decision, pixel
counts, estimated tokens saved) — a real-usage ledger so the estimate below can be replaced
with a measured number over time.

Run `node visual-diff.js --self-test` to verify the diff/crop/downsample logic against two
synthetic PNGs (no fixtures, no test framework).

## Why this exists

Validating an AI-made edit to a rendered artifact (a slide, a UI mockup) usually means viewing
a full-resolution screenshot through vision — every time, even when nothing changed. That's
thousands of image tokens spent confirming a no-op. A pixel diff is mechanical; it doesn't
need a model to compute. This tool does that part in a subprocess so vision tokens go only to
the pixels that actually changed. See the case study for measured numbers:
[examples/visual-validation-pipeline.md](../../examples/visual-validation-pipeline.md).

## Claude Code users

[`SKILL.md`](SKILL.md) packages this as a Claude Code skill, so Claude routes to it
automatically on requests like "check this slide looks right" or "did that edit work" —
before viewing any screenshot, not after. Drop this folder into your skills directory to use
it that way; the CLI script works standalone regardless of what agent or editor you're using.
