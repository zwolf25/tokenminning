# Tokenminning

<p align="center">
  <img src="resources/logo-dark.png" alt="Tokenminning" width="400"/>
</p>

<p align="center">
  <strong>Maximize intelligence per token</strong>
  <br/>
  <em>Not by minimizing tokens, but by delivering the right context at the right time</em>
</p>

<p align="center">
  <a href="https://github.com/zwolf25/tokenminning/stargazers"><img src="https://img.shields.io/github/stars/zwolf25/tokenminning?style=flat-square&color=111111&label=stars" alt="GitHub Stars"></a>
  <a href="https://github.com/zwolf25/tokenminning/commits/main"><img src="https://img.shields.io/github/commit-activity/m/zwolf25/tokenminning?style=flat-square&color=111111&label=commits%2Fmo" alt="Monthly Commits"></a>
  <a href="https://github.com/zwolf25/tokenminning/commits/main"><img src="https://img.shields.io/github/last-commit/zwolf25/tokenminning?style=flat-square&color=111111&label=last%20commit" alt="Last Commit"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square&color=111111" alt="License"></a>
  <a href="https://github.com/zwolf25/tokenminning/pulls"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square&color=111111" alt="PRs Welcome"></a>
  <a href="https://medium.com/@zwolf25"><img src="https://img.shields.io/badge/medium-%40zwolf25-000000?style=flat-square&logo=medium&color=111111" alt="Medium"></a>
</p>

<p align="center">
  <a href="#case-studies">Case Studies</a> •
  <a href="#principles">Principles</a> •
  <a href="#techniques">Techniques</a> •
  <a href="#real-world-results">Results</a> •
  <a href="CONTRIBUTING.md">Contributing</a> •
  <a href="https://medium.com/@zwolf25">Articles</a>
</p>

---

## Why Tokenminning?

| Tokenmaxxing | Tokenminning |
|:---|:---|
| "How do I give the model **more** context?" | "How do I give the model the **right** context?" |
| Add more context | Add **better** context |
| Bigger prompts | **Denser** prompts |
| Load everything | **Retrieve what matters** |
| More memory | **Better memory architecture** |
| More tokens | **More intelligence per token** |

> **Tokenminning is not:** minimizing tokens to cut costs, aggressively shortening prompts, removing useful context, or avoiding large context windows.
>
> **Tokenminning is:** improving information density, eliminating context debt, and designing systems where the right context arrives at the right time.

![Tokenmaxxing vs Tokenminning](resources/TokenmaxxingVsTokenminning)

---

## Quick Start

Tokenminning isn't a tool—it's a design philosophy. Apply it in 3 steps:

```bash
# 1. Audit what's always loaded
grep -r "always.*load\|preload\|startup" .claude/ CLAUDE.md

# 2. Replace full clones with stubs (summary + source-path)
# 3. Add escalation ladder: local cache → stub → on-demand read
```

**Start here:** Read the [Principles](#principles) → Pick a [Case Study](#case-studies) → Apply one technique to your setup.

---

## Principles

| # | Principle | One-Liner |
|:---:|:---|:---|
| 1 | **🔍 Retrieve, don't preload** | Supply relevance on demand |
| 2 | **🗜️ Compress, don't repeat** | Cut redundant instructions & history |
| 3 | **📋 Structure, don't narrate** | Prefer structured data over prose |
| 4 | **🎯 Spend tokens where reasoning matters** | Allocate budget to high-value thinking |
| 5 | **🏗️ Design systems, not prompts** | Architecture (retrieval, tools, memory) drives savings |
| 6 | **⚙️ Optimize context, not complexity** | "What does the model need right now?" |
| 7 | **🧹 Eliminate context debt continuously** | Audit memories, routing, config like production code |

![Tokenminning Decision Tree](resources/TokenminningDecisionTree.png)

> [!NOTE]
> These principles emerged from production Second Brain workflows at ServiceChannel, not theoretical speculation.

---

## Techniques

| Technique | Description | Case Study |
|:---|:---|:---|
| **Stub Pattern** | Replace full clones with `summary + source-path` pointers | [Second Brain](examples/second-brain-system.md) |
| **Grep-before-read** | Never read a folder wholesale; search first | [Config Audit](examples/second-brain-config-audit.md) |
| **Escalation Ladder** | Level 1: local cache → Level 2: stub lookup → Level 3: on-demand read | [All] |
| **Compaction** | Keep active context ≤ 15K tokens | [Wiki Pipeline](examples/wiki-pipeline.md) |
| **Thin Routers** | Startup instructions = behavior/routing only; retrieve details on demand | [Config Audit](examples/second-brain-config-audit.md) |
| **Single Source of Truth** | Store durable knowledge once, reference everywhere | [All] |
| **Deterministic Pre-filter** | Run a zero-dep script first; model only judges flagged items | [Wiki Lint](examples/vault-lint-case-study.md) |
| **Zero-Token Content Processing** | Convert binary (PDF/DOCX/VTT) locally via subprocess; model only sees file path | [Doc Pipeline](examples/document-processing.md) |
| **Schema-Enforced Extraction** | Rigid output schema (7 categories) forces structured data; no prose summaries | [Doc Pipeline](examples/document-processing.md) |
| **Failure-Mode Driven Escalation** | Each ladder level has documented failure mode → next level; no guessing | [Web Ladder](examples/web-scraping-escalation.md) |
| **Contract-Driven Tool Discipline** | Versioned SKILL.md contracts enforce token rules, routing, composition by design | [Skill System](examples/skill-tooling-pattern.md) |

---

## Real-World Results

| Metric | Before | After | Change |
|:---|:---:|:---:|:---:|
| **Second Brain wiki words** | 211K | 28K | **87% ↓** |
| **Wiki pipeline cost/run** | $50+ (11 agents) | $15–25 (2–3 agents) | **~70% ↓ cost, 80% ↓ agents** |
| **CLAUDE.md size** | ~48.6 KB | 34.4 KB | **29% ↓ (~3,500 tokens/session)** |
| **Stale sync clones** | 66% | 0% | **100% eliminated** |
| **RTK adoption gap** | 94% commands bypassed | → upstream fix | **1.5M tokens/30d recovered** |
| **Wiki lint pre-filter (this repo)** | 8.5M tokens/run | ~1.2M est. | **~86% ↓** |

> [!NOTE]
> These are measured results from production Second Brain workflows, not synthetic benchmarks.

---

## Tooling Measured Results

*Production skill stack metrics (from Case Studies 6–8):*

| Workflow | Before (Prompt-Based) | After (Skill System) | Improvement |
|:---|:---:|:---:|:---:|
| **50-page PDF → Wiki** | ~80K tokens, manual | ~500 tokens, automated | **99.4% ↓** |
| **2-hr VTT → Decisions** | ~45K tokens, error-prone | ~300 tokens, schema-enforced | **99.3% ↓** |
| **Competitor research (10 sites)** | ~500K tokens, ad-hoc | ~5K tokens, ladder + cache | **99% ↓** |
| **Market research report** | $50+, 11 agents, manual | $15-25, 2-3 agents, pipeline | **~70% cost ↓** |
| **Context debt (stale clones)** | 66% of files | 0% (fingerprint dedup) | **Eliminated** |
| **Prompt drift / repeated instructions** | High (re-prompt every task) | Zero (contract loaded once) | **Eliminated** |
| **Tool usage consistency** | Variable (human-dependent) | 100% (enforced by skill) | **Guaranteed** |
| **New capability onboarding** | Hours (re-teach via prompt) | Minutes (install → auto-routes) | **100x faster** |

---

## Case Studies

<details>
<summary><strong>Case Study 1: Second Brain — 211K → 28K words (87% reduction)</strong></summary>

**Problem:** Team knowledge vault full of full-body clones  
**Fix:** Stub Pattern + Grep-before-read + Escalation ladder  
**Result:** 87% word reduction, $15–25 → $2–4/session, 66% → 0% stale clones

[Read full case study →](examples/second-brain-system.md)
</details>

<details>
<summary><strong>Case Study 2: RTK & LLMLingua Evaluation — 1.5M token adoption gap found</strong></summary>

**Problem:** Which external token tools improve CLI setup?  
**Fix:** Evaluated 4 repos → kept RTK (deterministic tool-output compression), rejected LLMLingua (lossy prompt compression)  
**Discovery:** `rtk discover` revealed only 6% of Bash calls used RTK (~1.5M tokens/30d missed)

[Read full case study →](examples/rtk-llmlingua-evaluation.md)
</details>

<details>
<summary><strong>Case Study 3: Config & Memory Audit — 3,500 tokens/session recurring savings</strong></summary>

**Problem:** CLAUDE.md files bloated, MEMORY.md growing unbounded  
**Fix:** 4-type memory classification + CLAUDE.md consistency audit + monthly auto-enforcement  
**Result:** 29% CLAUDE.md reduction, MEMORY.md → 0 bytes, recurring ~3,500 tokens/session saved

[Read full case study →](examples/second-brain-config-audit.md)
</details>

<details>
<summary><strong>Case Study 4: Wiki Pipeline — $50 → $15/run (80% fewer agents)</strong></summary>

**Problem:** Cleanup skill defaulted to full-vault audit (92 wikis) when only 12 changed  
**Fix:** Added "recently-touched" scope tier seeded from builder run; full-vault now opt-in via `--full`  
**Result:** 11→2–3 agents, ~70% cost reduction, 4 root-cause fixes across 2 skills

[Read full case study →](examples/wiki-pipeline.md)
</details>

<details>
<summary><strong>Case Study 5: Wiki Lint — 85% mechanical findings eliminated, 86% token reduction</strong></summary>

**Problem:** 4 wiki-maintenance skills re-read every file for 5 mechanical checks (~91 model `Read` calls/run)
**Fix:** Deterministic `vault-lint.py` (zero deps, ~2s) emits structured findings; skills now **only Read what's flagged**
**Result:** 90 → 13 mechanical findings (85.6% ↓), 73 stub freshness issues → 0, $8.12 → ~$1.15/run est.

[Read full case study →](examples/vault-lint-case-study.md)
</details>

<details>
<summary><strong>Case Study 6: Document Processing Pipeline — 99.3%+ token reduction via local subprocesses</strong></summary>

**Problem:** Reading raw binary (PDF, DOCX, VTT) into LLM context wastes 10K–100K+ tokens/file on formatting syntax
**Fix:** 3-skill local pipeline (doc-convert → vtt-normalizer → doc-ingest) — all conversion in subprocesses, zero tokens spent on content
**Result:** 99.4% ↓ tokens (50-page PDF), 99.3% ↓ (2-hr VTT), Haiku-only extraction cost ~$0.10/batch

[Read full case study →](examples/document-processing.md)
</details>

<details>
<summary><strong>Case Study 7: Web Scraping Escalation Ladder — 7-level fallback from API credits to free local tools</strong></summary>

**Problem:** No single web tool handles all cases (static, JS, Cloudflare, auth, bulk crawl) — defaulting to one burns credits/time
**Fix:** 7-level ladder encoded in firecrawl skill: search→scrape→cached→scrapling-fast→scrapling-stealth→webclaw→playwright, each with documented failure mode
**Result:** 100% credit savings on repeat fetches, ~95% fewer monitor fetches, unblocked when credits exhausted, 10x faster on Cloudflare pages

[Read full case study →](examples/web-scraping-escalation.md)
</details>

<details>
<summary><strong>Case Study 8: Skill Tooling Pattern — 100+ versioned skills as "Design systems not prompts"</strong></summary>

**Problem:** Prompt engineering doesn't scale — drifts, unversioned, untestable, every task a blank slate
**Fix:** Skill system where every capability is a versioned SKILL.md contract: composable, routes by trigger phrase, enforces token rules by design
**Result:** Eliminated prompt drift, 100% tool consistency, minutes-to-onboard new capabilities, systematic token discipline via contract

[Read full case study →](examples/skill-tooling-pattern.md)
</details>

---

## Technique Guides

Practical applications of tokenminning to specific systems:

| Guide | Focus |
|-------|-------|
| [Claude Code & `CLAUDE.md`](examples/claude-code.md) | Keep config focused; retrieve on demand |
| [MCP / Tool Scoping](examples/mcp.md) | Load capabilities only when workflow needs them |
| [Memory Systems](examples/memory.md) | Preserve decisions/constraints, not transcripts |
| [RAG Pipelines](examples/rag.md) | Rank → filter → focus; quality over quantity |
| [Local Document Pipeline](examples/document-processing.md) | Zero-token binary→markdown→structured extraction |
| [Web Scraping Escalation](examples/web-scraping-escalation.md) | 7-level ladder: credits → cache → free local → browser |
| [Skill System as DSNP](examples/skill-tooling-pattern.md) | 100+ versioned contracts, thin router, composable |
| [All Examples Index](examples/index.md) | Quick reference for all 13 patterns |

> These are *technique guides* — not measured case studies. Case studies in `examples/` (`second-brain-system.md`, etc.) show before/after metrics.

---

## How It Works

Tokenminning operates on a simple **escalation ladder** — the model only sees what it needs, when it needs it:

```
┌─────────────────────────────────────────────────────────────┐
│  LEVEL 1: LOCAL CACHE                                       │
│  Hot context, recent decisions, active task state           │
│  → Always loaded, ≤ 2K tokens                               │
├─────────────────────────────────────────────────────────────┤
│  LEVEL 2: STUB LOOKUP                                       │
│  Summary + source-path pointers to durable knowledge        │
│  → Loaded on reference, ~500 tokens each                    │
├─────────────────────────────────────────────────────────────┤
│  LEVEL 3: ON-DEMAND READ                                    │
│  Full source content retrieved only when explicitly needed  │
│  → Lazy, precise, unbounded depth                           │
└─────────────────────────────────────────────────────────────┘
```

**The key insight:** Most systems preload Level 3. Tokenminning makes Level 1 the default, Level 2 the bridge, Level 3 the exception.

![Before vs After Architecture](resources/BeforevsAfterArchitecture.png)
![Retrieval Escalation Pyramid](resources/RetrievalEscalationPyramid.png)

---

## Related Projects

| Project | Description | Relation |
|:---|:---|:---|
| **[RTK](https://github.com/rtk-ai/rtk)** | Rust CLI proxy for tool-output compression (60-90% savings) | Complementary — handles command output; tokenminning handles context architecture |
| **[Caveman](https://github.com/JuliusBrussee/caveman)** | Terse communication mode (65% fewer output tokens) | Sibling — reduces prompt verbosity; tokenminning reduces context surface |
| **[Ponytail](https://github.com/DietrichGebert/ponytail)** | YAGNI code generation philosophy (~54% less code) | Sibling — reduces implementation bloat; tokenminning reduces context bloat |
| **[GPTCache](https://github.com/zilliztech/GPTCache)** | Semantic caching for LLM APIs | Different layer — caches model responses; tokenminning optimizes what reaches the model |
| **[Firecrawl](https://github.com/mendableai/firecrawl)** | Web search/scrape API — search, scrape, crawl, monitor, interact | **Levels 1–3** of the escalation ladder (credits, cache, scheduled monitors) |
| **[Scrapling](https://github.com/Scrapling/Scrapling)** | Free local HTTP + stealth browser (Cloudflare bypass) | **Levels 4–5** of the ladder (credits exhausted, anti-bot pages) |
| **[markitdown](https://github.com/microsoft/markitdown)** | Universal document converter (PDF, DOCX, XLSX, PPTX, HTML, images) | `doc-convert` **fallback engine** for scanned/image-heavy formats |
| **[Headroom](https://github.com/headroomlabs-ai/headroom)** | Open-source context compression layer for AI agents (60-95% fewer tokens for JSON, 15-20% coding agents) | Complementary — compresses context that reaches the model; tokenminning selects/retrieves better context |

---

## Contributing

We welcome real-world examples, counterexamples, benchmarks, and tool-specific patterns.

1. **Case studies** — Add to `examples/` in `case-study-XX-name.md` format
2. **Techniques** — Document patterns in `techniques/`
3. **Counterexamples** — Where tokenminning *doesn't* apply (valuable!)
4. **Tool patterns** — Claude Code, Cursor, Codex, Continue, etc.

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## Star History

<a href="https://www.star-history.com/?repos=zwolf25%2Ftokenminning&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=zwolf25/tokenminning&type=date&theme=dark&legend=top-left&sealed_token=BBCppQ67mTa4wI5rBMGBoHAaX4Fxr2SsMs40OSQKRCC_ID7tfQjRuh7312IPHSbhT2E9RkqzBv3LszM73nygwCxRC44cn0MLz3av3yVGGNj84-7zQAi-Kw" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=zwolf25/tokenminning&type=date&legend=top-left&sealed_token=BBCppQ67mTa4wI5rBMGBoHAaX4Fxr2SsMs40OSQKRCC_ID7tfQjRuh7312IPHSbhT2E9RkqzBv3LszM73nygwCxRC44cn0MLz3av3yVGGNj84-7zQAi-Kw" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=zwolf25/tokenminning&type=date&legend=top-left&sealed_token=BBCppQ67mTa4wI5rBMGBoHAaX4Fxr2SsMs40OSQKRCC_ID7tfQjRuh7312IPHSbhT2E9RkqzBv3LszM73nygwCxRC44cn0MLz3av3yVGGNj84-7zQAi-Kw" />
 </picture>
</a>

---

## Visual Reference

<details>
<summary><strong>Architecture diagrams & decision flows</strong></summary>

| Diagram | Description |
|---------|-------------|
| ![Tokenmaxxing vs Tokenminning](resources/TokenmaxxingVsTokenminning) | Core contrast visualization |
| ![Before vs After Architecture](resources/BeforevsAfterArchitecture.png) | System architecture comparison |
| ![Tokenminning Decision Tree](resources/TokenminningDecisionTree.png) | Decision flow for technique selection |
| ![Context Surface](resources/ContextSurface.png) | Context surface vs. underlying system |
| ![Retrieval Escalation Pyramid](resources/RetrievalEscalationPyramid.png) | Escalation ladder visual |

</details>

---

## License

MIT — see [LICENSE](LICENSE.md) for details.

---

## Origin

The term "tokenminning" was introduced in July 2026 as a way to describe an emerging optimization philosophy centered on maximizing intelligence per token.

Inspired by the emerging concept of **tokenmaxxing**: intentionally using larger context windows and more tokens to improve AI performance. Tokenminning asks the opposite question: *what's the minimum context that still produces maximum reasoning?*
