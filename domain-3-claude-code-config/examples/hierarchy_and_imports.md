# Task Statement 3.1 — CLAUDE.md hierarchy, `@import`, and `.claude/rules/`

## The three levels

| Level | Path | Shared with team? | Scope |
|---|---|---|---|
| User | `~/.claude/CLAUDE.md` | **No** — lives in your home dir, not version control | Every project you open |
| Project | `.claude/CLAUDE.md` or root `CLAUDE.md` | **Yes** — committed to the repo | Everyone working in this repo |
| Directory | `<subdir>/CLAUDE.md` | Yes, if committed | Only work under that subdirectory |

## The classic diagnostic case

> "I told Claude to always run `pytest -q` before finishing, and it works for me but
> not for my teammate."

If that instruction lives in **your** `~/.claude/CLAUDE.md`, it only ever applied to
your sessions — it was never in version control, so your teammate's Claude Code never
saw it. The fix is moving it into the project-level `CLAUDE.md` (see
[`./CLAUDE.md`](./CLAUDE.md) in this folder) so it's committed and applies to everyone.
Run `/memory` in a session to see exactly which memory files are currently loaded —
that's the direct way to confirm whether an instruction is present at all, and at
which level.

## `@import` — keeping CLAUDE.md modular

Instead of duplicating shared standards into every package's `CLAUDE.md`, a package
can import them:

```markdown
# packages/billing/CLAUDE.md

@import ../../standards/monetary-values.md
@import ../../standards/testing.md

## Billing-specific
- All monetary amounts are integer cents internally, never floats.
- Every charge path needs an idempotency key.
```

The package maintainer only has to write what's actually specific to their package;
the shared standards files (`standards/monetary-values.md`, `standards/testing.md`)
are maintained once and pulled in wherever they're relevant — a maintainer who knows
their package touches money knows to import `monetary-values.md`, without needing to
re-author it.

## `.claude/rules/` vs. one monolithic CLAUDE.md

A `CLAUDE.md` that has grown to cover testing conventions, API conventions, and
deployment steps all in one file gets loaded in full on every single session,
regardless of what's being worked on. Splitting it into
[`.claude/rules/api.md`](./.claude/rules/api.md),
[`.claude/rules/tests.md`](./.claude/rules/tests.md), and a hypothetical
`deployment.md` means each topic only loads when its `paths` glob actually matches
what's being edited (Task Statement 3.3) — a session editing `src/api/orders.py`
never pays the token cost of the deployment rules.
