"""
Task Statement 5.1 — Persistent case-facts block vs lossy progressive
summarization; trimming verbose tool output.

Pattern:  extract precise transactional facts (amounts, dates, order ids,
          statuses) into a small persistent block carried in EVERY prompt,
          kept outside the part of history that gets summarized — so
          repeated summarization can't blur a number into "a modest
          amount." Trim verbose tool results down to the fields that
          actually matter before they accumulate across turns.
Avoids:   letting numeric/date precision degrade through repeated
          "summarize the summary" passes; carrying all 40 fields of a tool
          result in context when only 5 are ever used downstream.
"""

from dataclasses import dataclass, field


@dataclass
class CaseFacts:
    """Persistent, structured — never itself summarized."""
    order_id: str | None = None
    amount: float | None = None
    promised_date: str | None = None
    status: str | None = None

    def as_prompt_block(self) -> str:
        fields = {k: v for k, v in self.__dict__.items() if v is not None}
        return "CASE FACTS (authoritative, do not summarize further):\n" + "\n".join(
            f"  {k}: {v}" for k, v in fields.items()
        )


def progressive_summarization_demo():
    print("--- 5.1: progressive summarization loses precision ---")
    turn_1 = "Customer ordered item A-1001 for $129.99, promised delivery by 2026-09-05."
    # Round 1 summary
    summary_1 = "Customer has an order around $130, due early September."
    # Round 2 summary (summarizing the summary)
    summary_2 = "Customer has an order, some amount, due soon."

    print(f"  original:   {turn_1}")
    print(f"  summary v1: {summary_1}")
    print(f"  summary v2: {summary_2}")
    print("  (by v2, the exact amount $129.99, the exact date 2026-09-05, and the order id are all gone)")


def case_facts_demo():
    print("\n--- 5.1: case-facts block stays exact regardless of summarization ---")
    facts = CaseFacts(order_id="A-1001", amount=129.99, promised_date="2026-09-05", status="shipped")

    # Even if the surrounding conversation gets progressively summarized,
    # this block is injected fresh into every prompt, untouched.
    conversation_summary_v2 = "Customer has an order, some amount, due soon."
    full_prompt = f"{facts.as_prompt_block()}\n\nConversation summary: {conversation_summary_v2}"
    print(full_prompt)
    print("  (exact amount/date/order id survive even though the prose summary degraded)")


def trim_verbose_tool_output():
    print("\n--- 5.1: trimming verbose tool output to relevant fields ---")
    raw_order_lookup = {
        "order_id": "A-1001", "amount": 129.99, "status": "shipped", "promised_date": "2026-09-05",
        "warehouse_id": "W-77", "carrier_internal_code": "C-909", "packaging_type": "box-M",
        "sku_list_raw": ["SKU-1", "SKU-2"], "internal_routing_hash": "8f3a...", "customer_segment_score": 0.62,
        "fulfillment_center_lat": 47.6, "fulfillment_center_lon": -122.3, "picking_batch_id": "PB-4471",
        # ... imagine ~30 more internal fields
    }
    relevant_for_returns = {"order_id", "amount", "status", "promised_date"}
    trimmed = {k: v for k, v in raw_order_lookup.items() if k in relevant_for_returns}

    print(f"  raw tool result: {len(raw_order_lookup)} fields")
    print(f"  trimmed for a returns conversation: {len(trimmed)} fields -> {trimmed}")
    print("  (the other fields would just accumulate token cost across every future turn)")


def main():
    print("=" * 72)
    print("[MOCK] 5.1 — case facts vs lossy summarization; trimming tool output")
    print("=" * 72)
    progressive_summarization_demo()
    case_facts_demo()
    trim_verbose_tool_output()


if __name__ == "__main__":
    main()
