# derived-stale

Content-hash staleness check for model-generated documents derived from a source page. Zero dependencies (Python 3 stdlib), local, no model tokens. Extracted from the [Stale Detection for Derived Documents](../../examples/derived-doc-staleness.md) case study.

```bash
python3 derived-stale.py check SOURCE OUTDIR   # exit 1 + reason if stale
python3 derived-stale.py stamp SOURCE OUTDIR   # run after a refresh
python3 derived-stale.py guard SOURCE REPORT   # exit 1 if source < 0.9x report; else writes REPORT.prev
python3 derived-stale.py peers SOURCE...       # flag sources under 0.5x the median size
python3 derived-stale.py --self-test
```

- **Sidecar** `OUTDIR/.source-hash` holds `<12-hex sha256> <date> <bytes>` of the source body (frontmatter stripped, line endings and trailing spaces normalized). A sidecar, not an in-document comment, because converters copy HTML comments into the rendered file.
- **Stale** = hash changed AND (dated entries newer than the sidecar date OR size moved 5% or more). A frontmatter `updated:` bump or a one-line note stays fresh.
- **Guard** blocks regenerating from a source thinner than the existing report.
- Thresholds (5%, 0.9, 0.5) are fit to one corpus; edit the constants at the top and re-measure on yours.
- Not included: the output lint and the weekly nudge from the case study. Add when needed.
