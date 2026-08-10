# Tokenminning Examples — Tooling Implementations

> **These three examples are new additions** showcasing the tooling stack that *achieves* the tokenminning principles documented in the original 7 philosophy examples. They demonstrate **production-hardened implementations** of "Design systems not prompts," "Compress don't repeat," "Retrieve don't preload," and "Eliminate context debt continuously."

---

## New Tooling Case Studies

| Example | Core Principle | Token Savings | Key Tools |
|---------|----------------|---------------|-----------|
| **[Document Processing Pipeline](document-processing.md)** | Compress don't repeat, Retrieve don't preload, Structure don't narrate, Design systems not prompts, Eliminate context debt | **99.3–99.6%** vs LLM-based extraction | `doc-convert`, `vtt-normalizer`, `doc-ingest` (local subprocesses + Haiku extraction) |
| **[Web Scraping Escalation Ladder](web-scraping-escalation.md)** | Retrieve don't preload, Optimize context not complexity, Escalation ladder, Stub Pattern, Eliminate context debt | **90–100%** credit savings via cache + free local fallbacks | `firecrawl` (40+ sub-skills), `scrapling` (fast + stealth), `webclaw`, `playwright` |
| **[Skill Tooling Pattern](skill-tooling-pattern.md)** | Design systems not prompts, Structure don't narrate, Thin Routers, Stub Pattern, Compress don't repeat | **Systematic** — eliminates prompt drift, enforces token discipline by contract | 100+ versioned skills across 14 categories, plugin-managed |

---

## How These Connect to Original Philosophy Examples

| Original Example | Philosophy | Tooling Implementation (New) |
|------------------|------------|------------------------------|
| **1. Coding** | Retrieve relevant files, not entire repo | `wiki-builder` fingerprint-dedup, `doc-ingest` batch extraction |
| **2. Knowledge** | Preserve decisions/constraints, not noise | `doc-ingest` 7-category schema, `wiki-builder` incremental merge |
| **3. RAG** | Better retrieval beats larger retrieval | `firecrawl` search→scrape→map→crawl ladder, `firecrawl-cached` |
| **4. Agents** | Context matches task | Each skill = one capability, loads on demand via thin router |
| **5. Memory** | Remember decisions, discard temporary work | `log-it`/`sc-log-it` structured notes, `wiki-cleanup` audit |
| **6. MCP/Tools** | Enable tools intentionally | 100+ skills, each with `allowed-tools` frontmatter gate |
| **7. System vs Context** | Optimize surface, not size | Every skill returns stub (file path), never raw content |

---

## Quick Reference: The Complete Tokenminning Stack

```
┌─────────────────────────────────────────────────────────────────────┐
│                        TOKENMINNING ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐  │
│  │   INPUTS     │───▶│   SKILLS     │───▶│      OUTPUTS         │  │
│  │              │    │              │    │                      │  │
│  │ • Documents  │    │ doc-convert  │    │ • .md files (stubs)  │  │
│  │ • VTT files  │    │ vtt-normalizer    │ • Structured notes   │  │
│  │ • URLs       │    │ doc-ingest   │    │ • Wiki updates       │  │
│  │ • Topics     │    │ firecrawl*   │    │ • Charts/Diagrams    │  │
│  │ • Questions  │    │ scrapling    │    │ • Battlecards        │  │
│  │              │    │ playwright   │    │ • Reports (MR)       │  │
│  │              │    │ gsd:*        │    │ • PRDs/Roadmaps      │  │
│  │              │    │ 100+ skills  │    │ • Comms (LI/Med/Slack)│ │
│  └──────────────┘    └──────────────┘    └──────────────────────┘  │
│         │                   │                      │                │
│         ▼                   ▼                      ▼                │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    ENFORCED DISCIPLINE                        │  │
│  │  • Token rules in every SKILL.md ("do not break")            │  │
│  │  • Stub Pattern: output = file path, never content           │  │
│  │  • Thin Router: trigger phrase → skill (no prompt eng)       │  │
│  │  • Composability: skills call skills explicitly              │  │
│  │  • Versioning: plugin semver + git                           │  │
│  │  • Fallback ladders: encoded in skills, not memory           │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Measured Aggregate Impact

| Workflow | Before (Prompt-Based) | After (Skill System) | Improvement |
|----------|----------------------|---------------------|-------------|
| **50-page PDF → Wiki** | ~80K tokens, manual | ~500 tokens, automated | **99.4% ↓** |
| **2-hr VTT → Decisions** | ~45K tokens, error-prone | ~300 tokens, schema-enforced | **99.3% ↓** |
| **Competitor research (10 sites)** | ~500K tokens, ad-hoc | ~5K tokens, ladder + cache | **99% ↓** |
| **Market research report** | $50+, 11 agents, manual | $15-25, 2-3 agents, pipeline | **~70% cost ↓** |
| **Context debt (stale clones)** | 66% of files | 0% (fingerprint dedup) | **Eliminated** |

---

## Getting Started

```bash
# View all installed skills
ls ~/.claude/skills/

# See skill descriptions (routing triggers)
cat ~/.claude/skills/doc-convert/SKILL.md | head -20

# Run a skill directly
doc-convert "convert this.pdf to markdown"

# The system auto-routes: "convert this vtt" → vtt-normalizer
#                         "ingest these documents" → doc-ingest
#                         "search for X" → firecrawl-search
```

---

## Repository Structure

```
tokenminning/
├── examples/
│   ├── index.md                           ← This file
│   ├── claude-code.md                     ← Original: context management
│   ├── context-debt.md                    ← Original: context debt reduction
│   ├── mcp.md                             ← Original: MCP tool discipline
│   ├── memory.md                          ← Original: memory as signal
│   ├── rag.md                             ← Original: better retrieval
│   ├── rtk-llmlingua-evaluation.md        ← Original: compression eval
│   ├── second-brain-config-audit.md       ← Original: config audit
│   ├── second-brain-system.md             ← Original: second brain optimization
│   ├── vault-lint-case-study.md           ← Original: vault linting
│   ├── wiki-pipeline.md                   ← Original: wiki pipeline optimization
│   ├── document-processing.md             ← NEW: Local document pipeline
│   ├── web-scraping-escalation.md         ← NEW: 7-level web ladder
│   └── skill-tooling-pattern.md           ← NEW: Skill system as DSNP
└── ...
```

---

## Contributing

These tooling examples are **living documentation** — they describe the actual production stack. When the stack evolves:

1. Update the relevant example file
2. Keep measured impact numbers current
3. Add new anti-patterns replaced
4. Cross-link to related examples

The goal: every tokenminning principle has a **working, measured implementation** in this repo.
