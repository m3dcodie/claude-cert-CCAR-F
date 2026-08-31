"""
Task Statement 4.1 — Explicit criteria reduce false positives; vague
confidence-based instructions don't.

Pattern:  concrete, checkable criteria per finding category ("flag ONLY
          when claimed behavior contradicts actual behavior") beat vague
          instructions ("be conservative", "only report high-confidence
          findings"). This simulates a reviewer prompt run against the same
          5 code comments under both instruction styles and measures the
          false-positive rate.
Avoids:   treating "be conservative" as if it were a precision fix —
          it doesn't give the model anything concrete to check, so
          it doesn't reliably change the false-positive rate.
"""

from dataclasses import dataclass


@dataclass
class Comment:
    text: str
    code: str
    is_actually_wrong: bool  # ground truth for this demo


COMMENTS = [
    Comment("# returns the user's full name", "return f'{first} {last}'", is_actually_wrong=False),
    Comment("# returns the user's full name", "return first", is_actually_wrong=True),
    Comment("# retries 3 times on failure", "for _ in range(3): ...", is_actually_wrong=False),
    Comment("# retries 3 times on failure", "for _ in range(1): ...", is_actually_wrong=True),
    Comment("# sorted ascending", "arr.sort()  # default ascending in this lang", is_actually_wrong=False),
]


def vague_instruction_reviewer(comment: Comment) -> bool:
    """
    Simulates a model given only "check that comments are accurate, be
    conservative, only report high-confidence findings" — with nothing
    concrete to check against, it falls back to surface heuristics like
    "comment mentions a number" as a proxy for risk, which is noisy.
    """
    return "3" in comment.text or "retries" in comment.text  # noisy surface heuristic


def explicit_criteria_reviewer(comment: Comment) -> bool:
    """
    Simulates a model given the EXPLICIT criterion: "flag a comment only
    when the claimed behavior contradicts the actual code behavior." This
    stands in for the model actually checking claim vs. code, which is what
    the ground-truth label represents in this toy example.
    """
    return comment.is_actually_wrong


def false_positive_rate(flags: list[bool], truth: list[bool]) -> float:
    flagged_and_wrong = [f for f, t in zip(flags, truth) if f and not t]
    total_flagged = [f for f in flags if f]
    if not total_flagged:
        return 0.0
    return len(flagged_and_wrong) / len(total_flagged)


def main():
    print("=" * 72)
    print("[MOCK] 4.1 — explicit criteria vs vague 'be conservative' instructions")
    print("=" * 72)

    truth = [c.is_actually_wrong for c in COMMENTS]

    vague_flags = [vague_instruction_reviewer(c) for c in COMMENTS]
    explicit_flags = [explicit_criteria_reviewer(c) for c in COMMENTS]

    print("\n--- Vague instruction ('be conservative, only high-confidence') ---")
    for c, flag in zip(COMMENTS, vague_flags):
        marker = "FLAGGED" if flag else "skipped"
        correct = "correct" if flag == c.is_actually_wrong else "WRONG"
        print(f"  [{marker:7}] ({correct:7}) {c.text!r} vs `{c.code}`")
    print(f"  false positive rate: {false_positive_rate(vague_flags, truth):.0%}")

    print("\n--- Explicit criterion ('flag only when claim contradicts code') ---")
    for c, flag in zip(COMMENTS, explicit_flags):
        marker = "FLAGGED" if flag else "skipped"
        correct = "correct" if flag == c.is_actually_wrong else "WRONG"
        print(f"  [{marker:7}] ({correct:7}) {c.text!r} vs `{c.code}`")
    print(f"  false positive rate: {false_positive_rate(explicit_flags, truth):.0%}")

    print(
        "\nTakeaway: the explicit criterion checks the actual claim-vs-code relationship "
        "for every comment; the vague instruction has no concrete check to fall back on, "
        "so it drifts toward surface heuristics and produces false positives."
    )


if __name__ == "__main__":
    main()
