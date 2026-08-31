"""
Exercise 3: End-to-end structured data extraction pipeline.

Combines: tool_use JSON-schema extraction with nullable/enum-other fields
(D4 4.3), validation-retry with error feedback (D4 4.4), confidence-based
human review routing (D5 5.5), and batch correlation via custom_id (D4 4.5).
"""

import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.mock_client import MockAnthropic, print_mock_banner  # noqa: E402


EXTRACTION_SCHEMA = {
    "name": "extract_invoice",
    "description": "Extract structured fields from an invoice document.",
    "input_schema": {
        "type": "object",
        "properties": {
            "invoice_number": {"type": "string"},
            "stated_total": {"type": "number"},
            "line_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {"description": {"type": "string"}, "amount": {"type": "number"}},
                },
            },
            "payment_terms": {"type": "string", "enum": ["net_30", "net_60", "due_on_receipt", "other"]},
            "confidence": {"type": "number", "description": "Model's self-reported extraction confidence, 0-1."},
        },
        "required": ["invoice_number", "stated_total", "line_items", "payment_terms", "confidence"],
    },
}


@dataclass
class Document:
    custom_id: str
    text: str


@dataclass
class PipelineResult:
    custom_id: str
    extraction: dict | None = None
    validation_errors: list[str] = field(default_factory=list)
    routed_to_human: bool = False


def validate(extraction: dict) -> list[str]:
    errors = []
    calculated = sum(i["amount"] for i in extraction["line_items"])
    if abs(extraction["stated_total"] - calculated) > 0.01:
        errors.append(f"stated_total ({extraction['stated_total']}) != sum(line_items) ({calculated})")
    return errors


CONFIDENCE_THRESHOLD = 0.85  # pretend this came from calibration against a labeled set (D5 5.5)


def extract_with_retry(client: MockAnthropic, doc: Document) -> PipelineResult:
    response = client.messages.create(model="claude-sonnet-5", tools=[EXTRACTION_SCHEMA], messages=[{"role": "user", "content": doc.text}])
    extraction = next(b for b in response.content if b.type == "tool_use").input
    errors = validate(extraction)

    if errors:
        retry_prompt = (
            f"Original document: {doc.text!r}\nYour extraction: {extraction}\n"
            f"Validation errors: {errors}\nCorrect stated_total to match the line items."
        )
        response = client.messages.create(model="claude-sonnet-5", tools=[EXTRACTION_SCHEMA], messages=[{"role": "user", "content": retry_prompt}])
        extraction = next(b for b in response.content if b.type == "tool_use").input
        errors = validate(extraction)

    result = PipelineResult(doc.custom_id, extraction=extraction, validation_errors=errors)
    if not errors and extraction["confidence"] < CONFIDENCE_THRESHOLD:
        result.routed_to_human = True
    return result


def run_pipeline(client: MockAnthropic, docs: list[Document]) -> list[PipelineResult]:
    return [extract_with_retry(client, doc) for doc in docs]


def main():
    print_mock_banner("Exercise 3", "extraction -> validate/retry -> confidence routing -> batch summary")
    client = MockAnthropic()

    docs = [
        Document("doc-1", "Invoice INV-01: $60 + $40 = $100, net 30."),
        Document("doc-2", "Invoice INV-02: $200 + $50, states total $260 (wrong)."),  # needs retry
        Document("doc-3", "Invoice INV-03: $15, due on receipt, handwriting hard to read."),  # low confidence
    ]

    # doc-1: clean extraction, high confidence.
    client.queue_response(stop_reason="tool_use", tool_calls=[{
        "name": "extract_invoice",
        "input": {"invoice_number": "INV-01", "stated_total": 100, "line_items": [{"description": "A", "amount": 60}, {"description": "B", "amount": 40}], "payment_terms": "net_30", "confidence": 0.97},
    }])

    # doc-2: first attempt has a bad total, then a corrected retry.
    client.queue_response(stop_reason="tool_use", tool_calls=[{
        "name": "extract_invoice",
        "input": {"invoice_number": "INV-02", "stated_total": 260, "line_items": [{"description": "A", "amount": 200}, {"description": "B", "amount": 50}], "payment_terms": "net_60", "confidence": 0.9},
    }])
    client.queue_response(stop_reason="tool_use", tool_calls=[{
        "name": "extract_invoice",
        "input": {"invoice_number": "INV-02", "stated_total": 250, "line_items": [{"description": "A", "amount": 200}, {"description": "B", "amount": 50}], "payment_terms": "net_60", "confidence": 0.9},
    }])

    # doc-3: valid but low confidence (hard to read) -> route to human.
    client.queue_response(stop_reason="tool_use", tool_calls=[{
        "name": "extract_invoice",
        "input": {"invoice_number": "INV-03", "stated_total": 15, "line_items": [{"description": "A", "amount": 15}], "payment_terms": "due_on_receipt", "confidence": 0.6},
    }])

    results = run_pipeline(client, docs)

    print("\nPer-document results:")
    for r in results:
        status = "ROUTED TO HUMAN (low confidence)" if r.routed_to_human else ("VALID" if not r.validation_errors else f"INVALID: {r.validation_errors}")
        print(f"  {r.custom_id}: {status}  extraction={r.extraction}")

    auto_processed = [r for r in results if not r.routed_to_human and not r.validation_errors]
    print(f"\nBatch-eligible (auto-processed, no human review needed): {[r.custom_id for r in auto_processed]}")
    print(f"Routed to human review: {[r.custom_id for r in results if r.routed_to_human]}")


if __name__ == "__main__":
    main()
