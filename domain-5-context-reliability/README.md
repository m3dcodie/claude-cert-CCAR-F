# Domain 5: Context Management & Reliability (15%)

## Task Statement 5.1 — Manage conversation context across long interactions

**Knowledge:** progressive summarization silently drops precision — numbers,
percentages, dates, and customer-stated expectations turn into vague prose over
several rounds of "summarize the summary." The **"lost in the middle"** effect means a
model reliably attends to the start and end of a long input but can miss findings
buried in the middle. Tool results accumulate disproportionately to their relevance —
a 40-field order lookup where only 5 fields matter still burns tokens on all 40 every
time it's re-read from history. Full conversation history generally needs to be
resent each API request to keep coherence — the burden is on trimming what goes IN,
not skipping what gets sent.

**Skills:** extract transactional facts (amounts, dates, order numbers, statuses) into
a persistent "case facts" block carried in every prompt, kept OUTSIDE the summarized
history so it can't be lossily compressed; trim verbose tool output to only the
relevant fields before it accumulates; put key-findings summaries at the START of
aggregated inputs with explicit section headers, to counter the middle-attention drop;
require subagents to tag structured output with metadata (dates, sources) so
downstream synthesis has what it needs; have upstream agents return structured facts
instead of verbose reasoning chains when the downstream agent has a small context
budget.

**Example:** [`examples/01_case_facts_extraction.py`](./examples/01_case_facts_extraction.py)

## Task Statement 5.2 — Design effective escalation and ambiguity resolution patterns

**Knowledge:** real escalation triggers are: an explicit customer request for a human,
a genuine policy gap/exception (not just "this is complicated"), or the agent
concretely unable to make progress. Escalating the instant a customer *asks* is
correct; escalating a *merely complex but in-policy* issue is not — offer to resolve it
first. Sentiment analysis and the model's own self-reported confidence are both
unreliable proxies for actual complexity — a frustrated customer with a simple issue
shouldn't auto-escalate, and a calm customer with a genuinely ambiguous policy
question should. Multiple ambiguous customer matches need a clarifying question
(more identifiers), never a heuristic guess at which customer was meant.

**Skills:** encode escalation triggers with few-shot examples of escalate-vs-resolve
decisions in the system prompt; honor an explicit "let me talk to a human" immediately,
no investigation first; acknowledge frustration while still offering to resolve
in-capability issues, escalating only if the customer reiterates; escalate when policy
is silent on the specific request (e.g., competitor price-matching when policy only
covers same-site price adjustments); ask for another identifier rather than guessing
when a lookup returns multiple matches.

**Example:** [`examples/02_escalation_patterns.py`](./examples/02_escalation_patterns.py)

## Task Statement 5.3 — Implement error propagation strategies across multi-agent systems

**Knowledge:** structured error context (failure type, what was attempted, partial
results, alternative approaches) is what lets a coordinator make an intelligent
recovery decision instead of guessing. Access failures (a timeout — needs a retry
decision) are categorically different from valid empty results (query ran fine, found
nothing) — collapsing them loses information the coordinator needs. Two anti-patterns
at once: silently swallowing an error as if it were a successful empty result, and
killing the entire multi-agent workflow over one subagent's failure.

**Skills:** return structured error context (failure type + attempted query + partial
results + alternatives) so the coordinator can decide, not just detect; keep access
failures visibly distinct from empty-but-valid results; have subagents attempt local
recovery for transient failures and propagate to the coordinator only what they
genuinely couldn't resolve, with what was tried and any partial results; annotate
final synthesis output with coverage gaps rather than pretending coverage was complete.

**Example:** [`examples/03_error_propagation.py`](./examples/03_error_propagation.py)

## Task Statement 5.4 — Manage context effectively in large codebase exploration

**Knowledge:** in long exploration sessions, context degrades — the model starts
giving inconsistent answers and falls back to "typical patterns" language instead of
citing the specific classes it actually found earlier. Scratchpad files persist key
findings across a context boundary that would otherwise lose them. Delegating verbose
exploration to subagents keeps that raw noise out of the main agent's context while it
coordinates at a higher level. For crash recovery, each agent exports its state to a
known location and a coordinator loads a manifest on resume, rather than re-exploring
from scratch.

**Skills:** spawn subagents for specific, bounded investigations ("find all test
files", "trace refund flow dependencies") while the main agent stays at the
coordination level; maintain a scratchpad file of key findings and reference it on
later questions instead of re-deriving; summarize findings from one exploration phase
before spawning subagents for the next, injecting the summary as their starting
context; design a manifest-based state export/import for crash recovery; use
`/compact` when verbose discovery output is filling context during a long session.

**Example:** [`examples/04_scratchpad_and_delegation.py`](./examples/04_scratchpad_and_delegation.py)

## Task Statement 5.5 — Design human review workflows and confidence calibration

**Knowledge:** a headline aggregate accuracy number (e.g., 97%) can hide a document
type or field that's performing much worse — averaging masks the segment that actually
needs attention. Stratified random sampling (sampled *within* each document
type/field, not just overall) is how you catch both ongoing error-rate drift and novel
error patterns that a global average wouldn't surface. Field-level confidence scores
are only useful once **calibrated** against a labeled validation set — an
uncalibrated confidence number doesn't mean what it claims to mean.

**Skills:** implement stratified sampling of high-confidence extractions specifically
(the ones most likely to skip human review) for ongoing measurement; break down
accuracy by document type AND field before reducing human review anywhere; calibrate
confidence-score routing thresholds against a labeled set rather than trusting the raw
score; route low-confidence or contradictory-source extractions to human review first,
prioritizing scarce reviewer time.

**Example:** [`examples/05_confidence_calibration.py`](./examples/05_confidence_calibration.py)

## Task Statement 5.6 — Preserve information provenance and handle uncertainty in multi-source synthesis

**Knowledge:** summarization steps are exactly where source attribution gets lost —
compressing findings without carrying the claim→source mapping along means the final
report can no longer say *where* a claim came from. Conflicting statistics from two
credible sources should be presented with both values and their attribution, not
silently resolved by picking one. Temporal data (publication/collection dates) has to
be carried in structured output so a real time-based difference isn't misread as a
contradiction.

**Skills:** require subagents to emit structured claim→source mappings (URL, doc name,
excerpt) that downstream synthesis explicitly preserves rather than compressing away;
structure the final report with explicit "well-established" vs. "contested" sections;
when document analysis surfaces conflicting values, pass both forward with annotation
and let the coordinator decide how to reconcile, rather than resolving it silently
mid-pipeline; require publication/collection dates in structured output so temporal
differences read as temporal, not contradictory; render each content type in its
natural form in the final report (financial data as tables, news as prose, technical
findings as lists) instead of flattening everything into one uniform shape.

**Example:** [`examples/06_provenance_synthesis.py`](./examples/06_provenance_synthesis.py)
