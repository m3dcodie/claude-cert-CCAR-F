"""
Task Statements 1.4 & 1.5 — Programmatic enforcement vs prompt-based guidance,
Agent SDK hooks for interception and normalization.

Pattern:  hooks give DETERMINISTIC guarantees; prompt instructions give
          PROBABILISTIC compliance (non-zero failure rate). Use a hook
          whenever a rule must never be violated:
            - PreToolUse-style hook: block a tool call outright if a
              prerequisite hasn't run yet (e.g., no verified customer id
              before process_refund), or if it violates a business rule
              (e.g., refund > $500) — and redirect to an alternative
              workflow (escalation) instead of just failing silently.
            - PostToolUse hook: normalize heterogeneous tool output formats
              (Unix ts / ISO-8601 / numeric status code) BEFORE the model
              reasons over them, so the agent isn't the one guessing formats.
Avoids:   relying on a system-prompt instruction like "always verify the
          customer before refunding" as the ONLY safeguard — a prompt can be
          steered around; a hook cannot.
"""

from datetime import datetime, timezone


class PolicyViolation(Exception):
    def __init__(self, message: str, redirect_to: str):
        super().__init__(message)
        self.redirect_to = redirect_to


class PrerequisiteNotMet(Exception):
    pass


# --- 1.4: programmatic prerequisite gate -----------------------------------

class ConversationState:
    def __init__(self):
        self.verified_customer_id: str | None = None


def pre_tool_use_hook(state: ConversationState, tool_name: str, tool_input: dict) -> None:
    """
    Runs BEFORE a tool call is allowed to execute. This is what makes
    ordering deterministic instead of "the prompt asked nicely for this
    order" — a downstream call is blocked at the hook, not hoped-around.
    """
    if tool_name == "process_refund" and state.verified_customer_id is None:
        raise PrerequisiteNotMet(
            "process_refund blocked: get_customer must return a verified "
            "customer ID before any refund can be processed."
        )

    if tool_name == "process_refund":
        amount = tool_input.get("amount", 0)
        if amount > 500:
            raise PolicyViolation(
                f"Refund of ${amount} exceeds the $500 auto-approval threshold.",
                redirect_to="human_escalation",
            )


def get_customer(customer_id: str) -> dict:
    return {"customer_id": customer_id, "verified": True}


def process_refund(customer_id: str, amount: float) -> dict:
    return {"customer_id": customer_id, "refunded": amount}


def demo_prerequisite_gate():
    print("--- 1.4: prerequisite gate ---")
    state = ConversationState()

    # Attempt 1: refund called before verification -> blocked deterministically.
    try:
        pre_tool_use_hook(state, "process_refund", {"customer_id": "C1", "amount": 50})
    except PrerequisiteNotMet as e:
        print(f"BLOCKED (correct): {e}")

    # Now run the prerequisite for real.
    customer = get_customer("C1")
    state.verified_customer_id = customer["customer_id"]
    print(f"get_customer completed -> verified_customer_id={state.verified_customer_id}")

    # Attempt 2: now allowed.
    pre_tool_use_hook(state, "process_refund", {"customer_id": "C1", "amount": 50})
    result = process_refund("C1", 50)
    print(f"ALLOWED (correct): {result}")


def demo_policy_block_and_escalation():
    print("\n--- 1.5: pre-call policy block + escalation redirect ---")
    state = ConversationState()
    state.verified_customer_id = "C2"  # already verified

    try:
        pre_tool_use_hook(state, "process_refund", {"customer_id": "C2", "amount": 750})
    except PolicyViolation as e:
        print(f"BLOCKED (correct): {e} -> redirecting to {e.redirect_to!r}")
        # A real implementation would now route into a human-escalation
        # workflow with a structured handoff summary (see domain-5 examples).


# --- 1.5: PostToolUse normalization -----------------------------------------

def post_tool_use_normalize(tool_name: str, raw_result: dict) -> dict:
    """
    Different MCP tools return timestamps/status in different shapes. This
    hook normalizes them BEFORE the model sees them, so the agent's
    reasoning isn't the layer responsible for format-guessing.
    """
    normalized = dict(raw_result)

    if "created_unix_ts" in normalized:
        normalized["created_at"] = datetime.fromtimestamp(
            normalized.pop("created_unix_ts"), tz=timezone.utc
        ).isoformat()

    if "created_iso" in normalized:
        normalized["created_at"] = normalized.pop("created_iso")

    status_map = {0: "pending", 1: "shipped", 2: "delivered", 3: "cancelled"}
    if "status_code" in normalized:
        normalized["status"] = status_map.get(normalized.pop("status_code"), "unknown")

    return normalized


def demo_normalization():
    print("\n--- 1.5: PostToolUse normalization across heterogeneous tools ---")
    shipping_tool_result = {"order_id": "A-1", "created_unix_ts": 1_723_000_000, "status_code": 1}
    billing_tool_result = {"order_id": "A-1", "created_iso": "2026-08-20T10:00:00+00:00"}

    print(f"raw (shipping tool):  {shipping_tool_result}")
    print(f"normalized:            {post_tool_use_normalize('shipping', shipping_tool_result)}")
    print(f"raw (billing tool):    {billing_tool_result}")
    print(f"normalized:            {post_tool_use_normalize('billing', billing_tool_result)}")


def main():
    print("=" * 72)
    print("[MOCK] 1.4 & 1.5 — deterministic hooks vs probabilistic prompt guidance")
    print("=" * 72)
    demo_prerequisite_gate()
    demo_policy_block_and_escalation()
    demo_normalization()


if __name__ == "__main__":
    main()
