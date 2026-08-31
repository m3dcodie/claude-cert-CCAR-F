Claude Certified Architect – Foundations
Exam Guide
Version 1.0 · Effective July 2026 · Exam code: CCAR-F


Claude Code, the Claude Agent SDK, the Claude API, and ModelContext Protocol (MCP),
building agentic systems for customer support, designing multi-agent research pipelines,integrating Claude Code into CI/CD workflows, building developer productivity tools, and extractingstructured data from unstructured documents. Candidates must demonstrate not only conceptualknowledge but practical judgment about architecture, configuration, and tradeoffs in productiondeployments.


Building agentic applications using the Claude Agent SDK, including multi-agent orchestration,subagent delegation, tool integration, and lifecycle hooks
•
Configuring and customizing Claude Code for team workflows using CLAUDE.md files, Agent Skills,MCP server integrations, and plan mode
•
Designing Model Context Protocol (MCP) tool and resource interfaces for backend systemintegration
•
Engineering prompts that produce reliable structured output, leveraging JSON schemas, few-shotexamples, and extraction patterns


Managing context windows effectively across long documents, multi-turn conversations, and multi-agent handoffs
•
Integrating Claude into CI/CD pipelines for automated code review, test generation, and pull requestfeedback
•
Making sound escalation and reliability decisions, including error handling, human-in-the-loopworkflows, and self-evaluation patterns

building with Claude APIs, Agent SDK,Claude Code, and MCP, understanding both the capabilities and limitations of large language models inproduction environments.


Domain   Content Domain    Weight  
1        Agentic Architecture & Orchestration 27%
2        Tool Design & MCP Integration 18%
3        Claude Code Configuration & Workflows 20%
4        Prompt Engineering & Structured Output 20%
5        Context Management & Reliability 15%
| Total  100%


Detailed Objectives by Domain
Each domain below lists the task statements tested, with the knowledge and skills measured againsteach. Exam items are written against these objectives.


are appended to conversation history so the model can reason about the nextaction
•
The distinction between model-driven decision-making (Claude reasons about which tool to callnext based on context) and pre-configured decision trees or tool sequences
Skills in:
•
Implementing agentic loop control flow that continues when stop_reason is "tool_use" andterminates when stop_reason is "end_turn"
•
Adding tool results to conversation context between iterations so the model can incorporate newinformation into its reasoning
•
Avoiding anti-patterns such as parsing natural language signals to determine loop termination,setting arbitrary iteration caps as the primary stopping mechanism, or checking for assistant textcontent as a completion indicator
Task Statement 1.2: Orchestrate multi-agent systems with coordinator-subagentpatterns
Knowledge of:
•
Hub-and-spoke architecture where a coordinator agent manages all inter-subagent communication,error handling, and information routing
•
How subagents operate with isolated context—they do not inherit the coordinator's conversationhistory automatically
•
The role of the coordinator in task decomposition, delegation, result aggregation, and decidingwhich subagents to invoke based on query complexity
Claude Certification Program
Exam guide
•
Risks of overly narrow task decomposition by the coordinator, leading to incomplete coverage ofbroad research topics
Skills in:
•
Designing coordinator agents that analyze query requirements and dynamically select whichsubagents to invoke rather than always routing through the full pipeline
•
Partitioning research scope across subagents to minimize duplication (e.g., assigning distinctsubtopics or source types to each agent)
•
Implementing iterative refinement loops where the coordinator evaluates synthesis output for gaps,re-delegates to search and analysis subagents with targeted queries, and re-invokes synthesis untilcoverage is sufficient
•
Routing all subagent communication through the coordinator for observability, consistent errorhandling, and controlled information flow
Task Statement 1.3: Configure subagent invocation, context passing, and spawning
Knowledge of:
•
The Task tool as the mechanism for spawning subagents, and the requirement that allowedToolsmust include "Task" for a coordinator to invoke subagents
•
That subagent context must be explicitly provided in the prompt—subagents do not automaticallyinherit parent context or share memory between invocations
•
The AgentDefinition configuration including descriptions, system prompts, and tool restrictions foreach subagent type
•
Fork-based session management for exploring divergent approaches from a shared analysisbaseline
Skills in:
•
Including complete findings from prior agents directly in the subagent's prompt (e.g., passing websearch results and document analysis outputs to the synthesis subagent)
•
Using structured data formats to separate content from metadata (source URLs, document names,page numbers) when passing context between agents to preserve attribution
•
Spawning parallel subagents by emitting multiple Task tool calls in a single coordinator responserather than across separate turns
•
Designing coordinator prompts that specify research goals and quality criteria rather than step-by-step procedural instructions, to enable subagent adaptability
Claude Certification Program
Exam guide
Task Statement 1.4: Implement multi-step workflows with enforcement and handoffpatterns
Knowledge of:
•
The difference between programmatic enforcement (hooks, prerequisite gates) and prompt-basedguidance for workflow ordering
•
When deterministic compliance is required (e.g., identity verification before financial operations),prompt instructions alone have a non-zero failure rate
•
Structured handoff protocols for mid-process escalation that include customer details, root causeanalysis, and recommended actions
Skills in:
•
Implementing programmatic prerequisites that block downstream tool calls until prerequisite stepshave completed (e.g., blocking process_refund until get_customer has returned a verified customerID)
•
Decomposing multi-concern customer requests into distinct items, then investigating each inparallel using shared context before synthesizing a unified resolution
•
Compiling structured handoff summaries (customer ID, root cause, refund amount, recommendedaction) when escalating to human agents who lack access to the conversation transcript
Task Statement 1.5: Apply Agent SDK hooks for tool call interception and datanormalization
Knowledge of:
•
Hook patterns (e.g., PostToolUse) that intercept tool results for transformation before the modelprocesses them
•
Hook patterns that intercept outgoing tool calls to enforce compliance rules (e.g., blocking refundsabove a threshold)
•
The distinction between using hooks for deterministic guarantees versus relying on promptinstructions for probabilistic compliance
Skills in:
•
Implementing PostToolUse hooks to normalize heterogeneous data formats (Unix timestamps, ISO8601, numeric status codes) from different MCP tools before the agent processes them
•
Implementing tool call interception hooks that block policy-violating actions (e.g., refunds exceeding$500) and redirect to alternative workflows (e.g., human escalation)
•
Choosing hooks over prompt-based enforcement when business rules require guaranteedcompliance
Claude Certification Program
Exam guide
Task Statement 1.6: Design task decomposition strategies for complex workflows
Knowledge of:
•
When to use fixed sequential pipelines (prompt chaining) versus dynamic adaptive decompositionbased on intermediate findings
•
Prompt chaining patterns that break reviews into sequential steps (e.g., analyze each fileindividually, then run a cross-file integration pass)
•
The value of adaptive investigation plans that generate subtasks based on what is discovered ateach step
Skills in:
•
Selecting task decomposition patterns appropriate to the workflow: prompt chaining forpredictable multi-aspect reviews, dynamic decomposition for open-ended investigation tasks
•
Splitting large code reviews into per-file local analysis passes plus a separate cross-file integrationpass to avoid attention dilution
•
Decomposing open-ended tasks (e.g., "add comprehensive tests to a legacy codebase") by firstmapping structure, identifying high-impact areas, then creating a prioritized plan that adapts asdependencies are discovered
Task Statement 1.7: Manage session state, resumption, and forking
Knowledge of:
•
Named session resumption using --resume <session-name> to continue a specific priorconversation
•
fork_session for creating independent branches from a shared analysis baseline to exploredivergent approaches
•
The importance of informing the agent about changes to previously analyzed files when resumingsessions after code modifications
•
Why starting a new session with a structured summary is more reliable than resuming with staletool results
Skills in:
•
Using --resume with session names to continue named investigation sessions across work sessions
•
Using fork_session to create parallel exploration branches (e.g., comparing two testing strategies orrefactoring approaches from a shared codebase analysis)
•
Choosing between session resumption (when prior context is mostly valid) and starting fresh withinjected summaries (when prior tool results are stale)
Claude Certification Program
Exam guide
•
Informing a resumed session about specific file changes for targeted re-analysis rather thanrequiring full re-exploration
Domain 2: Tool Design & MCP Integration
Task Statement 2.1: Design effective tool interfaces with clear descriptions andboundaries
Knowledge of:
•
Tool descriptions as the primary mechanism LLMs use for tool selection; minimal descriptions leadto unreliable selection among similar tools
•
The importance of including input formats, example queries, edge cases, and boundary explanationsin tool descriptions
•
How ambiguous or overlapping tool descriptions cause misrouting (e.g., analyze_content vsanalyze_document with near-identical descriptions)
•
The impact of system prompt wording on tool selection: keyword-sensitive instructions can createunintended tool associations
Skills in:
•
Writing tool descriptions that clearly differentiate each tool's purpose, expected inputs, outputs,and when to use it versus similar alternatives
•
Renaming tools and updating descriptions to eliminate functional overlap (e.g., renaminganalyze_content to extract_web_results with a web-specific description)
•
Splitting generic tools into purpose-specific tools with defined input/output contracts (e.g., splittinga generic analyze_document into extract_data_points, summarize_content, andverify_claim_against_source)
•
Reviewing system prompts for keyword-sensitive instructions that might override well-written tooldescriptions
Task Statement 2.2: Implement structured error responses for MCP tools
Knowledge of:
•
The MCP isError flag pattern for communicating tool failures back to the agent
•
The distinction between transient errors (timeouts, service unavailability), validation errors (invalidinput), business errors (policy violations), and permission errors
Claude Certification Program
Exam guide
•
Why uniform error responses (generic "Operation failed") prevent the agent from makingappropriate recovery decisions
•
The difference between retryable and non-retryable errors, and how returning structured metadataprevents wasted retry attempts
Skills in:
•
Returning structured error metadata including errorCategory (transient/validation/permission),isRetryable boolean, and human-readable descriptions
•
Including retriable: false flags and customer-friendly explanations for business rule violations so theagent can communicate appropriately
•
Implementing local error recovery within subagents for transient failures, propagating to thecoordinator only errors that cannot be resolved locally along with partial results and what wasattempted
•
Distinguishing between access failures (needing retry decisions) and valid empty results(representing successful queries with no matches)
Task Statement 2.3: Distribute tools appropriately across agents and configure toolchoice
Knowledge of:
•
The principle that giving an agent access to too many tools (e.g., 18 instead of 4-5) degrades toolselection reliability by increasing decision complexity
•
Why agents with tools outside their specialization tend to misuse them (e.g., a synthesis agentattempting web searches)
•
Scoped tool access: giving agents only the tools needed for their role, with limited cross-role toolsfor specific high-frequency needs
•
tool_choice configuration options: "auto", "any", and forced tool selection ({"type": "tool", "name":"..."})
Skills in:
•
Restricting each subagent's tool set to those relevant to its role, preventing cross-specializationmisuse
•
Replacing generic tools with constrained alternatives (e.g., replacing fetch_url with load_documentthat validates document URLs)
•
Providing scoped cross-role tools for high-frequency needs (e.g., a verify_fact tool for the synthesisagent) while routing complex cases through the coordinator
Claude Certification Program
Exam guide
•
Using tool_choice forced selection to ensure a specific tool is called first (e.g., forcingextract_metadata before enrichment tools), then processing subsequent steps in follow-up turns
•
Setting tool_choice: "any" to guarantee the model calls a tool rather than returning conversationaltext
Task Statement 2.4: Integrate MCP servers into Claude Code and agent workflows
Knowledge of:
•
MCP server scoping: project-level (.mcp.json) for shared team tooling vs user-level (~/.claude.json)for personal/experimental servers
•
Environment variable expansion in .mcp.json (e.g., ${GITHUB_TOKEN}) for credential managementwithout committing secrets
•
That tools from all configured MCP servers are discovered at connection time and availablesimultaneously to the agent
•
MCP resources as a mechanism for exposing content catalogs (e.g., issue summaries,documentation hierarchies, database schemas) to reduce exploratory tool calls
Skills in:
•
Configuring shared MCP servers in project-scoped .mcp.json with environment variable expansionfor authentication tokens
•
Configuring personal/experimental MCP servers in user-scoped ~/.claude.json
•
Enhancing MCP tool descriptions to explain capabilities and outputs in detail, preventing the agentfrom preferring built-in tools (like Grep) over more capable MCP tools
•
Choosing existing community MCP servers over custom implementations for standard integrations(e.g., Jira), reserving custom servers for team-specific workflows
•
Exposing content catalogs as MCP resources to give agents visibility into available data withoutrequiring exploratory tool calls
Task Statement 2.5: Select and apply built-in tools (Read, Write, Edit, Bash, Grep, Glob)effectively
Knowledge of:
•
Grep for content search (searching file contents for patterns like function names, error messages,or import statements)
•
Glob for file path pattern matching (finding files by name or extension patterns)
•
Read/Write for full file operations; Edit for targeted modifications using unique text matching
Claude Certification Program
Exam guide
•
When Edit fails due to non-unique text matches, using Read + Write as a fallback for reliable filemodifications
Skills in:
•
Selecting Grep for searching code content across a codebase (e.g., finding all callers of a function,locating error messages)
•
Selecting Glob for finding files matching naming patterns (e.g., **/*.test.tsx)
•
Using Read to load full file contents followed by Write when Edit cannot find unique anchor text
•
Building codebase understanding incrementally: starting with Grep to find entry points, then usingRead to follow imports and trace flows, rather than reading all files upfront
•
Tracing function usage across wrapper modules by first identifying all exported names, thensearching for each name across the codebase


Domain 4: Prompt Engineering & Structured Output
Task Statement 4.1: Design prompts with explicit criteria to improve precision andreduce false positives
Knowledge of:
•
The importance of explicit criteria over vague instructions (e.g., "flag comments only when claimedbehavior contradicts actual code behavior" vs "check that comments are accurate")
•
How general instructions like "be conservative" or "only report high-confidence findings" fail toimprove precision compared to specific categorical criteria
•
The impact of false positive rates on developer trust: high false positive categories undermineconfidence in accurate categories
Skills in:
•
Writing specific review criteria that define which issues to report (bugs, security) versus skip(minor style, local patterns) rather than relying on confidence-based filtering
•
Temporarily disabling high false-positive categories to restore developer trust while improvingprompts for those categories
•
Defining explicit severity criteria with concrete code examples for each severity level to achieveconsistent classification
Task Statement 4.2: Apply few-shot prompting to improve output consistency andquality
Knowledge of:
•
Few-shot examples as the most effective technique for achieving consistently formatted,actionable output when detailed instructions alone produce inconsistent results
•
The role of few-shot examples in demonstrating ambiguous-case handling (e.g., tool selection forambiguous requests, branch-level test coverage gaps)
•
How few-shot examples enable the model to generalize judgment to novel patterns rather thanmatching only pre-specified cases
•
The effectiveness of few-shot examples for reducing hallucination in extraction tasks (e.g., handlinginformal measurements, varied document structures)
Claude Certification Program
Exam guide
Skills in:
•
Creating 2-4 targeted few-shot examples for ambiguous scenarios that show reasoning for why oneaction was chosen over plausible alternatives
•
Including few-shot examples that demonstrate specific desired output format (location, issue,severity, suggested fix) to achieve consistency
•
Providing few-shot examples distinguishing acceptable code patterns from genuine issues toreduce false positives while enabling generalization
•
Using few-shot examples to demonstrate correct handling of varied document structures (inlinecitations vs bibliographies, methodology sections vs embedded details)
•
Adding few-shot examples showing correct extraction from documents with varied formats toaddress empty/null extraction of required fields
Task Statement 4.3: Enforce structured output using tool use and JSON schemas
Knowledge of:
•
Tool use (tool_use) with JSON schemas as the most reliable approach for guaranteed schema-compliant structured output, eliminating JSON syntax errors
•
The distinction between tool_choice: "auto" (model may return text instead of calling a tool), "any"(model must call a tool but can choose which), and forced tool selection (model must call a specificnamed tool)
•
That strict JSON schemas via tool use eliminate syntax errors but do not prevent semantic errors(e.g., line items that don't sum to total, values in wrong fields)
•
Schema design considerations: required vs optional fields, enum fields with "other" + detail stringpatterns for extensible categories
Skills in:
•
Defining extraction tools with JSON schemas as input parameters and extracting structured datafrom the tool_use response
•
Setting tool_choice: "any" to guarantee structured output when multiple extraction schemas existand the document type is unknown
•
Forcing a specific tool with tool_choice: {"type": "tool", "name": "extract_metadata"} to ensure aparticular extraction runs before enrichment steps
•
Designing schema fields as optional (nullable) when source documents may not contain theinformation, preventing the model from fabricating values to satisfy required fields
•
Adding enum values like "unclear" for ambiguous cases and "other" + detail fields for extensiblecategorization
Claude Certification Program
Exam guide
•
Including format normalization rules in prompts alongside strict output schemas to handleinconsistent source formatting
Task Statement 4.4: Implement validation, retry, and feedback loops for extractionquality
Knowledge of:
•
Retry-with-error-feedback: appending specific validation errors to the prompt on retry to guide themodel toward correction
•
The limits of retry: retries are ineffective when the required information is simply absent from thesource document (vs format or structural errors)
•
Feedback loop design: tracking which code constructs trigger findings (detected_pattern field) toenable systematic analysis of dismissal patterns
•
The difference between semantic validation errors (values don't sum, wrong field placement) andschema syntax errors (eliminated by tool use)
Skills in:
•
Implementing follow-up requests that include the original document, the failed extraction, andspecific validation errors for model self-correction
•
Identifying when retries will be ineffective (e.g., information exists only in an external document notprovided) versus when they will succeed (format mismatches, structural output errors)
•
Adding detected_pattern fields to structured findings to enable analysis of false positive patternswhen developers dismiss findings
•
Designing self-correction validation flows: extracting "calculated_total" alongside "stated_total" toflag discrepancies, adding "conflict_detected" booleans for inconsistent source data
Task Statement 4.5: Design efficient batch processing strategies
Knowledge of:
•
The Message Batches API: 50% cost savings, up to 24-hour processing window, no guaranteedlatency SLA
•
Batch processing is appropriate for non-blocking, latency-tolerant workloads (overnight reports,weekly audits, nightly test generation) and inappropriate for blocking workflows (pre-mergechecks)
•
The batch API does not support multi-turn tool calling within a single request (cannot execute toolsmid-request and return results)
•
custom_id fields for correlating batch request/response pairs
Claude Certification Program
Exam guide
Skills in:
•
Matching API approach to workflow latency requirements: synchronous API for blocking pre-mergechecks, batch API for overnight/weekly analysis
•
Calculating batch submission frequency based on SLA constraints (e.g., 4-hour windows toguarantee 30-hour SLA with 24-hour batch processing)
•
Handling batch failures: resubmitting only failed documents (identified by custom_id) withappropriate modifications (e.g., chunking documents that exceeded context limits)
•
Using prompt refinement on a sample set before batch-processing large volumes to maximize first-pass success rates and reduce iterative resubmission costs
Task Statement 4.6: Design multi-instance and multi-pass review architectures
Knowledge of:
•
Self-review limitations: a model retains reasoning context from generation, making it less likely toquestion its own decisions in the same session
•
Independent review instances (without prior reasoning context) are more effective at catchingsubtle issues than self-review instructions or extended thinking
•
Multi-pass review: splitting large reviews into per-file local analysis passes plus cross-fileintegration passes to avoid attention dilution and contradictory findings
Skills in:
•
Using a second independent Claude instance to review generated code without the generator'sreasoning context
•
Splitting large multi-file reviews into focused per-file passes for local issues plus separateintegration passes for cross-file data flow analysis
•
Running verification passes where the model self-reports confidence alongside each finding toenable calibrated review routing
Domain 5: Context Management & Reliability
Task Statement 5.1: Manage conversation context to preserve critical informationacross long interactions
Knowledge of:
•
Progressive summarization risks: condensing numerical values, percentages, dates, and customer-stated expectations into vague summaries
Claude Certification Program
Exam guide
•
The "lost in the middle" effect: models reliably process information at the beginning and end of longinputs but may omit findings from middle sections
•
How tool results accumulate in context and consume tokens disproportionately to their relevance(e.g., 40+ fields per order lookup when only 5 are relevant)
•
The importance of passing complete conversation history in subsequent API requests to maintainconversational coherence
Skills in:
•
Extracting transactional facts (amounts, dates, order numbers, statuses) into a persistent "casefacts" block included in each prompt, outside summarized history
•
Extracting and persisting structured issue data (order IDs, amounts, statuses) into a separatecontext layer for multi-issue sessions
•
Trimming verbose tool outputs to only relevant fields before they accumulate in context (e.g.,keeping only return-relevant fields from order lookups)
•
Placing key findings summaries at the beginning of aggregated inputs and organizing detailedresults with explicit section headers to mitigate position effects
•
Requiring subagents to include metadata (dates, source locations, methodological context) instructured outputs to support accurate downstream synthesis
•
Modifying upstream agents to return structured data (key facts, citations, relevance scores)instead of verbose content and reasoning chains when downstream agents have limited contextbudgets
Task Statement 5.2: Design effective escalation and ambiguity resolution patterns
Knowledge of:
•
Appropriate escalation triggers: customer requests for a human, policy exceptions/gaps (not justcomplex cases), and inability to make meaningful progress
•
The distinction between escalating immediately when a customer explicitly demands it versusoffering to resolve when the issue is straightforward
•
Why sentiment-based escalation and self-reported confidence scores are unreliable proxies foractual case complexity
•
How multiple customer matches require clarification (requesting additional identifiers) rather thanheuristic selection
Skills in:
•
Adding explicit escalation criteria with few-shot examples to the system prompt demonstratingwhen to escalate versus resolve autonomously
Claude Certification Program
Exam guide
•
Honoring explicit customer requests for human agents immediately without first attemptinginvestigation
•
Acknowledging frustration while offering resolution when the issue is within the agent's capability,escalating only if the customer reiterates their preference
•
Escalating when policy is ambiguous or silent on the customer's specific request (e.g., competitorprice matching when policy only addresses own-site adjustments)
•
Instructing the agent to ask for additional identifiers when tool results return multiple matches,rather than selecting based on heuristics
Task Statement 5.3: Implement error propagation strategies across multi-agent systems
Knowledge of:
•
Structured error context (failure type, attempted query, partial results, alternative approaches) asenabling intelligent coordinator recovery decisions
•
The distinction between access failures (timeouts needing retry decisions) and valid empty results(successful queries with no matches)
•
Why generic error statuses ("search unavailable") hide valuable context from the coordinator
•
Why silently suppressing errors (returning empty results as success) or terminating entireworkflows on single failures are both anti-patterns
Skills in:
•
Returning structured error context including failure type, what was attempted, partial results, andpotential alternatives to enable coordinator recovery
•
Distinguishing access failures from valid empty results in error reporting so the coordinator canmake appropriate decisions
•
Having subagents implement local recovery for transient failures and only propagate errors theycannot resolve, including what was attempted and partial results
•
Structuring synthesis output with coverage annotations indicating which findings are well-supported versus which topic areas have gaps due to unavailable sources
Task Statement 5.4: Manage context effectively in large codebase exploration
Knowledge of:
•
Context degradation in extended sessions: models start giving inconsistent answers andreferencing "typical patterns" rather than specific classes discovered earlier
•
The role of scratchpad files for persisting key findings across context boundaries
Claude Certification Program
Exam guide
•
Subagent delegation for isolating verbose exploration output while the main agent coordinates high-level understanding
•
Structured state persistence for crash recovery: each agent exports state to a known location, andthe coordinator loads a manifest on resume
Skills in:
•
Spawning subagents to investigate specific questions (e.g., "find all test files," "trace refund flowdependencies") while the main agent preserves high-level coordination
•
Having agents maintain scratchpad files recording key findings, referencing them for subsequentquestions to counteract context degradation
•
Summarizing key findings from one exploration phase before spawning sub-agents for the nextphase, injecting summaries into initial context
•
Designing crash recovery using structured agent state exports (manifests) that the coordinatorloads on resume and injects into agent prompts
•
Using /compact to reduce context usage during extended exploration sessions when context fillswith verbose discovery output
Task Statement 5.5: Design human review workflows and confidence calibration
Knowledge of:
•
The risk that aggregate accuracy metrics (e.g., 97% overall) may mask poor performance on specificdocument types or fields
•
Stratified random sampling for measuring error rates in high-confidence extractions and detectingnovel error patterns
•
Field-level confidence scores calibrated using labeled validation sets for routing review attention
•
The importance of validating accuracy by document type and field segment before automating high-confidence extractions
Skills in:
•
Implementing stratified random sampling of high-confidence extractions for ongoing error ratemeasurement and novel pattern detection
•
Analyzing accuracy by document type and field to verify consistent performance across allsegments before reducing human review
•
Having models output field-level confidence scores, then calibrating review thresholds usinglabeled validation sets
•
Routing extractions with low model confidence or ambiguous/contradictory source documents tohuman review, prioritizing limited reviewer capacity
Claude Certification Program
Exam guide
Task Statement 5.6: Preserve information provenance and handle uncertainty in multi-source synthesis
Knowledge of:
•
How source attribution is lost during summarization steps when findings are compressed withoutpreserving claim-source mappings
•
The importance of structured claim-source mappings that the synthesis agent must preserve andmerge when combining findings
•
How to handle conflicting statistics from credible sources: annotating conflicts with sourceattribution rather than arbitrarily selecting one value
•
Temporal data: requiring publication/collection dates in structured outputs to prevent temporaldifferences from being misinterpreted as contradictions
Skills in:
•
Requiring subagents to output structured claim-source mappings (source URLs, document names,relevant excerpts) that downstream agents preserve through synthesis
•
Structuring reports with explicit sections distinguishing well-established findings from contestedones, preserving original source characterizations and methodological context
•
Completing document analysis with conflicting values included and explicitly annotated, letting thecoordinator decide how to reconcile before passing to synthesis
•
Requiring subagents to include publication or data collection dates in structured outputs to enablecorrect temporal interpretation
•
Rendering different content types appropriately in synthesis outputs—financial data as tables,news as prose, technical findings as structured lists—rather than converting everything to auniform format
7. How to Prepare
To prepare for this certification exam:
•
Build an agent with the Claude Agent SDK: implement a complete agentic loop with tool calling, errorhandling, and session management. Practice spawning subagents and passing context betweenthem.
•
Configure Claude Code for a real project: set up CLAUDE.md with a configuration hierarchy, createpath-specific rules in .claude/rules/, build custom skills with frontmatter options (context: fork,allowed-tools), and integrate
Design and test MCP tools: write tool descriptions that clearly differentiate similar tools. Implementstructured error responses with error categories and retryable flags. Test tool selection reliabilitywith ambiguous requests.
•
Build a structured data extraction pipeline: use tool_use with JSON schemas, implement validation-retry loops, design schemas with optional/nullable fields, and practice batch processing with theMessage Batches API.
•
Practice prompt engineering techniques: write few-shot examples for ambiguous scenarios. Defineexplicit review criteria to reduce false positives. Design multi-pass review architectures for largecode reviews.
•
Study context management patterns: practice extracting structured facts from verbose tooloutputs, implementing scratchpad files for long sessions, and designing subagent delegation tomanage context limits.
•
Review escalation and human-in-the-loop patterns: understand when to escalate (policy gaps,customer requests, inability to progress) versus resolve autonomously. Practice designing humanreview workflows with confidence-based routing.


8. Preparation Exercises
Complete these hands-on exercises to build practical familiarity with the topics covered on the exam.Each exercise is designed to reinforce knowledge across one or more exam domains.
Exercise 1: Build a Multi-Tool Agent with Escalation Logic
Objective:
Practice designing an agentic loop with tool integration, structured error handling, andescalation patterns.
Steps:
•
Define 3-4 MCP tools with detailed descriptions that clearly differentiate each tool's purpose,expected inputs, and boundary conditions. Include at least two tools with similar functionality thatrequire careful description to avoid selection confusion.
•
Implement an agentic loop that checks stop_reason to determine whether to continue toolexecution or present the final response. Handle both "tool_use" and "end_turn" stop reasonscorrectly.
•
Add structured error responses to your tools: include errorCategory(transient/validation/permission), isRetryable boolean, and human-readable descriptions. Test thatthe agent handles each error type appropriately (retrying transient errors, explaining businesserrors to the user).
Claude Certification Program
Exam guide
•
Implement a programmatic hook that intercepts tool calls to enforce a business rule (e.g., blockingoperations above a threshold amount), redirecting to an escalation workflow when triggered.
•
Test with multi-concern messages (e.g., requests involving multiple issues) and verify the agentdecomposes the request, handles each concern, and synthesizes a unified response.
Domains reinforced:
Domain 1 (Agentic Architecture & Orchestration), Domain 2 (Tool Design & MCPIntegration), Domain 5 (Context Management & Reliability)
Exercise 2: Configure Claude Code for a Team Development Workflow
Objective:
Practice configuring CLAUDE.md hierarchies, custom slash commands, path-specific rules,and MCP server integration for a multi-developer project.
Steps:
•
Create a project-level CLAUDE.md with universal coding standards and testing conventions. Verifythat instructions placed at the project level are consistently applied across all team members.
•
Create .claude/rules/ files with YAML frontmatter glob patterns for different code areas (e.g., paths:["src/api/**/*"] for API conventions, paths: ["**/*.test.*"] for testing conventions). Test that rulesload only when editing matching files.
•
Create a project-scoped skill in .claude/skills/ with context: fork and allowed-tools restrictions.Verify the skill runs in isolation without polluting the main conversation context.
•
Configure an MCP server in .mcp.json with environment variable expansion for credentials. Add apersonal experimental MCP server in ~/.claude.json and verify both are available simultaneously.
•
Test plan mode versus direct execution on tasks of varying complexity: a single-file bug fix, a multi-file library migration, and a new feature with multiple valid implementation approaches. Observewhen plan mode provides value.
Domains reinforced:
Domain 3 (Claude Code Configuration & Workflows), Domain 2 (Tool Design &MCP Integration)
Exercise 3: Build a Structured Data Extraction Pipeline
Objective:
Practice designing JSON schemas, using tool_use for structured output, implementingvalidation-retry loops, and designing batch processing strategies.
Steps:
•
Define an extraction tool with a JSON schema containing required and optional fields, an enum withan "other" + detail string pattern, and nullable fields for information that may not exist in sourcedocuments. Process documents where some fields are absent and verify the model returns nullrather than fabricating values.
Claude Certification Program
Exam guide
•
Implement a validation-retry loop: when Pydantic or JSON schema validation fails, send a follow-uprequest including the document, the failed extraction, and the specific validation error. Track whicherrors are resolvable via retry (format mismatches) versus which are not (information absent fromsource).
•
Add few-shot examples demonstrating extraction from documents with varied formats (e.g., inlinecitations vs bibliographies, narrative descriptions vs structured tables) and verify improvedhandling of structural variety.
•
Design a batch processing strategy: submit a batch of 100 documents using the Message BatchesAPI, handle failures by custom_id, resubmit failed documents with modifications (e.g., chunkingoversized documents), and calculate total processing time relative to SLA constraints.
•
Implement a human review routing strategy: have the model output field-level confidence scores,route low-confidence extractions to human review, and analyze accuracy by document type andfield to verify consistent performance.
Domains reinforced:
Domain 4 (Prompt Engineering & Structured Output), Domain 5 (ContextManagement & Reliability)
Exercise 4: Design and Debug a Multi-Agent Research Pipeline
Objective:
Practice orchestrating subagents, managing context passing, implementing errorpropagation, and handling synthesis with provenance tracking.
Steps:
•
Build a coordinator agent that delegates to at least two subagents (e.g., web search and documentanalysis). Ensure the coordinator's allowedTools includes "Task" and that each subagent receives itsresearch findings directly in its prompt rather than relying on automatic context inheritance.
•
Implement parallel subagent execution by having the coordinator emit multiple Task tool calls in asingle response. Measure the latency improvement compared to sequential execution.
•
Design structured output for subagents that separates content from metadata: each finding shouldinclude a claim, evidence excerpt, source URL/document name, and publication date. Verify that thesynthesis subagent preserves source attribution when combining findings.
•
Implement error propagation: simulate a subagent timeout and verify the coordinator receivesstructured error context (failure type, attempted query, partial results). Test that the coordinatorcan proceed with partial results and annotate the final output with coverage gaps.
•
Test with conflicting source data (e.g., two credible sources with different statistics) and verify thesynthesis output preserves both values with source attribution rather than arbitrarily selecting one,and structures the report to distinguish well-established from contested findings.
Domains reinforced:
Domain 1 (Agentic Architecture & Orchestration), Domain 2 (Tool Design & MCPIntegration), Domain 5 (Context Management & Reliability)

