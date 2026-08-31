"""
Task Statement 3.4 — Plan mode vs direct execution, and the Explore
subagent for isolating verbose discovery.

Pattern:  choose plan mode when a task has architectural implications
          (large-scale change, multiple valid approaches, multi-file
          scope); choose direct execution for a well-scoped, single-file,
          single-approach change. Within plan mode, delegate verbose
          discovery to the Explore subagent so pages of grep/read output
          never enter the main conversation -- only the summary does.
Avoids:   entering plan mode for a trivial fix (pure overhead); doing deep
          multi-file discovery directly in the main context, filling it
          with search noise before a single line of the actual plan exists.
"""

from dataclasses import dataclass


@dataclass
class Task:
    description: str
    files_affected: int
    multiple_valid_approaches: bool
    clear_single_fix: bool


def decide_mode(task: Task) -> str:
    if task.clear_single_fix and task.files_affected <= 1 and not task.multiple_valid_approaches:
        return "DIRECT EXECUTION: well-scoped, single approach, minimal blast radius."
    if task.multiple_valid_approaches or task.files_affected >= 10:
        return "PLAN MODE: architectural implications or wide blast radius -- explore and design first."
    return "DIRECT EXECUTION: moderate scope but no real ambiguity in approach."


TASKS = [
    Task("Add a null check before line 42 in orders.py, per the stack trace", files_affected=1, multiple_valid_approaches=False, clear_single_fix=True),
    Task("Migrate the codebase from requests to httpx", files_affected=45, multiple_valid_approaches=False, clear_single_fix=False),
    Task("Add real-time order updates to the dashboard (WebSockets vs SSE vs polling)", files_affected=8, multiple_valid_approaches=True, clear_single_fix=False),
]


def demo_mode_selection():
    print("--- 3.4: plan mode vs direct execution ---")
    for t in TASKS:
        print(f"  '{t.description}'")
        print(f"    -> {decide_mode(t)}")


def verbose_grep_discovery(module: str) -> list[str]:
    """Stand-in for what a REAL discovery pass looks like: many raw hits."""
    return [f"{module}/client.py:{i}: requests.{method}(...)" for i, method in enumerate(["get", "post", "put"] * 4, start=1)]


def explore_subagent_isolated_discovery(module: str) -> str:
    """
    The Explore subagent runs the verbose pass in its OWN context and
    returns only a compact summary -- the main conversation never sees the
    12 raw grep hits directly.
    """
    raw_hits = verbose_grep_discovery(module)
    call_count = len(raw_hits)
    methods_used = sorted({line.split("requests.")[1].split("(")[0] for line in raw_hits})
    return f"{module}: {call_count} requests call sites found, methods used: {methods_used}"


def demo_explore_subagent_isolation():
    print("\n--- 3.4: Explore subagent isolates verbose discovery ---")
    modules = ["billing", "notifications"]

    main_conversation_context = []  # only summaries land here
    total_raw_hits_that_would_have_leaked = 0

    for module in modules:
        raw_hits = verbose_grep_discovery(module)
        total_raw_hits_that_would_have_leaked += len(raw_hits)
        summary = explore_subagent_isolated_discovery(module)
        main_conversation_context.append(summary)

    print("  main conversation context after delegated discovery (summaries only):")
    for line in main_conversation_context:
        print(f"    {line}")
    print(f"  raw hits generated during discovery: {total_raw_hits_that_would_have_leaked}")
    print(f"  raw hits that entered main context: 0  (all isolated in the Explore subagent)")


def main():
    print("=" * 72)
    print("[MOCK] 3.4 — plan mode vs direct execution; Explore subagent isolation")
    print("=" * 72)
    demo_mode_selection()
    demo_explore_subagent_isolation()


if __name__ == "__main__":
    main()
