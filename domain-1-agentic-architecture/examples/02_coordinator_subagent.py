"""
Task Statement 1.2 — Coordinator-subagent hub-and-spoke orchestration.

Pattern:  a coordinator is the ONLY node that talks to subagents. Subagents
          never call each other. The coordinator: (1) analyzes the query and
          decides which subagents are even needed (not "always run the full
          pipeline"), (2) partitions scope across subagents to avoid
          duplicated work, (3) aggregates results, (4) evaluates the
          synthesis for gaps and re-delegates with targeted follow-ups until
          coverage is sufficient.
Avoids:   letting subagents call each other directly (breaks observability
          and consistent error handling); routing every query through every
          subagent regardless of need; decomposing so narrowly that broad
          topics end up with gaps no single subagent was ever asked about.
"""

from dataclasses import dataclass, field


@dataclass
class SubagentResult:
    subagent: str
    findings: list[str]
    gaps: list[str] = field(default_factory=list)


class WebSearchSubagent:
    name = "web_search"

    def run(self, query: str) -> SubagentResult:
        return SubagentResult(self.name, findings=[f"[web] finding about: {query}"])


class DocAnalysisSubagent:
    name = "doc_analysis"

    def run(self, query: str) -> SubagentResult:
        return SubagentResult(self.name, findings=[f"[docs] finding about: {query}"])


class Coordinator:
    """
    All inter-subagent communication routes through here — subagents never
    see each other's output directly; the coordinator decides what's needed,
    what's passed along, and when coverage is good enough to stop.
    """

    def __init__(self):
        self.subagents = {
            "web_search": WebSearchSubagent(),
            "doc_analysis": DocAnalysisSubagent(),
        }
        self.log: list[str] = []

    def decide_subagents(self, query: str) -> list[str]:
        # Dynamic selection, not "always invoke everything": a narrow factual
        # query doesn't need document analysis.
        if "internal policy" in query or "spec" in query:
            return ["web_search", "doc_analysis"]
        return ["web_search"]

    def run(self, query: str, max_refinement_rounds: int = 2) -> SubagentResult:
        chosen = self.decide_subagents(query)
        self.log.append(f"coordinator: selected subagents {chosen} for query={query!r}")

        all_findings: list[str] = []
        for name in chosen:
            result = self.subagents[name].run(query)
            self.log.append(f"coordinator: received {len(result.findings)} findings from {name}")
            all_findings.extend(result.findings)

        synthesis = SubagentResult("synthesis", findings=all_findings)

        # Iterative refinement: coordinator evaluates its own synthesis for
        # gaps and re-delegates targeted follow-ups rather than accepting a
        # first pass that under-covers a broad topic.
        round_n = 0
        while self._has_coverage_gap(synthesis) and round_n < max_refinement_rounds:
            round_n += 1
            gap_query = f"{query} (follow-up round {round_n}: fill coverage gap)"
            self.log.append(f"coordinator: gap detected, re-delegating -> {gap_query!r}")
            extra = self.subagents["web_search"].run(gap_query)
            synthesis.findings.extend(extra.findings)

        return synthesis

    def _has_coverage_gap(self, synthesis: SubagentResult) -> bool:
        # Toy heuristic: fewer than 2 findings means we probably didn't
        # decompose broadly enough — a stand-in for a real coverage check.
        return len(synthesis.findings) < 2


def main():
    print("=" * 72)
    print("[MOCK] 1.2 — hub-and-spoke coordinator, no real API calls needed for this pattern")
    print("=" * 72)

    coordinator = Coordinator()
    result = coordinator.run("What does the internal policy spec say about refunds?")

    for line in coordinator.log:
        print(line)
    print(f"\nFinal synthesis ({len(result.findings)} findings):")
    for f in result.findings:
        print(f"  - {f}")


if __name__ == "__main__":
    main()
