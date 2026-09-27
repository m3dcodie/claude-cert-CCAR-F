"""
Task Statement 2.1 — Review system prompts for keyword-sensitive instructions
that can override well-written tool descriptions.

Pattern:  a tool description can be perfectly disambiguated (see
          01_tool_description_disambiguation.py) and still get bypassed if
          the SYSTEM PROMPT contains a blunt keyword->tool rule ("if the
          user mentions 'refund', call process_refund"). That instruction
          fires on the literal word, ignoring the tool's own preconditions
          and boundary language, and can misfire on queries that only
          mention the keyword in passing (a policy question, not an
          action request). The fix is an intent/precondition-based
          instruction that defers to the tool's actual scope instead of a
          raw keyword trigger — and a simple audit pass that flags
          keyword-trigger phrasing in a system prompt before it ships.
Avoids:   writing careful tool descriptions and then undoing them with
          "whenever the user says X, call Y" rules in the system prompt;
          assuming a well-described tool is safe from override just
          because ITS OWN text is good — the override lives upstream, in
          the system prompt, not in the tool spec.
"""

import re
from dataclasses import dataclass


# --- BAD: keyword-triggered instruction in the system prompt ----------------

BAD_SYSTEM_PROMPT = """
You are a support assistant.
If the user mentions "refund", call the process_refund tool.
If the user mentions "cancel", call the cancel_order tool.
"""

# --- GOOD: intent + precondition based, deferring to each tool's own scope --

GOOD_SYSTEM_PROMPT = """
You are a support assistant.
Only call process_refund when the user explicitly requests a refund be
issued AND has provided a specific order ID. For general questions about
refund policy or eligibility, answer from documentation and do not call
any tool.
Only call cancel_order when the user explicitly requests cancellation of
an identified, specific order.
"""


@dataclass
class Query:
    text: str
    order_id: str | None
    is_action_request: bool  # explicit "do this" vs. informational question


def route_with_bad_prompt(q: Query) -> str:
    """Simulates the blunt keyword rule: literal word match -> tool call."""
    if "refund" in q.text.lower():
        return "process_refund"
    if "cancel" in q.text.lower():
        return "cancel_order"
    return "no_tool"


def route_with_good_prompt(q: Query) -> str:
    """
    Simulates the intent/precondition rule: only calls the tool when the
    query is an actual action request AND the tool's own precondition
    (order_id present) is satisfied — same boundary the tool description
    already declares, not re-litigated by keyword.
    """
    if "refund" in q.text.lower() and q.is_action_request and q.order_id:
        return "process_refund"
    if "cancel" in q.text.lower() and q.is_action_request and q.order_id:
        return "cancel_order"
    return "no_tool"


# --- Audit pass: flag keyword-trigger phrasing in a system prompt ----------

KEYWORD_TRIGGER_PATTERN = re.compile(
    r"\b(if|when|whenever)\b[^.]*\b(mentions?|says?|contains?|includes?)\b[^.]*"
    r"\bcall\b",
    re.IGNORECASE,
)


def audit_system_prompt(prompt: str) -> list[str]:
    """
    Crude static check for "if the user says/mentions X, call tool Y"
    phrasing — a real review still needs a human, but this catches the
    literal pattern so it doesn't ship unreviewed.
    """
    return [line.strip() for line in prompt.splitlines() if KEYWORD_TRIGGER_PATTERN.search(line)]


def main():
    print("=" * 72)
    print("[MOCK] 2.1 — reviewing system prompts for keyword-sensitive overrides")
    print("=" * 72)

    queries = [
        Query("What's your refund policy for damaged items?", order_id=None, is_action_request=False),
        Query("Please refund order A-1002, it arrived broken.", order_id="A-1002", is_action_request=True),
    ]

    print("\n--- BAD system prompt (keyword trigger) ---")
    print(BAD_SYSTEM_PROMPT.strip())
    for q in queries:
        print(f"\nquery: {q.text!r}")
        print(f"  routed to: {route_with_bad_prompt(q)}"
              f"{'  <-- WRONG: policy question, not an action request' if not q.is_action_request else ''}")

    print("\n--- GOOD system prompt (intent + precondition) ---")
    print(GOOD_SYSTEM_PROMPT.strip())
    for q in queries:
        print(f"\nquery: {q.text!r}")
        print(f"  routed to: {route_with_good_prompt(q)}")

    print("\n--- Audit pass over the BAD prompt ---")
    flags = audit_system_prompt(BAD_SYSTEM_PROMPT)
    for line in flags:
        print(f"  FLAGGED: {line!r}")
    print(f"  ({len(flags)} keyword-trigger instruction(s) found — review before shipping)")

    print("\n--- Audit pass over the GOOD prompt ---")
    flags = audit_system_prompt(GOOD_SYSTEM_PROMPT)
    print(f"  ({len(flags)} keyword-trigger instruction(s) found)")


if __name__ == "__main__":
    main()
