"""
Task Statement 3.5 — Iterative refinement: concrete examples, test-driven
iteration, the interview pattern, and batching interacting vs independent
issues.

Pattern:  when prose produces inconsistent results, 2-3 concrete
          input/output examples fix it more reliably than more prose.
          Test-driven iteration: write the test suite FIRST, then iterate
          against real failures. The interview pattern: ask clarifying
          questions before implementing in an unfamiliar domain, to
          surface considerations the developer didn't think to specify.
          Interacting issues go in ONE message (the fix has to account for
          all of them together); independent issues get fixed sequentially
          (each stays independently verifiable).
Avoids:   re-describing the same vague requirement in different words after
          each failed attempt instead of switching to concrete examples;
          implementing straight away in an unfamiliar domain without
          surfacing the design questions first; batching unrelated fixes
          into one big message where a regression in one masks a regression
          in another.
"""


# --- Concrete I/O examples fixing an inconsistent prose spec ---------------

def prose_only_spec_causes_drift():
    print("--- 3.5: prose-only spec produces inconsistent transformations ---")
    spec = "Normalize phone numbers to a standard format."
    attempts = [
        "(555) 123-4567 -> 5551234567",       # digits only
        "555-123-4567 -> +1-555-123-4567",    # E.164-ish with dashes
        "5551234567 -> (555) 123-4567",       # US display format
    ]
    print(f"  spec: {spec!r}")
    for a in attempts:
        print(f"    attempt: {a}")
    print("  (three different 'standard formats' across three attempts -- the prose never pinned down WHICH one)")


def concrete_examples_fix_it():
    print("\n--- 3.5: 2-3 concrete input/output examples remove the ambiguity ---")
    examples = [
        ("(555) 123-4567", "+15551234567"),
        ("555-123-4567", "+15551234567"),
        ("555.123.4567", "+15551234567"),
    ]
    print("  examples given:")
    for inp, out in examples:
        print(f"    {inp!r} -> {out!r}")
    print("  (E.164, no ambiguity left -- every future input normalizes the same way)")


# --- Test-driven iteration ---------------------------------------------------

def normalize_phone(raw: str) -> str:
    # Bug: always prepends "+1" without checking whether the input already
    # carries a country code -- exactly the kind of gap a test suite catches
    # and a re-description in prose would likely miss again.
    digits = "".join(c for c in raw if c.isdigit())
    return f"+1{digits}"


def demo_test_driven_iteration():
    print("\n--- 3.5: test-driven iteration (write tests first, iterate on failures) ---")
    test_cases = [
        ("(555) 123-4567", "+15551234567"),
        ("555-123-4567", "+15551234567"),
        ("+1 555 123 4567", "+15551234567"),  # already has country code
    ]
    failures = [(inp, expected, normalize_phone(inp)) for inp, expected in test_cases if normalize_phone(inp) != expected]
    for inp, expected, actual in failures:
        print(f"  FAIL: normalize_phone({inp!r}) == {actual!r}, expected {expected!r}")
    print(f"  {len(failures)} failing test(s) -- iterate by fixing THIS specific gap (already-prefixed input), not by re-guessing the whole function")


# --- Interview pattern -------------------------------------------------------

def interview_pattern_questions(task: str) -> list[str]:
    """
    Before implementing in an unfamiliar domain, surface the design
    questions a developer may not have thought to specify up front.
    """
    if "cache" in task:
        return [
            "What should happen to cached entries when the underlying data changes -- invalidate immediately or allow staleness up to some TTL?",
            "Should a cache-population failure block the request, or fall through to the uncached path?",
            "Is this cache shared across processes/instances, or per-process?",
        ]
    return ["No unfamiliar-domain considerations identified -- proceeding directly."]


def demo_interview_pattern():
    print("\n--- 3.5: interview pattern before implementing in an unfamiliar domain ---")
    task = "Add a cache layer in front of the pricing lookup"
    print(f"  task: {task!r}")
    for q in interview_pattern_questions(task):
        print(f"    ? {q}")
    print("  (answers to these change the implementation -- asking BEFORE writing code avoids rework)")


# --- Batching interacting vs sequential independent issues -------------------

def demo_batching_decision():
    print("\n--- 3.5: interacting issues batched, independent issues sequential ---")
    interacting = [
        "the retry logic doesn't respect the new timeout config",
        "the timeout config default was also wrong",
    ]
    independent = [
        "a docstring typo in utils.py",
        "an unrelated unused import in billing.py",
    ]
    print(f"  interacting (fix depend on each other) -> ONE message: {interacting}")
    print(f"  independent (no relationship) -> sequential, one at a time: {independent}")
    print("  (batching the interacting pair avoids fixing the retry logic against the WRONG timeout default)")


def main():
    print("=" * 72)
    print("[MOCK] 3.5 — iterative refinement: examples, TDD, interview pattern, batching")
    print("=" * 72)
    prose_only_spec_causes_drift()
    concrete_examples_fix_it()
    demo_test_driven_iteration()
    demo_interview_pattern()
    demo_batching_decision()


if __name__ == "__main__":
    main()
