"""
Task Statement 2.1 — Tool description quality drives tool selection.

Pattern:  the tool description is the PRIMARY signal an LLM uses to pick
          between similar tools. This simulates a simple description-based
          router (a stand-in for the model's own selection) to make the
          effect visible: near-identical descriptions cause misrouting;
          differentiated ones (purpose, input shape, boundary vs the other
          tool) don't.
Avoids:   minimal one-line descriptions ("Analyzes content.") on tools that
          are semantically close to another tool; leaving two tools with
          overlapping wording instead of renaming + narrowing one of them.
"""

from dataclasses import dataclass


@dataclass
class ToolSpec:
    name: str
    description: str


def keyword_overlap_score(query: str, description: str) -> int:
    """
    Toy stand-in for "the model's tool-selection reasoning" — real Claude
    reasons over full semantics, not keyword overlap, but this is enough to
    demonstrate why vague/overlapping descriptions cause ambiguous scores
    while differentiated ones produce a clear winner.
    """
    query_words = set(query.lower().split())
    desc_words = set(description.lower().replace(",", "").split())
    return len(query_words & desc_words)


def route(query: str, tools: list[ToolSpec]) -> tuple[str, dict[str, int]]:
    scores = {t.name: keyword_overlap_score(query, t.description) for t in tools}
    winner = max(scores, key=scores.get)
    return winner, scores


# --- BAD: overlapping, minimal descriptions ---------------------------------

bad_tools = [
    ToolSpec("analyze_content", "Analyzes content and returns insights."),
    ToolSpec("analyze_document", "Analyzes a document and returns insights."),
]

# --- GOOD: differentiated purpose, input shape, and explicit boundary ------

good_tools = [
    ToolSpec(
        "extract_web_results",
        "Extracts structured facts from a live web page given a URL. Use this "
        "ONLY for URLs fetched from the internet, not for local files or "
        "already-uploaded documents. Returns title, published_date, and key "
        "claims with byte offsets.",
    ),
    ToolSpec(
        "summarize_content",
        "Produces a short prose summary of an uploaded document (PDF/DOCX) "
        "already available in this conversation. Use this for local/uploaded "
        "files, NOT for fetching new content from a URL. Returns a 3-5 "
        "sentence summary string.",
    ),
]


def main():
    print("=" * 72)
    print("[MOCK] 2.1 — tool description quality vs selection reliability")
    print("=" * 72)

    query = "analyze this web page and pull out the key facts"

    print("\n--- BAD: near-identical descriptions ---")
    winner, scores = route(query, bad_tools)
    print(f"scores: {scores}")
    print(f"routed to: {winner}  <-- ambiguous, could easily flip on wording noise")

    print("\n--- GOOD: differentiated descriptions with explicit boundaries ---")
    winner, scores = route(query, good_tools)
    print(f"scores: {scores}")
    print(f"routed to: {winner}  <-- clear winner because 'web page' only matches one tool")

    # Splitting an overly generic tool into purpose-specific ones (2.1 skill):
    split_tools = [
        ToolSpec(
            "extract_data_points",
            "Extracts specific structured fields (dates, amounts, names) from "
            "a document into a typed schema. Use when you need discrete values.",
        ),
        ToolSpec(
            "verify_claim_against_source",
            "Checks whether a specific claim/sentence is supported by a given "
            "source document. Use when validating an assertion, not extracting.",
        ),
    ]
    query2 = "check whether this sentence is actually supported by the report"
    winner2, scores2 = route(query2, split_tools)
    print("\n--- Split-tool example (was one 'analyze_document' tool) ---")
    print(f"scores: {scores2}")
    print(f"routed to: {winner2}  <-- unambiguous because roles no longer overlap")


if __name__ == "__main__":
    main()
