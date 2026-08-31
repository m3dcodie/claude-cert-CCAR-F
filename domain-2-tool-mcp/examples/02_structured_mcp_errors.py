"""
Task Statement 2.2 — Structured error responses for MCP tools.

Pattern:  every tool failure carries `isError`, an `errorCategory`
          (transient/validation/business/permission), `isRetryable`, and a
          human-readable message — so the agent can make an actual recovery
          decision instead of guessing from "Operation failed". A business
          error additionally carries `retriable: false` plus a
          customer-facing explanation. A valid empty result is NOT an error
          at all and must be distinguishable from an access failure.
Avoids:   one generic error shape for everything; treating "zero results"
          the same as "couldn't reach the data source"; retrying a
          validation/business/permission error as if it might succeed next
          time.
"""

from dataclasses import dataclass, field
from typing import Any, Literal

ErrorCategory = Literal["transient", "validation", "business", "permission"]


@dataclass
class ToolResult:
    isError: bool
    content: Any = None
    errorCategory: ErrorCategory | None = None
    isRetryable: bool | None = None
    message: str | None = None
    retriable: bool | None = None  # business-error specific per outline wording


def lookup_order(order_id: str) -> ToolResult:
    """Simulated MCP tool with structured, distinguishable outcomes."""
    if order_id == "TIMEOUT":
        return ToolResult(
            isError=True,
            errorCategory="transient",
            isRetryable=True,
            message="Order service timed out after 5s.",
        )
    if order_id == "":
        return ToolResult(
            isError=True,
            errorCategory="validation",
            isRetryable=False,
            message="order_id must be a non-empty string.",
        )
    if order_id == "OVER_REFUND_LIMIT":
        return ToolResult(
            isError=True,
            errorCategory="business",
            isRetryable=False,
            retriable=False,
            message="Refund amount exceeds the $500 policy limit for this order.",
        )
    if order_id == "NO_PERMISSION":
        return ToolResult(
            isError=True,
            errorCategory="permission",
            isRetryable=False,
            message="Caller lacks the 'orders:read' scope for this account.",
        )
    if order_id == "NOT_FOUND_BUT_VALID_QUERY":
        # Success! Zero matches is not an error — distinct from an access failure.
        return ToolResult(isError=False, content={"matches": []})

    return ToolResult(isError=False, content={"order_id": order_id, "status": "shipped"})


def agent_recovery_policy(result: ToolResult) -> str:
    """
    What an agent SHOULD do with each structured outcome — this is the
    payoff of returning structured metadata instead of a generic failure.
    """
    if not result.isError:
        if result.content.get("matches") == []:
            return "Report to user: no orders matched that query (this is a real, successful answer)."
        return f"Proceed using content: {result.content}"

    if result.errorCategory == "transient" and result.isRetryable:
        return "Retry with backoff (transient, retryable)."
    if result.errorCategory == "validation":
        return f"Do NOT retry as-is; fix the input first: {result.message}"
    if result.errorCategory == "business":
        return f"Do NOT retry; explain to the customer and stop: {result.message}"
    if result.errorCategory == "permission":
        return f"Do NOT retry; escalate for elevated access: {result.message}"
    return "Unhandled error category — escalate to coordinator with full context."


def main():
    print("=" * 72)
    print("[MOCK] 2.2 — structured MCP error responses drive recovery decisions")
    print("=" * 72)

    for order_id in [
        "A-1001",
        "NOT_FOUND_BUT_VALID_QUERY",
        "TIMEOUT",
        "",
        "OVER_REFUND_LIMIT",
        "NO_PERMISSION",
    ]:
        result = lookup_order(order_id)
        decision = agent_recovery_policy(result)
        print(f"\norder_id={order_id!r}")
        print(f"  result:   {result}")
        print(f"  decision: {decision}")


if __name__ == "__main__":
    main()
