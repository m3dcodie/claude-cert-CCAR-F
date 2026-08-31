# Domain 3: Claude Code Configuration & Workflows (20%)

> **Note on source material:** `outline.md`'s "Detailed Objectives by Domain" section
> jumps from Domain 2 straight to Domain 4 — the numbered Task Statement breakdown for
> Domain 3 isn't present in the copy provided (likely a copy/paste gap when the outline
> was compiled). The topics below are reconstructed from `outline.md`'s domain summary
> bullet ("Configuring and customizing Claude Code for team workflows using CLAUDE.md
> files, Agent Skills, MCP server integrations, and plan mode") and from **Exercise 2**
> in §8, which explicitly targets this domain. If you get the real numbered task
> statements later, slot them in here — the example code won't need to change, just
> the citations.

## Topic: CLAUDE.md configuration hierarchy

**Knowledge:** `CLAUDE.md` files apply hierarchically — a project-level file at the repo
root sets universal standards every team member and every session picks up
automatically, with no per-developer setup. This is the mechanism for "everyone on the
team gets the same conventions" without relying on each person remembering them.

**Skills:** write a project-level `CLAUDE.md` with concrete, checkable standards
(testing conventions, style rules, architectural constraints) rather than vague
aspirations — a rule Claude can actually apply is one stated as a concrete instruction,
not a vibe.

**Example:** [`examples/CLAUDE.md`](./examples/CLAUDE.md)

## Topic: Path-specific rules (`.claude/rules/`)

**Knowledge:** `.claude/rules/*.md` files carry YAML frontmatter with a `paths` glob
list. A rule only loads into context when the file(s) being worked on match its glob —
so API conventions don't clutter context while editing tests, and vice versa. This
keeps `CLAUDE.md` itself from growing into an unfocused catch-all.

**Skills:** scope each rule file tightly to the area it governs (`src/api/**/*` for API
conventions, `**/*.test.*` for testing conventions) instead of one giant always-loaded
document; verify a rule loads only when a matching file is actually being edited.

**Example:** [`examples/.claude/rules/api.md`](./examples/.claude/rules/api.md),
[`examples/.claude/rules/tests.md`](./examples/.claude/rules/tests.md)

## Topic: Custom Agent Skills

**Knowledge:** a project-scoped skill lives in `.claude/skills/<name>/SKILL.md` with
frontmatter options like `context: fork` (the skill runs in an isolated forked context
so its intermediate work doesn't pollute the main conversation) and `allowed-tools`
(restricts what the skill can do, same rationale as scoping tools per-agent in Domain
2 Task Statement 2.3).

**Skills:** author a skill with a narrow, well-described trigger condition; set
`context: fork` for skills that produce a lot of intermediate tool output the caller
doesn't need verbatim; restrict `allowed-tools` to the minimum the skill's job requires.

**Example:** [`examples/.claude/skills/code-review/SKILL.md`](./examples/.claude/skills/code-review/SKILL.md)

## Topic: MCP server integration

Covered in depth under [Domain 2, Task Statement 2.4](../domain-2-tool-mcp/README.md#task-statement-24--integrate-mcp-servers-into-claude-code-and-agent-workflows) —
project-scoped `.mcp.json` vs. user-scoped `~/.claude.json`, env-var expansion for
credentials, and MCP resources. That material is directly part of "Claude Code
Configuration & Workflows" too; it's kept in one place rather than duplicated.

## Topic: Plan mode vs. direct execution

**Knowledge:** plan mode's value scales with task ambiguity and blast radius, not with
raw size. A single-file bug fix with an obvious fix doesn't need a planning pass — it
just adds latency. A multi-file library migration or a new feature with several valid
implementation approaches benefits from plan mode because it surfaces the approach (and
lets you redirect it) *before* files start changing, which is exactly when redirecting
is cheap.

**Skills:** recognize the signal for plan mode — multiple valid approaches, cross-file
blast radius, or architectural ambiguity — versus a task with one obvious fix where
direct execution is faster and plan mode is just overhead.

**Example:** [`examples/plan_mode_notes.md`](./examples/plan_mode_notes.md)
