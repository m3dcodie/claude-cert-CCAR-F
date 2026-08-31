"""
Task Statement 5.2 — Escalation triggers and ambiguity resolution.

Pattern:  escalate immediately on an explicit human request; offer to
          resolve first when the issue is in-policy and within capability,
          even if the customer sounds frustrated; escalate when policy is
          silent/ambiguous on the specific request, not just when a case
          feels complex; never guess between multiple ambiguous customer
          matches — ask for another identifier.
Avoids:   using sentiment ("customer sounds upset") or the model's own
          self-reported confidence as the escalation trigger — neither
          reliably tracks actual case complexity or policy applicability.
"""

from dataclasses import dataclass


@dataclass
class Case:
    customer_message: str
    explicit_human_request: bool
    sentiment: str  # "neutral" | "frustrated" -- deliberately NOT used as a trigger
    policy_covers_request: bool
    multiple_customer_matches: bool = False


def decide_escalation(case: Case) -> str:
    # Trigger 1: explicit request -- immediate, no investigation first.
    if case.explicit_human_request:
        return "ESCALATE_IMMEDIATELY: customer explicitly asked for a human."

    # Trigger 2 (before anything else): ambiguous customer identity needs
    # clarification, not a heuristic guess and not automatic escalation.
    if case.multiple_customer_matches:
        return "ASK_FOR_CLARIFICATION: multiple customer matches, request another identifier."

    # Trigger 3: genuine policy gap/exception -- not "this is hard", but
    # "policy doesn't actually address this specific request."
    if not case.policy_covers_request:
        return "ESCALATE: policy is silent on this specific request (exception, not just complexity)."

    # Otherwise: resolve it, regardless of sentiment. Frustration alone is
    # not a complexity signal and is not, by itself, an escalation trigger.
    return "RESOLVE: in-policy and within capability -- acknowledge sentiment if any, then resolve."


CASES = [
    Case(
        customer_message="I want to speak to a human right now.",
        explicit_human_request=True, sentiment="neutral", policy_covers_request=True,
    ),
    Case(
        customer_message="This is RIDICULOUS, my package is late!! Fix it now.",
        explicit_human_request=False, sentiment="frustrated", policy_covers_request=True,
    ),
    Case(
        customer_message="Can you match a competitor's lower price? Policy only covers matching OUR own site's price drops.",
        explicit_human_request=False, sentiment="neutral", policy_covers_request=False,
    ),
    Case(
        customer_message="I need a refund on my last order.",
        explicit_human_request=False, sentiment="neutral", policy_covers_request=True,
        multiple_customer_matches=True,
    ),
]


def main():
    print("=" * 72)
    print("[MOCK] 5.2 — escalation triggers: explicit request, policy gap, ambiguous identity")
    print("[MOCK] (sentiment is shown but deliberately NOT used as a trigger)")
    print("=" * 72)

    for case in CASES:
        decision = decide_escalation(case)
        print(f"\nmessage: {case.customer_message!r}")
        print(f"sentiment: {case.sentiment} (informational only, not a trigger)")
        print(f"decision: {decision}")


if __name__ == "__main__":
    main()
