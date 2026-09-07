---
name: auth-migration-2026-q3
description: "Auth middleware rewrite driven by compliance, not tech debt"
metadata:
  node_type: memory
  type: project
---

The legacy session-token middleware is being replaced because legal flagged its token-storage approach as non-compliant with a new data-retention policy — not because of code quality concerns.

**Why:** scope decisions on this migration should favor closing the compliance gap over unrelated cleanup. See [[feedback-no-mock-db-in-integration-tests]] for the testing standard this migration's persistence-layer changes must also meet.

**How to apply:** when reviewing PRs against this migration, deprioritize refactors that don't touch the flagged storage mechanism, even if they're adjacent and tempting. This is ephemeral project status — once the migration ships, promote the durable parts of "why" into permanent docs and remove this entry.
