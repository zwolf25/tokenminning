# Contributing to Tokenminning

We welcome real-world examples, counterexamples, and tool-specific patterns from practitioners.

## What We Want

| Type | Description | Format |
|------|-------------|--------|
| **Case Study** | Measured before/after results from production | `examples/case-study-XX-name.md` |
| **Technique Guide** | Practical application to a specific system | `examples/technique-name.md` |
| **Counterexample** | Where tokenminning doesn't apply / fails | Discussion → Counterexamples |
| **Tool Pattern** | How a specific tool (Cursor, Codex, etc.) applies tokenminning | `techniques/tool-name.md` |
| **Runnable Tool** | A generalizable, working script/utility implementing a tokenminning technique | `tools/tool-name/` (with its own README) |

## Guidelines

- **Real-world only** — no theoretical proposals
- **Measured results** — case studies need before/after metrics
- **Follow existing format** — match the structure of current case studies
- **Link context** — reference the original system/workflow

## How to Contribute

1. Fork the repo
2. Add your content to `examples/` or `techniques/`
3. Update the README tables if adding a new case study/technique
4. Open a PR

## Contributing a Tool

`tools/` holds runnable code (scripts, CLIs); `techniques/` holds prose about how a third-party tool applies tokenminning — pick the right one before you start.

1. Fork the repo
2. Add a self-contained `tools/<name>/` directory with its own README (install + usage)
3. Cross-link it from the relevant `examples/*.md` case study and from `examples/index.md`'s "Runnable Artifacts" table
4. Add a "Try it" link to the matching README.md table row
5. Open a PR

## Discussion First

For exploration, questions, or "does this belong here?" — start a [Discussion](https://github.com/zwolf25/tokenminning/discussions) instead.

## License

By contributing, you agree your contributions are licensed under MIT.
