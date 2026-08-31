# Task Statement 3.2 — Personal skill variants

The shared `code-review` skill in
[`.claude/skills/code-review/SKILL.md`](./.claude/skills/code-review/SKILL.md) is
committed and used by the whole team as-is. If one developer wants to experiment with
stricter criteria (say, also flagging missing docstrings) without changing what
everyone else gets, they create a **personal** variant under their own
`~/.claude/skills/` with a **different name** — never by editing the shared one in
place.

Illustrative personal variant (not written to a real home directory by this repo):

```
~/.claude/skills/code-review-strict/SKILL.md
```

```markdown
---
name: code-review-strict
description: Personal variant of code-review with stricter criteria (also flags missing docstrings on public functions).
context: fork
allowed-tools: Read, Grep, Glob
---

Same as the shared `code-review` skill, plus: flag any public function (no leading
underscore) that has no docstring.
```

Because the name is different (`code-review-strict` vs. `code-review`) and the file
lives under the personal `~/.claude/skills/` directory rather than the project's
`.claude/skills/`, this never gets committed and never affects a teammate invoking the
shared `code-review` skill — the two coexist without conflict.
