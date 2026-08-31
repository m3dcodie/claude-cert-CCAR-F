---
argument-hint: <pr-number>
---

# /review-pr

Project-scoped slash command — lives in `.claude/commands/`, committed to version
control, so every team member gets `/review-pr` automatically. A personal, one-off
command instead belongs in `~/.claude/commands/` (not shared).

Review PR #$ARGUMENTS against this repo's standards:

1. Fetch the diff for PR #$ARGUMENTS.
2. Apply the same criteria as the `code-review` skill (see
   `.claude/skills/code-review/SKILL.md`) — correctness bugs and reuse/simplification
   opportunities, not style nitpicks.
3. Post findings as `location | issue | severity | suggested_fix` lines.

If invoked as bare `/review-pr` with no PR number, the `argument-hint` above prompts
the developer for one instead of the command silently failing or guessing.
