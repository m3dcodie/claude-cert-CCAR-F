"""
Task Statement 4.6 — Multi-instance and multi-pass review architectures.

Pattern:  a model that just generated code retains its own reasoning
          context and is less likely to challenge its own decisions in the
          same session. An INDEPENDENT second instance, with no prior
          reasoning context, catches more. For large multi-file changes,
          split into per-file local-analysis passes plus a SEPARATE
          cross-file integration pass, rather than one pass over everything
          (attention dilution + contradictory findings).
Avoids:   "self-review" instructions on the same instance that generated
          the code as a substitute for real independence; a single review
          pass over many files at once for anything non-trivial.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.mock_client import MockAnthropic, print_mock_banner  # noqa: E402


def demo_self_review_vs_independent(client: MockAnthropic):
    print("--- 4.6: self-review (same instance) vs independent second instance ---")

    # The generating instance already "decided" this code was fine while
    # writing it — asking it to self-review reuses that same reasoning path.
    client.queue_response(
        stop_reason="end_turn",
        text="Self-review: looks correct, no issues found.",
    )
    self_review = client.messages.create(
        model="claude-sonnet-5",
        messages=[
            {"role": "assistant", "content": "def divide(a, b): return a / b"},
            {"role": "user", "content": "Review the code you just wrote."},
        ],
    )
    print(f"  self-review (same instance): {self_review.content[0].text!r}")

    # A fresh instance with only the code, no generation history, catches
    # what the generator's own reasoning had already talked itself past.
    client.queue_response(
        stop_reason="end_turn",
        text="Issue: no handling for b == 0, will raise ZeroDivisionError uncaught.",
    )
    independent_review = client.messages.create(
        model="claude-sonnet-5",
        messages=[{"role": "user", "content": "Review this code:\ndef divide(a, b): return a / b"}],
    )
    print(f"  independent instance (fresh):  {independent_review.content[0].text!r}")
    print("  (independent instance found the ZeroDivisionError the generator missed)")


def demo_multi_pass_review(client: MockAnthropic):
    print("\n--- 4.6: per-file local passes + separate cross-file integration pass ---")

    files = {
        "orders.py": "def create_order(items): return Order(items)",
        "billing.py": "def charge(order): return Order(order.items).total()",  # re-constructs Order, bug
    }

    print("  Local pass (per file, no cross-file context):")
    for fname, code in files.items():
        client.queue_response(stop_reason="end_turn", text=f"{fname}: no local issues found")
        resp = client.messages.create(model="claude-sonnet-5", messages=[{"role": "user", "content": code}])
        print(f"    {resp.content[0].text}")

    print("  Cross-file integration pass (sees both files together):")
    client.queue_response(
        stop_reason="end_turn",
        text=(
            "billing.py:charge() re-constructs an Order from order.items instead of "
            "using the Order instance passed in from orders.py:create_order() — "
            "duplicated construction logic, will drift if Order's constructor changes. "
            "(invisible in either file's local pass alone)"
        ),
    )
    resp = client.messages.create(
        model="claude-sonnet-5",
        messages=[{"role": "user", "content": f"Cross-file review:\n{files}"}],
    )
    print(f"    {resp.content[0].text}")


def main():
    print_mock_banner("4.6", "independent review instances + per-file/integration split")
    client = MockAnthropic()
    demo_self_review_vs_independent(client)
    demo_multi_pass_review(client)


if __name__ == "__main__":
    main()
