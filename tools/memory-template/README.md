# memory-template

A copy-pasteable structure for an AI agent's persistent memory: a short index file plus typed, frontmatter-tagged memory files. For the philosophy behind this pattern, see [examples/memory.md](../../examples/memory.md) — this directory is the runnable shape.

## Structure

```
memory/
├── MEMORY.md              # short index, one line per file
└── feedback-example.md    # individual memory files
└── project-example.md
└── reference-example.md
```

(This repo nests the examples under `examples/` to keep them separate from the empty template `MEMORY.md` — in your own agent's memory store, files typically live flat alongside the index.)

## Frontmatter schema

```yaml
---
name: kebab-case-slug          # mirrors the filename
description: "One-line summary — used to judge relevance without opening the file"
metadata:
  node_type: memory            # constant
  type: feedback | project | reference | user
---
```

- **`feedback`** — a correction or confirmed preference about how to approach work. Durable — stays indefinitely.
- **`project`** — status/context about in-flight work. Ephemeral — once the work ships or the fact becomes durable knowledge, promote it to your permanent docs/wiki and delete or shrink the entry.
- **`reference`** — a pointer to where something lives in an external system (a tracker, a dashboard, a doc). Durable — stays.
- **`user`** — facts about who you're working with (role, preferences, expertise). Durable — stays. (No example shipped here; shape is identical to the others.)

Body convention: bold labels **Why:** (the reasoning/incident behind the entry) and **How to apply:** (when it should change behavior), plus `[[wikilink]]`-style cross-references between memory files where one entry's context depends on another.

## The promotion policy

The index (`MEMORY.md`) should get *shorter* after a cleanup pass, not longer:

- `feedback` and `user` files are durable behavioral rules — they stay.
- `project` files are ephemeral status — promote anything worth keeping to your durable knowledge store, then trim or delete the entry.

A memory system that only ever accumulates becomes exactly the context debt this repo argues against — the whole point of typing entries is knowing which ones are supposed to leave.

## Runtime note

If you're implementing this inside Claude Code specifically: its built-in memory feature already auto-injects a staleness warning when a memory file is read (flagging its age so the agent verifies stale facts before treating them as current) — a free behavior worth knowing about if you're building on that feature rather than a from-scratch memory store.
