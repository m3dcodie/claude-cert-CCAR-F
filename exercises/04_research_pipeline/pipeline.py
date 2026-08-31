"""
Exercise 4: Multi-agent research pipeline with parallel spawning, error
propagation, and provenance-preserving synthesis.

Combines: parallel Task spawning (D1 1.2/1.3), structured error propagation
distinguishing access failures from valid results (D5 5.3), and
provenance-preserving synthesis of conflicting sources (D5 5.6).
"""

import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.mock_client import MockAnthropic, print_mock_banner  # noqa: E402


@dataclass
class Finding:
    claim: str
    source_name: str
    source_url: str
    published_date: str


@dataclass
class SubagentReport:
    subagent: str
    ok: bool
    findings: list[Finding] = field(default_factory=list)
    attempted: str = ""
    partial_findings: list[Finding] = field(default_factory=list)
    alternatives: list[str] = field(default_factory=list)


def spawn_subagents_in_parallel(client: MockAnthropic, query: str) -> list[str]:
    """Coordinator emits multiple Task calls in ONE turn (D1 1.3)."""
    client.queue_response(
        stop_reason="tool_use",
        tool_calls=[
            {"name": "Task", "input": {"subagent_type": "web_search", "prompt": f"Research goal: {query}"}},
            {"name": "Task", "input": {"subagent_type": "doc_analysis", "prompt": f"Research goal: {query}"}},
        ],
    )
    response = client.messages.create(model="claude-sonnet-5", messages=[{"role": "user", "content": query}])
    task_calls = [b for b in response.content if b.type == "tool_use" and b.name == "Task"]
    return [c.input["subagent_type"] for c in task_calls]


def web_search_subagent(query: str) -> SubagentReport:
    return SubagentReport(
        "web_search", ok=True,
        findings=[
            Finding(
                "Industry-wide return rate averaged 8.5% in Q2 2026.",
                "Retail Trends Report", "https://retail-trends.example.com/q2-2026", "2026-07-10",
            )
        ],
        attempted=f"web search for {query!r}",
    )


def doc_analysis_subagent_with_timeout(query: str) -> SubagentReport:
    """Simulates a timeout that IS locally unrecoverable and must propagate
    structured error context (D5 5.3) rather than a bare 'failed' string."""
    return SubagentReport(
        "doc_analysis", ok=False,
        attempted=f"analyzed internal policy docs for {query!r}, timed out after 2 retries",
        partial_findings=[
            Finding(
                "Internal policy doc (partially read before timeout) states a 45-day refund window.",
                "Internal Policy Wiki (partial)", "https://intranet.example.com/policy/refunds", "2026-08-20",
            )
        ],
        alternatives=["retry with a narrower doc scope", "fall back to the cached policy summary"],
    )


def conflicting_source_finding() -> Finding:
    return Finding(
        "Internal Q2 report states an 11% return rate for the same period.",
        "Internal Q2 Ops Report", "https://intranet.example.com/reports/q2-ops", "2026-07-15",
    )


def synthesize_with_provenance(reports: list[SubagentReport]) -> str:
    lines = ["## Synthesis"]

    industry_return_rate = next(f for r in reports for f in r.findings if "8.5%" in f.claim)
    refund_window = next(f for r in reports for f in r.partial_findings if "refund window" in f.claim)
    internal_return_rate = conflicting_source_finding()  # 11%, same metric as industry_return_rate -- genuine conflict

    lines.append("\n### Well-established")
    lines.append(f"- {refund_window.claim} [{refund_window.source_name}, {refund_window.published_date}]")

    lines.append("\n### Contested (conflicting sources on the SAME metric -- both preserved, not arbitrarily resolved)")
    lines.append(f"- {industry_return_rate.claim} [{industry_return_rate.source_name}, {industry_return_rate.published_date}]")
    lines.append(f"- {internal_return_rate.claim} [{internal_return_rate.source_name}, {internal_return_rate.published_date}]")

    lines.append("\n### Coverage gaps")
    for r in reports:
        if not r.ok:
            lines.append(
                f"- {r.subagent}: incomplete -- attempted='{r.attempted}', "
                f"proceeding with {len(r.partial_findings)} partial finding(s), "
                f"alternatives considered: {r.alternatives}"
            )
    return "\n".join(lines)


def main():
    print_mock_banner("Exercise 4", "parallel subagents, error propagation, provenance-preserving synthesis")
    client = MockAnthropic()

    query = "What is our current product return rate and refund policy window?"

    spawned = spawn_subagents_in_parallel(client, query)
    print(f"Coordinator spawned {len(spawned)} subagents in ONE turn: {spawned}")

    start = time.monotonic()
    reports = [web_search_subagent(query), doc_analysis_subagent_with_timeout(query)]
    elapsed = time.monotonic() - start
    print(f"(both subagents 'ran' -- {elapsed*1000:.1f}ms wall time in this simulation, "
          f"illustrating parallel vs. sequential is a runtime property, not shown by mocked calls alone)")

    for r in reports:
        status = "OK" if r.ok else "FAILED (structured, not silent)"
        print(f"\n  subagent={r.subagent} status={status}")
        print(f"    attempted: {r.attempted}")
        if not r.ok:
            print(f"    partial_findings: {[f.claim for f in r.partial_findings]}")
            print(f"    alternatives: {r.alternatives}")

    print()
    print(synthesize_with_provenance(reports))


if __name__ == "__main__":
    main()
