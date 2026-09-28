"""
Task Statement 3.2 — Custom slash commands vs skills: scoping, frontmatter,
and the choice between skill and CLAUDE.md.

Pattern:  .claude/commands/ (project, shared) vs ~/.claude/commands/
          (personal); skills add context: fork (isolate verbose output),
          allowed-tools (restrict actions), argument-hint (prompt for
          missing params instead of guessing). Skills are for on-demand,
          task-specific workflows; CLAUDE.md is for always-loaded universal
          standards -- picking the wrong one either forces a developer to
          remember to invoke something that should just always apply, or
          bloats every session with something only occasionally relevant.
Avoids:   editing a shared skill in place for personal experimentation
          (breaks it for teammates); omitting argument-hint on a skill that
          needs a required parameter (invocation silently does the wrong
          thing instead of prompting).
"""

from pathlib import Path


def parse_frontmatter(path: Path) -> dict:
    """
    Minimal flat `key: value` YAML-frontmatter parser -- no third-party
    dependency needed, since every command/skill frontmatter here is a flat
    mapping (unlike .claude/rules/*.md, which uses a YAML list for `paths`
    and is parsed with a real YAML library where that's warranted).
    """
    text = path.read_text()
    if not text.startswith("---"):
        return {}
    _, frontmatter, _ = text.split("---", 2)
    result = {}
    for line in frontmatter.splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, _, value = line.partition(":")
        result[key.strip()] = value.strip()
    return result


def demo_command_vs_skill_scoping():
    print("--- 3.2: project-scoped command vs project-scoped skill ---")
    base = Path(__file__).resolve().parent

    command_fm = parse_frontmatter(base / ".claude" / "commands" / "review-pr.md")
    skill_fm = parse_frontmatter(base / ".claude" / "skills" / "code-review" / "SKILL.md")

    print(f"  .claude/commands/review-pr.md frontmatter: {command_fm}")
    print(f"  .claude/skills/code-review/SKILL.md frontmatter: {skill_fm}")
    print("  (both are project-scoped/shared; the skill additionally isolates its")
    print("   work via context: fork and restricts itself via allowed-tools)")


def simulate_argument_hint_prompt(frontmatter: dict, invocation_args: str | None) -> str:
    if invocation_args:
        return f"proceeding with args={invocation_args!r}"
    hint = frontmatter.get("argument-hint")
    if hint:
        return f"no args given -- prompting developer using argument-hint: {hint!r}"
    return "no args given, no argument-hint configured -- would guess or fail ambiguously"


def demo_argument_hint():
    print("\n--- 3.2: argument-hint prevents silent guessing on under-specified invocation ---")
    base = Path(__file__).resolve().parent
    command_fm = parse_frontmatter(base / ".claude" / "commands" / "review-pr.md")

    print(f"  /review-pr 482        -> {simulate_argument_hint_prompt(command_fm, '482')}")
    print(f"  /review-pr (bare)     -> {simulate_argument_hint_prompt(command_fm, None)}")

    no_hint_fm = {}  # a command authored without argument-hint
    print(f"  /some-other-cmd (bare, no argument-hint configured) -> {simulate_argument_hint_prompt(no_hint_fm, None)}")


def decide_skill_vs_claude_md(behavior: str, always_relevant: bool) -> str:
    """
    The core 3.2 decision: does this behavior need to be invoked for a
    specific task (skill), or should every session just have it (CLAUDE.md)?
    """
    if always_relevant:
        return f"CLAUDE.md: '{behavior}' should apply to every session unconditionally."
    return f"Skill: '{behavior}' is task-specific -- invoke on demand, don't load it by default."


def demo_skill_vs_claude_md_decision():
    print("\n--- 3.2: choosing between a skill and CLAUDE.md ---")
    cases = [
        ("all Python functions need type hints", True),
        ("deep multi-file code review before a PR", False),
        ("always run tests before reporting done", True),
        ("brainstorm alternative refactor approaches", False),
    ]
    for behavior, always in cases:
        print(f"  {decide_skill_vs_claude_md(behavior, always)}")


def main():
    print("=" * 72)
    print("[MOCK] 3.2 — slash commands, skill frontmatter, skill vs CLAUDE.md")
    print("=" * 72)
    demo_command_vs_skill_scoping()
    demo_argument_hint()
    demo_skill_vs_claude_md_decision()


if __name__ == "__main__":
    main()
