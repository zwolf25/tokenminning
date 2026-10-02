# Case Study: Trimming Always-Loaded CLAUDE.md Context by 21%

## The Problem
Every session pays for the same resident context before the first prompt: a home `CLAUDE.md`, a project `CLAUDE.md`, and two tool-instruction imports. In this setup that was **32,157 bytes (~8K tokens)**. Much of it duplicated text the harness already injects: skill trigger descriptions, hook-injected mode rules, and a hierarchy explainer.

## The Approach
Remove text only if it meets one of three tests:
1. **Already injected elsewhere** (skill descriptions, hook-provided rules)
2. **Single-source violation** (the same rule stated in two files)
3. **Rarely needed** (replace with an on-demand pointer to a reference index)

Done in two tiers, with all edits to each file batched into one pass so the prompt cache is invalidated once, not repeatedly.

- **Tier 1:** removed skill-routing rows that duplicated skill descriptions; moved long reference material behind a new `reference/shared/README.md` index.
- **Tier 2:** collapsed the four-layers hierarchy table to prose; condensed the "Reference materials" section.

## Results
| File | Before | After |
|------|--------|-------|
| Home `CLAUDE.md` | 11,596 B | 8,950 B |
| Project `CLAUDE.md` | 17,318 B | 13,045 B |
| Tool imports + memory index | 3,243 B | 3,370 B |
| **Total resident** | **32,157 B** | **25,365 B** |

About -6.8K bytes, roughly **1.7K tokens (-21%)** per session, using a chars/4 estimate rather than billed usage.

## Verification
- Static check: every skill and doc named in the trimmed files resolves. Two "dangling" skills were in fact bundled with the harness and not on disk, so the audit now checks bundled skills before flagging.
- Routing check: 8 representative prompts (PRD, battlecard, market research, diagram, product doc, LinkedIn post, wiki lookup, Jira status) each still map to a route in the trimmed files. A later headless re-run (`claude -p`, routing-only prompts, cold-loaded files, nothing executed) passed 7 of 8; the Jira prompt cited the right rule ("search the local archive first") but named the remote connector call first, so it is the one rule to watch.

## What Broke When the Same Trim Was Applied to a Shared Template
The same tests were then applied to a `CLAUDE.md` template that is copied to a team (21,776 -> 17,544 chars, -19%). A folder list of 21 bullets was the target: 15 occasional-use bullets moved to an on-demand index file, leaving one pointer line.

A control test caught what a read-through did not. Each routing-only prompt was run against the old template and the trimmed one, in a scratch directory holding only that file. Of 6 prompts, **2 regressed**:
- "Drop competitive intel for the team" routed to a generic logging skill instead of the intake skill. That skill was named in exactly one place: the moved folder bullet.
- "Where does a Q1 roadmap get written?" routed to a generic working folder instead of the roadmap skill, for the same reason.

Fix: keep the two routing facts in the pointer line (+~200 chars). All retests then matched the old template.

## Lessons
- The biggest wins were duplicates of what the harness already injects, not prose tightening.
- Encode the removal tests into your audit tooling so the trim does not drift back.
- Run [`claude-md-lint`](../tools/lint) on your own stack before and after: it reports resident chars and ~tokens (chars/4) plus dangling imports and cross-file duplicates, so you can reproduce the table above.
- A bullet that is the only place naming a skill or route is not a duplicate, even if it looks like a lookup-table row. Before moving an entry out, check what else names its target, and keep that one fact inline.
- A static read-through will not find these. Run the same routing-only prompts against the old and new files; a regression shows up as a difference, not as a judgement call. Use real folder and skill names (a made-up ticket prefix once made a correct answer look like a miss).
- At 21% this is a modest win; it is worth doing once, not a headline number.
