# Domain 1: Agentic Architecture & Orchestration (27%)

## Task Statement 1.1 — Implement the agentic loop control flow

**Knowledge:** tool results get appended to conversation history so the model can
reason about its next action. The loop continues while `stop_reason == "tool_use"` and
ends when `stop_reason == "end_turn"`. This is *model-driven* decision-making — Claude
decides which tool to call next from context, not a pre-coded decision tree.

**Anti-patterns to avoid:** parsing the assistant's natural-language text to decide
whether to stop; using an arbitrary iteration cap as the *primary* stop mechanism
(a cap is a safety backstop, not the control signal); checking "did it produce text"
as a completion indicator (a model can emit text *and* still want to call a tool).

**Example:** [`examples/01_agentic_loop.py`](./examples/01_agentic_loop.py)

## Task Statement 1.2 — Orchestrate multi-agent systems with coordinator-subagent patterns

**Knowledge:** hub-and-spoke — a coordinator owns *all* inter-subagent communication,
error handling, and routing; subagents never talk to each other directly. Subagents
have isolated context — they do **not** automatically inherit the coordinator's
conversation history. The coordinator decomposes the task, decides which subagents to
invoke (not always the full pipeline), aggregates results, and iteratively
re-delegates to close coverage gaps. Overly narrow decomposition by the coordinator is
a real risk — it silently leaves parts of a broad topic uncovered.

**Example:** [`examples/02_coordinator_subagent.py`](./examples/02_coordinator_subagent.py)

## Task Statement 1.3 — Configure subagent invocation, context passing, and spawning

**Knowledge:** the `Task` tool spawns subagents — a coordinator's `allowedTools` must
include `"Task"`. Subagent context is **explicit**: whatever isn't in the prompt isn't
known to the subagent. `AgentDefinition` configures a subagent type's description,
system prompt, and tool restrictions. `fork_session` branches off a shared analysis
baseline to explore divergent approaches independently.

**Skills:** include *complete* prior findings directly in the subagent's prompt (not a
summary reference); separate content from metadata (source URL, doc name, page number)
with structured formats to preserve attribution; emit multiple `Task` calls in a
*single* coordinator turn to run subagents in parallel (not across separate turns);
write coordinator prompts as goals + quality criteria, not step-by-step procedures, so
subagents can adapt.

**Example:** [`examples/03_subagent_context_passing.py`](./examples/03_subagent_context_passing.py)

## Task Statement 1.4 — Implement multi-step workflows with enforcement and handoff patterns

**Knowledge:** programmatic enforcement (hooks, prerequisite gates) vs. prompt-based
guidance — prompt instructions alone have a non-zero failure rate, so anything that
must be deterministic (e.g., identity verification before a financial operation) needs
a programmatic gate, not just an instruction. Structured handoff protocols for
escalation must include customer details, root-cause analysis, and a recommended
action — the human agent has no access to the conversation transcript.

**Skills:** block downstream tool calls programmatically until prerequisites are met
(e.g., block `process_refund` until `get_customer` has returned a verified ID);
decompose multi-concern requests into distinct items, investigate each in parallel
sharing context, then synthesize one resolution; compile a structured handoff summary
on escalation.

**Example:** [`examples/04_hooks_enforcement.py`](./examples/04_hooks_enforcement.py) (prerequisite-gate half)

## Task Statement 1.5 — Apply Agent SDK hooks for tool call interception and data normalization

**Knowledge:** `PostToolUse` hooks intercept a tool's *result* to transform it before
the model sees it (e.g., normalizing timestamps). Pre-call hooks intercept an
*outgoing* tool call to enforce compliance (e.g., block refunds over $500). Hooks give
**deterministic** guarantees; prompt instructions give **probabilistic** compliance —
use hooks whenever the business rule must never be violated.

**Skills:** `PostToolUse` hooks that normalize heterogeneous formats (Unix timestamp,
ISO-8601, numeric status code) from different MCP tools before the agent reasons over
them; interception hooks that block policy-violating calls and redirect to an
alternative workflow (e.g., human escalation).

**Example:** [`examples/04_hooks_enforcement.py`](./examples/04_hooks_enforcement.py)

## Task Statement 1.6 — Design task decomposition strategies for complex workflows

**Knowledge:** fixed sequential pipelines (**prompt chaining**) fit predictable,
multi-aspect work (e.g., analyze each file, then a cross-file integration pass).
**Dynamic adaptive decomposition** fits open-ended investigation where subtasks are
generated from what's discovered at each step.

**Skills:** split large code reviews into per-file local-analysis passes plus a
separate cross-file integration pass (avoids attention dilution from doing it all in
one pass); for open-ended tasks (e.g., "add tests to a legacy codebase"), map
structure first, identify high-impact areas, then build a plan that adapts as
dependencies are discovered — don't fix the plan up front.

**Example:** [`examples/05_task_decomposition.py`](./examples/05_task_decomposition.py)

## Task Statement 1.7 — Manage session state, resumption, and forking

**Knowledge:** `--resume <session-name>` continues a named prior conversation.
`fork_session` branches independently from a shared baseline. When resuming after code
changed, you must tell the agent what changed — it won't know on its own. Starting a
**new** session with a structured summary is more reliable than resuming a session
whose tool results have gone stale (e.g., file contents it read earlier have since
changed).

**Skills:** use named `--resume` across work sessions; use `fork_session` to compare
two approaches (e.g., two refactor strategies) from one shared analysis; choose resume
vs. fresh-with-summary based on whether prior tool results are still valid; when
resuming, name the specific files that changed rather than forcing a full re-explore.

**Example:** [`examples/06_session_resume_fork.py`](./examples/06_session_resume_fork.py)
