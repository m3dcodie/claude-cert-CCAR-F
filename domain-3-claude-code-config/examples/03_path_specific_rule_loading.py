"""
Task Statement 3.3 — Path-specific rules: conditional loading by glob,
and why glob rules beat directory-level CLAUDE.md for scattered file types.

Pattern:  a .claude/rules/*.md file's `paths` frontmatter glob determines
          whether it loads for a given file being edited -- irrelevant
          rules never enter context. A glob like **/*.test.tsx applies a
          convention to every matching file regardless of which directory
          it lives in, which a directory-scoped CLAUDE.md cannot do when
          matching files are scattered across the tree (e.g. tests living
          next to the code they cover, not gathered under one tests/ dir).
Avoids:   relying on directory-level CLAUDE.md files for a convention that
          doesn't line up with the directory structure.
"""

import re
from dataclasses import dataclass
from pathlib import Path


def glob_to_regex(pattern: str) -> re.Pattern:
    """
    `fnmatch` treats "**" as just two "*"s and requires a literal "/" to
    follow, so "src/api/**/*" would NOT match "src/api/orders.py" (no
    extra directory level) under plain fnmatch -- which is wrong: rule
    globs like this are meant to match files directly inside the
    directory too, not only in subdirectories. This translates "**/" to
    "zero or more path segments" so both cases match correctly.
    """
    placeholder = "\x00"
    pattern = pattern.replace("**/", placeholder)
    out = ["^"]
    for ch in pattern:
        if ch == placeholder:
            out.append("(?:.*/)?")
        elif ch == "*":
            out.append("[^/]*")
        elif ch == "?":
            out.append("[^/]")
        else:
            out.append(re.escape(ch))
    out.append("$")
    return re.compile("".join(out))


def parse_paths_frontmatter(path: Path) -> list[str]:
    """Minimal parser for the one field these rule files need: paths: [...]."""
    text = path.read_text()
    _, frontmatter, _ = text.split("---", 2)
    for line in frontmatter.splitlines():
        line = line.strip()
        if line.startswith("paths:"):
            # inline list form: paths: ["a/**/*", "b/**/*"]
            inline = line.split(":", 1)[1].strip()
            if inline.startswith("["):
                import ast
                return ast.literal_eval(inline)
    # block-list form:
    #   paths:
    #     - "a/**/*"
    #     - "b/**/*"
    globs = []
    in_paths = False
    for line in frontmatter.splitlines():
        stripped = line.strip()
        if stripped == "paths:":
            in_paths = True
            continue
        if in_paths:
            if stripped.startswith("- "):
                globs.append(stripped[2:].strip().strip('"').strip("'"))
            else:
                break
    return globs


@dataclass
class Rule:
    name: str
    globs: list[str]


def rule_loads_for_file(rule: Rule, file_path: str) -> bool:
    return any(glob_to_regex(g).match(file_path) for g in rule.globs)


def which_rules_load(rules: list[Rule], file_path: str) -> list[str]:
    return [r.name for r in rules if rule_loads_for_file(rule=r, file_path=file_path)]


def main():
    print("=" * 72)
    print("[MOCK] 3.3 — path-scoped rule loading by glob")
    print("=" * 72)

    base = Path(__file__).resolve().parent
    rules = [
        Rule("api.md", parse_paths_frontmatter(base / ".claude" / "rules" / "api.md")),
        Rule("tests.md", parse_paths_frontmatter(base / ".claude" / "rules" / "tests.md")),
    ]
    for r in rules:
        print(f"  loaded rule spec: {r.name} -> paths={r.globs}")

    print("\nWhich rules load for each edited file:")
    files_being_edited = [
        "src/api/orders.py",
        "src/api/orders.test.py",  # note: test file, but ALSO under src/api/
        "src/utils/helpers.py",
        "tests/test_billing.py",
        "packages/checkout/checkout.test.tsx",  # scattered location, still a test file
    ]
    for f in files_being_edited:
        loaded = which_rules_load(rules, f)
        print(f"  {f}: {loaded if loaded else '(no rule loads -- no wasted context)'}")

    print(
        "\nNote: 'src/api/orders.test.py' loads BOTH rules -- a glob-based system "
        "naturally handles a file that is simultaneously 'under src/api/' and 'a "
        "test file', which a single directory-level CLAUDE.md hierarchy could not "
        "express as cleanly."
    )
    print(
        "Note: 'packages/checkout/checkout.test.tsx' loads tests.md purely by file "
        "TYPE, with no directory-level CLAUDE.md anywhere near it -- this is exactly "
        "the case where glob-pattern rules beat directory-scoped CLAUDE.md files."
    )


if __name__ == "__main__":
    main()
