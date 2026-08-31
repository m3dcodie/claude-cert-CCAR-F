# Claude Certified Architect – Foundations (CCAR-F) — Study Repo

Theory + runnable practical examples for the [Claude Certified Architect – Foundations
exam guide](./outline.md) (v1.0, effective July 2026). Built to (1) prep for the exam
retake and (2) hand working examples to teammates as a reference.

## How this is organized

One folder per exam domain. Each domain folder has:

- `README.md` — theory notes, one section per **Task Statement**, numbered to match
  `outline.md` exactly, each ending with a link to the example(s) that demonstrate it.
- `examples/*.py` — runnable, self-contained scripts. Each has a docstring naming the
  task statement it covers, the pattern it shows, and the anti-pattern it avoids.

`exercises/` holds the 4 official capstone exercises from `outline.md` §8, each wiring
together examples from multiple domains into one end-to-end mini-project.

## Running the examples

No API key required. Every script imports `common/mock_client.py`, a small offline
stand-in for the Anthropic SDK client (scripted `messages.create()` responses, same
`.content` / `.stop_reason` / tool_use shapes as the real thing). Each script prints a
`[MOCK]` banner and runs standalone:

```bash
python3 domain-1-agentic-architecture/examples/01_agentic_loop.py
```

To run any script against the **real** API instead: set `ANTHROPIC_API_KEY`, swap
`from common.mock_client import MockAnthropic as Anthropic` for
`from anthropic import Anthropic`, and drop the `.queue_response(...)` setup calls
(everything else — the loop logic, hook logic, schema, prompts — is unchanged). That's
the one intentional seam in every example.

## Domains

| # | Domain | Weight | Folder |
|---|--------|--------|--------|
| 1 | Agentic Architecture & Orchestration | 27% | [`domain-1-agentic-architecture/`](./domain-1-agentic-architecture/) |
| 2 | Tool Design & MCP Integration | 18% | [`domain-2-tool-mcp/`](./domain-2-tool-mcp/) |
| 3 | Claude Code Configuration & Workflows | 20% | [`domain-3-claude-code-config/`](./domain-3-claude-code-config/) |
| 4 | Prompt Engineering & Structured Output | 20% | [`domain-4-prompt-engineering/`](./domain-4-prompt-engineering/) |
| 5 | Context Management & Reliability | 15% | [`domain-5-context-reliability/`](./domain-5-context-reliability/) |

## Study plan (weighted by the mock exam attempt)

See [`mock_exam_notes.md`](./mock_exam_notes.md) for the full gap analysis. Priority
order for review, weakest first:

1. **Domain 2 — Tool Design & MCP** (40% on the mock) — start here.
2. **Domain 4 — Prompt Engineering & Structured Output** (50%).
3. **Domain 5 — Context Management & Reliability** (60%).
4. **Domain 1 — Agentic Architecture** (83%) — spot-check only.
5. **Domain 3 — Claude Code Configuration** (83%) — spot-check only.

Then work through `exercises/` end to end — they deliberately cross domain boundaries
the way exam scenario questions do:

| Exercise | Wires together | Folder |
|---|---|---|
| 1. Multi-Tool Agent with Escalation Logic | D1, D2, D5 | [`exercises/01_multi_tool_agent_escalation/`](./exercises/01_multi_tool_agent_escalation/) |
| 2. Team Development Workflow Config | D3, D2 | [`exercises/02_team_workflow_config/`](./exercises/02_team_workflow_config/) |
| 3. Structured Data Extraction Pipeline | D4, D5 | [`exercises/03_extraction_pipeline/`](./exercises/03_extraction_pipeline/) |
| 4. Multi-Agent Research Pipeline | D1, D2, D5 | [`exercises/04_research_pipeline/`](./exercises/04_research_pipeline/) |

Exercises 1, 3, and 4 are runnable Python (`python3 <folder>/agent.py` or `pipeline.py`).
Exercise 2 is a config/CLI walkthrough — its README points at the real config files to
copy into a test project and a verification checklist to run in Claude Code itself.

## Sharing with others

This is a local git repo (no remote configured). Push it to a private GitHub/GitLab repo
whenever you're ready to actually share it with teammates — nothing here has been
pushed anywhere yet.
