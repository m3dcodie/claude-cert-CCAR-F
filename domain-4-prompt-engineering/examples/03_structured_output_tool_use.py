"""
Task Statement 4.3 — Enforce structured output using tool_use + JSON schemas.

Pattern:  define an extraction "tool" whose input_schema IS the desired
          output shape; read the structured result out of the tool_use
          block instead of parsing free-text/JSON-in-a-string (which
          eliminates syntax errors, though NOT semantic ones like a total
          that doesn't match its line items). Nullable fields let the model
          say "not present" instead of inventing a value to satisfy
          `required`. Enums get an "other" + detail-string escape hatch for
          categories you know are incomplete.
Avoids:   asking the model to "respond with JSON" in prose (parseable but
          not guaranteed valid); making every field required, which
          pressures the model to fabricate values for genuinely absent data.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.mock_client import MockAnthropic, print_mock_banner  # noqa: E402


INVOICE_EXTRACTION_SCHEMA = {
    "name": "extract_invoice",
    "description": "Extract structured fields from an invoice document.",
    "input_schema": {
        "type": "object",
        "properties": {
            "invoice_number": {"type": "string"},
            "total_amount": {"type": "number"},
            # Nullable: many invoices don't have a PO number. Making this
            # required would pressure the model to invent one.
            "purchase_order_number": {"type": ["string", "null"]},
            "line_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "amount": {"type": "number"},
                    },
                    "required": ["description", "amount"],
                },
            },
            # enum + "other" + detail: extensible without an open free-text field.
            "payment_terms": {
                "type": "string",
                "enum": ["net_30", "net_60", "due_on_receipt", "other"],
            },
            "payment_terms_detail": {
                "type": ["string", "null"],
                "description": "Required when payment_terms == 'other'; null otherwise.",
            },
        },
        "required": ["invoice_number", "total_amount", "line_items", "payment_terms"],
    },
}


def extract(client: MockAnthropic, document_text: str, tool_choice: dict) -> dict:
    response = client.messages.create(
        model="claude-sonnet-5",
        tools=[INVOICE_EXTRACTION_SCHEMA],
        tool_choice=tool_choice,
        messages=[{"role": "user", "content": document_text}],
    )
    tool_call = next(b for b in response.content if b.type == "tool_use")
    return tool_call.input


def demo_nullable_field():
    print("--- 4.3: nullable field instead of fabricated value ---")
    client = MockAnthropic()
    client.queue_response(
        stop_reason="tool_use",
        tool_calls=[{
            "name": "extract_invoice",
            "input": {
                "invoice_number": "INV-2201",
                "total_amount": 450.00,
                "purchase_order_number": None,  # correctly null, not invented
                "line_items": [{"description": "Consulting hours", "amount": 450.00}],
                "payment_terms": "net_30",
                "payment_terms_detail": None,
            },
        }],
    )
    result = extract(client, "Invoice INV-2201, total $450, net 30 terms.", {"type": "tool", "name": "extract_invoice"})
    print(f"  extracted: {result}")
    assert result["purchase_order_number"] is None
    print("  (no PO number in the source -> null, not a fabricated string)")


def demo_enum_other_pattern():
    print("\n--- 4.3: enum + 'other' + detail for an extensible category ---")
    client = MockAnthropic()
    client.queue_response(
        stop_reason="tool_use",
        tool_calls=[{
            "name": "extract_invoice",
            "input": {
                "invoice_number": "INV-2202",
                "total_amount": 900.00,
                "purchase_order_number": "PO-77",
                "line_items": [{"description": "Hardware", "amount": 900.00}],
                "payment_terms": "other",
                "payment_terms_detail": "50% upfront, 50% on delivery",
            },
        }],
    )
    result = extract(client, "Invoice INV-2202, 50% upfront 50% on delivery.", {"type": "tool", "name": "extract_invoice"})
    print(f"  extracted: {result}")
    assert result["payment_terms"] == "other" and result["payment_terms_detail"]
    print("  (non-standard term captured via 'other' + detail, schema stayed closed)")


def demo_tool_choice_any_unknown_doc_type():
    print("\n--- 4.3: tool_choice='any' when the document type is unknown up front ---")
    client = MockAnthropic()
    receipt_schema = {
        "name": "extract_receipt",
        "description": "Extract fields from a retail receipt (not an invoice).",
        "input_schema": {
            "type": "object",
            "properties": {"merchant": {"type": "string"}, "total": {"type": "number"}},
            "required": ["merchant", "total"],
        },
    }
    client.queue_response(
        stop_reason="tool_use",
        tool_calls=[{"name": "extract_receipt", "input": {"merchant": "Corner Store", "total": 12.50}}],
    )
    response = client.messages.create(
        model="claude-sonnet-5",
        tools=[INVOICE_EXTRACTION_SCHEMA, receipt_schema],
        tool_choice={"type": "any"},
        messages=[{"role": "user", "content": "Corner Store receipt, total $12.50"}],
    )
    tool_call = next(b for b in response.content if b.type == "tool_use")
    print(f"  model self-selected schema: {tool_call.name} (correctly picked receipt over invoice)")


def main():
    print_mock_banner("4.3", "tool_use + JSON schema structured extraction")
    demo_nullable_field()
    demo_enum_other_pattern()
    demo_tool_choice_any_unknown_doc_type()


if __name__ == "__main__":
    main()
