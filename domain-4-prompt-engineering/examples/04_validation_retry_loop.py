"""
Task Statement 4.4 — Validation, retry-with-error-feedback, and the limits
of retrying.

Pattern:  on a semantic validation failure (values don't sum, wrong field),
          send a follow-up request with the ORIGINAL document, the FAILED
          extraction, and the SPECIFIC error — the model can usually
          self-correct a structural mistake. Retry is USELESS when the
          missing information simply isn't in the source document; that
          case needs to be flagged as missing, not retried. A
          `detected_pattern` field on findings lets you analyze what keeps
          triggering false positives, in aggregate, later.
Avoids:   retrying blindly without telling the model what was wrong;
          retrying indefinitely on a document that genuinely lacks the
          requested field (wastes calls, never converges).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.mock_client import MockAnthropic, print_mock_banner  # noqa: E402


def validate_extraction(extraction: dict) -> list[str]:
    """Semantic validation tool_use schemas don't catch on their own."""
    errors = []
    stated = extraction.get("stated_total")
    calculated = sum(item["amount"] for item in extraction.get("line_items", []))
    if stated is not None and abs(stated - calculated) > 0.01:
        errors.append(
            f"stated_total ({stated}) does not match sum of line_items ({calculated})"
        )
    return errors


def retry_is_worthwhile(errors: list[str], source_document: str) -> bool:
    """
    Distinguish "format/structural error, retry will likely fix it" from
    "the field genuinely isn't in the source, retry cannot fix it."
    """
    for err in errors:
        if "does not match" in err:
            return True  # structural/arithmetic mismatch -> retryable
    return False


def demo_retry_fixes_structural_error(client: MockAnthropic):
    print("--- 4.4: retry-with-error-feedback fixes a structural error ---")
    document = "Invoice: 2 items, $30 + $45. Stated total: $80."

    # First attempt: model mis-stated the total.
    first_attempt = {
        "stated_total": 80,
        "line_items": [{"description": "Item A", "amount": 30}, {"description": "Item B", "amount": 45}],
    }
    errors = validate_extraction(first_attempt)
    print(f"  first attempt: {first_attempt}")
    print(f"  validation errors: {errors}")

    if errors and retry_is_worthwhile(errors, document):
        retry_prompt = (
            f"Original document: {document!r}\n"
            f"Your previous extraction: {first_attempt}\n"
            f"Validation error(s): {errors}\n"
            f"Please correct stated_total to match the actual line items."
        )
        client.queue_response(
            stop_reason="tool_use",
            tool_calls=[{
                "name": "extract_invoice",
                "input": {
                    "stated_total": 75,
                    "line_items": [{"description": "Item A", "amount": 30}, {"description": "Item B", "amount": 45}],
                },
            }],
        )
        response = client.messages.create(model="claude-sonnet-5", messages=[{"role": "user", "content": retry_prompt}])
        corrected = next(b for b in response.content if b.type == "tool_use").input
        print(f"  retry succeeded: {corrected}")
        print(f"  remaining errors: {validate_extraction(corrected)}")


def demo_retry_cannot_fix_missing_data():
    print("\n--- 4.4: retry CANNOT fix data that's genuinely absent from the source ---")
    document = "Invoice: 2 items, $30 + $45. (no purchase order number mentioned anywhere)"
    extraction = {"purchase_order_number": None, "line_items": [{"description": "A", "amount": 30}, {"description": "B", "amount": 45}]}

    print(f"  document: {document!r}")
    print(f"  extraction: {extraction}")
    print(
        "  decision: purchase_order_number is null because it is NOT in the source — "
        "retrying would not produce a real PO number, only risk the model fabricating "
        "one to satisfy a retry request. Correct action: leave null, do not retry."
    )


def demo_detected_pattern_tracking():
    """Standalone illustration of the module docstring's last point: this isn't
    invoice extraction like the other two demos — it's a code-review-findings
    scenario showing why each finding should carry a stable `detected_pattern`
    id (not just free-text `issue` text), so dismissals can be aggregated by
    pattern to spot which rules are noisy, instead of re-litigating retries."""
    print("\n--- 4.4: detected_pattern field for aggregate false-positive analysis ---")
    findings = [
        {"issue": "bare except", "detected_pattern": "except_no_log", "dismissed_by_dev": True},
        {"issue": "bare except", "detected_pattern": "except_no_log", "dismissed_by_dev": True},
        {"issue": "magic number", "detected_pattern": "literal_int_gt_1", "dismissed_by_dev": True},
        {"issue": "sql injection", "detected_pattern": "string_concat_query", "dismissed_by_dev": False},
    ]
    from collections import Counter
    dismissed_patterns = Counter(f["detected_pattern"] for f in findings if f["dismissed_by_dev"])
    print(f"  findings logged with detected_pattern: {len(findings)}")
    print(f"  most-dismissed patterns (candidates to fix/disable, per 4.1): {dismissed_patterns.most_common()}")


def main():
    print_mock_banner("4.4", "validation-retry loop + the limits of retrying")
    client = MockAnthropic()
    demo_retry_fixes_structural_error(client)
    demo_retry_cannot_fix_missing_data()
    demo_detected_pattern_tracking()


if __name__ == "__main__":
    main()
