"""
Task Statement 2.3 — Distribute tools across agents; configure tool_choice.

Pattern:  give each agent only the tools its role needs (not "give
          everyone everything") — a synthesis agent with a web_search tool
          will sometimes use it instead of synthesizing. tool_choice has 3
          modes: "auto" (may return text instead of a tool call), "any"
          (must call A tool, model picks which), forced
          {"type": "tool", "name": "..."} (must call THIS tool).
Avoids:   handing every agent the full tool catalog "just in case" (18
          tools on one agent measurably degrades selection reliability vs.
          4-5); using tool_choice: "auto" when you actually need a
          guaranteed tool call (e.g., enforcing a required first step).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.mock_client import MockAnthropic, print_mock_banner  # noqa: E402


# --- Scoped tool distribution -----------------------------------------------

ALL_TOOLS = [
    "web_search", "load_document", "extract_data_points", "verify_fact",
    "summarize_content", "send_email", "process_refund", "get_customer",
    "update_ticket", "close_ticket", "translate_text", "ocr_scan",
    "calendar_lookup", "geocode_address", "currency_convert", "sentiment_score",
    "spell_check", "generate_chart",
]

ROLE_TOOLS = {
    # Scoped: each role gets only what it needs, plus ONE deliberate
    # high-frequency cross-role tool where justified (verify_fact for synthesis).
    "search_agent": ["web_search", "load_document"],
    "synthesis_agent": ["summarize_content", "verify_fact"],
    "refund_agent": ["get_customer", "process_refund"],
}


def demo_scoped_distribution():
    print("--- 2.3: scoped tool distribution ---")
    print(f"Unscoped (anti-pattern): every agent gets all {len(ALL_TOOLS)} tools.")
    for role, tools in ROLE_TOOLS.items():
        print(f"  {role}: {len(tools)} tools -> {tools}")
    print(
        "  (going from ~4-5 tools to ~18 on one agent measurably degrades "
        "tool-selection reliability — this is why refund_agent doesn't also "
        "get web_search, generate_chart, etc.)"
    )


# --- tool_choice modes -------------------------------------------------------

def demo_tool_choice_modes():
    print("\n--- 2.3: tool_choice modes ---")
    client = MockAnthropic()

    # "auto": model may return plain text instead of calling a tool.
    client.queue_response(stop_reason="end_turn", text="I don't need a tool for this, here's the answer.")
    resp = client.messages.create(
        model="claude-sonnet-5", tool_choice={"type": "auto"}, messages=[{"role": "user", "content": "hi"}]
    )
    print(f"tool_choice=auto   -> stop_reason={resp.stop_reason} (model chose NOT to call a tool)")

    # "any": model must call some tool, but picks which.
    client.queue_response(stop_reason="tool_use", tool_calls=[{"name": "verify_fact", "input": {"claim": "x"}}])
    resp = client.messages.create(
        model="claude-sonnet-5", tool_choice={"type": "any"}, messages=[{"role": "user", "content": "check this"}]
    )
    called = resp.content[0].name
    print(f"tool_choice=any    -> stop_reason={resp.stop_reason}, model picked: {called}")

    # forced: must call this exact tool (e.g. to guarantee ordering — run
    # extract_metadata before any enrichment tool, in a follow-up turn).
    client.queue_response(
        stop_reason="tool_use",
        tool_calls=[{"name": "extract_metadata", "input": {"doc_id": "D-1"}}],
    )
    resp = client.messages.create(
        model="claude-sonnet-5",
        tool_choice={"type": "tool", "name": "extract_metadata"},
        messages=[{"role": "user", "content": "process this document"}],
    )
    forced_call = resp.content[0]
    assert forced_call.name == "extract_metadata"
    print(f"tool_choice=forced -> stop_reason={resp.stop_reason}, guaranteed call: {forced_call.name}")
    print("  (enrichment tools would run in a LATER turn, after this forced first step)")


def main():
    print_mock_banner("2.3", "scoped tool distribution + tool_choice auto/any/forced")
    demo_scoped_distribution()
    demo_tool_choice_modes()


if __name__ == "__main__":
    main()
