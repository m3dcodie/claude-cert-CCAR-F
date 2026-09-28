# Exercise 4: Design and Debug a Multi-Agent Research Pipeline

**Official objective (outline.md §8):** practice orchestrating subagents, managing
context passing, implementing error propagation, and handling synthesis with
provenance tracking.

**Domains reinforced:** D1 (Agentic Architecture & Orchestration), D2 (Tool Design &
MCP Integration), D5 (Context Management & Reliability).

## What this wires together

- A coordinator that spawns two subagents (web search, document analysis) in
  **parallel** — multiple `Task` calls in one turn (D1 1.2/1.3).
- Each subagent's findings passed to synthesis as complete, structured content with
  separate metadata, not references to "earlier findings" (D1 1.3, D5 5.6).
- A simulated subagent timeout, propagated as structured error context so the
  coordinator can proceed with partial results and annotate the coverage gap (D5 5.3).
- Conflicting statistics from two sources, preserved with attribution instead of
  arbitrarily resolved (D5 5.6).

Run it:

```bash
python3 pipeline.py
```
