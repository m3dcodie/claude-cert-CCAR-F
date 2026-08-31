"""
Task Statement 2.5 — Built-in tools: Grep, Glob, Read, Write, Edit.

Pattern:  Grep searches file CONTENTS (function names, error strings).
          Glob finds files by PATH PATTERN. Read/Write operate on whole
          files; Edit does a targeted unique-text replacement. When Edit's
          anchor text isn't unique, fall back to Read + Write. Build
          codebase understanding incrementally: Grep for entry points ->
          Read to follow imports -> repeat, rather than reading every file
          upfront.

This runs for real against THIS repo's own files (no mocking needed — Grep/
Glob/Read/Write/Edit are just file-system operations, not model calls).
"""

import re
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]  # .../claude-cert


def grep(pattern: str, root: Path, glob_pattern: str = "*.py") -> dict[Path, list[tuple[int, str]]]:
    """Content search — like the Grep tool: find PATTERN across file contents."""
    hits: dict[Path, list[tuple[int, str]]] = {}
    regex = re.compile(pattern)
    for path in root.rglob(glob_pattern):
        try:
            lines = path.read_text().splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        matches = [(i + 1, line) for i, line in enumerate(lines) if regex.search(line)]
        if matches:
            hits[path] = matches
    return hits


def glob_files(root: Path, pattern: str) -> list[Path]:
    """Path-pattern search — like the Glob tool: find files by NAME pattern."""
    return sorted(root.rglob(pattern))


def demo_incremental_exploration():
    print("--- 2.5: incremental exploration (Grep entry points -> Read to trace) ---")

    domain1_dir = REPO_ROOT / "domain-1-agentic-architecture"

    # Step 1: Grep for an entry point — every place run_agentic_loop is defined or called.
    hits = grep(r"run_agentic_loop", domain1_dir)
    print(f"Grep 'run_agentic_loop' across {domain1_dir.name}: {len(hits)} file(s)")
    for path, matches in hits.items():
        for lineno, line in matches:
            print(f"  {path.relative_to(REPO_ROOT)}:{lineno}: {line.strip()}")

    # Step 2: Glob for all example files, to know the full surface before reading.
    examples = glob_files(domain1_dir, "0*.py")
    print(f"\nGlob '0*.py' in {domain1_dir.name}/examples: {len(examples)} files")
    for p in examples:
        print(f"  {p.relative_to(REPO_ROOT)}")

    # Step 3: Read one specific file to follow the trace (not reading all of them).
    target = domain1_dir / "examples" / "01_agentic_loop.py"
    content = target.read_text()
    print(f"\nRead {target.name}: {len(content.splitlines())} lines "
          f"(only this one file, because Grep already told us where the definition is)")


def demo_grep_vs_glob():
    print("\n--- 2.5: Grep (content) vs Glob (path pattern) ---")
    test_hits = grep(r"^def test_", REPO_ROOT, "*.py")
    print(f"Grep '^def test_' (content search): {len(test_hits)} files with test functions")

    test_files = glob_files(REPO_ROOT, "*test*.py")
    print(f"Glob '*test*.py' (path pattern search): {len(test_files)} files with 'test' in the filename")
    print("(These answer different questions — a file can match one and not the other.)")


def demo_edit_fallback():
    print("\n--- 2.5: Edit-fails-on-non-unique-text -> Read + Write fallback ---")

    with tempfile.TemporaryDirectory() as tmp:
        sample = Path(tmp) / "sample.py"
        sample.write_text(
            "def handler(x):\n"
            "    return x\n"
            "\n"
            "def other_handler(x):\n"
            "    return x\n"
        )

        anchor = "    return x\n"
        content = sample.read_text()
        occurrences = content.count(anchor)
        print(f"Anchor text {anchor!r} occurs {occurrences} times -> Edit would refuse (not unique).")

        # Fallback: Read the whole file, do the targeted change in memory
        # against a unique, larger context window, then Write it back.
        lines = content.splitlines(keepends=True)
        # Uniquely target the second occurrence using surrounding context.
        target_idx = next(
            i for i, line in enumerate(lines)
            if line == anchor and "other_handler" in "".join(lines[max(0, i - 3):i])
        )
        lines[target_idx] = "    return x * 2  # only other_handler is doubled\n"
        sample.write_text("".join(lines))

        print("Read + Write fallback applied. Result:")
        print(sample.read_text())


def main():
    print("=" * 72)
    print("[MOCK] 2.5 — built-in tool selection: Grep, Glob, Read, Write, Edit")
    print("[MOCK] (these run for real — no model call needed for file-system ops)")
    print("=" * 72)
    demo_incremental_exploration()
    demo_grep_vs_glob()
    demo_edit_fallback()


if __name__ == "__main__":
    main()
