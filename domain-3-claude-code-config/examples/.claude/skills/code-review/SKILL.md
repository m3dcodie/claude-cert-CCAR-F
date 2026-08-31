---
name: code-review
description: Review a diff for correctness bugs and reuse/simplification opportunities. Runs isolated so exploration noise doesn't pollute the main conversation.
context: fork
allowed-tools: Read, Grep, Glob
argument-hint: <file-or-pr-scope>
---

# Code review skill

Run this when asked to review a diff, a PR, or "changes I just made."

`argument-hint: <file-or-pr-scope>` — if invoked bare (no target given), this prompts
the developer for what to review instead of the skill guessing at a scope. Compare
with `.claude/commands/review-pr.md`, which is the slash-command form of a related
workflow: skills and commands overlap in shape, but a skill is the right choice when
the work benefits from running in an isolated forked context (see below), while a
plain command is enough for something that doesn't need that isolation.

`context: fork` — this skill runs in a forked context. It can read as many files as it
needs to build understanding without every intermediate file read cluttering the
caller's conversation; only the final findings come back.

`allowed-tools: Read, Grep, Glob` — deliberately read-only. This skill reviews code, it
does not fix it (that's a separate, explicit step) and it never needs `Bash`/`Edit`/
`Write` to do its job — restricting the tool set here follows the same "scope tools to
the role" principle as Domain 2 Task Statement 2.3, just applied to a skill instead of
a subagent.

## Steps

1. Identify the changed files (via the diff/PR context provided by the caller).
2. `Grep` for the symbols touched to find callers that might be affected but weren't
   changed.
3. `Read` each changed file plus any affected callers found in step 2.
4. Report findings as: file, line, summary, concrete failure scenario — not vague
   "this could be better" comments.
