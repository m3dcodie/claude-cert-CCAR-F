"""
Task Statement 3.1 — CLAUDE.md hierarchy, @import resolution, and the
/memory diagnostic.

Pattern:  user-level (~/.claude/CLAUDE.md) is personal and NEVER reaches
          teammates via version control; project-level (.claude/CLAUDE.md
          or root CLAUDE.md) is what actually reaches the whole team;
          directory-level CLAUDE.md files scope further down. @import
          pulls a shared standards file into a package's CLAUDE.md instead
          of duplicating it. `/memory` lists every memory file actually
          loaded in a session -- that's the tool for diagnosing "why isn't
          this instruction being followed."
Avoids:   writing a team-wide rule into a personal ~/.claude/CLAUDE.md and
          being surprised teammates don't see it; duplicating a shared
          standards doc into every package's CLAUDE.md by hand.
"""

from dataclasses import dataclass, field
from pathlib import PurePosixPath


@dataclass
class MemoryFile:
    path: str
    level: str  # "user" | "project" | "directory"
    shared_via_vcs: bool
    content_summary: str


def resolve_memory_files(all_files: list[MemoryFile], working_dir: str) -> list[MemoryFile]:
    """
    Simulates what `/memory` reports: every memory file that actually
    applies to a session working in `working_dir` -- user-level always
    applies, project-level always applies, directory-level applies only if
    working_dir is under it.
    """
    resolved = []
    for f in all_files:
        if f.level in ("user", "project"):
            resolved.append(f)
        elif f.level == "directory":
            # crude prefix check standing in for "is working_dir under this dir"
            rule_dir = f.path.rsplit("/CLAUDE.md", 1)[0]
            if PurePosixPath(working_dir).is_relative_to(rule_dir) or working_dir == rule_dir:
                resolved.append(f)
    return resolved


def diagnose_missing_instruction(files: list[MemoryFile], instruction_keyword: str, teammate_working_dir: str) -> str:
    """The classic case: a rule exists somewhere, but a teammate doesn't see it."""
    matches = [f for f in files if instruction_keyword in f.content_summary]
    if not matches:
        return f"'{instruction_keyword}' not found in ANY memory file -- it was never written down."

    for m in matches:
        if m.level == "user":
            return (
                f"Found in {m.path} (level=user). This is PERSONAL -- it is not in "
                f"version control and will never reach teammates. Fix: move this "
                f"content into a project-level CLAUDE.md."
            )

    # It's at project or directory level -- check it actually resolves for the teammate.
    resolved_for_teammate = resolve_memory_files(files, teammate_working_dir)
    if any(instruction_keyword in f.content_summary for f in resolved_for_teammate):
        return f"Correctly resolves for teammate working in {teammate_working_dir} -- not a hierarchy issue."
    return f"Exists at project/directory level but doesn't resolve for {teammate_working_dir} -- check directory scoping."


def resolve_import(claude_md_content: str, standards_dir: str) -> str:
    """Simulates @import expansion: replace @import lines with the referenced file's content."""
    standards = {
        f"{standards_dir}/monetary-values.md": "Monetary amounts are integer cents internally, never floats.",
        f"{standards_dir}/testing.md": "Every code path needs a corresponding test; no untested branches.",
    }
    lines = claude_md_content.splitlines()
    expanded = []
    for line in lines:
        if line.strip().startswith("@import "):
            ref = line.strip().removeprefix("@import ").strip()
            # Simplified: resolve relative to standards_dir for this demo.
            key = f"{standards_dir}/{PurePosixPath(ref).name}"
            expanded.append(f"[imported from {ref}]: {standards.get(key, '<not found>')}")
        else:
            expanded.append(line)
    return "\n".join(expanded)


def main():
    print("=" * 72)
    print("[MOCK] 3.1 — CLAUDE.md hierarchy diagnosis + @import resolution")
    print("=" * 72)

    files = [
        MemoryFile("~/.claude/CLAUDE.md", "user", shared_via_vcs=False,
                   content_summary="always run pytest -q before finishing"),
        MemoryFile(".claude/CLAUDE.md", "project", shared_via_vcs=True,
                   content_summary="type hints required on all function signatures"),
        MemoryFile("packages/billing/CLAUDE.md", "directory", shared_via_vcs=True,
                   content_summary="monetary amounts are integer cents"),
    ]

    print("\n--- Diagnosing 'pytest -q' not applying to a teammate ---")
    diagnosis = diagnose_missing_instruction(files, "pytest -q", teammate_working_dir="packages/billing")
    print(f"  {diagnosis}")

    print("\n--- Diagnosing 'type hints' (correctly project-level) ---")
    diagnosis = diagnose_missing_instruction(files, "type hints", teammate_working_dir="packages/billing")
    print(f"  {diagnosis}")

    print("\n--- Resolving @import in a package CLAUDE.md ---")
    package_claude_md = (
        "# packages/billing/CLAUDE.md\n"
        "@import ../../standards/monetary-values.md\n"
        "@import ../../standards/testing.md\n"
        "\n"
        "## Billing-specific\n"
        "- Every charge path needs an idempotency key.\n"
    )
    print(resolve_import(package_claude_md, standards_dir="standards"))


if __name__ == "__main__":
    main()
