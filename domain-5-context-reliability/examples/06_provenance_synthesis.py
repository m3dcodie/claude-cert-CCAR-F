"""
Task Statement 5.6 — Provenance and uncertainty in multi-source synthesis.

Pattern:  every claim carries a claim -> source mapping (URL/doc name,
          excerpt, publication date) that survives synthesis instead of
          being compressed away. Conflicting statistics from credible
          sources are presented WITH both values and their attribution --
          never silently resolved by picking one. Dates travel with claims
          so a real temporal difference isn't misread as a contradiction.
          Different content types render in their natural form (financial
          data as tables, news as prose) rather than one flattened shape.
Avoids:   a synthesis step that drops source_url/date fields while
          compressing findings into prose; arbitrarily picking one of two
          conflicting numbers instead of surfacing both.
"""

from dataclasses import dataclass


@dataclass
class Finding:
    claim: str
    source_name: str
    source_url: str
    published_date: str


def lossy_synthesis(findings: list[Finding]) -> str:
    """Anti-pattern: compress to prose, provenance falls out."""
    return " ".join(f.claim for f in findings)


def provenance_preserving_synthesis(findings: list[Finding]) -> str:
    """Each claim keeps its source and date through synthesis."""
    lines = ["## Findings (with provenance)"]
    for f in findings:
        lines.append(f"- {f.claim} [{f.source_name}, {f.published_date}]({f.source_url})")
    return "\n".join(lines)


def demo_provenance_loss_vs_preservation():
    print("--- 5.6: lossy synthesis vs provenance-preserving synthesis ---")
    findings = [
        Finding(
            "The refund window is 45 days.",
            "Internal Policy Wiki", "https://intranet.example.com/policy/refunds", "2026-08-20",
        ),
        Finding(
            "Q2 return rate was 4.1%.",
            "Q2 Ops Report", "https://intranet.example.com/reports/q2-ops", "2026-07-15",
        ),
    ]
    print("  lossy (anti-pattern):")
    print(f"    {lossy_synthesis(findings)}")
    print("  provenance-preserving:")
    print(provenance_preserving_synthesis(findings))


def demo_conflicting_sources():
    print("\n--- 5.6: conflicting stats from credible sources, both preserved ---")
    conflict = [
        Finding("Customer satisfaction score: 4.2/5", "CS Dashboard (live)", "https://cs.internal/dashboard", "2026-08-25"),
        Finding("Customer satisfaction score: 3.8/5", "Q2 Board Report", "https://reports.internal/q2-board", "2026-07-01"),
    ]
    print("  NOT resolved by picking one -- both surfaced, annotated as conflicting, with dates:")
    print(f"    - {conflict[0].claim} ({conflict[0].source_name}, {conflict[0].published_date})")
    print(f"    - {conflict[1].claim} ({conflict[1].source_name}, {conflict[1].published_date})")
    print("  annotation: values differ; note the ~2 month date gap before assuming a real contradiction")
    print("  (this could be genuine improvement over time, NOT conflicting measurements of the same period)")


def demo_content_type_rendering():
    print("\n--- 5.6: rendering different content types in their natural form ---")
    financial = {"Q1": 120_000, "Q2": 135_500, "Q3": 128_900}
    print("  financial data -> table:")
    print("    | Quarter | Revenue  |")
    print("    |---------|----------|")
    for q, v in financial.items():
        print(f"    | {q}      | ${v:,}  |")

    news_items = ["Regulatory filing published clarifying data retention rules."]
    print("  news -> prose:")
    for item in news_items:
        print(f"    {item}")

    technical_findings = ["Auth token TTL reduced from 24h to 1h.", "New refresh-token rotation deployed."]
    print("  technical findings -> structured list:")
    for f in technical_findings:
        print(f"    - {f}")


def main():
    print("=" * 72)
    print("[MOCK] 5.6 — provenance preservation, conflicting sources, content-type rendering")
    print("=" * 72)
    demo_provenance_loss_vs_preservation()
    demo_conflicting_sources()
    demo_content_type_rendering()


if __name__ == "__main__":
    main()
