# Quiz Bank — CCAR-F Practice Questions by Domain & Task Statement

A question bank for self-testing against the Claude Certified Architect – Foundations
(CCAR-F) exam guide documented in [`outline.md`](./outline.md) and the `domain-*/README.md`
files in this repo. Each question is tagged to the Task Statement it tests — cross-check
the tag against that domain's README if you want the underlying theory before or after
attempting the question.

**How to use this:** read a question cold, pick an answer and write down *why*, then check
the Answer Key at the end of that domain's section. Getting the mechanism right but not
the specific detail (a flag, a field name) is a partial pass — drill it again.

---

## Domain 1 — Agentic Architecture & Orchestration

### T.S. 1.1 — Agentic loop control flow

**Q1.** A refactoring agent's loop terminates by parsing the assistant's last message for
the phrase "refactoring complete," running 20 iterations even on simple classes. Logs show
`stop_reason` actually returns `"end_turn"` after iteration 4. What is the correct fix?

A. Add a tool the agent must call explicitly to signal completion, and check for that tool call each iteration
B. Lower the iteration cap to 5 so the agent stops sooner, matching where `stop_reason` already returns `end_turn`
C. Improve the phrase detection to also check for "finished," "done," and "all changes applied"
D. Replace the natural-language parsing with `stop_reason` inspection: exit on `"end_turn"`, continue on `"tool_use"`

### T.S. 1.2 — Coordinator-subagent orchestration

**Q2.** A multi-agent research system produces a report on "renewable energy technologies"
that only covers solar and wind, missing geothermal, tidal, biomass, and nuclear fusion.
Each subagent produced thorough coverage of its assigned topic. Where is the root cause?

A. The document analysis subagent lacked access to sources on the missing categories
B. The coordinator's task decomposition assigned only solar and wind, omitting the other categories
C. The web search subagent scoped its queries too narrowly
D. The synthesis subagent failed to audit its inputs for coverage gaps

**Q3.** A coordinator always invokes the full pipeline of five subagents (web search,
document analysis, data extraction, synthesis, formatting) for every query, including
simple factual lookups that only need web search. This adds unnecessary latency and cost.
What is the correct architectural fix?

A. Add a caching layer so subagents with no work return a cached empty result
B. Have the coordinator select which subagents to invoke per query, not always the full pipeline
C. Split into two separate systems: one for simple queries, one for complex
D. Allow subagents to communicate directly so they can skip unnecessary steps

### T.S. 1.3 — Subagent invocation, context passing, spawning

**Q4.** A coordinator spawns a web search subagent (completes in 8s) and a document
analysis subagent (completes in 12s) sequentially across separate turns; the two are
investigating independent topics. Total latency is 20s. How should this be reduced?

A. Emit both `Task` tool calls in a single response to spawn both subagents in parallel, cutting latency to roughly 12s
B. Let the web search subagent directly invoke the document analysis subagent when it finishes
C. Merge the two subagents into one to reduce coordination overhead
D. Use `fork_session` to split the coordinator into two parallel branches

**Q5.** A coordinator's system prompt correctly describes a delegation workflow, yet when
it tries to invoke a subagent nothing happens — no subagent is created, no error is
thrown. What is the most likely cause?

A. The coordinator needs to pass full conversation history to the subagent to initialize it
B. Subagents must be registered in a central agent registry the coordinator loads at startup
C. The subagent's `AgentDefinition` is missing a `description` field
D. The coordinator's `allowedTools` list does not include the `Task` tool, so it cannot spawn subagents

**Q6.** A coordinator delegates refactoring work to a schema-migration agent, an API-layer
agent, and a test-update agent. The test-update agent frequently produces tests that
reference database schemas the schema-migration agent has already renamed. The subagents
do not communicate with each other. What is the root cause?

A. The test-update agent should have read access to the schema migration files itself
B. The subagents need a shared message bus to query each other for the latest schema names
C. The coordinator is not passing the schema-migration agent's output as context when delegating to the test-update agent
D. The two agents should run sequentially instead of in parallel to avoid race conditions

**Q7.** A moderation request contains both potentially defamatory text and an embedded
image that may violate graphic-content policy. What is the correct delegation strategy?

A. Triage the whole report to whichever subagent handles the more severe category
B. Send the report to the text classifier first, then forward its output to the image analyser
C. Spawn a new combined text-and-image subagent so one specialist owns the whole decision
D. Route the text and image to their respective specialist subagents in parallel, then aggregate both results

### T.S. 1.4 — Multi-step workflows with enforcement and handoff

**Q8.** A customer lookup returns three accounts with the same name but different
addresses and account ages. The agent selects the most recently active account and
processes a refund; the refund lands on the wrong account. What should the agent have
done differently?

A. Asked the customer for additional identifying information to disambiguate the accounts
B. Selected the account with the oldest creation date
C. Processed the refund across all three accounts
D. Escalated to a human agent immediately because the results were ambiguous

### T.S. 1.5 — Agent SDK hooks for tool call interception and data normalization

**Q9.** An account-deletion agent sometimes processes deletions autonomously when a
customer is insistent, but company policy requires human approval before any permanent
deletion. What approval mechanism should be implemented?

A. A `PostToolUse` hook that reviews the deletion after it's processed and reverts it if unapproved
B. A `PreToolUse` hook on `delete_account` that pauses execution and routes the request to a human approval queue
C. Remove the `delete_account` tool entirely and require a phone line instead
D. A system prompt instruction: "Always get manager approval before processing account deletions"

**Q10.** An agent occasionally processes international transfers without required
anti-money-laundering (AML) checks. Compliance requires 100% enforcement. What is the
correct approach?

A. Add detailed AML check instructions to the system prompt with examples
B. Add a `PostToolUse` hook to flag completed transfers that skipped AML checks
C. Implement a `PreToolUse` hook that blocks transfer execution until AML verification returns a pass result
D. Train the agent with few-shot examples showing the correct AML workflow

**Q11.** A team wants every Java file written during refactoring to be automatically
formatted with the project's Checkstyle rules before being saved; developers occasionally
forget to run the formatter manually. What is the correct hook configuration?

A. A `PreToolUse` hook on `Write` that runs Checkstyle on the content before the file is written
B. A `PreToolUse` hook on `Read` that verifies Java files are Checkstyle-compliant before being read
C. A `PostToolUse` hook on file-write operations that runs the Checkstyle formatter on the written file, auto-correcting violations
D. Add "Always run Checkstyle before saving files" to `CLAUDE.md`

**Q12.** A fintech company requires all API response payloads be normalized to
`snake_case` before logging, and any file write to `src/api/` be automatically linted —
deterministically, not relying on the model remembering. Which hook configuration
achieves both?

A. A `PreToolUse` hook blocking writes to `src/api/` unless already linted, plus a `PreToolUse` hook blocking API calls unless normalization is configured
B. A `PostToolUse` hook on writes to `src/api/` that runs the linter, plus a `PostToolUse` hook on data processing that normalizes to `snake_case`
C. A `PreToolUse` hook on file writes that runs the linter before the write completes, plus a `PostToolUse` hook on API response handling that normalizes field names to `snake_case`
D. Add both requirements to `CLAUDE.md` with examples, plus a `PreToolUse` hook that reminds the model of the rules before each call

### T.S. 1.6 — Task decomposition strategies

**Q13.** A coordinator receives a request to extract a payment-processing module into a
standalone microservice: new API endpoints, database migration, 40+ call sites, and
integration tests. A junior developer suggests the coordinator handle the entire task
itself to avoid subagent communication overhead. Why is this wrong?

A. The coordinator's API rate limits would be exceeded processing 40+ files
B. Loading 40+ files into one context dilutes attention — the coordinator should delegate to scoped subagents instead
C. The coordinator should never write code, only route tasks
D. The coordinator cannot access filesystem tools

**Q14.** A team needs to add a comprehensive test suite to a large legacy codebase with
no existing tests, unclear dependencies, and unknown critical areas. Which task
decomposition strategy is most appropriate?

A. A single-pass analysis processing the entire codebase at once
B. A fixed sequential pipeline reviewing files alphabetically
C. A multi-pass architecture with per-file analysis plus a cross-file integration pass, like a standard code review
D. Dynamic adaptive decomposition: map the codebase, find high-impact areas, and adapt the plan as dependencies emerge

### T.S. 1.7 — Session state, resumption, and forking

**Q15.** An agent has spent 30 minutes debugging a failing test suite mid-refactor,
trying three different approaches that each modified configuration files. None worked,
and its context now holds three sets of conflicting modifications. The developer wants to
try a completely different strategy. What should they do?

A. Start a completely new session with no prior context, re-read the failing tests from scratch
B. Use `fork_session` from the point before the first debugging attempt
C. Start a fresh session summarizing the three failed approaches and why each failed, then pursue the new strategy with clean context
D. Continue in the current session and ask the agent to ignore all previous attempts

**Q16.** An agent has been working on a feature branch for 45 minutes and accumulated
extensive context. Several tool results from early in the session (file reads from 40
minutes ago) are now stale because a colleague pushed changes to those files, and the
agent is making recommendations based on outdated contents. What is the best recovery
strategy?

A. Start a fresh session with a summary of the key findings and decisions, then read the changed files for current state
B. Use `fork_session` to create a new branch that excludes the stale tool results while keeping the rest of the context
C. Continue in the current session and simply ask the agent to re-read the files a colleague changed
D. Start a completely new session with no context carried over at all

**Q17.** A developer wants to explore two decomposition strategies for an order-processing
module — splitting by business capability vs. splitting by data ownership — in parallel,
without losing either analysis. What is the correct approach?

A. Use `fork_session` to create two parallel exploration branches from the current session's baseline, one per strategy
B. Open two terminal tabs and run separate Claude Code sessions
C. Use `--resume` to alternate between the two strategies in a single session
D. Instruct the agent to evaluate both strategies sequentially in the same session, then compare

**Q18.** After completing an initial analysis, a team wants to explore two competing
hypotheses (a statistical-modelling approach and a machine-learning approach) starting
from the same baseline, proceeding independently. Which session management strategy is
correct?

A. Start two fresh sessions, each with an injected summary of the initial analysis
B. Resume the session twice with `--resume`, one after the other
C. Use the initial session and explore both hypotheses sequentially
D. Use `fork_session` to create two independent branches from the shared analysis baseline, exploring one hypothesis in each fork

**Q19.** In a content-moderation appeals workflow, the same agent that made the original
decision re-evaluates the appeal, and overturn rates are suspiciously low. What is the
most effective architectural change?

A. Route every appeal to a human reviewer, removing the agent from the appeal path entirely
B. Add stronger instructions requiring the agent to weigh the user's perspective fairly
C. Automatically overturn decisions whenever the user provides any justification
D. Route appeals to a separate agent instance that cannot see the original reasoning, given only the content and the user's justification

<details><summary>Answer key — Domain 1</summary>

**Q1 — D.** `stop_reason` inspection is the actual control signal; parsing assistant text
is the anti-pattern this task statement explicitly warns against, no matter how the
phrase-matching is refined (C is the same anti-pattern, just patched).

**Q2 — B.** Trace coverage failures to their origin. The synthesis agent (D) can only work
with what it's given — it can't synthesize topics nobody researched. Blame starts at
decomposition, not the last agent in the chain.

**Q3 — B.** Dynamic subagent selection based on query complexity, not an always-on full
pipeline.

**Q4 — A.** Multiple `Task` calls in one coordinator turn run subagents in parallel;
across separate turns (the original setup) is sequential and slower.

**Q5 — D.** Without `"Task"` in `allowedTools`, the coordinator physically cannot spawn
subagents — this is a configuration issue, not a prompt issue (ruling out A/C, which are
about context/description quality, not the spawning mechanism itself).

**Q6 — C.** Subagents have isolated context by design; the coordinator must explicitly
pass prior output forward. No shared memory or message bus exists between subagents (B is
a fabricated mechanism).

**Q7 — D.** Decompose independent concerns into parallel subtasks, then aggregate —
sequential (B) adds needless latency; a combined agent (C) duplicates existing capability.

**Q8 — A.** Multiple ambiguous matches require a clarifying question for more identifiers,
never a heuristic guess.

**Q9 — B.** Irreversible/high-stakes actions need a `PreToolUse` gate that blocks before
execution, not a post-hoc review (A) or a prompt instruction (D) with a non-zero failure
rate.

**Q10 — C.** Same logic as Q9 — regulatory 100% enforcement requires a deterministic
`PreToolUse` block, not prompt instructions or few-shot examples.

**Q11 — C.** `PostToolUse` fires after the file exists on disk, which is when there's
something to format. A `PreToolUse` hook on `Write` (A) fires before the file exists — 
nothing to format yet.

**Q12 — C.** Linting a write needs to happen before the write completes (`PreToolUse`);
normalizing an API *response* happens after it's received (`PostToolUse`) — the two
requirements need different hook types, matched to what's being enforced.

**Q13 — B.** More tools/files in one context isn't a rate-limit or permissions issue —
it's attention dilution, which is what scoped subagent delegation is for.

**Q14 — D.** Open-ended, dependency-unclear work needs adaptive decomposition; a fixed
pipeline (B) or single pass (A) assumes a predictable structure that doesn't exist here.

**Q15 — C.** Preserve the record of what's been tried (so the new strategy doesn't repeat
a dead end) while dropping the polluted context (three sets of conflicting edits) — fresh
session + structured summary is the standard pattern for stale/polluted tool results.

**Q16 — A.** Same pattern as Q15 — a fresh session with a summary is more reliable than
resuming a session whose tool results have gone stale.

**Q17 — A.** `fork_session` branches independently from a shared baseline — exactly for
comparing divergent approaches without losing either.

**Q18 — D.** Same mechanism as Q17, applied to hypothesis comparison instead of
architecture comparison.

**Q19 — D.** Same root cause as self-review bias (Domain 4, T.S. 4.6): an agent reviewing
its own decision retains the original reasoning and is biased toward agreeing with it. A
fresh instance with no access to that reasoning is the fix.

</details>

---

## Domain 2 — Tool Design & MCP Integration

### T.S. 2.1 — Effective tool interfaces with clear descriptions and boundaries

**Q1.** A CI/CD system prompt defines two review categories with the instructions "Check
for security vulnerabilities in each function" and "Check for performance issues in each
loop." The model frequently calls `performance_check` for security issues found inside
loops, and `security_check` for performance issues in security-sensitive functions. What
is the root cause and best fix?

A. Add a rule that security always takes priority over performance
B. Force `tool_choice` to `"auto"` and let the model determine the correct tool
C. Keyword overlap between the instruction phrasing and the tool names causes the confusion; rewrite them to use distinct, non-overlapping terms
D. Add more detailed tool descriptions explaining exactly when each tool should be called

**Q2.** An agent has two tools: `analyze_content` ("Analyses content") and
`extract_web_results` ("Extracts data from web pages"). After a system prompt update
added "Always analyse content before responding," the agent started routing
web-extraction tasks to `analyze_content` despite the unchanged descriptions. What is the
most likely cause and fix?

A. The tool descriptions have degraded over time and need to be rewritten
B. The system prompt's "analyse content" phrasing keyword-matches the `analyze_content` tool; rephrase it to remove the overlap
C. Rename `analyze_content` to something less generic, like `summarize_document`
D. Add few-shot examples to the system prompt showing when to use each tool

**Q3.** A tool called `analyze_content`, described as "Analyses content from various
sources," is used indiscriminately for web scraping, document parsing, and code analysis,
leading to poor results for each use case. What is the most effective fix?

A. Improve the description to list all supported content types and formats
B. Implement a routing layer inside `analyze_content` that dispatches by content type
C. Add few-shot examples showing which content types it handles well
D. Split `analyze_content` into purpose-specific tools: `extract_web_results`, `parse_document`, `analyze_code`

**Q4.** Tools `search_knowledge_base` ("Searches help articles") and `process_action`
("Handles customer actions like refunds and plan changes") keep cross-routing on
cancellation queries: the agent picks `search_knowledge_base` for "cancel my
subscription," and after "subscription cancellations" was added to `process_action`'s
description, it started picking `process_action` for pure knowledge queries like "how
does cancellation work?" What is the most effective solution?

A. Remove the word "cancellation" from both tool descriptions entirely
B. Add boundary descriptions to both tools that separate *executing* a cancellation from *learning how* cancellation works
C. Consolidate both tools into one that determines the correct action based on intent
D. Add few-shot examples showing five cancellation scenarios with the correct tool for each

**Q5.** A `query_snowflake` tool's description reads only "Queries Snowflake data
warehouse. Accepts SQL." The agent correctly uses the tool but frequently sends
PostgreSQL-specific syntax (e.g. `string_agg`, which Snowflake spells `LISTAGG`) that
Snowflake rejects. What is the most effective fix?

A. Add a system prompt instruction listing all Snowflake-specific SQL functions
B. Add a SQL syntax validation layer in front of the MCP tool
C. Have the MCP server automatically translate PostgreSQL syntax to Snowflake syntax
D. State in the tool description that it expects the Snowflake SQL dialect, not PostgreSQL, with example functions

### T.S. 2.2 — Structured error responses for MCP tools

**Q6.** A research agent calls an external API via an MCP server. After the 30th query in
a batch of 50, the API starts returning HTTP 429 errors. The MCP server returns a generic
"Request failed" for every failure, so the agent abandons the batch after three
consecutive failures. What MCP server change would most improve resilience?

A. Implement automatic retry with exponential backoff inside the MCP server, hiding rate limits from the agent entirely
B. Return `errorCategory: "business", isRetryable: false` to tell the agent to stop
C. Return `errorCategory: "transient", isRetryable: true`, with a `retryAfterMs` field
D. Queue all 50 requests server-side and process them sequentially with built-in rate limiting

### T.S. 2.3 — Distributing tools across agents and configuring tool choice

**Q7.** A web search agent has 9 tools: `web_search`, `url_fetch`, `html_parse`,
`pdf_extract`, `image_ocr`, `translate`, `summarise`, `keyword_extract`,
`sentiment_analysis`. In testing it frequently calls `summarise` and `sentiment_analysis`
when it should only fetch raw data. How should this be fixed?

A. Merge the web search and synthesis agents into one
B. Keep all 9 tools but add `PreToolUse` hooks blocking `summarise`/`sentiment_analysis`
C. Reduce the web search agent to the 4-5 data-fetching tools and move the analysis tools to specialist agents
D. Add system prompt instructions to ignore the analysis tools

**Q8.** A synthesis agent frequently returns control to the coordinator for simple fact
verification, adding 2-3 round trips per task and 40% latency. 85% of verifications are
simple lookups. What is the most effective solution?

A. Add a coordinator-level cache of verification results
B. Remove fact verification from the synthesis workflow altogether
C. Increase the coordinator's parallelism to absorb the round trips
D. Give the synthesis agent a scoped `verify_fact` tool for simple lookups, escalating only complex checks to the coordinator

**Q9.** A team's agent must generate a weekly report on the first turn of every
conversation by calling `generate_report`. With `tool_choice: "auto"`, it sometimes
responds with text instead. The team wants to guarantee `generate_report` is called on
turn one while allowing normal tool selection afterward. What is the correct
configuration?

A. Set `tool_choice` to `"any"` on every turn
B. Remove all tools except `generate_report` from turn one, add the rest afterward
C. Add a system prompt instruction "Always call `generate_report` on the first turn," leave `tool_choice` on `"auto"`
D. Force selection of `generate_report` for the first turn, then switch to `"auto"` for subsequent turns

**Q10.** A documentation agent must always call `extract_metadata` before generating
documentation, but in testing it sometimes skips that step. What is the correct
`tool_choice` configuration to enforce the mandatory first step?

A. Force selection of `extract_metadata` for the first turn, then switch to `"auto"` for subsequent turns
B. Remove all other tools except `extract_metadata` entirely
C. Set `tool_choice` to `"any"` and rely on the description to guide it there first
D. Set `tool_choice` to `"auto"` and add a system prompt instruction requiring it

### T.S. 2.4 — Integrating MCP servers into Claude Code and agent workflows

**Q11.** A team needs to integrate with Jira for issue tracking. A developer proposes
building a custom MCP server. What is the correct first step?

A. Build a custom MCP server with the exact endpoints the team needs
B. Use the Jira REST API directly from Bash commands instead of MCP
C. Evaluate existing community MCP servers for Jira and only build custom if they can't handle team-specific workflows
D. Add the Jira integration to `~/.claude.json` so each developer configures it independently

**Q12.** A data-analysis agent connects to an MCP server exposing 40 database tables.
Before almost every query, it makes several exploratory calls to discover which tables
exist and what columns they hold, adding latency and token cost. What is the most
effective change?

A. Enlarge the agent's context window so discovery results persist across turns
B. Expose the table catalogue and column schemas as MCP resources for upfront visibility
C. Reduce the server to the five most frequently queried tables
D. Add a `describe_schema` tool and instruct the agent to call it before every query

**Q13.** An MCP server exposes a `query_database` tool for Snowflake with structured
results (column types, pagination). Agents ignore it and run SQL via the built-in `Bash`
tool against the Snowflake CLI instead, producing worse results. What is the most likely
cause and fix?

A. Disable the `Bash` tool entirely
B. Add a system prompt instruction telling the agent to always use `query_database`
C. The MCP server isn't connected — restart it and verify
D. Enhance the sparse description to spell out the tool's structured output and pagination advantages over `Bash`

### T.S. 2.5 — Built-in tools (Read, Write, Edit, Bash, Grep, Glob)

**Q14.** A developer needs to find all files that call a deprecated function
`processLegacyOrder()`, and for each caller file, check whether a corresponding test file
exists. Which tool sequence is correct?

A. Read every source file, then Read every test file
B. Glob for `*processLegacyOrder*` to find callers, then Grep for matching test files
C. Grep for `processLegacyOrder` to find callers, then Glob to match their test files by name
D. Bash with `find | xargs grep` for both

**Q15.** A developer needs to rename a variable from `userData` to `customerData` in one
file, where it appears 12 times. What is the most efficient approach?

A. Bash with `sed` for a global find-and-replace
B. Read the whole file, Write it back with all 12 changed by hand
C. Use Edit with `replace_all` set to `true`
D. Grep for the 12 occurrences, then call Edit 12 times with unique context

**Q16.** An engineering team needs to update all references to a renamed API endpoint
(`POST /api/v1/users/create` → `POST /api/v2/users`) across a 500,000-line codebase, and
doesn't yet know which files reference it. What is the correct tool sequence?

A. Bash with `sed` across all files in one command
B. Grep for the old endpoint to find every file, then Edit to replace in each match
C. Read the API router file and trace references by hand
D. Glob for `**/*.md`, Read each, Edit matches

**Q17.** An Edit fails to update a config value because the matched text appears in three
places in the file. What is the correct next step?

A. Grep to find which of the three occurrences is correct, then give Edit more surrounding context to make the match unique
B. Switch to Bash with `sed`, which handles multiple matches natively
C. Fall back to Read the full file, then Write the complete modified file
D. Use Glob to find all files containing the value, and edit each one individually

**Q18.** Investigating a data inconsistency, a developer needs to find all files that
reference a Snowflake table `fact_revenue_daily`, then check the directory structure for
related migration files. Which tool sequence is correct?

A. Read all SQL files to search for the table name, then Read all migration files
B. Grep for `fact_revenue_daily` to find all content references, then Glob for `**/migrations/*.sql` to find migration files by path pattern
C. Glob for `**/*fact_revenue_daily*` to find references, then Glob for `**/migrations/**`
D. Grep for `fact_revenue_daily` for both steps

**Free-recall drills (T.S. 2.5)** — write the tool sequence and reasoning yourself before
checking the answer key.

**S1.** Find every place the function `sendWelcomeEmail()` is called, and for each caller
file, check whether a corresponding test file exists.

**S2.** A config file has the string `"env": "staging"` appearing once. Change it to
`"env": "production"`.

**S3.** The same config file has `timeout: 30` appearing in 5 different service blocks,
and you want all 5 changed to `timeout: 60` — same value, same reason, no exceptions.

**S4.** You try to Edit a line containing `port: 8080` to `port: 9090`, but it fails —
that exact string appears in 4 places in the file, each in a different service block with
genuinely different surrounding context available.

<details><summary>Answer key — Domain 2</summary>

**Q1 — C.** The overlap is between instruction *phrasing* and the tool *name* — rewrite
the wording, not the description (D targets the wrong side of the mismatch).

**Q2 — B.** Same failure mode as Q1, but the overlap originates in the system prompt, not
the tool description — the fix is symmetrical: reword the instruction.

**Q3 — D.** Split an overly generic tool into purpose-specific ones with defined
contracts, rather than trying to patch one tool's description to cover three unrelated
use cases.

**Q4 — B.** Boundary descriptions resolve ambiguity by *intent* (executing vs. learning
about); removing the shared keyword (A) makes both tools *less* discoverable for the
queries that need them.

**Q5 — D.** The description never named a SQL dialect, so the model defaulted to the more
common one (Postgres). Naming the dialect fixes the misrouting at its source, cheaper
than a validation layer or auto-translation.

**Q6 — C.** A 429 is a textbook transient, retryable error — the fix is specific,
structured metadata (`errorCategory`, `isRetryable`, `retryAfterMs`), not a generic
failure message or hiding the problem via automatic retry inside the server.

**Q7 — C.** Scope the agent down to its core 4-5 tools; agents given tools outside their
specialization tend to misuse them.

**Q8 — D.** A narrow, high-frequency, scoped tool for the 85% common case, escalating only
the remaining complex cases — not full access, not removing verification altogether.

**Q9 — D.** Force the specific tool on turn one, then release to `"auto"` — guarantees
the mandatory step without permanently restricting tool choice.

**Q10 — A.** Same pattern as Q9.

**Q11 — C.** Evaluate existing community servers before building custom — reserve custom
servers for genuinely team-specific workflows.

**Q12 — B.** MCP resources expose a content catalogue so the agent has visibility
up front, without burning exploratory tool calls to discover it.

**Q13 — D.** A sparse MCP description makes the agent default to a more "familiar"
built-in tool; enhancing the description (not disabling `Bash` or troubleshooting the
connection) is the direct fix.

**Q14 — C.** Grep (content search) to find callers by function name, then Glob (path
pattern) to find their test files by naming convention — not the reverse, since you can't
Glob by name for something you haven't identified via content search yet.

**Q15 — C.** `Edit` with `replace_all: true` is the built-in, purpose-fit mechanism for
"every occurrence, same reason" — `sed` (A) bypasses the reviewable, structured tool call
this task statement is testing.

**Q16 — B.** Grep to find every file with the old string, then Edit each match — you
don't know which files are involved ahead of time, so start with content search.

**Q17 — A.** Widen the anchor with distinguishing surrounding context first; Read+Write
(C) is the fallback only when widening truly cannot disambiguate.

**Q18 — B.** Grep for content (you're searching for references *in* code), Glob for path
pattern (migration files identified by directory, not by containing the table name).

**S1.** Grep for `sendWelcomeEmail` (content search) to find callers, then Glob for each
caller's likely test-file naming pattern. Grep-then-Glob, not the reverse.

**S2.** Plain `Edit`. Single, already-unique occurrence — no flags needed.

**S3.** `Edit` with `replace_all: true`, one call — same value changing for the same
reason, no distinguishing context needed between occurrences.

**S4.** NOT Read+Write. Widen the `old_string` anchor using the surrounding context that
differs for that one target block (service name, adjacent keys) so the match becomes
unique, then Edit normally. Read+Write is the last resort only when no amount of added
context can disambiguate — that's not the case here.

</details>

---

## Domain 3 — Claude Code Configuration & Workflows

### T.S. 3.1 — CLAUDE.md hierarchy, scoping, and modular organization

**Q1.** A project's `.claude/CLAUDE.md` says "use 4-space indentation matching the
existing codebase." A senior architect's user-level `~/.claude/CLAUDE.md` says "use
2-space indentation." The architect's code keeps coming back in 2 spaces and breaking the
build. The team needs a guarantee that 4-space indentation is applied on every save. What
should they do?

A. Add a `PostToolUse` hook that runs the team's formatter after every Write/Edit
B. Leave the rule in project-level `CLAUDE.md` — the more specific scope wins on conflicts
C. Move the rule into a `CLAUDE.local.md` at the project root so it's appended last
D. Ask the architect to delete their user-level `CLAUDE.md`

**Q2.** A Java naming convention (`com.company.service.<service-name>`) must be applied on
every run. Subagents sometimes use inconsistent package names instead. A team member
proposes adding stronger instructions to the system prompt. Reviewers have already caught
Claude following a developer's personal preference over the team rule in a similar case.
What is the correct approach?

A. Create a separate validation subagent that reviews all written files for naming compliance after each batch
B. Implement a `PostToolUse` hook that inspects written files and normalizes any package declarations to the correct format
C. Add the naming convention to the system prompt with three concrete examples
D. Use `tool_choice` to restrict the agent to a custom `write_java_file` tool that enforces the convention

**Q3.** A consultancy works across 12 client projects simultaneously. Each developer has
personal preferences; the firm has firm-wide coding standards; each client project has its
own conventions; some client projects have subsystems with additional specialized rules.
What is the correct configuration architecture?

A. User `~/.claude/CLAUDE.md` for personal preferences and firm-wide standards; project `.claude/CLAUDE.md` for client-specific conventions; directory-level `CLAUDE.md` or `.claude/rules/` with `paths` for subsystem rules
B. User `~/.claude/CLAUDE.md` for everything; use `@import` to pull in project-specific files
C. A single `CLAUDE.md` at the root of each project containing all four levels, with clear section headings
D. User `~/.claude/CLAUDE.md` for personal preferences only; project `.claude/CLAUDE.md` for firm-wide standards and client conventions; directory-level rules for subsystems

**Q4.** A team wants to archive the full conversation transcript to a log file every time
`/compact` runs. Which Claude Code hook should they use, and why?

<details><summary>Answer</summary>
A <b>PreCompact</b> hook — it's a dedicated Claude Code lifecycle hook that fires
immediately before <code>/compact</code> summarizes the conversation, and receives the
pre-compaction transcript so it can be archived before the detail is lost. The common
wrong instinct is to look for a <code>PreToolUse</code> hook on a "Compact tool" — but
compaction is a lifecycle event, not a model-invoked tool, so <code>PreToolUse</code>
can't intercept it.
</details>

### T.S. 3.2 — Custom slash commands and skills

**Q5.** A team creates a reusable `/extract-service` skill that guides Claude Code through
the standard steps of extracting a module into a microservice. Where should this skill be
stored so every team member who clones the repository has access?

A. In `~/.claude/skills/` on each developer's machine, distributed via the team wiki
B. In the repository's `.claude/skills/` directory, committed to version control
C. In the repository-root `CLAUDE.md` as an inline procedure
D. In a shared MCP server that all team members connect to

### T.S. 3.3 — Path-specific rules for conditional convention loading

**Q6.** A polyglot codebase has Terraform files in `terraform/`, Kubernetes manifests in
`k8s/`, and Dockerfiles scattered throughout service directories. The team wants
Claude Code to automatically apply infrastructure-specific conventions per file type,
without loading all conventions for every session. What is the correct approach?

A. Create three path-scoped `.claude/rules/` files (`terraform.md`, `kubernetes.md`, `docker.md`), each targeting its own file types
B. Create three directory-level `CLAUDE.md` files, one per directory
C. Add all infrastructure conventions to the root `CLAUDE.md` with clear section headings
D. Create a single `.claude/rules/infrastructure.md` with `paths: ["**/*"]` containing everything

**Q7.** A codebase has test files co-located with source files throughout 50+ directories
(e.g. `Button.test.tsx` next to `Button.tsx`). The team wants all tests to follow the same
conventions regardless of location. What is the most maintainable approach?

A. A `.claude/rules/` file with frontmatter `paths: ["**/*.test.tsx", "**/*.test.ts"]` holding the test conventions
B. Add all test conventions to the root `CLAUDE.md`
C. Create a skill in `.claude/skills/` with a `paths` frontmatter matching test files, auto-activating on edit
D. Place a copy of `CLAUDE.md` in every one of the 50+ directories

### T.S. 3.4 — Plan mode vs. direct execution

**Q8.** A developer extracting a notification subsystem faces 12 cross-module
dependencies, 3 messaging patterns, and several valid extraction strategies. They start in
direct execution mode. After moving 8 files, the chosen approach breaks a circular
dependency with the user-profile module. What should they have done differently?

A. Delegated the entire extraction to a subagent to isolate the risk
B. Used direct execution but with more detailed upfront instructions
C. Used plan mode to map the 12 dependencies and evaluate extraction strategies before committing
D. Used direct execution but processed only 2 files at a time

**Q9.** A developer wants to explore logs, trace request flows, and form hypotheses about
a distributed system bug without making any changes. Partway through, they identify a
one-line config fix and want to apply it immediately. What is the optimal workflow?

A. Use plan mode for the entire session, including the one-line fix
B. Start in plan mode for investigation, then switch to direct execution for the one-line fix once identified
C. Use `allowedTools` restricted to read-only for investigation, then start a new session with write permissions
D. Use direct execution throughout, with detailed upfront instructions covering both investigation and potential fixes

### T.S. 3.5 — Iterative refinement techniques

**Q10.** A developer is new to a healthcare compliance domain and needs to build an audit
logging system. They understand the technical implementation options but are unsure about
regulatory requirements that might affect the design. Which technique is most
appropriate?

A. Start with direct execution using a simple implementation, iterate on test failures
B. Use plan mode to have Claude explore the codebase and propose multiple architectures
C. Provide concrete input/output examples of the desired audit log format
D. Use the interview pattern so Claude asks clarifying questions about compliance requirements, retention policies, and access control before proposing a design

**Q11.** A code review prompt classifies severity using prose descriptions like "critical
means the code is dangerous" and "minor means the code is slightly suboptimal."
Developers report identical code patterns receive different severity ratings across
runs. What is the most effective improvement?

A. Add a confidence threshold so only findings above 90% confidence are reported
B. Replace prose severity descriptions with concrete code examples for each severity level
C. Lower the model temperature to 0
D. Add a second model pass that re-evaluates each finding's severity

### T.S. 3.6 — Integrating Claude Code into CI/CD pipelines

**Q12.** A CI pipeline needs to run Claude Code for both PR review (structured JSON output
for a dashboard) and test generation (standard text output). How should the two steps be
configured?

A. Run both steps with `-p` and have the dashboard parse plain text from both
B. Run the review step with `-p --output-format json`, and the test generation step with `-p` only, as separate non-interactive invocations
C. Run both steps with `--output-format json` and have test generation extract code from the JSON
D. Run both in a single session with `-p`, using different prompts

**Q13.** A 3-step CI pipeline (generate a changelog → review it for accuracy → check for
breaking changes) never catches inaccuracies in step 2, and step 3 misses breaking
changes the changelog omits. What is the root cause?

A. The `-p` flag isn't being used, so each step waits for interactive input
B. The steps need `--output-format json` so each can parse the prior step's output
C. `CLAUDE.md` doesn't contain changelog formatting standards
D. The three steps share session context, so steps 2 and 3 inherit step 1's reasoning instead of judging the changelog independently

**Q14.** A team wants three Claude Code instances working in parallel — one extracting the
authentication service, one extracting the billing service, one updating shared libraries
— all committing to the same repository without conflicts. What is the correct setup?

A. Run all three in the same working directory on separate branches, switching as needed
B. Use `git worktree` to create three separate working directories, each on its own branch, one Claude Code instance per worktree
C. Use `fork_session` to run the three tasks as parallel branches within a single session
D. Clone the repository three times into separate directories and merge manually

**Q15.** Two Claude Code instances in separate git worktrees both need to modify a shared
`OrderService.java` (Instance A extracting payment logic, Instance B extracting inventory
logic). How should the team coordinate this?

A. Instance A completes and merges first; Instance B then rebases onto the updated main before modifying the shared file
B. Use file locking via git to prevent simultaneous modification
C. Let both modify independently and resolve the merge conflict when merging to main
D. Create a third instance dedicated only to modifying shared files

**Q16.** A team asks the same Claude session to critique its own generated code
immediately after generation, in the same conversation. Reviews are overly favourable and
miss bugs an external reviewer would catch. What is the root cause and fix?

A. Lower the temperature during the review phase
B. Enable extended thinking so the model reasons more carefully
C. Route the review to a separate Claude instance with no access to the generation conversation
D. Add a comprehensive review checklist to the prompt

<details><summary>Answer key — Domain 3</summary>

**Q1 — A.** `CLAUDE.md` files are *concatenated* into context, not merged by
specificity-wins-conflicts — conflicting rules can be picked arbitrarily. A `PostToolUse`
hook applies deterministically regardless of what the model decides, which is the actual
guarantee the team needs.

**Q2 — B.** Same principle: a hook that runs after every write and normalizes the output
gives a hard guarantee; a system prompt instruction (C) is exactly the mechanism that
already failed once.

**Q3 — A.** User-level for what's genuinely personal-and-firm-wide (this consultant's
personal prefs *and* the standards they carry to every client); project-level for
*client*-specific; directory/rules for subsystem-specific. (D misassigns firm-wide
standards to project-level, which would require duplicating them into every client repo.)

**Q4 — PreCompact** hook (see inline answer above).

**Q5 — B.** Project-scoped `.claude/skills/`, version-controlled — the only option that's
automatically available to every clone with no manual distribution step.

**Q6 — A.** Path-scoped rules load only for matching files, giving per-type conventions
without loading all of them every session — directory-level `CLAUDE.md` (B) doesn't fit
when Dockerfiles are scattered rather than confined to one directory.

**Q7 — A.** Glob-pattern rules beat directory-level `CLAUDE.md` specifically when a
convention spans files scattered by *type* across the tree, not gathered by location.

**Q8 — C.** 12 dependencies, multiple valid strategies, and a real unresolved choice is
the textbook plan-mode case — direct execution (regardless of instruction detail or batch
size) can't discover an unknown circular dependency ahead of time.

**Q9 — B.** Combine modes: plan mode for genuine investigation, direct execution once the
fix is simple and identified — this is the correct middle path, not "one mode for
everything."

**Q10 — D.** The interview pattern surfaces considerations (regulatory requirements) the
developer doesn't know to specify up front — concrete I/O examples (C) don't help when the
developer doesn't yet know what the correct output should be.

**Q11 — B.** Concrete examples per severity level fix inconsistent classification; prose
descriptions ("dangerous," "suboptimal") are exactly the ambiguity causing the drift.

**Q12 — B.** Match each step's flag to its own output-format need — one step doesn't need
JSON just because the other does.

**Q13 — D.** Shared session context means the "review" step inherits the generation step's
reasoning instead of judging independently — same underlying pattern as self-review bias
in T.S. 4.6, just across CI steps instead of within one turn.

**Q14 — B.** `git worktree` gives each instance its own working directory and branch,
eliminating file-system conflicts between parallel instances.

**Q15 — A.** Sequence modifications to a shared file: complete-and-merge, then
rebase-and-see-the-change, rather than resolving conflicts after the fact or inventing
locking mechanisms git doesn't have.

**Q16 — C.** Same-session self-review is fundamentally biased toward agreement because the
reviewing pass retains the generating pass's reasoning — an independent instance is the
only fix that addresses the actual mechanism.

</details>

---

## Domain 4 — Prompt Engineering & Structured Output

### T.S. 4.1 — Explicit criteria to reduce false positives

**Q1.** A specific finding category is producing too many false positives. What is the
recommended move?

A. Rewrite the entire prompt from scratch
B. Temporarily disable that category while its prompt gets fixed, rather than letting it keep eroding trust
C. Add a disclaimer telling users to double-check
D. Switch to a larger/more capable model

**Q2.** A CI/CD code review pipeline has a 40% false-positive rate on "documentation
mismatch" findings, causing developers to ignore *all* review categories. What is the most
effective fix?

A. Add a second model pass to verify each finding before reporting
B. Increase the model temperature for more varied results, filter outliers
C. Temporarily disable the documentation mismatch category while refining its prompt with explicit criteria and code examples
D. Add "only report high-confidence documentation issues" to the system prompt

**Q3.** A moderation prompt instructs Claude to "be conservative when moderating and err
on the side of caution." Reviewers find innocuous posts about cooking with knives, news
articles about violence, and fictional war stories are all being flagged as violations.
What is the root cause and fix?

A. The model is too sensitive — lower the temperature
B. Add a second moderation pass that re-reads flagged posts under the same "be conservative" guidance
C. Replace "be conservative" with explicit categorical criteria defining each violation category, with concrete examples
D. Add an allowlist of safe topics (cooking, news, fiction) that should never be flagged

### T.S. 4.2 — Few-shot prompting for consistency

**Q4.** Why pair acceptable-pattern examples against genuine-issue examples in a few-shot
prompt?

A. To increase the total example count for better averaging
B. To cut false positives without losing recall
C. To test the model's context window limits
D. To satisfy `tool_use` schema requirements

**Q5.** An agent generates unit tests in a CI pipeline with inconsistent assertion styles
(`expect().toBe()` vs. `assert.equal()`, sometimes mixed in the same file). Adding more
detailed instructions about assertion style did not fix it. What should be done next?

A. Switch to a different model that better follows formatting instructions
B. Add a linter post-processing step to convert all assertions to a single style
C. Add 2-4 few-shot examples demonstrating the desired assertion style with reasoning for each testing decision, covering edge cases
D. Add 2-4 few-shot examples showing complete test files with the desired assertion style and reasoning for *why that style was chosen over alternatives*

**Q6.** A moderation system classifies explicit slurs accurately but misses coded language
and dog-whistle terms that human moderators easily recognise, despite detailed written
rules about coded-language patterns in the prompt. What intervention would most improve
detection?

A. Add 2-4 few-shot examples of coded hate speech, with reasoning naming the coded language and the targeted group
B. Add 20+ examples covering every known category of coded hate speech
C. Add a comprehensive dictionary of every known coded term to the system prompt
D. Increase the model's context window to consider more post history

### T.S. 4.3 — Structured output via tool use and JSON schemas

**Q7.** Why does `tool_use` with a JSON schema eliminate output errors that plague
plain-text JSON generation?

A. It eliminates both syntax and semantic errors — the model can no longer misplace a value in the wrong field
B. It only eliminates syntax errors; semantic errors (like line items not summing to the stated total) are still possible
C. It eliminates semantic errors but not syntax errors
D. It has no effect on error rates — it only changes response format

**Q8.** A classification schema's `category` field is free-text. Auditors find 47
different values intended to be the same category (`"hate speech"`, `"Hate Speech"`,
`"hate-speech"`, `"hateful content"`, `"hate_speech"`). What is the best schema fix?

A. Add a post-processing normalization step mapping all variations to canonical names
B. Add few-shot examples showing the correct category formatting
C. Add detailed prompt instructions listing the exact category names and capitalization
D. Change `category` from free-text to an enum with values like `hate_speech`, `spam`, `harassment`, plus an `other` option

**Q9.** A 15-required-field extraction schema is used across varied document types; for
some types, only 8 of the 15 fields ever actually appear, and the model fabricates the
other 7 despite explicit "do not fabricate" instructions. What is the fix?

A. Make the 7 sometimes-absent fields optional (nullable) in a single schema
B. Create separate schemas per document type

### T.S. 4.4 — Validation, retry, and feedback loops

**Q10.** A moderation system validates that every classification includes a non-empty
`reasoning` field, retrying on failure. Retries succeed for most posts but consistently
fail for posts in unfamiliar languages. What should the system do?

A. Retry format errors on analysable posts; route capability gaps like unfamiliar languages to human review
B. Remove the reasoning validation requirement for unfamiliar-language posts
C. Increase the retry count from 1 to 5 for unfamiliar-language posts
D. Add the unfamiliar language to the system prompt as "supported" to encourage the model to try harder

**Q11.** A classification tool includes a `detected_patterns` array where the model lists
specific patterns it identified. Validation checks whether the patterns match the assigned
category, and on mismatch retries with feedback like "you classified this as spam but
detected patterns of hate speech, please re-evaluate." What is the primary benefit of the
`detected_patterns` field here?

A. It provides an auditable evidence trail of which content features drove the decision
B. It lets the system auto-correct the category by overriding the model's classification with a rule-based match
C. It increases accuracy by forcing the model to identify patterns before assigning a category
D. It lets validation detect reasoning inconsistencies and feed back targeted errors the model uses to self-correct

### T.S. 4.5 — Efficient batch processing strategies

**Q12.** A pipeline must extract data from 2,000 contracts. For each, the model has to
call an internal `lookup_counterparty` tool mid-extraction and use the result to finish.
The team wants the Batch API's 50% savings. What should they do?

A. Submit to the Batch API and poll each individual request until its pending tool call resolves
B. Submit the whole workflow to the Batch API, since batch requests support the same tool-calling loop as synchronous requests
C. Run the tool-calling extraction synchronously, because a batch request cannot continue from a tool result
D. Split each contract across two batches, feeding the first batch's output in as the second batch's tool result

**Q13.** A manager proposes switching both a blocking pre-merge code review and an
overnight technical debt report to the Message Batches API for 50% cost savings. How
should this be evaluated?

A. Switch both to batch with a timeout fallback to real-time if batches take too long
B. Use batch processing for the technical debt reports only; keep real-time calls for pre-merge checks
C. Switch both to batch processing with status polling
D. Keep real-time calls for both to avoid batch result ordering issues

**Q14.** A CI/CD nightly security-audit pipeline uses the Message Batches API. A batch of
200 documents completes overnight, but 15 fail because they exceeded the context window.
The team proposes resubmitting the entire batch of 200. What is the correct failure
handling strategy?

A. Increase the batch processing timeout
B. Switch the entire pipeline to synchronous processing
C. Resubmit the entire batch since you can't identify which documents failed
D. Resubmit only the 15 failed documents identified by `custom_id`, chunking the oversized documents first

**Q15.** After a code-review batch completes, a team needs to match each review result
back to the corresponding pull request. What is the correct correlation mechanism?

A. Submit each PR as a separate batch of one item to preserve correlation via batch ID
B. Parse review content to identify which PR it refers to based on filenames mentioned
C. Use the `custom_id` field in each batch request to store the PR identifier, then match results by `custom_id`
D. Rely on the batch API returning results in the same order they were submitted

### T.S. 4.6 — Multi-instance and multi-pass review architectures

**Q16.** A code review agent processes 14 files, producing detailed feedback for the first
5 but missing obvious bugs in files 10-14. It also flags a pattern as problematic in one
file while approving identical code in another. What is the root cause and solution?

A. The model's context window is too small — upgrade to a model with a larger window
B. Add a stronger system prompt emphasizing reviewing all files equally
C. Split the review into per-file local analysis passes plus a separate cross-file integration pass
D. Reduce the number of files reviewed per run to 5 and process in batches

**Q17.** A single Claude session classifies a post, then is immediately asked to review
its own classification for quality assurance, in the same session. The "review" agrees
with the original 98% of the time, including cases human auditors later identify as
errors. Why is this self-review ineffective?

A. Self-review is effective; the 98% agreement rate simply reflects high initial accuracy
B. The model needs a stronger review prompt with explicit instructions to look for errors
C. The model's temperature is too low, producing deterministic agreement — increase it for the review pass
D. The same session retains the model's reasoning, so it stays anchored to its own classification; use a fresh, independent instance to review

<details><summary>Answer key — Domain 4</summary>

**Q1 — B.** Disable the noisy category while its prompt gets fixed — a full rewrite risks
breaking categories that already work.

**Q2 — C.** Same pattern as Q1, with the added detail: explicit criteria + concrete
examples are the actual fix mechanism, not just "disable and hope."

**Q3 — C.** Vague hedge language ("be conservative") gives the model nothing concrete to
check against; explicit criteria with examples of both violations *and* legitimate content
is what actually calibrates the decision.

**Q4 — B.** Pairing acceptable-vs-genuine examples teaches the *boundary* between them,
cutting false positives on the acceptable pattern without losing recall on real issues.

**Q5 — D.** The tested distinction is "reasoning for choosing one option over a plausible
alternative" (D) vs. "reasoning for each individual decision" (C, similar-sounding but
weaker framing) — few-shot examples' real value is demonstrating *why* over a competing
option, which generalizes to novel cases.

**Q6 — A.** A small number of examples with reasoning teaches the *pattern-recognition
process*, letting the model generalize to coded terms it hasn't seen — a static dictionary
(C) or example flood (B) doesn't generalize the same way.

**Q7 — B.** `tool_use` guarantees schema-valid *shape*, not correct *values* — a
structurally valid response can still contain a wrong number in the right-shaped field.

**Q8 — D.** Enum fields (with `strict: true`) constrain the model to predefined values,
eliminating spelling/formatting variance at the schema level — deterministic, unlike
prompt instructions or few-shot examples.

**Q9 — A.** Nullable/optional fields remove the schema-level pressure to fabricate a value
just to satisfy a `required` constraint when the source document legitimately lacks it.

**Q10 — A.** Retry-with-feedback fixes *format* problems; it cannot fix a genuine
*capability gap* (the model doesn't understand the language) — route that to human review
instead of retrying indefinitely.

**Q11 — D.** The field's core purpose here is enabling programmatic detection of
reasoning-vs-conclusion mismatches, feeding back a targeted, actionable error — auditability
(A) is a secondary benefit, not the primary one in this validation/retry framing.

**Q12 — C.** The Batch API doesn't support mid-request tool-calling loops — a workflow
that needs a tool result to continue can't run in a single batch request.

**Q13 — B.** Match API choice to latency tolerance per workflow — batch (no SLA, up to
24h) fits the overnight report; it does not fit a blocking pre-merge check.

**Q14 — D.** Resubmit only the failed `custom_id`s, with the specific fix needed (chunking
oversized documents) — resubmitting all 200 wastes the 185 that already succeeded.

**Q15 — C.** `custom_id` is the purpose-built correlation mechanism; response order is not
guaranteed to match submission order.

**Q16 — C.** Split into per-file passes plus a cross-file integration pass — this is
attention dilution across a single long pass, not a context-window-size problem, and
shrinking the batch (D) just moves the symptom rather than fixing it.

**Q17 — D.** The reviewing pass retains the generating pass's reasoning in the same
session and stays anchored to it — an independent instance with no access to that
reasoning is the only fix that addresses the actual mechanism (temperature and stronger
prompts don't touch it).

</details>

---

## Domain 5 — Context Management & Reliability

### T.S. 5.1 — Managing conversation context across long interactions

**Q1.** A multi-agent research workflow runs 45 minutes. Around the 30-minute mark, the
coordinator's synthesis quality drops: it refers to "the key findings" instead of specific
statistics it cited earlier, and misattributes a claim between subagents. No token limits
or errors have been hit. What is the diagnosis and mitigation?

A. The token limit has been silently exceeded and the API is truncating early messages — upgrade to a larger context window
B. The model is experiencing "fatigue" from a long session and needs a cooldown period
C. Subagents are returning inconsistent data, confusing the coordinator — add data validation to subagent output
D. Context degradation: early results are buried deep in a long context — consolidate key findings into a structured block near the end

**Q2.** An agent receives 200 rows of financial data placed mid-prompt, between system
instructions and the user's follow-up question. Asked to identify the row with the
highest margin, it picks the 45th row (32%) over the 142nd row (47%). What is happening?

A. Anchoring bias — the agent fixates on the first high-margin row and stops scanning
B. The lost-in-the-middle effect: the agent favours the start and end of the context, missing the row buried in the middle
C. Recency bias — the agent prioritizes data near the end of the context window
D. Token limit truncation — rows beyond the 100th are silently dropped

**Q3.** An agent joins data via federated queries and progressively summarizes earlier
results between rounds to manage context. After three rounds, it reports "revenue
increased in Q3" but cannot give the exact figure ($14.2M), which was lost in
summarization. What is the most effective fix?

A. Increase the context window size so summarization triggers less often
B. Extract key numerical facts into a persistent facts block, kept outside the summarized history
C. Re-run the original query to retrieve the exact figure
D. Instruct the agent to always include exact figures in its summaries

**Q4.** An agent has a 200k-token budget: system prompt 8k, conversation history 120k,
most recent tool result 65k. It's struggling to produce thorough responses. What is the
cause and fix?

A. It needs a higher `max_tokens` parameter for longer responses
B. Input already consumes 193k of the 200k budget — summarize history or trim verbose tool results
C. The 8k system prompt is too large and should be cut to under 2k
D. Clear conversation history entirely for a fresh context each response

### T.S. 5.2 — Escalation and ambiguity resolution

**Q5.** A customer says: "This is ridiculous, I have been waiting 20 minutes. Just connect
me to a real person." The agent can see the issue is a simple password reset (30 seconds).
What should the agent do?

A. Ask whether the customer prefers to wait for a human or let the agent resolve it quickly
B. Escalate to a human immediately without attempting resolution, because the customer explicitly requested a human
C. Run sentiment analysis to confirm genuine frustration before deciding
D. Acknowledge the frustration and offer to resolve the password reset quickly, since the issue is straightforward

### T.S. 5.3 — Error propagation across multi-agent systems

**Q6.** A web search subagent times out researching a complex topic. What approach to
propagating this failure back to the coordinator best enables intelligent recovery?

A. Catch the timeout and return an empty result set marked as successful
B. Propagate the exception to a top-level handler that terminates the entire workflow
C. Return structured error context: failure type, attempted query, partial results, and potential alternative approaches
D. Retry automatically with exponential backoff, returning a generic "search unavailable" status only after retries are exhausted

**Q7.** An academic-database subagent hits a 403 Forbidden on a specific journal, catches
the error, and returns an empty result set marked as successful. The coordinator produces
a final report with no academic sources. What is the critical failure here?

A. The subagent silently suppressed an access failure by returning empty results as success, preventing the coordinator from recovering or noting the coverage gap
B. The subagent should have retried with exponential backoff, since 403s are often transient
C. The entire workflow should have terminated when the subagent hit the 403
D. The coordinator should validate that all subagents return non-empty results before producing the final report

**Q8.** A subagent queries an academic database and gets zero matching articles (a
successful query, no results); simultaneously, a second subagent querying a different API
gets a connection timeout. The coordinator currently handles both identically, retrying
3x. What should change?

A. Remove retries entirely and escalate both immediately to a human
B. Add exponential backoff to all retries
C. Distinguish access failures from valid empty results: retry the timeout as transient, accept the zero-match response as a valid finding and annotate the coverage gap
D. Increase the retry count to five for both cases

### T.S. 5.4 — Managing context in large codebase exploration

**Q9.** A coordinator spawns four subagents to explore a large codebase overnight (data
layer, API routes, tests, dependencies). Three hours in, the machine restarts, and on
rerun the coordinator starts every exploration again from zero. What design change lets a
restarted run continue from where the crash left off?

A. Run the four explorations sequentially in one session so findings stay in a single context
B. Have each agent export structured state to a manifest the coordinator loads on resume
C. Wrap each subagent in automatic retries so transient failures cannot end the run
D. Resume the coordinator's previous session so the conversation history is restored

### T.S. 5.5 — Human review workflows and confidence calibration

**Q10.** A contract extraction system reports 96% overall accuracy; the team plans to
auto-approve extractions above 90% model confidence. A pilot reveals party-name extraction
at 99% accuracy but indemnification-clause extraction at only 71%, even though the model
reports high confidence on both. What should they implement before automating?

A. Raise the automation confidence threshold from 90% to 99%
B. Train a separate classification model to predict extraction accuracy
C. Exclude indemnification clauses from automation entirely; keep automating other fields at 90%
D. Calibrate confidence thresholds per field type using labelled validation sets, and implement stratified sampling to continuously monitor accuracy by document type and field segment

**Q11.** Reviewers sample 50 reports and find an overall accuracy rate of 97%; management
approves the system for production. Three weeks later, users report that a specific
calculation type is wrong 40% of the time. How did the review process fail?

A. The sample size of 50 was too small to detect a 40% error rate
B. The reviewers weren't domain experts in the failing calculation type
C. The agent's accuracy degraded over time due to model drift
D. The reviewers used aggregate accuracy metrics that masked a category-specific failure rate

### T.S. 5.6 — Provenance and uncertainty in multi-source synthesis

**Q12.** Three subagents (financial filings, news, technical white papers) each return
properly attributed findings, but the final synthesized report has no source attribution
— stakeholders can't trace which claim came from which source. Which fix addresses the
root cause?

A. Store all subagent outputs in a database; have synthesis reference entries by ID
B. Require subagents to output structured claim-source mappings, and instruct the synthesis agent to preserve and merge them
C. Have subagents include source URLs as inline hyperlinks in prose output
D. Append a bibliography section at the end listing all sources each subagent consulted

**Q13.** A synthesis agent receives conflicting growth-rate statistics from two credible
sources (12% growth, 2023 data, vs. 8% growth, 2024 data) and currently just selects the
more recent value. What is the correct approach?

A. Average the two values and report 10%, noting the variance
B. Annotate both values with source and publication dates, letting the consumer interpret them
C. Flag the conflict and escalate to a human researcher before including it in the report
D. Always use the most recent source, on the grounds that it reflects the latest data

**Q14.** A synthesis agent must produce a recommendation for a medical advisory board on a
compound's efficacy. A 2022 peer-reviewed clinical trial reports 78% efficacy; a 2024
preprint (larger sample, not yet peer-reviewed) reports 45%. Which approach correctly
handles the conflicting sources?

A. Average the two values (61.5%) and present it as the best estimate, noting variance
B. Present both findings with full provenance — source identity, publication date, peer-review status, sample size, methodology, and any differences that may explain the discrepancy — and let the advisory board weigh the evidence
C. Use the 2024 preprint since it has a larger sample and is more recent, noting it supersedes the 2022 study
D. Exclude both findings and report that no reliable consensus exists

<details><summary>Answer key — Domain 5</summary>

**Q1 — D.** Consolidating key findings into a structured block near the end counters the
lost-in-the-middle effect that's degrading synthesis quality — no token limit or error was
actually hit, ruling out A.

**Q2 — B.** Lost-in-the-middle: strong attention at start/end, weak in the middle — the
model found row 45 (early) but missed row 142 (deep middle), which rules out recency bias
(C, which would favor the *end*) and truncation (D, which would make row 142 invisible
entirely rather than merely overlooked).

**Q3 — B.** A persistent facts block *outside* the summarized history preserves exact
numbers across summarization rounds — a larger window (A) only delays the same failure.

**Q4 — B.** The budget math: 8k + 120k + 65k = 193k of 200k already consumed by input,
leaving almost nothing for the response — `max_tokens` (A) can't exceed the remaining
budget regardless of its setting.

**Q5 — B.** An explicit request for a human is one of the three valid, immediate
escalation triggers — the simplicity of the underlying issue is irrelevant to that
trigger.

**Q6 — C.** Structured error context (failure type + attempted query + partial results +
alternatives) is what lets the coordinator make an *intelligent* recovery decision, not
just detect that something failed.

**Q7 — A.** Silently converting an access failure into a "successful" empty result hides
the coverage gap from the coordinator entirely — the report reads as complete when it
isn't.

**Q8 — C.** Access failures (timeout) and valid empty results (zero matches, query
succeeded) are categorically different and need different handling — collapsing them into
one retry policy loses information the coordinator needs.

**Q9 — B.** Manifest-based state export per agent, loaded by the coordinator on resume, is
what enables actual crash recovery — resuming a session (D) restores conversation history,
not the underlying exploration state.

**Q10 — D.** Per-field calibration against labelled data, plus ongoing stratified sampling,
is the only option that fixes the underlying mechanism rather than patching the one field
that got caught (C) or adding unnecessary machinery (B).

**Q11 — D.** Aggregate accuracy averages over categories, hiding a bad-performing segment
behind good-performing ones — stratified sampling within each category is what would have
caught it; sample size (A) is not the actual problem if the sampling wasn't stratified in
the first place.

**Q12 — B.** Structured claim-source mappings, explicitly preserved and merged through
synthesis, are what keep attribution alive — free-form mechanisms (inline links, a
trailing bibliography) don't survive the synthesis step reliably.

**Q13 — B.** Present both values with full attribution and let the consumer interpret —
averaging (A) invents a number neither source reported; always-most-recent (D) is the
original flawed behavior being corrected.

**Q14 — B.** Full provenance for a high-stakes medical decision — the advisory board needs
peer-review status and methodology to weigh the evidence themselves; picking one value or
averaging removes information they need to make that judgment.

</details>
