# Project conventions (example team CLAUDE.md)

**Level: project** (`.claude/CLAUDE.md` or root `CLAUDE.md`, committed to version
control). This is the level a rule needs to be at for the whole team to get it — a
teammate not receiving an instruction here is usually a sign it was accidentally
written into their personal `~/.claude/CLAUDE.md` instead (see
[`hierarchy_and_imports.md`](./hierarchy_and_imports.md)).

This file applies to every session opened in this repo — it's the "everyone gets the
same baseline" layer. Keep it short and concrete; put anything path-specific in
`.claude/rules/` instead so it only loads when relevant, and pull in shared standards
with `@import` rather than duplicating them per package.

## Testing

- Every new function in `src/` needs a corresponding test in `tests/`, same relative
  path with a `test_` prefix.
- Run `pytest -q` before considering any change done. Don't report a task complete
  without having run it.
- Prefer real fixtures over mocks for anything touching the database layer.

## Code style

- Python: type hints on all function signatures, no bare `except:`.
- Keep functions under ~40 lines; extract a helper if you're going over.

## Architecture constraints

- No new MCP server dependency without adding it to `.mcp.json` (never hardcode
  credentials — use `${ENV_VAR}` expansion).
- Business-rule enforcement (thresholds, prerequisite ordering) belongs in hooks, not
  only in prompt instructions — see `domain-1-agentic-architecture/examples/04_hooks_enforcement.py`
  for the pattern this team follows.
