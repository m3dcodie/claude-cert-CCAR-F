# Contributing

This repo maps 1:1 to the [CCAR-F exam guide](./outline.md): 5 domain folders,
each with theory notes, runnable examples, and tagged quiz questions. Useful
contributions stay inside that shape rather than growing new ones.

## What's welcome

- **Fixes** to an example, a domain `README.md`, `outline.md`, or `quiz_bank.md` —
  wrong explanation, broken script, outdated task-statement numbering.
- **New examples** for a task statement that's under-covered (theory in a
  domain README with no matching runnable pattern, or only one narrow example).
- **New quiz questions**, tagged to an existing task statement.
- **New exercises** only if they genuinely combine multiple domains the way
  `exercises/01`–`04` do — open an issue to discuss scope first.

Not a fit: rewrites of existing correct content, unrelated tooling, or
anything that requires a live Anthropic API key to run (see below).

## Conventions to match

**Examples (`domain-*/examples/*.py`)**
- Self-contained, runs standalone: `python3 domain-N-.../examples/NN_name.py`.
- No API key. Import `common/mock_client.py` and queue scripted responses —
  don't call the real Anthropic API from an example (this is offline-first by
  design, so anyone can run it without a key or spend).
- Docstring at the top names the **Task Statement** it covers, the **Pattern**
  it demonstrates, and the **anti-pattern(s)** it **Avoids** — follow the shape
  already used in any existing example file.
- Filename: next number in that domain's sequence (`07_name.py`). If you're
  adding a second/third example for a task statement that already has one,
  use a lettered suffix on that same number (`01_a_name.py`, `01_b_name.py`),
  matching `domain-2-tool-mcp/examples/01_a_input_output_contracts.py`.
- Wire it in: add a link to the new file on the matching task statement's
  `**Example:**` line in that domain's `README.md`. Multiple examples for one
  task statement are comma-separated on that line — see
  `domain-2-tool-mcp/README.md` T.S. 2.1 for the pattern.

**Quiz questions (`quiz_bank.md`)**
- Add under the matching `### T.S. x.y` heading, numbered `**Qn.**` with
  options `A.`–`D.`.
- Add the answer + a one-to-two sentence explanation to that domain's
  `<details><summary>Answer key — Domain N</summary>` block at the end of the
  section, as `**Qn — LETTER.**`.
- Scenario-based (a concrete failure or situation), not a definition lookup —
  match the existing question style.

**Theory notes (`domain-*/README.md`, `outline.md`)**
- Keep task-statement numbering (`T.S. x.y`) identical across `outline.md`,
  the domain README, and any quiz tags that reference it — they're
  cross-referenced by that number.

## Before opening a PR

- Run any script you added or changed and confirm it exits `0` with sane
  output — no unrelated debug prints left in.
- If you added an example, confirm the domain README actually links it.
- Keep the diff scoped to the fix/addition — no drive-by reformatting of
  unrelated sections.

## Reporting issues / feedback

Open a GitHub issue. Say which file (`domain-N.../README.md`,
`examples/NN_name.py`, `quiz_bank.md` question tag, `outline.md`) and what's
wrong or missing — a wrong answer key, an example that doesn't run, a task
statement that's thin. General feedback ("this section was confusing",
"more coverage needed on X") is welcome too, even without a fix attached.
