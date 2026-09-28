"""
Exercise 1: Multi-Tool Agent with Escalation Logic.

Combines: differentiated tool descriptions (D2 2.1), the stop_reason
agentic loop (D1 1.1), structured MCP-style error responses (D2 2.2), a
programmatic pre-call enforcement hook (D1 1.4/1.5), and multi-concern
decomposition with escalation (D1 1.4, D5 5.2).
"""

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.mock_client import MockAnthropic, print_mock_banner  # noqa: E402


# --- Tools: two intentionally similar ones, differentiated per D2 2.1 ------

TOOL_SPECS = [
    {
        "name": "get_order_status",
        "description": (
            "Returns ONLY the current shipping status and ETA for one order "
            "(e.g., 'shipped', 2 days). Use for 'where is my order' questions. "
            "Does NOT return price or line-item detail -- use get_order_details for that."
        ),
    },
    {
        "name": "get_order_details",
        "description": (
            "Returns the full line-item breakdown and price for one order. "
            "Use for 'what did I pay for' / refund-amount questions. "
            "Does NOT return shipping status -- use get_order_status for that."
        ),
    },
    {"name": "get_customer", "description": "Looks up and verifies a customer by customer_id."},
    {"name": "process_refund", "description": "Issues a refund for a verified customer's order."},
]


def get_order_status(order_id: str) -> dict:
    return {"order_id": order_id, "status": "shipped", "eta_days": 2}


def get_order_details(order_id: str) -> dict:
    return {"order_id": order_id, "amount": 89.50, "items": ["Wireless Mouse", "USB-C Cable"]}


def get_customer(customer_id: str) -> dict:
    return {"customer_id": customer_id, "verified": True}


def process_refund(customer_id: str, order_id: str, amount: float) -> dict:
    return {"customer_id": customer_id, "order_id": order_id, "refunded": amount}


TOOL_IMPLS = {
    "get_order_status": get_order_status,
    "get_order_details": get_order_details,
    "get_customer": get_customer,
    "process_refund": process_refund,
}


# --- Structured tool error responses (D2 2.2) -------------------------------

ErrorCategory = Literal["transient", "validation", "business", "permission"]


@dataclass
class ToolResult:
    isError: bool
    content: dict | None = None
    errorCategory: ErrorCategory | None = None
    isRetryable: bool | None = None
    message: str | None = None


# --- Programmatic enforcement hook (D1 1.4/1.5) -----------------------------

class PrerequisiteNotMet(Exception):
    pass


class PolicyViolation(Exception):
    def __init__(self, message: str, redirect_to: str):
        super().__init__(message)
        self.redirect_to = redirect_to


REFUND_THRESHOLD = 500.0


@dataclass
class ConversationState:
    verified_customer_id: str | None = None


def pre_tool_use_hook(state: ConversationState, tool_name: str, tool_input: dict) -> None:
    if tool_name == "process_refund":
        if state.verified_customer_id is None:
            raise PrerequisiteNotMet(
                "process_refund blocked: get_customer must verify the customer first."
            )
        if tool_input.get("amount", 0) > REFUND_THRESHOLD:
            raise PolicyViolation(
                f"Refund of ${tool_input['amount']} exceeds ${REFUND_THRESHOLD} auto-approval limit.",
                redirect_to="human_escalation",
            )


def execute_tool_call(state: ConversationState, name: str, tool_input: dict) -> ToolResult:
    try:
        pre_tool_use_hook(state, name, tool_input)
    except PrerequisiteNotMet as e:
        return ToolResult(isError=True, errorCategory="validation", isRetryable=False, message=str(e))
    except PolicyViolation as e:
        return ToolResult(
            isError=True, errorCategory="business", isRetryable=False,
            message=f"{e} Redirecting to {e.redirect_to}.",
        )

    result = TOOL_IMPLS[name](**tool_input)
    if name == "get_customer" and result.get("verified"):
        state.verified_customer_id = result["customer_id"]
    return ToolResult(isError=False, content=result)


# --- Agentic loop (D1 1.1) --------------------------------------------------

def run_agentic_loop(client: MockAnthropic, state: ConversationState, user_message: str) -> str:
    messages = [{"role": "user", "content": user_message}]
    for _ in range(6):  # safety backstop, not the stop condition
        response = client.messages.create(model="claude-sonnet-5", tools=TOOL_SPECS, messages=messages)
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            return "".join(b.text for b in response.content if b.type == "text")

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                result = execute_tool_call(state, block.name, block.input)
                tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": str(result)})
            messages.append({"role": "user", "content": tool_results})
            continue

    raise RuntimeError("Exceeded safety backstop without end_turn.")


# --- Multi-concern decomposition (D1 1.4, D5 5.2) ---------------------------

def handle_multi_concern_message(client: MockAnthropic) -> None:
    print("--- Multi-concern message: 'where is my order, and can I get a $750 refund on it?' ---")
    state = ConversationState()

    # Concern 1: order status.
    client.queue_response(
        stop_reason="tool_use",
        tool_calls=[{"name": "get_order_status", "input": {"order_id": "A-1001"}}],
    )
    client.queue_response(stop_reason="end_turn", text="Order A-1001 has shipped, 2 days out.")
    status_answer = run_agentic_loop(client, state, "Where is order A-1001?")
    print(f"  concern 1 (status): {status_answer}")

    # Concern 2: refund request over the auto-approval threshold -- verify,
    # then get blocked by the hook and see the structured business error.
    client.queue_response(
        stop_reason="tool_use",
        tool_calls=[{"name": "get_customer", "input": {"customer_id": "C-9"}}],
    )
    client.queue_response(
        stop_reason="tool_use",
        tool_calls=[{"name": "process_refund", "input": {"customer_id": "C-9", "order_id": "A-1001", "amount": 750}}],
    )
    client.queue_response(
        stop_reason="end_turn",
        text="I can't auto-approve a $750 refund (over our $500 limit) -- I've flagged this for a human agent to review.",
    )
    refund_answer = run_agentic_loop(client, state, "Can I get a $750 refund on order A-1001?")
    print(f"  concern 2 (refund):  {refund_answer}")

    print("\n  synthesized response to customer:")
    print(f"    1) {status_answer}")
    print(f"    2) {refund_answer}")


def main():
    print_mock_banner("Exercise 1", "multi-tool agent with structured errors + escalation hook")
    client = MockAnthropic()
    handle_multi_concern_message(client)


if __name__ == "__main__":
    main()
