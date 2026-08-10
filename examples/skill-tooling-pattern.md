# Case Study: Skill Tooling Pattern — "Design Systems Not Prompts"

**Problem:** Most AI-assisted workflows rely on *prompt engineering* — crafting the right prompt for each task, hoping the model follows it consistently. This doesn't scale: prompts drift, context rots, expertise lives in heads not systems, and every new task is a blank slate.

**Solution:** A **skill system** where every reusable capability is a versioned, self-documenting tool with a deterministic contract (SKILL.md) — not a prompt. Skills compose, route by intent, emit file paths (stubs), and enforce token discipline *by design*, not by reminder.

---

## What a Skill Is

```
┌─────────────────────────────────────────────────────────────────┐
│                        SKILL STRUCTURE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  skill-name/                                                    │
│  ├── SKILL.md           ← CONTRACT (frontmatter + instructions) │
│  ├── scripts/           ← Local executables (Python, Node, Bash)│
│  └── ...                ← Any supporting files                  │
│                                                                 │
│  SKILL.md frontmatter:                                          │
│  ─────────────────────                                          │
│  name: doc-convert                                              │
│  description: "Convert documents locally, without spending      │
│    tokens — PDF/DOCX → Markdown, Markdown → styled DOCX..."     │
│  allowed-tools:                                                 │
│    - Bash(uv run *)                                             │
│    - Bash(node *)                                               │
│    - Read                                                       │
│    - Write                                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**The contract is executable.** The frontmatter `description` is the *routing trigger* — the system matches "convert this pdf" → `doc-convert` automatically. The body is the *execution spec* — deterministic steps, not suggestions.

---

## Tokenminning Principles Applied

| Principle | How Skills Embody It |
|-----------|---------------------|
| **Design systems not prompts** | Skills are *infrastructure*, not prompts. Versioned in git. Composable (`doc-convert` → `vtt-normalizer` → `doc-ingest` → `wiki-builder`). Testable. Upgradeable. |
| **Structure don't narrate** | SKILL.md = structured contract (frontmatter + numbered steps + code blocks). Not "please do X." The skill *is* the structure. |
| **Stub Pattern** | Every skill returns **file path + one-line status** — never content. `WROTE /path/to/output.md (45K chars)`. Context stays clean. |
| **Thin Routers** | Routing by trigger phrase in `description` frontmatter. "convert this vtt" → `vtt-normalizer`. Intent classification, not prompt engineering. |
| **Compress don't repeat** | Common patterns encoded *once* in the skill: prerequisite gates, fallback ladders, token rules, output conventions. Never re-prompted. |
| **Retrieve don't preload** | Skills load on demand (Skill tool). 40+ firecrawl sub-skills exist but only the one matched by intent loads. |
| **Eliminate context debt continuously** | Hard rules in SKILL.md: "NEVER read raw .vtt", "NEVER echo converted content", "Report output path only." The *contract enforces discipline*. |

---

## The Skill Ecosystem (This Machine)

### Core Categories

| Category | Skills | Purpose |
|----------|--------|---------|
| **Document Processing** | `doc-convert`, `doc-ingest`, `vtt-normalizer`, `markitdown` | Local, token-free binary ↔ markdown ↔ DOCX |
| **Web Research** | `firecrawl*` (40+), `scrapling`, `webclaw`, `playwright-browser`, `playwright-test` | 7-level escalation ladder (see web-scraping-escalation.md) |
| **Second Brain** | `wiki-builder`, `wiki-cleanup`, `log-it`, `sc-log-it`, `inbox-review`, `inbox-share`, `working-folder-cleanup`, `working-style-interview`, `submit-suggestion`, `sc-shared-folder` | Personal + shared knowledge base ops |
| **Visualization** | `mekko-chart`, `pareto-chart`, `dataviz`, `web-artifacts-builder`, `frontend-design`, `ui-ux-pro-max` | Charts, diagrams, HTML artifacts |
| **Product Management** | `write-spec`, `product-brainstorming`, `competitive-brief`, `roadmap-update`, `sprint-planning`, `stakeholder-update`, `synthesize-research`, `metrics-review`, `pm-prioritize`, `guesstimate`, `ost-builder`, `pre-mortem`, `steeple-analysis`, `experiment-design`, `launch-readiness`, `business-case`, `propose-solutions`, `sc-tshirt-size`, `sc-prd-doc`, `sc-roadmap-doc`, `sc-doc-skills:sc-innovation-questions` | PM frameworks, SC-specific docs |
| **Market Research** | `sc-market-research:mr-*` (intake, sizing, fit, competitive, PMF, report, run, transaction, upsell, adjacent) | End-to-end MR pipeline |
| **Competitive Intel** | `sc-competitor-research`, `sc-battlecard`, `sc-partner-profile` | Evidence-tagged research + dual council gate |
| **Writing/Comms** | `linkedin`, `medium`, `leadership-comms`, `slack-celebration`, `weekly-news-roundup`, `the-humanizer` | Audience-facing content (auto-humanized) |
| **Planning/Execution** | `gsd:*` (plan-phase, execute-phase, verify-work, code-review, debug, spec-phase, ui-phase, secure-phase, etc.), `deep-plan`, `ponytail`, `caveman` | Structured delivery, code philosophy |
| **Document Gen** | `document-skills:docx`, `pdf`, `pptx`, `xlsx` | Professional docs (SC style guide) |
| **Infra/Config** | `mcp-builder`, `skill-creator`, `update-config`, `keybindings-help`, `init`, `run`, `verify`, `fewer-permission-prompts`, `loop`, `schedule` | Tooling, automation, env config |
| **Code Quality** | `code-review`, `security-review`, `simplify`, `playwright-test` | Review, test, verify |

**Total: 100+ skills** across 14 categories. Each: versioned, composable, contract-driven.

---

## Routing: Thin Router in Action

The system doesn't "guess" which skill — the skill's **frontmatter `description`** *is* the routing key.

```yaml
# doc-convert SKILL.md frontmatter
description: >
  Convert documents locally, without spending tokens — PDF/DOCX → Markdown,
  and Markdown → styled DOCX (auto-applying the shared Second Brain style
  guide, or a named style preset like market-research). A local CloudConvert-
  style tool. Use when the user says "convert this to markdown", "pdf to md",
  "docx to markdown", "turn this markdown into a Word doc", "convert to docx",
  "md to docx", or gives a source file + wants it in the other format.
```

**User says:** "convert this PDF to markdown"
**System matches:** Trigger phrases in description → `doc-convert` loads
**Skill executes:** Deterministic steps from SKILL.md body

No prompt engineering. No "you are a document converter." The skill *is* the converter.

---

## Composition: Skills Calling Skills

Skills compose explicitly in their SKILL.md bodies — not via prompting.

### Example: `doc-ingest` composes `vtt-normalizer`

```markdown
## Step 1: Pre-process documents

**VTT files:**
Use the `vtt-normalizer` skill (already installed) to clean speaker labels
and timestamps, then save the normalized output as `<filename>.txt` in scratchpad.
```

### Example: `firecrawl` skill encodes the entire fallback ladder

```markdown
## Firecrawl failed? Fall back to Scrapling or webclaw

1. Credits exhausted, single-URL fetch → Scrapling fast path
2. Blocked by page (403, Cloudflare) → Scrapling STEALTH path  
3. Credits exhausted, crawl/map need → webclaw (NOT Scrapling)

Do not stop and do not silently switch to WebFetch.
```

### Example: `sc-market-research:mr-run` orchestrates 5 study types

```markdown
# mr-run orchestrates the correct stage sequence per study type:

geo:      intake → sizing → demand → product-fit → competitive → pmf-gtm → report
vertical: intake → sizing → demand → product-fit → competitive → pmf-gtm → report
upsell:   intake → opportunity → competitive → pmf → report
transaction: intake → economics → competitive → viability → report
adjacent: intake → sizing → demand → adjacent-fit → adjacent-pmf → report
```

**Each stage is a separate skill** (`mr-intake`, `mr-market-sizing`, `mr-product-fit`, etc.) — composable, reusable, independently versioned.

---

## Token Discipline Enforced by Contract

Every skill that touches external content has a **Token Rule** section — non-negotiable.

### `doc-convert`:
> **Token rule (do not break):** the conversion happens in a subprocess. Run it, then report the output path + the one-line status the tool prints. **Never read the converted file back into context** — a large document echoed into the chat is thousands of wasted tokens.

### `vtt-normalizer`:
> **Token rule (do not break):** the conversion runs as a local Python subprocess. Run it, then read/report the `.md` output. **Never `Read` the raw `.vtt`** — cue-arrow syntax and repeated timestamp lines are wasted tokens for zero extra information once the `.md` exists.

### `firecrawl`:
> **Avoid redundant fetches:** `search --scrape` already fetches full page content. Don't re-scrape those URLs. Check `.firecrawl/` for existing data before fetching again.

### `doc-ingest`:
> **Token budget awareness:** for large batches, note the estimated cost before launching extraction agents. The pre-processing and Haiku extraction are cheap; the synthesis and `direct`-mode wiki reads are where cost accumulates.

**These aren't suggestions. They're contract terms.** The skill *cannot* be used correctly without following them.

---

## Versioning & Distribution

Skills live in two repositories:

| Repo | Scope | Update Mechanism |
|------|-------|------------------|
| `skills-repo/second-brain-skills` | Shared (team) | Plugin: `second-brain-skills@sc-pm-skills` — `claude plugin update` |
| `skills-repo/pm-thinking-skills` | Shared (team) | Plugin: `pm-thinking-skills@sc-pm-skills` |
| `skills-repo/sc-market-research` | Shared (team) | Plugin: `sc-pm-skills` (bundled) |
| `skills-repo/sc-competitive-intel` | Shared (team) | Plugin: `sc-pm-skills` |
| `skills-repo/sc-doc-skills` | Shared (team) | Plugin: `sc-pm-skills` |
| `zacai-skills` | Personal (Zac) | Local only — `~/.claude/skills/` symlinks |
| `example-skills` | Experimental | Plugin: `example-skills` — enable to use |

**Plugin versioning:** `second-brain-skills@sc-pm-skills` at `1.0.78` (vault) vs `1.0.76` (installed) → `claude plugin update` syncs.

**No "prompt drift."** Skills are code. They're reviewed, tested, versioned, and deployed like any other dependency.

---

## Anti-Patterns This Replaces

| Anti-Pattern | Problem | Skill System Fix |
|--------------|---------|------------------|
| "Write a prompt to do X" for every task | Inconsistent, unversioned, untestable | Skill = versioned contract, reusable |
| Copy-paste prompt library | Drift, no composition, no routing | Skills compose explicitly; routing by trigger |
| "Remember to never do Y" | Relies on human memory | Contract enforces: "Token rule (do not break)" |
| Ad-hoc tool use (`Read` raw PDF, `WebFetch` everything) | Token waste, inconsistent output | Skills encapsulate correct tool + output pattern |
| One-off scripts in scratchpad | Lost, not reusable, not discoverable | Skills in repo → installed → auto-routes |
| Prompt engineering as "skill" | Not executable, not testable | SKILL.md = executable spec + allowed tools |

---

## Measured Impact

| Metric | Prompt-Based | Skill System | Improvement |
|--------|--------------|--------------|-------------|
| **Token waste on repeated instructions** | High (re-prompt every task) | Zero (contract loaded once) | **Eliminated** |
| **Consistency of tool usage** | Variable (human-dependent) | 100% (enforced by skill) | **Guaranteed** |
| **Onboarding new capability** | Re-teach via prompt | Install plugin → auto-routes | **Minutes vs hours** |
| **Composability** | Manual (copy-paste) | Native (skills call skills) | **Native** |
| **Version control** | None (chat history) | Git + plugin semver | **Full** |
| **Token discipline** | Best effort | Contract-enforced | **Systematic** |

---

## Creating New Skills

The `skill-creator` skill bootstraps new skills:

```bash
# Interactive: asks for name, description, triggers, tools, steps
/skill-creator
```

Generates:
- `SKILL.md` with frontmatter + template steps
- Correct allowed-tools based on declared needs
- Proper trigger phrasing for routing
- Token rule template if content-processing

**No blank slate.** The meta-skill encodes the pattern.

---

## Related Examples

- [`document-processing.md`](document-processing.md) — Pipeline of 3 composed skills (doc-convert → vtt-normalizer → doc-ingest)
- [`web-scraping-escalation.md`](web-scraping-escalation.md) — 7-level ladder encoded in `firecrawl` skill fallback logic

---

## Source Code

- **Shared skills**: `/Users/zackwolf/Library/CloudStorage/OneDrive-Fortive/SVC-Product_Management - Second Brain/skills-repo/`
- **Installed skills**: `~/.claude/skills/` (symlinks to shared + local zacai-skills + plugin skills)
- **Skill metadata**: `~/.claude/plugins/cache/<plugin>/<skill>/SKILL.md` (versioned per plugin)
- **Plugin registry**: `~/.claude/plugins/plugin-registry.json`

Run `ls ~/.claude/skills/` to see all 100+ available skills.
Run `/skills` in Claude Code for interactive list with descriptions.
