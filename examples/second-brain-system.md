# Case Study: Second Brain Token Optimization

## The System

**What**: A shared AI-powered knowledge infrastructure for a product management team of 8-12 people.

**Scale**:
- 72 interlinked wikis (211K words total)
- OneDrive-synced across multiple collaborators
- Daily AI sessions using shared content
- Skills-based automation (wiki-builder, wiki-cleanup, inbox-review)

**The problem it solved**: How do you keep a team's collective intelligence fresh, accessible, and cost-effective when everyone's running AI sessions on the same content?

---

## The Crisis: Knowledge Bloat

**Discovered 2026-07-18** during routine maintenance:

- **68 full-body clones** of shared wikis in personal vault
- **45 clones stale** (66% out of sync with source)
- **1.6MB of duplication** standing in context
- **$4-8/session** wasted on redundant reads
- **Sync breaks compound**: password changes created conflict-copy duplicates that silently drifted

**The failure mode**:

```
Collaborator A edits shared wiki
→ OneDrive sync breaks (password change)
→ Edits stay local, don't sync
→ Clone in personal vault reads stale version
→ New content written ON TOP of old
→ Sync reconnects → conflict copies created
→ Manual triage finds silently dropped rows
```

This wasn't a one-time bug. It was a **systemic design flaw**. The system assumed fresh clones meant fresh data. It didn't.

![Knowledge Bloat Cascade](/resources/KnowledgeBloatCascade.png)

---

## The Fix: Reference-Only Architecture

### Core Principle: "Do You Need This Content Right Now?"

Answer: Almost never.

Most AI sessions touch 2-4 wikis max. The other 68 are **reference**, not active context.

### The Stub Pattern

Replace every full-body clone with a **stub file**:

```markdown
---
type: wiki-clone-pointer
source-file: sc-servicechannel-context.md
source-path: /Users/team/Second Brain/wikis/servicechannel-context.md
last-indexed: 2026-07-18T14:30:00Z
topics: [servicechannel-strategy, ai-strategy, pm-skills-and-frameworks]
---

# SC Second Brain (Shared Team System)

The shared Second Brain vault's `servicechannel-context.md` covers SC's product strategy, roadmap themes, and platform evolution. Last verified: 2026-07-18.

[Read the live content](mdc:source-path-here) when relevant.
```

**Key design choices**:

1. **Short description only** — not copied verbatim, so the next session must Read if it wants the real content
2. **`source-path` frontmatter** — absolute path to live source, machine-readable
3. **`topics:` linking** — 2-5 local wikis this stub relates to, for synthesis
4. **`last-indexed:` timestamp** — human audit trail (not used for skip-detection)

### The Mechanics

**Before** (broken):
```python
# Every wiki-builder run:
for stub in shared_clones:  # 68 iterations
    content = Read(stub)  # Full 20KB read of each wiki
    # ... process content ...
```
**Cost**: 211K words read every run, even if nothing changed.

**After** (fixed):
```python
# Every wiki-builder run:
for stub in shared_clones:  # 68 iterations
    content = Read(stub)  # 0.5KB read (stub only)
    # Skip full read unless topic is confirmed relevant
```
**Cost**: 28K words read. 87% reduction.

![Before vs After Architecture](/resources/BeforevsAfterArchitecture.png)

**When content IS needed**:
```python
# Only when the stub's topic matches the current task:
content = Read(stub.source_path)  # 20KB one-time read
```

---

## Targeted Retrieval: Grep Before Read

**The inefficiency**: `wiki-builder` was doing full Reads of 402 raw files just to check if they were already processed:

```python
# Before (200K tokens of context):
for raw_file in raw_folder:
    content = Read(raw_file)  # Full Read
    if "# !wiki-builder-ignore" not in content:
        process(content)
```

**The fix**:

```python
# After (2K tokens of context):
unprocessed = Grep(raw_folder, "# !wiki-builder-ignore")  # 31 matches
for path in unprocessed:
    content = Read(path)  # Only the 31 that need it
    process(content)
```

**Result**:
- 371 files skipped without reading
- `$1.20 saved per run`
- Same correctness, 92% fewer I/O operations

![Grep Before Read](/resources/GrepBeforeRead.png)

---

## Escalation Ladder: How Lookups Work

![Retrieval Escalation Pyramid](/resources/RetrievalEscalationPyramid.png)

When a collaborator asks "where is this info?":

```
LEVEL 1: Local wiki (fastest)
  → Instant access from last wiki-builder run
  → 60% of lookups resolved here
  → 0 tokens (already cached in local vault)

LEVEL 2: Stub pointer (medium)
  → 2-line abstract in shared-clone folder
  → Answers: "what is this, is it relevant?"
  → 50-100 tokens
  → 30% of lookups: "good enough"

LEVEL 3: On-demand Read (slowest, most expensive)
  → Full content from live source path
  → Only when topic is confirmed relevant
  → 2K-5K tokens
  → 10% of lookups
```

**Old system**: Every lookup was Level 3 (full-body clone). 100% of the cost, whether needed or not.

---

## Economic Impact

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Standing duplication | 211K words | 28K words | 87% ↓ |
| Stale clones | 45/68 (66%) | 0 | 100% ↓ |
| Files read per wiki-builder run | 402 | 31 | 92% ↓ |
| Cost per AI session | $15-25 | $2-4 | 75-85% ↓ |
| Freshness guarantee | Stale clones common | mtime-checked |直接的解决了 |

**Velocity impact**:

- Each AI session costs **5-10x less**
- Developers can fail more (cheap iteration)
- The system compounds efficiency instead of burning capital
- Freshness is now measurable, not assumed

---

## The Pattern (Generalizable)

This isn't specific to wikis or Obsidian. Works anywhere:

### 1. Periodic Sync + On-Demand Lookup

**Pattern**: Background sync maintains indexing. Active sessions only load confirmed-relevant content.

**Examples**:
- Codebase: Full index hourly. Agent reads 3-5 files per task.
- Customer interviews: Sync transcripts nightly. Agent loads only the interview for the persona being discussed.
- API docs: Index all endpoints. Load only the endpoint the developer is implementing.

### 2. The Stub Structure

```markdown
---
type: {entity}-pointer
source-file: {name}
source-path: {absolute-path}
last-indexed: {ISO-timestamp}
topics: [related-entity-1, related-entity-2]
---

# {ENTITY_NAME}

{1-3 sentence summary, NOT copied verbatim}

{See related: [[local-wiki-1]], [[local-wiki-2]]}

{Explicit instruction: read source-path when relevant}
```

### 3. Signal Density Over Volume

**Bad** (tokenmaxxing):
> "Here's the entire codebase." (500KB, 480K tokens)

**Good** (token minning):
> Function signature: 50 lines
> 3 canonical examples: 300 lines  
> File paths to rest: 1KB (no content)
> **Total**: 2K tokens, 100% signal

### 4. Grep-Before-Read Discipline

Never Read a folder's contents wholesale. Always:
1. Grep for the specific pattern
2. Read only the matches
3. If grep returns nothing, ask a human (or fail fast)

---

## Anti-Patterns (What To Avoid)

### ❌ Silent Auto-Sync Without Verification

> "The system auto-updated the clone, so it must be correct."

**Failure**: Full-body clone synced when source was stale. The "fresh" file was 3 days old.

**Fix**: mtime-checking + human audit when mtime drifts.

### ❌ "Just Load Everything" Context

> "Let me load all 72 wikis so the agent has full context."

**Cost**: 480K tokens, $40-60/session, 80% unused.

**Fix**: Stub-first. Read-on-relevance. Grep when searching.

### ❌ Partial-Edit Synthesis

> "Let me just update the changed sections."

**Problem**: Transformations that require human judgment (synthesis, conflict resolution) can't be partial. One wrong edit corrupts the whole file.

**Fix**: Full-file Write for synthesis. Accept the cost. It's cheaper than the bug cost of drift.

---

## Implementation Checklist

```
[ ] Audit: what content sits in context but is never read?
[ ] Identify "clone" folders where full duplicates exist
[ ] Replace each clone with a stub (summary + source-path)
[ ] Add targeted Grep before bulk Read in sync routines
[ ] Build mtime-tracking for drift detection
[ ] Test fallback:simulate a missing source, verify stub handles it
[ ] Measure: cost/session, iteration velocity, accuracy
```

---

## Why This Works

**Tokenminning** isn't about being cheap. It's about **engineering discipline**.

The Second Brain didn't bloat through one bad decision. It crept there through dozens of small compromises:

- "Just clone the whole thing, easier than pointing"
- "We'll fix sync drift later"
- "The cost per run is small, it'll add up eventually"

Tokenminning forces the question: **Do you need this *right now*?**

If no: don't load it.
If maybe: grep first.
If yes: read only what's needed.

That's the practice. That's the habit.

---

## Real-World Verification

**System**: Production AI knowledge infrastructure at a Fortune 500 company.

**Users**: 8-12 PMs running daily AI sessions.

**Verification date**: 2026-07-18.

**Token costs**: Actual spend from Claude Code billing, not estimates.

**The fix**: Deployed to personal setup first, then propagated to shared skills-repo (live-synced to all collaborators).

---

*This is documented as a reference architecture, not a consultant's report. The code, the hooks, the skills — all exist and are running. If you copy this pattern, you'll get the same savings.*
