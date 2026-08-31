"""
Task Statement 5.5 — Human review workflows and confidence calibration.

Pattern:  an aggregate accuracy number can hide a badly-performing segment.
          Stratified sampling (per document type/field) catches both
          ongoing drift and novel errors that a global average would
          smooth over. Raw model confidence scores need calibration
          against a labeled validation set before they're used to route
          review -- an uncalibrated "0.9 confidence" doesn't necessarily
          mean 90% likely correct.
Avoids:   trusting one blended accuracy number as if it applied uniformly
          everywhere; routing review purely off raw model-reported
          confidence without ever checking that confidence against ground
          truth.
"""

import random
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class Extraction:
    doc_type: str
    field: str
    model_confidence: float
    correct: bool  # ground truth, known only for labeled/sampled data


def make_dataset() -> list[Extraction]:
    random.seed(7)
    data = []
    # Invoices: strong performance across the board.
    for _ in range(80):
        data.append(Extraction("invoice", "total_amount", random.uniform(0.9, 0.99), correct=True))
    # Receipts: total_amount is fine, but merchant_name is quietly bad --
    # this is exactly what a single blended accuracy number would hide.
    for _ in range(60):
        data.append(Extraction("receipt", "total_amount", random.uniform(0.85, 0.98), correct=True))
    for _ in range(40):
        correct = random.random() > 0.35  # ~65% accurate, hidden inside the blend
        data.append(Extraction("receipt", "merchant_name", random.uniform(0.7, 0.95), correct=correct))
    return data


def aggregate_accuracy(data: list[Extraction]) -> float:
    return sum(e.correct for e in data) / len(data)


def stratified_accuracy(data: list[Extraction]) -> dict[tuple[str, str], float]:
    groups = defaultdict(list)
    for e in data:
        groups[(e.doc_type, e.field)].append(e)
    return {key: sum(e.correct for e in items) / len(items) for key, items in groups.items()}


def calibrate_confidence_threshold(data: list[Extraction], target_precision: float = 0.95) -> float:
    """
    Find the lowest confidence threshold such that everything AT OR ABOVE
    it meets target_precision against ground truth -- this is what turns a
    raw score into something routing decisions can actually trust.
    """
    thresholds = sorted({round(e.model_confidence, 2) for e in data})
    for t in thresholds:
        above = [e for e in data if e.model_confidence >= t]
        if not above:
            continue
        precision = sum(e.correct for e in above) / len(above)
        if precision >= target_precision:
            return t
    return 1.0


def main():
    print("=" * 72)
    print("[MOCK] 5.5 — aggregate accuracy hides segments; confidence needs calibration")
    print("=" * 72)

    data = make_dataset()

    print(f"\nAggregate accuracy (misleading): {aggregate_accuracy(data):.1%}")

    print("\nStratified accuracy by (doc_type, field) -- the real picture:")
    for key, acc in sorted(stratified_accuracy(data).items()):
        flag = "  <-- below target, needs review" if acc < 0.90 else ""
        print(f"  {key}: {acc:.1%}{flag}")

    threshold = calibrate_confidence_threshold(data, target_precision=0.95)
    print(f"\nCalibrated confidence threshold for 95% precision: >= {threshold}")
    print("(extractions below this threshold get routed to human review; the raw")
    print(" model confidence number alone, uncalibrated, would not tell you where to cut)")


if __name__ == "__main__":
    main()
