"""
Task Statement 5.3 — Error propagation across multi-agent systems.

Pattern:  structured error context (failure type, what was attempted,
          partial results, alternatives) lets the coordinator make a real
          recovery decision. Access failures (timeout) are NOT the same as
          valid empty results (query succeeded, nothing matched) -- keep
          them visibly distinct. Subagents try local recovery for transient
          failures first; only genuinely unresolvable errors propagate up,
          carrying partial results and what was attempted.
Avoids:   a subagent returning "no results" for BOTH a timeout and a
          real empty match (indistinguishable to the coordinator); killing
          the whole workflow because one subagent failed; a bare
          "search unavailable" string with no actionable context.
"""

from dataclasses import dataclass, field
from enum import Enum


class Outcome(Enum):
    SUCCESS_WITH_RESULTS = "success_with_results"
    SUCCESS_EMPTY = "success_empty"          # valid empty result, NOT an error
    ACCESS_FAILURE = "access_failure"        # needs a retry/escalation decision
    UNRECOVERABLE = "unrecoverable"          # propagated after local recovery failed


@dataclass
class SubagentReport:
    outcome: Outcome
    results: list[str] = field(default_factory=list)
    attempted: str = ""
    partial_results: list[str] = field(default_factory=list)
    alternatives: list[str] = field(default_factory=list)


def search_subagent(query: str, simulate: str) -> SubagentReport:
    if simulate == "timeout_then_local_recovery_succeeds":
        # Local recovery: retry once locally instead of immediately
        # bubbling the transient failure up to the coordinator.
        return SubagentReport(
            outcome=Outcome.SUCCESS_WITH_RESULTS,
            results=["finding after local retry"],
            attempted=f"searched {query!r}, first attempt timed out, retried locally and succeeded",
        )
    if simulate == "timeout_unrecoverable":
        return SubagentReport(
            outcome=Outcome.UNRECOVERABLE,
            attempted=f"searched {query!r}, timed out twice, local retry budget exhausted",
            partial_results=["partial finding gathered before final timeout"],
            alternatives=["try a narrower query", "try a different data source"],
        )
    if simulate == "valid_empty":
        return SubagentReport(
            outcome=Outcome.SUCCESS_EMPTY,
            attempted=f"searched {query!r}, query executed successfully",
        )
    raise ValueError(simulate)


def coordinator_handle(report: SubagentReport) -> str:
    """
    This is the payoff: distinct outcomes produce distinct, correct
    coordinator behavior -- nothing gets silently swallowed or conflated.
    """
    if report.outcome == Outcome.SUCCESS_WITH_RESULTS:
        return f"proceed with {len(report.results)} result(s): {report.results}"
    if report.outcome == Outcome.SUCCESS_EMPTY:
        return "report to user: query ran successfully, genuinely no matches (NOT an error)"
    if report.outcome == Outcome.UNRECOVERABLE:
        return (
            f"proceed with partial coverage ({report.partial_results}), "
            f"annotate output with a coverage gap, note attempted='{report.attempted}', "
            f"consider alternatives={report.alternatives} -- do NOT abort the whole workflow"
        )
    raise ValueError(f"unhandled outcome: {report.outcome}")


def main():
    print("=" * 72)
    print("[MOCK] 5.3 — structured error propagation vs generic failure / silent empty results")
    print("=" * 72)

    scenarios = ["timeout_then_local_recovery_succeeds", "valid_empty", "timeout_unrecoverable"]
    for scenario in scenarios:
        report = search_subagent("refund policy exceptions", scenario)
        decision = coordinator_handle(report)
        print(f"\nscenario: {scenario}")
        print(f"  subagent report: outcome={report.outcome.value}, attempted={report.attempted!r}")
        print(f"  coordinator decision: {decision}")


if __name__ == "__main__":
    main()
