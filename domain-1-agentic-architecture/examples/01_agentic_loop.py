"""
Task Statement 1.1 — Implement agentic loop control flow.

Pattern:  loop while stop_reason == "tool_use", append tool results to the
          conversation, stop on stop_reason == "end_turn".
Avoids:   (a) parsing assistant text for phrases like "I'm done" to decide
          whether to stop, (b) using a hard iteration cap as the *primary*
          stop condition instead of a safety backstop, (c) treating "the
          model produced some text" as completion — it can emit text AND
          still want to call a tool in the same turn.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.mock_client import MockAnthropic, print_mock_banner  # noqa: E402

MAX_ITERATIONS = 8  # safety backstop only — NOT the loop's stopping condition


def get_order_status(order_id: str) -> dict:
    """Pretend tool implementation."""
    return {"order_id": order_id, "status": "shipped", "eta_days": 2}


TOOLS = {"get_order_status": get_order_status}


def run_agentic_loop(client: MockAnthropic, user_message: str) -> str:
    messages = [{"role": "user", "content": user_message}]
    iterations = 0

    while True:
        iterations += 1
        if iterations > MAX_ITERATIONS:
            # Safety backstop — should be rare in practice, never the intended path.
            raise RuntimeError("Exceeded max iterations without end_turn; investigate.")

        response = client.messages.create(model="claude-sonnet-5", messages=messages)
        messages.append({"role": "assistant", "content": response.content})

        # Correct stop condition: stop_reason, not "did we see text".
        if response.stop_reason == "end_turn":
            final_text = "".join(b.text for b in response.content if b.type == "text")
            return final_text

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                result = TOOLS[block.name](**block.input)
                # Tool results are appended to context so the model can reason
                # about them on the next turn — this is what makes the loop
                # "agentic" rather than a single fixed call.
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result),
                    }
                )
            messages.append({"role": "user", "content": tool_results})
            continue  # loop again; do NOT stop just because a tool was called

        raise RuntimeError(f"Unhandled stop_reason: {response.stop_reason}")


def main():
    print_mock_banner("1.1", "agentic loop keyed on stop_reason")
    client = MockAnthropic()

    # Turn 1: model decides to call a tool.
    client.queue_response(
        stop_reason="tool_use",
        tool_calls=[{"name": "get_order_status", "input": {"order_id": "A-1001"}}],
    )
    # Turn 2: model has the tool result, produces a final answer.
    client.queue_response(
        stop_reason="end_turn",
        text="Order A-1001 has shipped and is 2 days out.",
    )

    answer = run_agentic_loop(client, "Where is order A-1001?")
    print(f"Final answer: {answer}")
    print(f"API calls made: {len(client.calls)} (one per loop iteration)")


if __name__ == "__main__":
    main()
