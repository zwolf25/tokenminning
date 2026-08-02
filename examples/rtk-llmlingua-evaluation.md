# Case Study: RTK & LLMLingua Evaluation

**Scope:** Evaluated 4 external token-optimization GitHub repos against existing Claude Code setup (RTK proxy + caveman/ponytail modes)  
**Result:** Kept RTK for CLI tool-output compression; rejected LLMLingua (wrong use case); skipped 3 repos (license, redundancy, gated skill)  
**Unexpected discovery:** Only 6% of Bash calls routed through RTK (~1.5M tokens/30 days missed) — hook gap in `&&`/pipe chains  

---

## Context

Zac's existing setup:
- **RTK** — Rust CLI proxy rewriting Bash commands (`git status` → `rtk git status`), cuts tool-output tokens deterministically, lossless
- **Caveman mode** — drops filler/preambles from prompts
- **Ponytail mode** — blocks over-engineering (YAGNI, stdlib-first)
- **gsd:graphify** skill — codebase mapping (already installed, per-project gated)

Question: *Do any external repos improve this?*

---

## Repos Evaluated

| Repo | Verdict | Reason |
|------|---------|--------|
| `microsoft/LLMLingua` | **Rejected** | Lossy prompt compression via local model (GPT2/phi-2); garbles code; wrong tool for CLI output |
| `alexgreensh/token-optimizer` | **Skipped** | PolyForm Noncommercial license (blocks Fortive/SC commercial use); competing PreToolUse hook layer conflicts with RTK |
| `drona23/claude-token-efficient` | **Skipped** | Prompt-only CLAUDE.md; redundant with caveman + ponytail already active |
| `Graphify-Labs/graphify` | **No action** | Already wired as `gsd:graphify` skill, per-project gated |
| `olivomarco/github-copilot-token-optimization` | **Skipped** | Copilot-specific; inspired unused-MCP-connector audit idea (not acted on) |

---

## LLMLingua Deep Dive

**What it does:** Runs a second local model to compress *prompt* text (RAG contexts, ICL examples, long conversations) — output is lossy by design.

**Why it fails for CLI:**
| RTK (CLI) | LLMLingua (Research) |
|-----------|----------------------|
| Compresses **tool output** (git diffs, logs, command results) | Compresses **prompt/input** text |
| Deterministic, exact text preserved | Lossy — own README example mangles words |
| Zero dependencies (single binary) | Requires pip + local model (GPT2/phi-2/BERT) |
| Solves: "command output too verbose" | Solves: "RAG context too long for context window" |

**Correct future use case:** SC AI product feature with long RAG contexts (agentic AI roadmap). Filed under `claude-api` skill's LLM-shaped-task trigger.

---

## The Real Finding: RTK Adoption Gap

`rtk discover` analyzes Claude Code history for missed optimization opportunities.

**Result:** Only **6% of Bash calls** in last 30 days routed through RTK.

**Root cause:** RTK's hook doesn't rewrite commands inside:
- `&&` chains: `git status && git diff`
- Pipe chains: `cat file | grep foo`
- Heredocs / subshells

**Tokens missed:** ~1.5M tokens / 30 days

**Upstream issue:** Exact duplicate already open (rtk-ai/rtk#2425, filed 3 days prior). Added corroborating comment with 16.7K-command sample vs. original 941-command report.

---

## Genuine Addition: Retry-Loop Warning Hook

Instead of building a competing output-trimming hook (RTK already has compact-output subcommands: `test`, `err`, `log`, `jest`, `vitest`, `tsc`, `lint`, etc.), built `loop-detect.sh`:

```bash
# PreToolUse hook — warns (doesn't block) on 3rd consecutive identical tool call
if [ "$COUNT" -eq 3 ]; then
  jq -nc --arg tool "$TOOL" '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "ask",
      permissionDecisionReason: "Same \($tool) call repeated 3x in a row — possible retry loop, confirm to continue."
    }
  }'
fi
```

**Design choice:** `permissionDecision: "ask"` (warn) not exit-code-2 (hard block) — avoids breaking legitimate polling while catching blind retry loops.

---

## Token Savings

| Category | Amount | Notes |
|----------|--------|-------|
| **RTK tool-output compression** | Ongoing (existing) | Deterministic, lossless, ~60-90% on command output |
| **LLMLingua vocab reduction** | **~60-70%** (claimed) | Not applicable to CLI — wrong compression target |
| **RTK adoption gap fixed** | **~1.5M tokens/30 days** | Once upstream hook fix lands (rewrite leading command in chains) |
| **Retry-loop prevention** | Unquantified | Stops infinite retries before they accumulate |

---

## Mapping to Tokenminning Principles

| Principle | Applied Here |
|-----------|--------------|
| **Retrieve, don't preload** | `rtk discover` analyzes history to find missed opportunities — query-driven, not preload-all |
| **Compress, don't repeat** | RTK compresses tool output once at source; LLMLingua would have added lossy re-compression |
| **Structure, don't narrate** | Hook rewrite is structured (command → proxied command), not narrative |
| **Design systems, not prompts** | RTK = architecture (proxy + hook); not "write shorter prompts" |
| **Optimize context, not complexity** | RTK binary + hook = simple; LLMLingua = pip + local model + inference = complex |
| **Eliminate context debt continuously** | `rtk discover` = scheduled audit; retry-loop hook = prevents new debt |
| **Spend tokens where reasoning matters** | Tokens saved on verbose command output; preserved for actual reasoning |

---

## Key Insights

1. **Tool-output compression ≠ prompt compression** — different problems, different tools. RTK solves the CLI problem; LLMLingua solves the RAG/ICL problem.

2. **Audit your own adoption** — `rtk discover` revealed 94% of commands bypassed the optimizer. The tool worked; the hook didn't reach it.

3. **Check installed tools first** — RTK already had compact-output subcommands for test/lint/jest output. Building a new hook would have duplicated existing tooling.

4. **Corroborate, don't duplicate** — Found exact-match GitHub issue; added data instead of filing new issue. Faster resolution, less noise.

5. **Warn, don't block** — Retry-loop hook uses `permissionDecision: "ask"` respecting legitimate repeats (polling) while catching blind loops.

---

## Files / Artifacts

- **Raw notes:** `2026-07-24 - LLMLingua evaluated for RTK setup.md`, `2026-07-25 - RTK token-optimization repo review.md`
- **Wiki:** `ai-tools-and-workflows.md` (lines 442-446, 466)
- **Hook:** `loop-detect.sh` (PreToolUse, all tools)
- **Upstream:** rtk-ai/rtk#2425 (corroborating comment)
- **Memory:** `rtk-compound-command-gap.md`, `github-token-optimization-repo-review.md`
- **Plan:** `~/.claude/plans/loop-detection-and-output-trim-hooks.md`
