# Case Study: Incremental Wiki Refresh — Hash Gate and Diff-First Folding

## The Problem
A scheduled export mirrors a documentation site (Confluence) into markdown, and an agent folds changed pages into a shared knowledge base of roughly 200 wikis. The expensive part is not the export (a script, zero tokens) but the fold: every page the export flags gets read in full, matched to a wiki by searching the wiki folder, and merged.

One measured run: **27 queued pages plus 6 raw notes cost about 565K tokens** (main context ~85K, four subagents ~479K). 13 of the 27 pages were "no material change" and still cost ~190K, because the queue was keyed on the page *version number*, and a version bumps on any save.

## The Approach
Move every decision that does not need a model into the export script:

1. **Content-hash gate.** Store a hash of each page body at the moment it was last folded (`state.json`, plus a copy of that body as a snapshot). Queue a page only when the new hash differs. A version bump with identical content never reaches the agent.
2. **Diff-first reading.** The script writes a unified diff against the snapshot and puts its path in the queue entry. The agent reads the diff, not the page, unless the diff is more than about half the page size.
3. **Pre-computed target.** The state file remembers which wiki each page was folded into, so the agent opens one wiki instead of listing the folder and searching.
4. **Explicit bookkeeping.** A `--mark-folded` command records the fold and removes the entry from the queue, so the agent never edits queue state by hand.

## Results
| | Before | After |
|---|---|---|
| Queue key | version number | content hash of normalized body |
| Agent input per page | full page | unified diff (full page only for new or large changes) |
| Subagents | 4 | 0 (all folded in the main context) |
| Tokens for the fold | ~565K (27 pages + 6 raw notes) | see below |

The first run on the new pipeline queued 21 pages and folded them inline. Measured from the session transcript, the **entire session** (queue inspection, the export run, the fold, and a code fix described next) used about **121K fresh tokens** (output + cache creation + uncached input), against 565K for the earlier fold alone. The fold itself was well under that figure. About 3.3M further tokens were cache reads of the same context, which are not comparable to the baseline.

Treat this as a single run, not a benchmark: the queues held different pages, and the baseline figure counted context sizes across agents without splitting fresh from cached tokens.

## What the Hash Gate Missed
Reading the diffs showed that **14 of the 21 queued pages were rendering noise**, not content: panel markers (`panel_c1`), links flattened from markdown link syntax to plain text, attachment filenames, and macro identifiers. A whitespace-only normalization cannot see these, because the markdown really does differ.

Fix: normalize before hashing and before diffing (strip panel and note markers, collapse links to their text, drop macro ids), then recompute the stored hashes from the snapshots so nothing re-queues. A full re-export afterwards updated 0 of ~1,800 pages, and a self-test asserts that a link-only change hashes the same while a real edit does not.

## Lessons
- The same hash-sidecar idea guards derived documents in [Derived-Doc Staleness](derived-doc-staleness.md); here it gates the queue instead.
- Key the queue on content, not on a version counter the source system bumps freely.
- A script-computed diff is a better agent input than the page: the agent only has to judge whether the change matters.
- Read the first batch of diffs by hand. The noise only showed up as a pattern once someone looked, and it was the largest remaining saving.
- After changing the normalization function, rehash the stored state from the snapshots, or every page queues once.
- Compare cheap numbers honestly: separate fresh tokens from cache reads, and say when the two runs are not the same workload.
