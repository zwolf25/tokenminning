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

Instead, tokenminning is about improving **information density**.

Sometimes the correct tokenminning solution uses **more** tokens—if those additional tokens significantly improve reasoning quality.

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

![Context Surface](/resources/ContextSurface.png)

## Examples

**Pattern examples:**
- **CLAUDE.md**: Focused operating guidance, separate docs retrieved as needed
- **Memory architecture**: Compress decisions, summarize volatile state
- **RAG systems**: Rank and filter before retrieval, don't dump everything
- **Tool design**: Every capability introduces context tradeoffs

**Deep case study:**
- **[Second Brain System](examples/second-brain-system.md)** — How a team knowledge vault went from 211K words of duplication to 28K words reference-only (87% reduction).

## Why this matters

As AI systems become more capable, the bottleneck shifts from context availability to context quality.

Larger context windows do not eliminate the need for good information architecture.

The future is not unlimited context.

The future is intelligent context selection.

## Real-World Results

| System | Before | After | Savings |
|--------|--------|-------|---------|
| Second Brain (wikis) | 211K words duplication | 28K words | 87% ↓ |
| AI session cost | $15-25/session | $2-4/session | 75-85% ↓ |
| Stale sync clones | 45/68 (66%) | 0 | 100% ↓ |

See the [Second Brain case study](examples/second-brain-system.md) for the full breakdown.


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

Placement: After the "Origin" section, before "Contributing"

## More

Article:
[Token Maxxing is Dead. Long Live Token Minning.](https://medium.com/@zwolf25/token-maxxing-is-dead-long-live-token-minning-707fffbf2b95)

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
