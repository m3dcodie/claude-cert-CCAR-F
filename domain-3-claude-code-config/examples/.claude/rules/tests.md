---
paths:
  - "**/*.test.*"
  - "tests/**/*"
---

# Testing conventions

Only loaded into context when editing a test file, regardless of where it lives in the
tree — this is deliberately broader than `api.md`'s single directory glob.

- One assertion concept per test; if you need "and" in the test name, split it.
- No sleeps as a synchronization mechanism — use an explicit wait/poll condition.
- Integration tests hit a real (test) database; don't mock the DB layer for these.
