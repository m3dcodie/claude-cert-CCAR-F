# Domain 2: Tool Design & MCP Integration (18%) — Priority: weakest domain on the mock (40%)

## Task Statement 2.1 — Design effective tool interfaces with clear descriptions and boundaries

**Knowledge:** the tool **description** is the primary signal an LLM uses for tool
selection — a minimal description ("Analyzes content") is unreliable when there's a
similar tool nearby. Descriptions should cover input formats, example queries, edge
cases, and where the boundary with similar tools sits. Ambiguous/overlapping
descriptions (`analyze_content` vs `analyze_document` with near-identical wording)
cause misrouting. The **system prompt's wording** matters too — a keyword-sensitive
instruction can accidentally bias tool selection toward one tool over another.

**Skills:** write descriptions that state purpose, expected input/output, and "use
this vs. that" guidance explicitly; rename + rewrite instead of leaving overlap (e.g.
`analyze_content` → `extract_web_results` with a web-specific description); split an
overly generic tool into purpose-specific ones with defined contracts (`analyze_document`
→ `extract_data_points` / `summarize_content` / `verify_claim_against_source`); review
system prompts for keyword bias that could override good tool descriptions.

**Example:** [`examples/01_tool_description_disambiguation.py`](./examples/01_tool_description_disambiguation.py)

**Beyond the outline:** the API also has `strict: true` on a custom tool definition,
which guarantees Claude's `tool_use` input matches your JSON schema exactly (no missing
required fields, no type mismatches) — this closes the gap a good description alone
can't: a well-disambiguated tool can still get malformed input. Good descriptions solve
*which* tool gets picked; `strict: true` solves *whether the call to it is well-formed*.

## Task Statement 2.2 — Implement structured error responses for MCP tools

**Knowledge:** MCP tools signal failure with the `isError` flag. Errors fall into
categories the agent needs to tell apart: **transient** (timeout, unavailable — worth
retrying), **validation** (bad input — not retryable as-is, needs a fixed input),
**business** (policy violation — not retryable, needs a different action), **permission**
(not retryable, needs different credentials/escalation). A generic `"Operation failed"`
gives the agent nothing to act on. Returning `isRetryable` explicitly prevents wasted
retry loops. A **valid empty result** (query succeeded, zero matches) is not an error at
all — conflating it with an access failure is a common bug.

**Skills:** return `errorCategory` + `isRetryable` + a human-readable description;
include `retriable: false` plus a customer-friendly explanation for business-rule
violations so the agent can *explain* rather than retry; let subagents attempt local
recovery for transient errors and only escalate to the coordinator what they can't fix
themselves, along with partial results and what was attempted; keep "no results" and
"couldn't access the data" as distinct, never collapse them into one error shape.

**Example:** [`examples/02_structured_mcp_errors.py`](./examples/02_structured_mcp_errors.py)

## Task Statement 2.3 — Distribute tools appropriately across agents and configure tool choice

**Knowledge:** more tools on one agent is not free — going from ~4-5 to ~18 tools on a
single agent measurably degrades selection reliability (more decision complexity, more
chances for a near-miss). Agents given tools outside their specialization tend to
misuse them (a synthesis agent that starts doing its own web searches instead of
synthesizing). Prefer scoped access: each agent gets only what its role needs, with a
small number of deliberately shared cross-role tools for genuinely high-frequency needs.
`tool_choice` has three modes: `"auto"` (model may respond with text instead of a tool
call), `"any"` (must call *some* tool, model picks which), and forced
`{"type": "tool", "name": "..."}` (must call that specific tool).

**Skills:** restrict each subagent's tool set to its role; replace an overly generic
tool with a constrained one (`fetch_url` → `load_document` that validates the URL is an
actual document); give a narrow, high-frequency cross-role tool (e.g. `verify_fact` on
a synthesis agent) instead of full search access, routing anything bigger through the
coordinator; force a specific tool first with `tool_choice: {"type": "tool", "name": ...}`
when a step must run before others (e.g. `extract_metadata` before enrichment); use
`tool_choice: "any"` to guarantee a tool call instead of conversational text.

**Example:** [`examples/03_tool_distribution_and_choice.py`](./examples/03_tool_distribution_and_choice.py)

**Beyond the outline:** two more real levers worth knowing alongside the three
`tool_choice` modes:
- `tool_choice: {"type": "auto", "disable_parallel_tool_use": true}` caps a turn to at
  most one tool call — useful when you need to inspect/act on each result before the
  next call rather than getting several `tool_use` blocks at once.
- The **tool search tool** (`tool_search_tool_*`) is Anthropic's answer to the "18
  tools degrades selection" problem at real scale: instead of hand-scoping every
  agent's tool list, tools are registered but not loaded into context up front, and
  Claude searches/loads the relevant ones on demand. Manual scoping (this task
  statement) and tool search solve the same problem at different scales — scoping for
  a handful of agents each with a handful of tools, tool search when one agent
  legitimately needs access to hundreds.

## Task Statement 2.4 — Integrate MCP servers into Claude Code and agent workflows

**Knowledge:** MCP servers are scoped — **project-level** `.mcp.json` for shared team
tooling (checked into the repo), **user-level** `~/.claude.json` for personal/
experimental servers. `.mcp.json` supports environment-variable expansion
(`${GITHUB_TOKEN}`) so credentials never get committed. Tools from **every** configured
server are discovered at connection time and are all simultaneously available to the
agent — there's no lazy/on-demand loading. MCP **resources** expose content catalogs
(issue summaries, doc hierarchies, DB schemas) so the agent can see what's available
without burning exploratory tool calls to find out.

**Skills:** configure shared servers in project-scoped `.mcp.json` with `${ENV}`
expansion for tokens; configure personal/experimental servers in user-scoped
`~/.claude.json`; write detailed MCP tool descriptions so the agent doesn't default to
a less-capable built-in (e.g., preferring a real code-search MCP tool over `Grep`
because the built-in's description reads as more familiar); prefer an existing
community MCP server (e.g., for Jira) over building one from scratch, reserving custom
servers for genuinely team-specific workflows; expose a resource for a content catalog
instead of making the agent explore for it.

**Example:** [`examples/04_mcp_server_config/`](./examples/04_mcp_server_config/)

## Task Statement 2.5 — Select and apply built-in tools (Read, Write, Edit, Bash, Grep, Glob) effectively

**Knowledge:** `Grep` is for searching file **contents** (function names, error
strings, import statements). `Glob` is for finding files by **path pattern**
(`**/*.test.tsx`). `Read`/`Write` operate on whole files; `Edit` does targeted,
unique-text-anchored modifications. When `Edit` fails because the anchor text isn't
unique, the reliable fallback is `Read` the whole file, then `Write` it back modified —
not repeatedly trying looser anchors.

**Skills:** use `Grep` to find all callers of a function or all occurrences of an error
message; use `Glob` for naming-pattern file discovery; fall back to `Read` + `Write`
when `Edit`'s anchor isn't unique; build codebase understanding incrementally —
`Grep` for entry points, then `Read` to follow imports and trace flow — rather than
reading everything upfront; trace a function across re-export/wrapper modules by first
listing every exported name, then `Grep`-ing for each name across the codebase.

**Example:** [`examples/05_builtin_tools_patterns.py`](./examples/05_builtin_tools_patterns.py)
