# tokenminning with Claude Code

Claude Code is a strong example of where tokenminning principles apply because agent workflows are heavily influenced by context architecture, retrieval patterns, and information flow.

## Problem

AI coding agents often improve initially by adding:

- More instructions
- More tools
- More memory
- More project context

However, indiscriminate context growth can create noise, increase cost, and make it harder for the model to identify the information most relevant to the task.

---

## tokenmaxxing approach

A project may evolve into:

- A large `CLAUDE.md` containing every project detail regardless of relevance
- All MCP servers enabled regardless of task requirements
- Complete conversation history preserved instead of extracting decisions
- Every skill exposed by default
- Documentation duplicated across multiple locations

The system has more information, but not necessarily better information.

---

## tokenminning approach

A tokenminning workflow:

### Keep always-loaded context intentional

`CLAUDE.md` should contain:

- Project purpose
- Critical rules
- Development workflow
- Important constraints

The goal is not the smallest possible `CLAUDE.md`.

The goal is ensuring always-loaded information provides durable value.

Detailed information should live elsewhere.

---

### Retrieve information when needed

Instead of:

> "Load everything about this project"

Use:

> "Find the relevant information for this task"

Examples:

- Search documentation
- Retrieve architecture decisions
- Load relevant files
- Query knowledge bases

---

### Make tools intentional

Every tool adds capability, but also introduces selection and maintenance tradeoffs.

Prefer:

- Task-specific MCP servers
- Scoped tools
- On-demand capabilities

---

### Preserve decisions, not history

The valuable output of an AI session is usually:

- Decisions made
- Code changes
- Lessons learned
- Updated requirements

Not:

- Entire conversation transcripts
- Debugging attempts
- Temporary exploration

---

## Practical checklist

A Claude Code workflow is moving toward tokenminning when:

✅ `CLAUDE.md` becomes more focused over time
✅ Documentation is retrieved instead of copied  
✅ Skills are modular  
✅ MCP servers are intentional  
✅ Decisions are captured separately from conversations  
✅ Context is loaded based on the task

---

## Example from a real workflow

A large knowledge base was redesigned from duplicated documents into lightweight pointers.

Instead of loading every source document:

```
Pointer → Source → Retrieve when needed
```

The system preserves access to information without continuously exposing all information to the model.

---

## Principle

The best Claude Code workflows are not the ones with the most context.

They are the ones that provide the right context at the right time.

---

## Advanced example

A sophisticated Claude Code environment can still be tokenminning.

The measure is not:

> "How many files, tools, or skills exist?"

The measure is:

> "Does the model receive the information needed for this task, and only when needed?"
