# Domain 3: Claude Code Configuration & Workflows (20%)

## Task Statement 3.1 — Configure CLAUDE.md files with appropriate hierarchy, scoping, and modular organization

**Knowledge:** three levels of `CLAUDE.md` apply together — **user-level**
(`~/.claude/CLAUDE.md`, personal, never shared via version control), **project-level**
(`.claude/CLAUDE.md` or a root `CLAUDE.md`, shared with the whole team), and
**directory-level** (a `CLAUDE.md` inside a subdirectory, scoped to work under it). A
common failure mode: a new teammate "isn't getting" the team's instructions because
they were written into that person's own `~/.claude/CLAUDE.md` rather than the
project-level file — user-level settings never propagate to anyone else. The `@import`
syntax pulls an external file into a `CLAUDE.md` (e.g. a package's `CLAUDE.md`
importing a shared standards doc) so common content isn't duplicated across every
package. `.claude/rules/` is the alternative to one large monolithic `CLAUDE.md` —
splitting by topic instead of accumulating everything in one file. The `/memory`
command lists which memory files are actually loaded in the current session, which is
how you diagnose "why isn't Claude following this instruction" or "why does behavior
differ between sessions."

**Skills:** diagnose a hierarchy issue by checking which level an instruction actually
lives at (`/memory` shows this directly); use `@import` to selectively pull in only the
standards relevant to a given package instead of hand-copying them; split an
overgrown `CLAUDE.md` into `.claude/rules/testing.md`, `api-conventions.md`,
`deployment.md`, etc.

**Example:** [`examples/CLAUDE.md`](./examples/CLAUDE.md),
[`examples/hierarchy_and_imports.md`](./examples/hierarchy_and_imports.md),
[`examples/01_claude_md_hierarchy.py`](./examples/01_claude_md_hierarchy.py)

## Task Statement 3.2 — Create and configure custom slash commands and skills

**Knowledge:** project-scoped commands live in `.claude/commands/` and are shared via
version control; user-scoped commands live in `~/.claude/commands/` and are personal.
Skills live in `.claude/skills/<name>/SKILL.md` with frontmatter: `context: fork` runs
the skill in an isolated sub-agent context so its (often verbose) output doesn't
pollute the main conversation; `allowed-tools` restricts what the skill can do while
running (e.g., write-only, no `Bash`); `argument-hint` prompts the developer for a
required parameter when the skill is invoked with none supplied. A developer can
create a personal variant of a shared skill under `~/.claude/skills/` with a different
name, so their experimentation doesn't affect teammates using the shared one. The
general choice: **skills** for on-demand, task-specific workflows; **CLAUDE.md** for
standards that should always be loaded, every session, no invocation needed.

**Skills:** put team-wide commands in `.claude/commands/`; set `context: fork` on
skills with verbose or exploratory output (codebase analysis, brainstorming
alternatives); scope `allowed-tools` down to what the skill actually needs (e.g.,
write-only to block destructive actions); add `argument-hint` so an under-specified
invocation prompts for the missing parameter instead of guessing; decide skill vs.
`CLAUDE.md` based on whether the behavior should be always-on or invoked per task.

**Example:** [`examples/.claude/commands/review-pr.md`](./examples/.claude/commands/review-pr.md),
[`examples/.claude/skills/code-review/SKILL.md`](./examples/.claude/skills/code-review/SKILL.md),
[`examples/personal_skill_variant.md`](./examples/personal_skill_variant.md),
[`examples/02_commands_and_skills.py`](./examples/02_commands_and_skills.py)

## Task Statement 3.3 — Apply path-specific rules for conditional convention loading

**Knowledge:** `.claude/rules/*.md` files carry YAML frontmatter with a `paths` glob
list; a rule loads into context only when a file being edited matches its glob,
keeping irrelevant conventions out of context and off the token budget. Glob-pattern
rules beat directory-level `CLAUDE.md` files specifically when a convention spans
files scattered across the tree by *type* rather than *location* — e.g. test files
living next to the code they test throughout the repo, not gathered under one
`tests/` directory.

**Skills:** write `paths: ["terraform/**/*"]`-style frontmatter so a rule only loads
for matching files; use a type-based glob (`**/*.test.tsx`) to apply one convention
everywhere that file type appears, regardless of directory; choose path-specific rules
over subdirectory `CLAUDE.md` files whenever the convention doesn't line up with the
directory tree.

**Example:** [`examples/.claude/rules/api.md`](./examples/.claude/rules/api.md),
[`examples/.claude/rules/tests.md`](./examples/.claude/rules/tests.md),
[`examples/03_path_specific_rule_loading.py`](./examples/03_path_specific_rule_loading.py)

## Task Statement 3.4 — Determine when to use plan mode vs direct execution

**Knowledge:** plan mode fits complex tasks — large-scale change, several valid
approaches, architectural decisions, multi-file scope — because it lets you explore
and design safely before anything is committed, avoiding costly rework. Direct
execution fits simple, well-scoped changes (one function, one clear fix). The
**Explore** subagent isolates a verbose discovery phase (grepping/reading widely) into
its own context, returning only a summary — this is what keeps a long multi-phase task
from exhausting the main conversation's context window.

**Skills:** choose plan mode for architecturally significant work (a migration
touching 45+ files, a restructuring with multiple valid infrastructure approaches);
choose direct execution for a well-understood, clearly-scoped fix (a stack-trace-clear
bug fix, one added conditional); reach for the Explore subagent specifically to keep
verbose discovery output out of the main context during a multi-phase task; combine
the two — plan mode to investigate and decide the approach, then direct execution to
carry out the plan.

**Example:** [`examples/plan_mode_notes.md`](./examples/plan_mode_notes.md),
[`examples/04_plan_mode_and_explore.py`](./examples/04_plan_mode_and_explore.py)

## Task Statement 3.5 — Apply iterative refinement techniques for progressive improvement

**Knowledge:** when a prose description gets interpreted inconsistently, 2-3 concrete
input/output examples communicate the intended transformation far more reliably than
more prose. **Test-driven iteration**: write the test suite first (expected behavior,
edge cases, performance requirements), then iterate by feeding back actual test
failures rather than re-describing what's wrong in words. The **interview pattern**:
have Claude ask clarifying questions before implementing, to surface considerations
(cache invalidation, failure modes) the developer may not have thought to specify up
front. When issues interact, put them all in one detailed message so the fix accounts
for the interaction; when they're independent, fix them one at a time so each change
stays easy to verify in isolation.

**Skills:** give 2-3 concrete input/output pairs when natural-language instructions
keep producing inconsistent results; write the test suite before the implementation
and iterate against real failures; use the interview pattern in unfamiliar domains
before writing code; give specific input/expected-output test cases for edge-case
fixes (e.g., null handling in a migration script); batch interacting issues into one
message, keep independent issues sequential.

**Example:** [`examples/05_iterative_refinement.py`](./examples/05_iterative_refinement.py)

## Task Statement 3.6 — Integrate Claude Code into CI/CD pipelines

**Knowledge:** `-p` / `--print` runs Claude Code non-interactively, which is required
in a pipeline — without it, a prompt for input just hangs the job. `--output-format
json` plus `--json-schema` forces machine-parseable structured output, so CI can post
findings as inline PR comments programmatically instead of parsing free text.
`CLAUDE.md` is how CI-invoked Claude Code gets the same project context (testing
standards, fixture conventions, review criteria) an interactive session would have.
The same session that generated code is measurably worse at reviewing its own
changes than an independent instance would be (same root cause as Domain 4 Task
Statement 4.6) — CI review steps should spin up a fresh session, not reuse the
generation session.

**Skills:** always run CI invocations with `-p`; pair `--output-format json` with
`--json-schema` to get structured findings ready for automated PR comment posting;
when re-reviewing after new commits, include prior findings in context and instruct
Claude to report only new/unaddressed issues, avoiding duplicate comments; provide
existing test files in context so generated tests don't duplicate coverage that
already exists; document testing standards and available fixtures in `CLAUDE.md` so
CI-generated tests are actually useful instead of low-value boilerplate.

**Example:** [`examples/ci/review-workflow.yml`](./examples/ci/review-workflow.yml),
[`examples/06_ci_cd_integration.py`](./examples/06_ci_cd_integration.py)
