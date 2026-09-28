"""
Task Statement 1.6 — Task decomposition strategies: prompt chaining vs
dynamic adaptive decomposition.

Pattern:  PROMPT CHAINING fits predictable, multi-aspect work where the
          steps are known ahead of time (e.g., review each file, then a
          separate cross-file integration pass). DYNAMIC DECOMPOSITION fits
          open-ended work where you don't know the subtasks until you've
          discovered something (e.g., "add tests to a legacy codebase" —
          you must map structure and find high-impact areas FIRST).
Avoids:   using a rigid fixed pipeline for open-ended exploration (you'll
          miss whatever the plan didn't anticipate); using unstructured
          dynamic exploration for a review that would be more consistent
          and cheaper as a fixed per-file + integration pipeline.
"""


# --- Prompt chaining: fixed, predictable steps ------------------------------

def prompt_chaining_code_review(files: list[str]) -> dict:
    """
    Splitting a large review into per-file local-analysis passes plus a
    separate cross-file integration pass avoids attention dilution — one
    giant pass over everything at once tends to miss cross-file issues.
    """
    per_file_findings = {}
    for f in files:
        # Step 1 (repeated per file): local analysis only.
        per_file_findings[f] = f"local analysis of {f}: no obvious bugs"

    # Step 2 (single pass, after all local passes): cross-file integration.
    integration_findings = (
        f"cross-file pass over {files}: checked call-site consistency "
        f"across all {len(files)} files"
    )

    return {"per_file": per_file_findings, "integration": integration_findings}


# --- Dynamic decomposition: subtasks generated from discoveries ------------

def dynamic_decomposition_add_tests(codebase_summary: dict) -> list[str]:
    """
    "Add comprehensive tests to a legacy codebase" can't be fully planned up
    front — the plan should adapt as dependencies are discovered. This
    simulates: map structure -> identify high-impact areas -> build a
    prioritized, adaptive plan.
    """
    plan: list[str] = []

    # Step 1: map structure (discovery, not execution).
    modules = codebase_summary["modules"]
    plan.append(f"mapped structure: {len(modules)} modules discovered")

    # Step 2: identify high-impact areas from what was found.
    high_impact = [m for m in modules if m["untested_call_sites"] > 10]
    plan.append(f"identified {len(high_impact)} high-impact untested modules")

    # Step 3: build a plan that ADAPTS — each module's subtask depends on
    # what step 1/2 discovered about it, not a template decided beforehand.
    for m in sorted(high_impact, key=lambda x: -x["untested_call_sites"]):
        if m.get("has_circular_deps"):
            plan.append(
                f"module {m['name']}: circular deps found -> break dependency "
                f"first, THEN add tests (discovered mid-plan, not anticipated)"
            )
        else:
            plan.append(f"module {m['name']}: add unit tests directly")

    return plan


def main():
    print("=" * 72)
    print("[MOCK] 1.6 — prompt chaining vs dynamic decomposition")
    print("=" * 72)

    print("\n--- Prompt chaining: fixed multi-file review pipeline ---")
    result = prompt_chaining_code_review(["auth.py", "billing.py", "refunds.py"])
    for f, finding in result["per_file"].items():
        print(f"  [local]  {finding}")
    print(f"  [cross]  {result['integration']}")

    print("\n--- Dynamic decomposition: adaptive test-coverage plan ---")
    codebase_summary = {
        "modules": [
            {"name": "auth", "untested_call_sites": 14, "has_circular_deps": False},
            {"name": "billing", "untested_call_sites": 22, "has_circular_deps": True},
            {"name": "utils", "untested_call_sites": 3, "has_circular_deps": False},
        ]
    }
    for step in dynamic_decomposition_add_tests(codebase_summary):
        print(f"  {step}")


if __name__ == "__main__":
    main()
