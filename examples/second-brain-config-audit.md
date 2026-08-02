# Case Study: Second Brain Config & Memory Audit

**Before:** ~48.6 KB combined CLAUDE.md, MEMORY.md growing unbounded, no automated bloat prevention  
**After:** 34.4 KB combined CLAUDE.md (~29% ↓), MEMORY.md at 0 bytes, monthly auto-enforcement active  
**Recurring savings:** ~3,500 tokens/session (always-loaded content)

---

## Context

A review of `alexgreensh/token-optimizer` (Claude Code plugin, PolyForm Noncommercial license — not adoptable) surfaced a key insight: **command-output compression (what RTK does) is only ~15-25% of real token waste**. The bigger opportunity is structural bloat — configs, stale memory, unused skills, duplicated instructions.

This session applied that lens to Zac's own Second Brain setup (personal + shared team vault, 17 collaborators).

---

## Root Causes

| ID | Problem | Why It Persisted |
|----|---------|------------------|
| **A** | CLAUDE.md files never audited for staleness/dead refs/contradictions | `wiki-cleanup` only migrated memory→wikis; never looked at CLAUDE.md itself |
| **B** | 4-layer CLAUDE.md hierarchy mislabeled (3 layers instead of 4) | Home-workspace layer (`~/CLAUDE.md`) was undocumented |
| **C** | Cross-file pointer drift (ZacAI CLAUDE.md pointed to wrong file for hierarchy rules) | Skill migration (2026-07-15) updated skills but not routing docs |
| **D** | Memory classification incomplete — `feedback`/`user`/`reference` types had no destination | Only `project` type migrated to wikis; other 3 types accumulated forever |
| **E** | CLAUDE.md sections duplicated skill auto-injected descriptions | Plugin migration (2026-07-15) gave skills rich descriptions; CLAUDE.md wasn't trimmed |
| **F** | Web/Browser tool priority section (6.1 KB) duplicated in `ai-tools-and-workflows.md` wiki | Never consolidated after wiki created |
| **G** | Monthly scheduled task ran stale fallback logic; docs claimed "no automation" | Drift between code and documentation |
| **H** | No ongoing bloat enforcement — one-time trims regressed | No audit check for "CLAUDE.md section duplicates wiki/skill description" |

---

## Fixes Applied

### 1. CLAUDE.md consistency audit (new `wiki-cleanup` phase)
Added 4 checks to full-audit mode (shared skill → all 17 collaborators):
1. Referenced files exist
2. Self-reference accuracy ("this file" claims)
3. Dead skill/agent references
4. Cross-file contradiction

**Immediate catches:** 4 real bugs (hierarchy table, 3 dead skill refs, 2 empty wiki files deleted).

### 2. Memory architecture redesign — "near-blank MEMORY.md" policy
| Memory Type | Old Destination | New Destination |
|-------------|-----------------|-----------------|
| `project` | Wiki (as page) | Wiki (as page) |
| `feedback` | Memory (permanent) | Wiki section → `Rule:`/`Preference:` inline |
| `user` | Memory (permanent) | Persona doc (`shared/persona.md`) |
| `reference` | Memory (permanent) | CLAUDE.md pointer table |

**Live test:** 3 `feedback` memories migrated → MEMORY.md **0 bytes**.

**Duplicate elimination:** One memory had 90% overlap with existing wiki bullet → merged, avoided ~1.4 KB redundant content.

### 3. CLAUDE.md size minimization (category-C cuts only — confirmed homes)

| File | Cut | Verified Home |
|------|-----|---------------|
| ZacAI CLAUDE.md | Inline RTK block (~1 KB) | Global CLAUDE.md `@RTK.md` import |
| ZacAI CLAUDE.md | Model routing section | `shared/opus-routing.md` (verbatim match) |
| ZacAI CLAUDE.md | Working-folder hygiene | `working-folder-cleanup` skill description |
| ZacAI CLAUDE.md | Reference materials listing | Subfolder routing table only |
| ZacAI CLAUDE.md | SC Second Brain stub detail | `sc-second-brain-system.md` wiki |
| ZacAI CLAUDE.md | 8 PM skill routing rows | Skills' auto-injected descriptions |
| `~/CLAUDE.md` | Web/Browser priority (6.1 KB) | `ai-tools-and-workflows.md` wiki |
| `~/CLAUDE.md` | PM routing table (1.8 KB) | Skills' auto-injected descriptions |
| `~/CLAUDE.md` | LLM Council section | Skill's 962-char description |

**Measured:**
| File | Before | After | Reduction |
|------|--------|-------|-----------|
| ZacAI CLAUDE.md | ~26.5 KB | 19,923 B | ~25% |
| `~/CLAUDE.md` | ~22.1 KB | 14,482 B | ~35% |
| **Combined** | **~48.6 KB** | **34,405 B** | **~29%** |

### 4. Ongoing enforcement (mechanism, not one-time)
- **9th audit check** added to `wiki-cleanup`: flags CLAUDE.md sections duplicating wiki/skill descriptions → auto-compresses to pointer
- Runs monthly via existing scheduled task
- CLAUDE-template.md corrected so new collaborators start clean
- 16 collaborators notified via `inbox-share` with exact replacement text

---

## Token Savings

| Category | Amount | Confidence | Notes |
|----------|--------|------------|-------|
| **Always-loaded CLAUDE.md reduction** | **~3,500 tokens/session** | Measured (byte counts) | Recurs every session, all tasks |
| **MEMORY.md index eliminated** | ~225 tokens/session | Measured | Was permanently growing |
| **Duplicate content avoided** | ~1.4 KB (one instance) | Measured | 90% overlap merged |
| **Future feedback/user/reference memories** | Unbounded growth stopped | Structural | No fixed number — prevents accumulation |

**Not counted as token savings:**
- CLAUDE.md correctness bugs (dead refs, self-reference errors) → reliability
- Monthly cron, new audit check → mechanisms that preserve the above

---

## Mapping to Tokenminning Principles

| Principle | Applied Here |
|-----------|--------------|
| **Retrieve, don't preload** | CLAUDE.md now points to wikis/skills instead of inlining detail |
| **Compress, don't repeat** | 8 PM skill rows, Web/Browser section, LLM Council — all duplicated skill descriptions removed |
| **Structure, don't narrate** | Reference materials: file list → routing table by use case |
| **Eliminate context debt continuously** | 9th audit check + monthly cron = ongoing, not one-time |
| **Design systems, not prompts** | Memory classification system routes 4 types to 4 homes; not "clean up memory" prompt |
| **Optimize context, not complexity** | System is more complex (more routing), but context surface is smaller |
| **Spend tokens where reasoning matters** | Tokens now spent on *active* task context, not stale config |

---

## The Pattern: Config as Code, Audited Like Code

```
BEFORE:
  CLAUDE.md = documentation written once, rots forever
  Memory = append-only log, never expires
  Skills = rich descriptions, but CLAUDE.md duplicates them anyway

AFTER:
  CLAUDE.md = thin router, audited monthly for bloat/contradictions
  Memory = 4-type classification, every type has a real home (or is ephemeral)
  Skills = single source of truth for their own triggers; CLAUDE.md only points
```

**Key insight:** The largest token savings came not from compressing prompts, but from **removing information that never needed to be loaded in the first place** — duplicated skill descriptions, a 6 KB decision tree already in a wiki, an entire memory index that grew unbounded.

---

## Files Changed

**Personal:**
- `~/CLAUDE.md` — hierarchy corrected, trimmed
- `~/ZacAI/CLAUDE.md` — trimmed, memory policy added
- `~/Second Brain Obsidian/wikis/ai-tools-and-workflows.md` — 4 new subsections
- `~/Second Brain Obsidian/wikis/ai-empowerment-initiative.md` — 1 bullet enriched
- `~/Second Brain Obsidian/wikis/sc-second-brain-system.md` — stub mechanism detail moved here
- `~/.claude/projects/.../memory/MEMORY.md` — 0 bytes
- `~/.claude/scheduled-tasks/monthly-wiki-cleanup/SKILL.md` — stale reference fixed

**Shared (all 17 collaborators):**
- `wiki-cleanup/SKILL.md` — memory classification, 4 CLAUDE.md checks, bloat check, version 1.0.40→1.0.47
- `sc-wiki-cleanup/SKILL.md` — owner-tier config consistency phase
- `CLAUDE-template.md` — memory policy corrected, lean checklist
- 16 collaborator inbox notes — exact replacement text
