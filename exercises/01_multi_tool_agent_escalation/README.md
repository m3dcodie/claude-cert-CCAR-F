# Exercise 1: Build a Multi-Tool Agent with Escalation Logic

**Official objective (outline.md §8):** practice designing an agentic loop with tool
integration, structured error handling, and escalation patterns.

**Domains reinforced:** D1 (Agentic Architecture & Orchestration), D2 (Tool Design &
MCP Integration), D5 (Context Management & Reliability).

## What this wires together

- Two similar tools with carefully differentiated descriptions (D2 2.1), to check tool
  selection doesn't get confused between them.
- An agentic loop keyed on `stop_reason` (D1 1.1).
- Structured tool error responses with `errorCategory`/`isRetryable` (D2 2.2).
- A programmatic pre-call hook blocking refunds over $500 and redirecting to escalation
  (D1 1.4/1.5).
- A multi-concern customer message, decomposed and handled item by item, then
  synthesized into one response (D1 1.4, D5 5.1 case facts).

Run it:

```bash
python3 agent.py
```

No API key needed — see [`agent.py`](./agent.py); it reuses `common/mock_client.py`
from the repo root the same way every domain example does.
