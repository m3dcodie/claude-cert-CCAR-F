"""
Task Statement 2.1 — Defined input/output contracts, not just prose descriptions.

Pattern:  a tool's schema is part of its disambiguation signal, not just its
          description string. A typed, constrained input schema (required
          fields, enums, no freeform catch-alls) tells the model what the
          tool is FOR as structurally as the description does. A typed,
          stable output schema lets the model (and any code chaining tool
          calls) parse the result reliably instead of re-reading prose to
          figure out what came back.
Avoids:   a single loosely-typed `input: str` / `output: str` shape shared
          across tools with different purposes; returning prose that varies
          in structure call-to-call, forcing the caller to re-parse instead
          of accessing typed fields; letting two tools look identical at the
          schema level even though their descriptions differ.
"""

from dataclasses import dataclass
from typing import Literal


# --- BAD: one generic contract reused across unrelated tools ----------------
#
# analyze_document(input: str) -> str
#
# Same shape for "pull out dates" and "summarize this" and "check this claim".
# Nothing about the schema tells the model which fields it'll get back, so
# even a well-written description has to do ALL the disambiguation work, and
# the caller has to re-parse free text after every call.


@dataclass
class ExtractDataPointsInput:
    document_id: str
    fields: list[Literal["date", "amount", "name"]]


@dataclass
class ExtractDataPointsOutput:
    document_id: str
    values: dict[str, str | None]  # one entry per requested field, None if absent


def extract_data_points(req: ExtractDataPointsInput) -> ExtractDataPointsOutput:
    """
    Contract: caller must specify WHICH fields it wants (no implicit "get
    everything"); the response always has one key per requested field, so a
    caller can do `result.values["amount"]` without inspecting a blob first.
    """
    fake_doc = {"date": "2026-03-01", "amount": "$412.00", "name": None}
    return ExtractDataPointsOutput(
        document_id=req.document_id,
        values={f: fake_doc.get(f) for f in req.fields},
    )


@dataclass
class VerifyClaimInput:
    claim: str
    source_document_id: str


@dataclass
class VerifyClaimOutput:
    supported: bool
    evidence_span: str | None
    confidence: float  # 0.0-1.0


def verify_claim_against_source(req: VerifyClaimInput) -> VerifyClaimOutput:
    """
    Contract: always returns a boolean verdict plus evidence and a confidence
    score — never a prose paragraph the caller has to re-read to find the
    verdict. The shape itself signals "this tool judges", not "this tool
    extracts" or "this tool summarizes".
    """
    if "refund" in req.claim.lower():
        return VerifyClaimOutput(
            supported=True,
            evidence_span="Refunds are issued within 5-7 business days.",
            confidence=0.92,
        )
    return VerifyClaimOutput(supported=False, evidence_span=None, confidence=0.4)


@dataclass
class SummarizeContentInput:
    document_id: str
    max_sentences: int = 5


@dataclass
class SummarizeContentOutput:
    summary: str
    sentence_count: int


def summarize_content(req: SummarizeContentInput) -> SummarizeContentOutput:
    """
    Contract: bounded by max_sentences (no open-ended "however long the model
    feels like"), and reports back sentence_count so a caller can verify the
    bound was respected without re-counting the string itself.
    """
    text = (
        "The report covers Q1 shipments. Volumes rose 12% over Q4. "
        "Refunds are issued within 5-7 business days. No major delays "
        "were recorded."
    )
    sentences = [s.strip() for s in text.split(".") if s.strip()][: req.max_sentences]
    summary = ". ".join(sentences) + "."
    return SummarizeContentOutput(summary=summary, sentence_count=len(sentences))


def main():
    print("=" * 72)
    print("[MOCK] 2.1 — defined input/output contracts")
    print("=" * 72)

    extract_result = extract_data_points(
        ExtractDataPointsInput(document_id="DOC-1", fields=["date", "amount"])
    )
    print("\nextract_data_points ->")
    print(f"  {extract_result}")
    print(f"  typed access: values['amount'] = {extract_result.values['amount']!r}")

    verify_result = verify_claim_against_source(
        VerifyClaimInput(
            claim="Refunds take 5-7 business days",
            source_document_id="DOC-1",
        )
    )
    print("\nverify_claim_against_source ->")
    print(f"  {verify_result}")
    print(f"  typed access: supported = {verify_result.supported}")

    summary_result = summarize_content(
        SummarizeContentInput(document_id="DOC-1", max_sentences=2)
    )
    print("\nsummarize_content ->")
    print(f"  {summary_result}")
    print(f"  contract honored: sentence_count <= max_sentences -> "
          f"{summary_result.sentence_count <= 2}")


if __name__ == "__main__":
    main()
