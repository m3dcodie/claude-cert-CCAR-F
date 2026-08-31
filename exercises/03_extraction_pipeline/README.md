# Exercise 3: Build a Structured Data Extraction Pipeline

**Official objective (outline.md §8):** practice designing JSON schemas, using
`tool_use` for structured output, implementing validation-retry loops, and designing
batch processing strategies.

**Domains reinforced:** D4 (Prompt Engineering & Structured Output), D5 (Context
Management & Reliability).

## What this wires together

- A `tool_use` extraction schema with required/optional/nullable fields and an
  `enum` + `"other"` pattern (D4 4.3).
- A validation-retry loop that appends the specific validation error on retry, and
  knows when retrying is pointless (D4 4.4).
- Field-level confidence scores routed to human review below a calibrated threshold
  (D5 5.5).
- A batch-processing pass over the documents that succeeded validation, with
  `custom_id` correlation (D4 4.5).

Run it:

```bash
python3 pipeline.py
```
