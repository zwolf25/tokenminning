# Case Study: Count the Problem Before Installing the Fix

## The Problem
A new open-source local search tool (hybrid ripgrep, BM25 and vector search, published benchmarks of about 38% fewer input tokens and 44% fewer tool calls) looked like it could improve retrieval over a markdown knowledge base of about 1,200 personal notes and 11,600 shared ones. The first plan was to install it, run a 40-query A/B (360 runs), dogfood it for two weeks, then pilot it with collaborators.

## What Stopped It
The setup already named its own trigger for adding vector search: a retrieval-gaps log, to be appended whenever Claude failed to surface something that existed. Checking it showed "(none yet)" 76 days after it was created. Two things followed:

1. **An empty log is not evidence.** Nothing wrote to it. Only a person remembering to append could fill it, so zero entries could mean zero gaps or zero logging.
2. **The benchmark did not transfer.** The published numbers came from public code and web corpora, self-reported. The knowledge base here is mostly markdown with exact-lookup work (ticket keys, customer IDs, churn figures), which is where hybrid search is weakest and plain grep is right.

## The Cheap Measurement
Instead of the 360-run plan, a short stdlib script ([`tools/retrieval-gaps`](../tools/retrieval-gaps)) scanned every Claude Code transcript for user messages that sound like a retrieval correction ("check the X wiki", "it's in...", "you missed", "didn't you see").

| Measure | Result |
|---------|--------|
| Transcripts scanned | all projects, 2026-07-14 to 2026-10-25 |
| User messages | 3,306 over 55 active days |
| Candidate hits, strict phrases | 4 |
| Candidate hits, broader pass (wiki/vault/manifest words + correction words) | 11 |
| Verified retrieval misses after hand review | **0** |

The plan's own rule decided the outcome: fewer than 5 verified misses in 90 days meant no ranked-search build, no collaborator rollout, no install. The earlier shape of the answer was the same in July, when an embedding-search script was scoped and rejected on measured file sizes.

## What Was Still Worth Borrowing
- **A routing rule** (exact lookups to grep, conceptual questions to description triage, then section gist, then section read). It already existed in the config, so adding it again would have changed nothing.
- **Disposable, local indexes.** Any future index lives outside synced folders and can be rebuilt from scratch.
- **Keep the heavy part off the manifest.** An earlier manifest extension (topics and path columns) was built and reverted: about 4.3K extra tokens per read with no consumers. Section-level detail stays on demand.

## Limits
The script only sees misses that were said out loud. A silent miss, where Claude answered without the right file and nobody noticed, is invisible, so a zero here reads as "no voiced misses". Hand review mattered: every regex hit was a false positive (a routing test, a deck-edit complaint, a question about Jira fields).

## Reusable Pattern
Trigger log, then a cheap measurement of the trigger, then a decision rule written before the data arrives. A tool earns its install only when the count clears the threshold. Record the no-go and the revisit condition so the question does not get re-litigated.

## Related
- [Context Debt](context-debt.md): cost of always-loaded context that does not pay back
- [Wiki Lint](vault-lint-case-study.md): deterministic pre-filter pattern, same shape of answer
