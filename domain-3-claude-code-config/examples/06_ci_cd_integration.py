"""
Task Statement 3.6 — CI/CD integration: non-interactive mode, structured
output, prior-findings dedup, and session isolation for review.

Pattern:  `-p` runs non-interactively (no hang waiting for input in a CI
          job). `--output-format json` + `--json-schema` forces a fixed,
          parseable shape so findings can be posted as inline PR comments
          programmatically. Re-running review after new commits includes
          PRIOR findings in context so only new/unaddressed issues get
          reported -- not the same comment posted again on every push. A
          fresh review session (not the one that generated the code) is
          used for review, same rationale as Domain 4 Task Statement 4.6.
Avoids:   running Claude Code interactively in a CI job (hangs waiting for
          input that will never come); free-text findings that need a
          fragile regex/LLM re-parse before they can become PR comments;
          re-posting the same finding on every commit because prior
          findings were never given as context.
"""

from dataclasses import dataclass, field


@dataclass
class Finding:
    file: str
    line: int
    summary: str
    severity: str


REVIEW_FINDINGS_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "file": {"type": "string"},
                    "line": {"type": "integer"},
                    "summary": {"type": "string"},
                    "severity": {"type": "string", "enum": ["low", "medium", "high"]},
                },
                "required": ["file", "line", "summary", "severity"],
            },
        }
    },
    "required": ["findings"],
}


def simulate_ci_invocation(prior_findings: list[Finding], current_diff_findings: list[Finding]) -> dict:
    """
    Simulates what `claude -p ... --output-format json --json-schema ...`
    would return: only NEW or still-unaddressed findings, given the prior
    run's findings as context (so a fix removes a finding permanently, and
    a still-broken issue doesn't get re-reported as if it were new).
    """
    prior_keys = {(f.file, f.line, f.summary) for f in prior_findings}
    new_or_unaddressed = [f for f in current_diff_findings if (f.file, f.line, f.summary) not in prior_keys]
    return {"findings": [f.__dict__ for f in new_or_unaddressed]}


def validate_against_schema(output: dict, schema: dict) -> list[str]:
    """Minimal structural check standing in for real JSON-schema validation."""
    errors = []
    for key in schema.get("required", []):
        if key not in output:
            errors.append(f"missing required field: {key}")
    return errors


def demo_dedup_across_commits():
    print("--- 3.6: prior-findings dedup across re-runs ---")

    first_commit_findings = [
        Finding("src/billing.py", 42, "no null check on customer_id", "high"),
        Finding("src/billing.py", 88, "unused import", "low"),
    ]
    print(f"  commit 1 review result: {[f.summary for f in first_commit_findings]}")

    # Developer fixed the null check but the unused import is STILL there,
    # and a NEW issue was introduced.
    second_commit_findings = [
        Finding("src/billing.py", 88, "unused import", "low"),               # still present
        Finding("src/billing.py", 51, "refund amount not validated", "high"),  # new
    ]
    result = simulate_ci_invocation(prior_findings=first_commit_findings, current_diff_findings=second_commit_findings)
    print(f"  commit 2 raw findings in diff: {[f.summary for f in second_commit_findings]}")
    print(f"  commit 2 posted findings (deduped against prior run): {[f['summary'] for f in result['findings']]}")
    print("  (the fixed null-check finding correctly disappeared; the still-open unused")
    print("   import was correctly SKIPPED as not new; the genuinely new issue was posted)")


def demo_schema_enforcement():
    print("\n--- 3.6: --json-schema catches malformed CI output before it's posted ---")
    good_output = {"findings": [{"file": "a.py", "line": 1, "summary": "x", "severity": "low"}]}
    bad_output = {"finding_list": []}  # wrong key entirely -- would break the posting script

    print(f"  good_output errors: {validate_against_schema(good_output, REVIEW_FINDINGS_JSON_SCHEMA)}")
    print(f"  bad_output errors:  {validate_against_schema(bad_output, REVIEW_FINDINGS_JSON_SCHEMA)}")


def demo_session_isolation_for_ci_review():
    print("\n--- 3.6: CI review uses a FRESH session, not the generation session ---")
    print("  PR author's local session: wrote the diff, already reasoned through its own decisions.")
    print("  CI review job: spins up an independent `claude -p` invocation with NO prior")
    print("  conversation history from the author's session -- same rationale as Domain 4")
    print("  Task Statement 4.6 (independent review instances catch more than self-review).")


def main():
    print("=" * 72)
    print("[MOCK] 3.6 — CI/CD integration: -p, --json-schema, dedup, session isolation")
    print("=" * 72)
    demo_dedup_across_commits()
    demo_schema_enforcement()
    demo_session_isolation_for_ci_review()


if __name__ == "__main__":
    main()
