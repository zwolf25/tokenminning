// Pixel-diff pre-filter for screenshot validation. Compares a screenshot against a cached
// baseline for the same artifact; skips showing the image at all when nothing meaningfully
// changed, and crops+downsamples to just the changed region when it did.
//
// Usage:
//   node visual-diff.js <screenshot-path> --key <artifact-key> [--threshold 0.5] [--pad 24]
//                        [--max-dim 768] [--cache-dir <path>] [--no-update-baseline]
//   node visual-diff.js --self-test

const fs = require('fs');
const path = require('path');
const os = require('os');
const crypto = require('crypto');

// `pixelmatch`/`pngjs` are installed globally (`npm install -g pixelmatch pngjs`) — resolve via
// the global node_modules root if a plain require() can't find it, same pattern as doc-style/convert.js.
function requireGlobal(name) {
  try {
    return require(name);
  } catch (e) {
    if (e.code !== 'MODULE_NOT_FOUND') throw e;
    const { execSync } = require('child_process');
    const globalRoot = execSync('npm root -g', { encoding: 'utf8' }).trim();
    return require(path.join(globalRoot, name));
  }
}
const { PNG } = requireGlobal('pngjs');
// pixelmatch v7+ is ESM-only; Node's require() interop wraps it as { default: fn }.
const pixelmatchModule = requireGlobal('pixelmatch');
const pixelmatch = pixelmatchModule.default || pixelmatchModule;

function parseArgs(argv) {
  const args = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const key = a.slice(2);
      const next = argv[i + 1];
      if (next === undefined || next.startsWith('--')) {
        args[key] = true;
      } else {
        args[key] = next;
        i++;
      }
    } else {
      args._.push(a);
    }
  }
  return args;
}

function sha256(s) {
  return crypto.createHash('sha256').update(s).digest('hex');
}

function readPNG(filePath) {
  return PNG.sync.read(fs.readFileSync(filePath));
}

function writePNG(png, filePath) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, PNG.sync.write(png));
}

// Anthropic image-token approximation: tokens ~= width_px * height_px / 750.
function estimateTokens(width, height) {
  return Math.round((width * height) / 750);
}

function diffAndBBox(imgA, imgB) {
  const { width, height } = imgA;
  const diff = new PNG({ width, height });
  const numDiffPixels = pixelmatch(imgA.data, imgB.data, diff.data, width, height, {
    threshold: 0.1,
    diffMask: true,
  });
  let minX = width, minY = height, maxX = -1, maxY = -1;
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const idx = (width * y + x) << 2;
      if (diff.data[idx + 3] !== 0) {
        if (x < minX) minX = x;
        if (x > maxX) maxX = x;
        if (y < minY) minY = y;
        if (y > maxY) maxY = y;
      }
    }
  }
  const diffPercent = (numDiffPixels / (width * height)) * 100;
  const bbox = maxX >= minX ? { x: minX, y: minY, width: maxX - minX + 1, height: maxY - minY + 1 } : null;
  return { diffPercent, bbox };
}

function padBBox(bbox, pad, width, height) {
  const x = Math.max(0, bbox.x - pad);
  const y = Math.max(0, bbox.y - pad);
  const x2 = Math.min(width, bbox.x + bbox.width + pad);
  const y2 = Math.min(height, bbox.y + bbox.height + pad);
  return { x, y, width: x2 - x, height: y2 - y };
}

function cropPNG(png, box) {
  const out = new PNG({ width: box.width, height: box.height });
  PNG.bitblt(png, out, box.x, box.y, box.width, box.height, 0, 0);
  return out;
}

// Nearest-neighbor stride downsample — a real resize lib (sharp/Jimp) is overkill for
// "shrink until it fits the token budget"; ponytail: crop already did the heavy lifting.
function downsample(png, maxDim) {
  const { width, height } = png;
  const longEdge = Math.max(width, height);
  if (longEdge <= maxDim) return png;
  const scale = maxDim / longEdge;
  const newWidth = Math.max(1, Math.round(width * scale));
  const newHeight = Math.max(1, Math.round(height * scale));
  const out = new PNG({ width: newWidth, height: newHeight });
  for (let y = 0; y < newHeight; y++) {
    const srcY = Math.min(height - 1, Math.floor(y / scale));
    for (let x = 0; x < newWidth; x++) {
      const srcX = Math.min(width - 1, Math.floor(x / scale));
      const srcIdx = (width * srcY + srcX) << 2;
      const dstIdx = (newWidth * y + x) << 2;
      out.data[dstIdx] = png.data[srcIdx];
      out.data[dstIdx + 1] = png.data[srcIdx + 1];
      out.data[dstIdx + 2] = png.data[srcIdx + 2];
      out.data[dstIdx + 3] = png.data[srcIdx + 3];
    }
  }
  return out;
}

function defaultCacheDir() {
  return process.env.VISUAL_DIFF_CACHE_DIR || path.join(os.homedir(), '.claude', 'cache', 'visual-diff');
}

function appendGainLog(cacheDirPath, entry) {
  fs.mkdirSync(cacheDirPath, { recursive: true });
  fs.appendFileSync(path.join(cacheDirPath, 'gain.jsonl'), JSON.stringify(entry) + '\n');
}

function assertEq(actual, expected, msg) {
  if (actual !== expected) {
    console.error('SELF-TEST FAILED:', msg, '(actual:', actual, ', expected:', expected, ')');
    process.exit(1);
  }
}

function selfTest() {
  const width = 200, height = 150;

  const base = new PNG({ width, height });
  base.data.fill(255);
  const same = new PNG({ width, height });
  same.data.fill(255);
  const r1 = diffAndBBox(base, same);
  assertEq(r1.diffPercent === 0, true, 'identical images should have 0% diff');
  assertEq(r1.bbox, null, 'identical images should have no bbox');

  const changed = new PNG({ width, height });
  changed.data.fill(255);
  for (let y = 60; y < 110; y++) {
    for (let x = 80; x < 130; x++) {
      const idx = (width * y + x) << 2;
      changed.data[idx] = 255; changed.data[idx + 1] = 0; changed.data[idx + 2] = 0; changed.data[idx + 3] = 255;
    }
  }
  const r2 = diffAndBBox(base, changed);
  assertEq(r2.diffPercent > 0, true, 'changed image should have nonzero diff');
  assertEq(!!r2.bbox, true, 'bbox should exist for a real change');
  assertEq(r2.bbox.x, 80, `bbox.x should match the changed block, got ${JSON.stringify(r2.bbox)}`);
  assertEq(r2.bbox.y, 60, `bbox.y should match the changed block, got ${JSON.stringify(r2.bbox)}`);

  const cropped = cropPNG(changed, padBBox(r2.bbox, 10, width, height));
  assertEq(cropped.width, r2.bbox.width + 20, 'padded crop width should include padding');

  const big = new PNG({ width: 2000, height: 1000 });
  const small = downsample(big, 500);
  assertEq(small.width, 500, 'downsample should cap the long edge');
  assertEq(small.height, 250, 'downsample should preserve aspect ratio');

  const untouched = downsample(base, 500);
  assertEq(untouched.width, width, 'downsample should no-op when already under max-dim');

  console.log('self-test OK');
}

function main() {
  const argv = process.argv.slice(2);
  const args = parseArgs(argv);

  if (args['self-test']) {
    selfTest();
    return;
  }

  const screenshotPath = args._[0];
  if (!screenshotPath || !args.key) {
    console.error('Usage: node visual-diff.js <screenshot-path> --key <artifact-key> [--threshold 0.5] [--pad 24] [--max-dim 768] [--cache-dir <path>] [--no-update-baseline]');
    process.exit(1);
  }

  const threshold = args.threshold !== undefined ? parseFloat(args.threshold) : 0.5;
  const pad = args.pad !== undefined ? parseInt(args.pad, 10) : 24;
  const maxDim = args['max-dim'] !== undefined ? parseInt(args['max-dim'], 10) : 768;
  const cacheBase = typeof args['cache-dir'] === 'string' ? args['cache-dir'] : defaultCacheDir();
  const updateBaseline = !args['no-update-baseline'];

  const key = args.key;
  const keyHash = sha256(key);
  const artifactDir = path.join(cacheBase, keyHash);
  const baselinePath = path.join(artifactDir, 'baseline.png');
  const metaPath = path.join(artifactDir, 'meta.json');

  const current = readPNG(screenshotPath);
  const { width, height } = current;
  const fullTokens = estimateTokens(width, height);

  let result;
  let baselineExists = fs.existsSync(baselinePath);
  let baseline = null;
  if (baselineExists) {
    baseline = readPNG(baselinePath);
    if (baseline.width !== width || baseline.height !== height) {
      baselineExists = false; // can't diff mismatched dimensions — treat as first sight
    }
  }

  if (!baselineExists) {
    result = {
      decision: 'full',
      diffPercent: null,
      key,
      imagePath: screenshotPath,
      estimatedTokensBaseline: fullTokens,
      estimatedTokensActual: fullTokens,
      estimatedTokensSaved: 0,
    };
  } else {
    const { diffPercent, bbox } = diffAndBBox(baseline, current);
    if (diffPercent < threshold || !bbox) {
      result = {
        decision: 'skip',
        diffPercent,
        key,
        estimatedTokensBaseline: fullTokens,
        estimatedTokensActual: 0,
        estimatedTokensSaved: fullTokens,
      };
    } else {
      const padded = padBBox(bbox, pad, width, height);
      const coverage = (padded.width * padded.height) / (width * height);
      const cropBox = coverage < 0.9 ? padded : null;
      const preDownsample = cropBox ? cropPNG(current, cropBox) : current;
      const outImg = downsample(preDownsample, maxDim);
      const outPath = path.join(os.tmpdir(), 'visual-diff', `${keyHash}-${Date.now()}.png`);
      writePNG(outImg, outPath);
      const actualTokens = estimateTokens(outImg.width, outImg.height);
      result = {
        decision: 'crop',
        diffPercent,
        key,
        cropPath: outPath,
        cropBox,
        estimatedTokensBaseline: fullTokens,
        estimatedTokensActual: actualTokens,
        estimatedTokensSaved: Math.max(0, fullTokens - actualTokens),
      };
    }
  }

  if (updateBaseline) {
    writePNG(current, baselinePath);
    fs.writeFileSync(metaPath, JSON.stringify({
      key, width, height, diffPercent: result.diffPercent, updatedAt: new Date().toISOString(),
    }, null, 2));
  }

  appendGainLog(cacheBase, {
    timestamp: new Date().toISOString(),
    key,
    decision: result.decision,
    widthPx: width,
    heightPx: height,
    diffPercent: result.diffPercent,
    estimatedTokensSaved: result.estimatedTokensSaved,
  });

  console.log(JSON.stringify(result));
}

main();
