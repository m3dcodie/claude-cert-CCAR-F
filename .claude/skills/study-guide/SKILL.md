---
name: study-guide
description: Track progress through this CCAR-F study repo and run interactive quiz drills from quiz_bank.md. Use when the user asks what to study next, wants a progress check, wants to run an example, or wants to be quizzed on a domain or task statement.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
argument-hint: [status | next | quiz <domain-or-T.S.> | run <example>]
---

# Study guide skill

This skill is a navigator and quizzer over the repo's existing content
(`outline.md`, `domain-*/README.md`, `domain-*/examples/*.py`, `quiz_bank.md`,
`exercises/`). **It never writes new study material** — no new questions, no new
example scripts, no rewritten theory notes. If a gap in the content is found,
say so and suggest the user open an issue/PR upstream; don't patch it inline.
Passive authoring doesn't build retention here — quizzing and doing does.

## Progress file

State lives in `study-progress.md` at the repo root, created on first use if
missing (and added to `.gitignore` — this file is per-learner, never committed).
Structure:

```markdown
# Study Progress — CCAR-F

Started: <date>

## Domain 1 — Agentic Architecture & Orchestration (27%)
- [ ] README read
- [ ] 01_agentic_loop.py run
- [ ] 02_coordinator_subagent.py run
... (one line per example file, in numeric order)

Quiz attempts: Q1✅ Q3❌ Q7✅ ...
Weak task statements: 1.5, 1.7   <!-- any T.S. with an unresolved ❌ -->

## Domain 2 ...
## Domain 3 ...
## Domain 4 ...
## Domain 5 ...

## Exercises
- [ ] 01_multi_tool_agent_escalation
- [ ] 02_team_workflow_config
- [ ] 03_extraction_pipeline
- [ ] 04_research_pipeline

## Session Log
- <date>: <one-line summary of what happened this session>
```

A "weak" task statement is one where the most recent attempt on any question
tagged to it was ❌. Answering it correctly on a later attempt clears it.

## Commands

**`status` (default, no args)** — read `study-progress.md` (initialize it from
the template above if it doesn't exist, scanning each `domain-*/examples/` dir
to list actual filenames). Print a compact table: per domain, README read?,
examples run X/Y, quiz score, weak T.S. list. Then hand off to `next`.

**`next`** — recommend exactly one concrete next action, in this priority
order:
1. Any weak task statement → re-quiz it (few questions, fast feedback loop).
2. The next unread domain README, in weight order: D1 → D3 → D4 → D2 → D5
   (see root `README.md` for why this order).
3. The next un-run example in the current domain.
4. If all examples in a domain are run and no quiz attempted yet for it →
   quiz the whole domain.
5. Once all 5 domains are read + quizzed → the next un-started exercise in
   `exercises/` (numeric order).
Give the recommendation as one sentence plus the reason, not a menu.

**`quiz <domain N | T.S. x.y>`** — pull the matching questions from
`quiz_bank.md` (match on the `### T.S. x.y` heading or `## Domain N` heading).
Prioritize, in order: previously-missed questions, then unattempted ones. Ask
**one question at a time**, full text, options included, and *wait for the
user's answer* before revealing anything. Do not print the `<details>` answer
key up front. After each answer: say correct/incorrect, give the explanation
from the answer key, then record the result in `study-progress.md` (append to
Quiz attempts, update weak T.S. list) before moving to the next question. Stop
after all matched questions are covered or the user says stop.

**`run <example-path-or-number>`** — actually execute it
(`python3 domain-N-.../examples/NN_name.py`) via Bash. If it exits 0, mark
that line done in `study-progress.md`. If it fails, report the error — don't
silently mark it done, don't fix the repo's example code as a side effect
(that's a separate, explicit ask).

## Notes

- Task statement numbers in `quiz_bank.md` (`T.S. x.y`) match `outline.md` and
  each domain's `README.md` exactly — cross-reference by that tag.
- Never reveal quiz answers except one at a time, after the user has answered.
- Keep status output short — a table and one recommended next step, not a
  restatement of the whole repo README.
