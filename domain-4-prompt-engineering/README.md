# Domain 4: Prompt Engineering & Structured Output (20%) — Priority: weak on the mock (50%)

## Task Statement 4.1 — Design prompts with explicit criteria to reduce false positives

**Knowledge:** explicit, checkable criteria ("flag a comment only when claimed behavior
contradicts actual code behavior") beat vague instructions ("check that comments are
accurate"). Vague meta-instructions like "be conservative" or "only report
high-confidence findings" don't actually improve precision — they give the model
nothing concrete to check against, just a confidence dial with no calibration. A high
false-positive category poisons trust in the *accurate* categories too — one bad
"security" flag makes a developer skeptical of every future security flag.

**Skills:** define concrete report-vs-skip criteria per category (bugs/security: report;
minor style/local patterns: skip) instead of a global confidence threshold; temporarily
turn off a high-false-positive category entirely while its prompt gets fixed, rather
than letting it keep eroding trust; give concrete code examples per severity level so
classification is consistent across runs, not vibes-based.

**Example:** [`examples/01_explicit_criteria_prompts.py`](./examples/01_explicit_criteria_prompts.py)

## Task Statement 4.2 — Apply few-shot prompting to improve output consistency and quality

**Knowledge:** when detailed instructions alone still produce inconsistent formatting,
2-4 few-shot examples are the most effective fix. Their real value isn't matching
pre-specified cases — it's demonstrating *reasoning for ambiguous cases* so the model
generalizes that judgment to novel inputs it hasn't seen. This is also the strongest
lever for reducing hallucination in extraction (e.g., handling informal measurements,
varied document layouts).

**Skills:** write 2-4 examples that show *why* one action was chosen over a plausible
alternative, not just the input/output pair; include the desired output shape
explicitly (location, issue, severity, fix) in the examples themselves; pair
acceptable-pattern examples against genuine-issue examples to cut false positives
without losing recall; use varied-format examples (inline citations vs. bibliography,
narrative vs. table) to teach structural generalization.

**Example:** [`examples/02_few_shot_prompting.py`](./examples/02_few_shot_prompting.py)

## Task Statement 4.3 — Enforce structured output using tool use and JSON schemas

**Knowledge:** `tool_use` with a JSON schema is the most reliable way to get
schema-compliant output — it eliminates *syntax* errors entirely (no more "the model
almost produced valid JSON"). It does **not** eliminate *semantic* errors — line items
that don't sum to the stated total, a value placed in the wrong field, are still
possible and need separate validation. `tool_choice` again matters here: `"any"` when
multiple extraction schemas exist and you don't know the document type ahead of time;
forced `{"type": "tool", "name": "..."}` when a specific extraction must run first.
Nullable/optional fields prevent the model from fabricating a value just to satisfy a
`required` schema when the source document simply doesn't contain that field.

**Skills:** define the extraction schema as a tool's `input_schema`, read the result out
of the `tool_use` block; use `"other"` + a free-text detail field for
categories you know are incomplete, `"unclear"` for genuinely ambiguous cases; make a
field nullable rather than required when the source may legitimately omit it; pair the
strict schema with prompt-level normalization rules (e.g., "dates may appear as MM/DD or
DD/MM — infer from context and always output ISO-8601") for messy source formatting.

**Example:** [`examples/03_structured_output_tool_use.py`](./examples/03_structured_output_tool_use.py)

## Task Statement 4.4 — Implement validation, retry, and feedback loops for extraction quality

**Knowledge:** retry-with-error-feedback (append the *specific* validation error to a
follow-up prompt) fixes structural/format problems. It does **not** fix a case where
the required information simply isn't in the source document — no amount of retrying
recovers data that was never there. Tracking a `detected_pattern` field on findings
lets you later analyze *what* keeps triggering dismissed/false-positive findings, at
scale, instead of anecdotally.

**Skills:** on validation failure, send a follow-up with the original document, the
failed extraction, and the exact error, and ask for a corrected version; before
retrying, check whether the failure is "wrong shape" (retry will help) or "value doesn't
exist in the source" (retry cannot help — flag as missing instead); design
self-correction fields like `calculated_total` alongside `stated_total` so a
discrepancy is caught automatically rather than requiring a human to notice it.

**Example:** [`examples/04_validation_retry_loop.py`](./examples/04_validation_retry_loop.py)

## Task Statement 4.5 — Design efficient batch processing strategies

**Knowledge:** the Message Batches API gives ~50% cost savings with up to a 24-hour
processing window and **no latency SLA** — it's for non-blocking, latency-tolerant work
(overnight reports, weekly audits), never for a blocking pre-merge check. It does **not**
support multi-turn tool calling mid-request (you can't execute a tool and feed the
result back within one batch request). `custom_id` correlates each response back to its
originating request.

**Skills:** pick synchronous vs. batch by whether the workflow can tolerate up-to-24h
latency; if an SLA requires results within N hours, back-calculate a submission cadence
(e.g., submit every 4h to guarantee a 30h SLA against a 24h max batch window); on
partial batch failure, resubmit only the failed `custom_id`s, adjusted if needed (e.g.,
chunk a document that blew the context limit); tune the prompt on a small sample *before*
submitting the full batch, since a batch-wide prompt bug is expensive to discover after
the fact.

**Example:** [`examples/05_batch_processing.py`](./examples/05_batch_processing.py)

## Task Statement 4.6 — Design multi-instance and multi-pass review architectures

**Knowledge:** a model that just generated some code retains its own reasoning context
and is measurably less likely to question its own decisions in the same session —
self-review instructions and extended thinking don't fully substitute for genuine
independence. A **second, independent instance** with no prior reasoning context catches
more subtle issues. For large multi-file changes, a single monolithic review pass
suffers attention dilution and can produce contradictory findings — splitting into
per-file local passes plus a separate cross-file integration pass avoids that (same
principle as Domain 1 Task Statement 1.6).

**Skills:** route generated code to a fresh instance for review rather than asking the
generating instance to "double-check itself"; split large reviews into per-file +
integration passes; have the reviewing model self-report a confidence score per
finding so low-confidence findings can be routed for extra scrutiny (ties into Domain 5
Task Statement 5.5's confidence calibration).

**Example:** [`examples/06_multi_pass_review.py`](./examples/06_multi_pass_review.py)
