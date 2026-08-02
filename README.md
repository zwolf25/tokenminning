# Tokenminning

![tokenmaxxing vs tokenminning](/resources/TokenmaxxingVsTokenminning)

## Maximizing intelligence per token

Tokenminning is an optimization philosophy within **context engineering** that seeks to maximize **intelligence per token**.

Rather than asking:

> "How do I give the model more context?"

Tokenminning asks:

> "How do I give the model the *right* context at the right time?"

The goal is not to minimize tokens.

The goal is to maximize the value of the information presented to the model while preserving or improving performance.

Tokenminning optimizes the **model's context surface**, not the size or complexity of the underlying system.

## Tokenmaxxing vs Tokenminning

![Before vs After Architecture](/resources/BeforevsAfterArchitecture.png)

| Tokenmaxxing | Tokenminning |
|---|---|
| Add more context | Add better context |
| Bigger prompts | Denser prompts |
| Load everything | Retrieve what matters |
| More memory | Better memory architecture |
| More tokens | More intelligence per token |

## What Tokenminning Is Not

Tokenminning is **not**:

- Using fewer tokens simply to reduce API costs
- Aggressively shortening every prompt
- Removing useful context
- Avoiding large context windows

Instead, tokenminning is about improving information density and reducing unnecessary context.

Sometimes the correct tokenminning solution uses **more** tokens—if those additional tokens significantly improve reasoning quality.

Likewise, many of the biggest improvements come from deleting duplicated, obsolete, or permanently loaded information rather than making existing prompts shorter.

## Principles

![Tokenminning Decision Tree](/resources/TokenminningDecisionTree.png)

### 1. Retrieve, don't preload

Provide the model with relevant information when needed rather than loading everything upfront.

### 2. Compress, don't repeat

Reduce redundant instructions, explanations, and historical context.

### 3. Structure, don't narrate

Use structured information over long prose whenever possible.

### 4. Spend tokens where reasoning matters

Allocate context and inference budget to areas where additional reasoning creates value.

### 5. Design systems, not prompts

The best token optimization comes from architecture: retrieval, tools, memory, and workflows.

### 6. Optimize context, not complexity

Tokenminning is not about making systems smaller.

A complex system can still be tokenminning if it controls what information reaches the model.

The question is not:

> "How much exists?"

The question is:

> "What does the model need right now?"

### 7. Eliminate context debt continuously

Context naturally accumulates over time.

Instructions are copied instead of referenced. Memories outlive their usefulness. Routing tables drift. Configuration becomes duplicated. Dead references remain.

Tokenminning treats context like production code: it should be audited, refactored, and simplified continuously.

The largest token savings often come not from compressing prompts, but from removing information that never needed to be loaded in the first place.

A token-efficient system is not one that was optimized once—it is one that stays optimized.

![Context Surface](/resources/ContextSurface.png)

## Examples

**Pattern examples:**
- **CLAUDE.md**: Focused operating guidance, separate docs retrieved as needed
- **Memory architecture**: Compress decisions, summarize volatile state
- **RAG systems**: Rank and filter before retrieval, don't dump everything
- **Tool design**: Every capability introduces context tradeoffs

**Deep case studies:**
- **[RTK & LLMLingua Evaluation](examples/rtk-llmlingua-evaluation.md)** — Evaluated 4 token-optimization repos; kept RTK for CLI tool-output compression; rejected LLMLingua (lossy prompt compression, wrong use case); discovered 1.5M tokens/30-day RTK adoption gap in compound commands.
- **[Second Brain Config Audit](examples/second-brain-config-audit.md)** — Audited CLAUDE.md files, memory architecture, and config bloat; cut ~3,500 tokens/session (29% combined CLAUDE.md reduction) with monthly auto-enforcement.
- **[Wiki Pipeline](examples/wiki-pipeline.md)** — How sc-wiki-builder → sc-wiki-cleanup went from $50+/run (11 agents, full-vault default) to $15-25/run (2-3 agents, recently-touched scope) by fixing default scope architecture.

## Why this matters

AI systems accumulate **context debt** in the same way software accumulates technical debt.

Without ongoing maintenance, memories grow indefinitely, instructions become duplicated, routing drifts, and obsolete information continues consuming context long after it has stopped providing value.

Tokenminning is the practice of continuously paying down that debt.

As AI systems become more capable, the bottleneck shifts from context availability to context quality.

Larger context windows do not eliminate the need for good information architecture.

The future is not unlimited context.

The future is intelligent context selection.

## Real-World Results

### Context maintenance can outperform prompt optimization

Many token optimization discussions focus on summarization or prompt compression.

In practice, some of the largest recurring savings come from improving the architecture itself:

- Removing duplicated instructions
- Eliminating stale configuration
- Keeping startup context intentionally small
- Moving durable knowledge into retrievable sources
- Treating routing as a first-class design problem

These changes reduce token usage before a conversation even begins.

| System | Before | After | Savings |
|--------|--------|-------|---------|
| Second Brain (wikis) | 211K words duplication | 28K words | 87% ↓ |
| AI session cost | $15-25/session | $2-4/session | 75-85% ↓ |
| Stale sync clones | 45/68 (66%) | 0 | 100% ↓ |
| Wiki pipeline | $50+/run, 11 agents | $15-25/run, 2-3 agents | ~60-70% cost, 80% agents |
| Second Brain config/memory audit | ~48.6 KB CLAUDE.md | 34.4 KB | ~29% ↓ (~3,500 tokens/session) |
| RTK/LLMLingua evaluation | 4 repos reviewed | RTK kept; 1.5M tokens/30d gap found | Adoption gap → upstream fix |

See the [Second Brain case study](examples/second-brain-system.md), [RTK & LLMLingua Evaluation](examples/rtk-llmlingua-evaluation.md), [Config Audit case study](examples/second-brain-config-audit.md), and [Wiki Pipeline case study](examples/wiki-pipeline.md) for the full breakdown.

## Status

Tokenminning is an emerging concept.

This repository is intended to refine the philosophy through discussion, examples, and real-world engineering experience.

Feedback, counterexamples, and alternative viewpoints are encouraged.

## Origin

The term "tokenminning" was introduced in July 2026 as a way to describe an emerging optimization philosophy centered on maximizing intelligence per token.

Inspired by the emerging concept of tokenmaxxing: intentionally using larger context windows and more tokens to improve AI performance.

## Core Techniques

![Retrieval Escalation Pyramid](/resources/RetrievalEscalationPyramid.png)

- **[Stub Pattern](examples/second-brain-system.md#the-stub-pattern)** — Replace full-body clones with reference-only pointers (summary + source-path)
- **Grep-before-read** — Never read a folder wholesale; search for relevance first
- **Escalation ladder** — Level 1: local cache, Level 2: stub lookup, Level 3: on-demand read
- **Compaction** — Compress conversation history; keep active context under 15K tokens
- **Context hygiene** — Regularly audit memories, instructions, and routing for duplication, stale content, and obsolete references
- **Thin routers** — Keep startup instructions focused on behavior and routing; retrieve implementation details on demand
- **Single source of truth** — Store durable knowledge once and reference it instead of copying it into multiple always-loaded locations

## More

Articles:
- [Token Maxxing is Dead. Long Live Token Minning](https://medium.com/@zwolf25/token-maxxing-is-dead-long-live-token-minning-707fffbf2b95)
- [Tokenminning Is Not About Tokens](https://medium.com/@zwolf25/tokenminning-is-not-about-tokens-d7e08673589a?sharedUserId=zwolf25)
- [The 80% That Was Noise](https://medium.com/@zwolf25/the-80-that-was-noise-8984698ae4ea?sharedUserId=zwolf25)
- [The Context Window Is a Distraction](https://medium.com/@zwolf25/the-context-window-is-a-distraction-e6e86ac9f2a1?sharedUserId=zwolf25)
- [AI Tokenomics Measures. Tokenminning Builds](https://medium.com/@zwolf25/the-context-window-is-a-distraction-e6e86ac9f2a1?sharedUserId=zwolf25)
- [Context Debt: The Hidden Tax](https://medium.com/@zwolf25/context-debt-the-hidden-tax-making-your-ai-less-intelligent-12cb00c2895f?sharedUserId=zwolf25)
- [Your Prompt Isn’t the Problem. Your Workflow Is](https://medium.com/@zwolf25/your-prompt-isnt-the-problem-your-workflow-is-9dd29ca90a3c?sharedUserId=zwolf25)

## Contributing

Have you encountered an example of tokenminning?

Open an Issue or Pull Request with:

- Real-world examples
- Counterexamples
- Benchmarks
- Alternative definitions
- Related research
- Tool-specific patterns (Claude Code, Codex, Continue, Cursor, etc.)

The goal is to evolve the concept through practical experience rather than theory alone.
