# Exercise 2: Configure Claude Code for a Team Development Workflow

**Official objective (outline.md §8):** practice configuring CLAUDE.md hierarchies,
custom slash commands, path-specific rules, and MCP server integration for a
multi-developer project.

**Domains reinforced:** D3 (Claude Code Configuration & Workflows), D2 (Tool Design &
MCP Integration).

This exercise is config/CLI-shaped, not a Python script — every piece already exists
as a real, working example elsewhere in this repo. Do this exercise by actually
copying these into a real project and testing them live in Claude Code, using the
checklist below.

## Steps and where the example for each lives

1. **Project-level `CLAUDE.md`** with universal standards.
   Copy [`../../domain-3-claude-code-config/examples/CLAUDE.md`](../../domain-3-claude-code-config/examples/CLAUDE.md)
   into a test project's root. Verify: open a fresh Claude Code session in that
   project and confirm it references the testing/style conventions unprompted.

2. **Path-specific `.claude/rules/`** with YAML frontmatter globs.
   Copy [`../../domain-3-claude-code-config/examples/.claude/rules/api.md`](../../domain-3-claude-code-config/examples/.claude/rules/api.md)
   (`paths: ["src/api/**/*"]`) and
   [`.../rules/tests.md`](../../domain-3-claude-code-config/examples/.claude/rules/tests.md)
   (`paths: ["**/*.test.*", "tests/**/*"]`). Verify: edit a file under `src/api/` and
   confirm the API rule's guidance shows up; edit an unrelated file and confirm it
   doesn't.

3. **Project-scoped skill** with `context: fork` and `allowed-tools`.
   Copy [`../../domain-3-claude-code-config/examples/.claude/skills/code-review/SKILL.md`](../../domain-3-claude-code-config/examples/.claude/skills/code-review/SKILL.md).
   Verify: invoke it on a diff and confirm its exploration doesn't fill up the main
   conversation's context (forked), and that it never attempts a `Write`/`Edit`/`Bash`
   call (tool-restricted to read-only).

4. **MCP server config**, project- and user-scoped.
   Copy [`../../domain-2-tool-mcp/examples/04_mcp_server_config/.mcp.json`](../../domain-2-tool-mcp/examples/04_mcp_server_config/.mcp.json)
   to the project root, with real `${GITHUB_TOKEN}` / `${ISSUE_TRACKER_API_KEY}` env
   vars set in your shell. Add a personal experimental server to your own
   `~/.claude.json` (see the README in that same folder for the illustrative shape).
   Verify: both servers' tools are available in the same session simultaneously.

5. **Plan mode vs. direct execution**, across three task shapes.
   Use the three scenarios in
   [`../../domain-3-claude-code-config/examples/plan_mode_notes.md`](../../domain-3-claude-code-config/examples/plan_mode_notes.md)
   as your test cases: a single-file bug fix, a multi-file library migration, and a
   new feature with multiple valid approaches. Observe where plan mode actually
   changed the outcome (caught a bad approach before code was touched) versus where
   it was just overhead.

## What "done" looks like

A short note (a few sentences per step) on what you actually observed at each
verification point above — that observation is the exam-relevant skill, not just
having the files in place.
