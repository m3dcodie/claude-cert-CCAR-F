"""
Task Statement 5.4 — Context management in large codebase exploration:
scratchpad persistence, subagent delegation, crash-recovery manifests.

Pattern:  a scratchpad file persists key findings across a context boundary
          so a long session doesn't have to re-derive them (and doesn't
          drift into "typical patterns" language once it's lost specifics).
          Subagents isolate verbose exploration noise while the main agent
          stays at the coordination level. For crash recovery, each agent
          exports state to a known location and a coordinator reloads a
          manifest on resume instead of re-exploring from scratch.
Avoids:   keeping only in-context findings with no durable record (lost on
          compaction or a crash); one agent doing both deep exploration AND
          high-level coordination in the same context, drowning the latter
          in the former's noise.
"""

import json
import tempfile
from pathlib import Path


def demo_scratchpad():
    print("--- 5.4: scratchpad file persists findings across context boundaries ---")
    with tempfile.TemporaryDirectory() as tmp:
        scratchpad = Path(tmp) / "scratchpad.md"

        # Phase 1 finding, written durably instead of only living in context.
        scratchpad.write_text(
            "# Exploration scratchpad\n\n"
            "## Auth module\n"
            "- `AuthService.verify()` in src/auth/service.py:42 is the single "
            "entry point for token verification\n"
            "- 3 callers found: api/middleware.py, jobs/refresh.py, cli/login.py\n"
        )
        print(f"  wrote findings to {scratchpad.name}")

        # Much later (simulating a context boundary / compaction / new turn):
        # the agent re-reads the scratchpad instead of re-deriving from
        # scratch or falling back to "typically auth services look like...".
        recalled = scratchpad.read_text()
        print("  later, re-reading scratchpad instead of re-exploring or guessing:")
        for line in recalled.splitlines():
            if line.strip():
                print(f"    {line}")

        # Phase 2: append new findings rather than losing phase 1's.
        with scratchpad.open("a") as f:
            f.write("\n## Billing module\n- `charge()` reuses AuthService.verify() at src/billing/charge.py:8\n")
        print(f"  appended phase-2 findings; scratchpad now has {len(scratchpad.read_text().splitlines())} lines total")


def demo_subagent_delegation():
    print("\n--- 5.4: subagent delegation isolates verbose exploration ---")

    def verbose_subagent_trace_dependencies(module: str) -> list[str]:
        # Imagine this reads 40 files and produces pages of intermediate
        # reasoning -- NONE of that noise needs to reach the coordinator.
        return [f"{module}/service.py imports {module}/models.py", f"{module}/service.py imports shared/db.py"]

    coordinator_context = []  # only high-level summaries land here
    for module in ["auth", "billing"]:
        subagent_result = verbose_subagent_trace_dependencies(module)
        coordinator_context.append(f"{module}: {len(subagent_result)} dependency edges found")

    print("  coordinator context after delegation (compact, high-level):")
    for line in coordinator_context:
        print(f"    {line}")
    print("  (the subagent's full file-by-file trace never entered the coordinator's context)")


def demo_crash_recovery_manifest():
    print("\n--- 5.4: manifest-based crash recovery ---")
    with tempfile.TemporaryDirectory() as tmp:
        state_dir = Path(tmp)

        # Each agent exports its own state to a known location.
        (state_dir / "auth_agent_state.json").write_text(json.dumps({"status": "complete", "findings_count": 12}))
        (state_dir / "billing_agent_state.json").write_text(json.dumps({"status": "in_progress", "findings_count": 4}))

        manifest = {
            "agents": {
                "auth_agent": {"state_file": "auth_agent_state.json"},
                "billing_agent": {"state_file": "billing_agent_state.json"},
            }
        }
        (state_dir / "manifest.json").write_text(json.dumps(manifest))

        # Simulated crash. On resume, the coordinator loads the manifest
        # and re-injects only what's needed -- NOT a full re-exploration.
        loaded_manifest = json.loads((state_dir / "manifest.json").read_text())
        print("  resuming after simulated crash, loaded manifest:")
        for agent_name, info in loaded_manifest["agents"].items():
            agent_state = json.loads((state_dir / info["state_file"]).read_text())
            print(f"    {agent_name}: {agent_state}")
            if agent_state["status"] == "in_progress":
                print(f"      -> re-invoke {agent_name} to finish (only this one, not auth_agent which completed)")


def main():
    print("=" * 72)
    print("[MOCK] 5.4 — scratchpad persistence, subagent delegation, crash recovery")
    print("=" * 72)
    demo_scratchpad()
    demo_subagent_delegation()
    demo_crash_recovery_manifest()


if __name__ == "__main__":
    main()
