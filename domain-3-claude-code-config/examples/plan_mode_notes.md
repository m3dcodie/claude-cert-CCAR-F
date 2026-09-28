# Plan mode vs. direct execution — 3 worked scenarios

## Scenario 1: single-file bug fix — SKIP plan mode

"Fix the off-by-one in `paginate()` in `src/api/pages.py`." There's one obvious fix,
one file, low blast radius. Entering plan mode here adds a round trip for no benefit —
just fix it directly and show the diff.

## Scenario 2: multi-file library migration — USE plan mode

"Migrate from `requests` to `httpx` across the codebase." Touches many files, has a
mechanical-but-not-trivial translation (sync→async call sites, exception types
changing, session/client lifecycle differences). Plan mode value here: surfacing *which*
call sites need more than a mechanical swap (e.g., ones relying on `requests`-specific
retry behavior) before 40 files get touched, so the user can correct the approach once
instead of after the fact.

## Scenario 3: new feature with multiple valid approaches — USE plan mode

"Add real-time order status updates to the dashboard." WebSockets vs. SSE vs. polling
are all valid, with different infra tradeoffs the user may have opinions on (existing
infra, ops burden, browser support needed). Plan mode surfaces the choice and its
tradeoffs *before* committing code to one architecture — redirecting after code exists
is much more expensive than redirecting a plan.

## The general signal

Plan mode earns its keep when at least one of these is true: (a) more than one
reasonable implementation approach exists, (b) the change spans enough files/modules
that redirecting after the fact is expensive, (c) requirements are genuinely
underspecified and need exploration before a plan is even possible. None of those are
about *size* alone — a large but fully mechanical change (e.g., a scripted rename
across 200 files) doesn't need it either.

## The Explore subagent inside plan mode

A plan-mode investigation into "migrate from requests to httpx" might need to grep and
read dozens of files to find every call site and understand each one's retry/session
behavior. That exploration is verbose — pages of file contents and search hits — and
none of it needs to sit in the main conversation once it's done being useful. The
**Explore** subagent runs that discovery phase in its own isolated context and returns
just a summary (e.g., "40 call sites across 12 files; 6 rely on requests-specific
retry behavior and need more than a mechanical swap"). This is what keeps a
multi-phase investigation from exhausting the main context window before a plan is
even written — see
[`04_plan_mode_and_explore.py`](./04_plan_mode_and_explore.py) for a simulation of
the isolation effect, and Domain 5 Task Statement 5.4's
[`04_scratchpad_and_delegation.py`](../../domain-5-context-reliability/examples/04_scratchpad_and_delegation.py)
for the same "isolate verbose exploration, keep only the summary" pattern applied to
codebase exploration generally.
