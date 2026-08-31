"""
Task Statement 4.2 — Few-shot examples for output consistency and
ambiguous-case generalization.

Pattern:  2-4 targeted few-shot examples, each showing the REASONING for
          why one action was picked over a plausible alternative, teach the
          model to generalize that judgment to novel inputs — not just to
          match the exact examples given. This compares a zero-shot prompt
          (inconsistent output shape) against a few-shot prompt (consistent
          shape, and correct handling of a genuinely new ambiguous case).
Avoids:   few-shot examples that only show input/output with no reasoning
          (teaches pattern-matching, not judgment); assuming detailed
          instructions alone will fix formatting inconsistency once you've
          already seen it drift.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.mock_client import MockAnthropic, print_mock_banner  # noqa: E402


ZERO_SHOT_SYSTEM_PROMPT = (
    "You are a code reviewer. Report issues you find in the code."
)

FEW_SHOT_SYSTEM_PROMPT = """You are a code reviewer. Report each issue in this exact
format: `location | issue | severity | suggested_fix`.

Example 1 (ambiguous: is a broad except clause an issue?):
  code: `except Exception: pass`
  -> line 12 | bare exception swallowed silently, will hide real bugs | high | log the exception or narrow the except type
  Reasoning: it's flagged because failures are silently swallowed with no
  logging, not merely because a broad except type was used — a broad
  except that logs and re-raises would NOT be flagged.

Example 2 (ambiguous: is a magic number an issue?):
  code: `if retries > 3:`
  -> skip (not reported)
  Reasoning: `3` here is a locally-obvious retry count, not a magic number
  hiding real complexity — flagging every literal integer would be noise,
  so only literals whose meaning isn't locally obvious get reported.
"""


def simulate_zero_shot_runs(client: MockAnthropic) -> list[str]:
    """Without few-shot examples, output format drifts run to run."""
    client.queue_response(stop_reason="end_turn", text="Line 12: bare except is bad practice.")
    client.queue_response(
        stop_reason="end_turn",
        text="- Found an issue at line 12, severity high\n- consider fixing the except clause",
    )
    client.queue_response(stop_reason="end_turn", text='{"issue": "except too broad", "line": 12}')

    outputs = []
    for _ in range(3):
        resp = client.messages.create(
            model="claude-sonnet-5",
            system=ZERO_SHOT_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": "review: except Exception: pass"}],
        )
        outputs.append("".join(b.text for b in resp.content if b.type == "text"))
    return outputs


def simulate_few_shot_runs(client: MockAnthropic) -> list[str]:
    """With few-shot examples demonstrating the exact shape, output is consistent."""
    for _ in range(3):
        client.queue_response(
            stop_reason="end_turn",
            text="line 12 | bare exception swallowed silently, will hide real bugs | high | log the exception or narrow the except type",
        )

    outputs = []
    for _ in range(3):
        resp = client.messages.create(
            model="claude-sonnet-5",
            system=FEW_SHOT_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": "review: except Exception: pass"}],
        )
        outputs.append("".join(b.text for b in resp.content if b.type == "text"))
    return outputs


def simulate_novel_ambiguous_case(client: MockAnthropic) -> str:
    """
    A case NOT in the few-shot examples: does a narrow except with a log
    statement get flagged? The few-shot reasoning (Example 1: flagged
    because failures are silently swallowed) should generalize to "this one
    logs, so it's fine" without that exact case being spelled out.
    """
    client.queue_response(stop_reason="end_turn", text="skip (not reported)")
    resp = client.messages.create(
        model="claude-sonnet-5",
        system=FEW_SHOT_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": "review: except ValueError as e: logger.warning(e)"}],
    )
    return "".join(b.text for b in resp.content if b.type == "text")


def main():
    print_mock_banner("4.2", "few-shot examples for consistency + judgment generalization")
    client = MockAnthropic()

    print("\n--- Zero-shot: same input, 3 runs, format drifts ---")
    for i, out in enumerate(simulate_zero_shot_runs(client), 1):
        print(f"  run {i}: {out!r}")

    print("\n--- Few-shot: same input, 3 runs, consistent format ---")
    for i, out in enumerate(simulate_few_shot_runs(client), 1):
        print(f"  run {i}: {out!r}")

    print("\n--- Few-shot generalization to a NOVEL ambiguous case ---")
    print(f"  input: except ValueError as e: logger.warning(e)  (not in the examples)")
    print(f"  output: {simulate_novel_ambiguous_case(client)!r}")
    print("  (correctly generalized from Example 1's REASONING — 'flagged because silent, "
          "not because broad' — to 'this logs, so it's fine', without that exact case "
          "ever being shown)")


if __name__ == "__main__":
    main()
