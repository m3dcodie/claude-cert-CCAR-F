---
paths:
  - "src/api/**/*"
---

# API conventions

Only loaded into context when editing a file under `src/api/`.

- Every endpoint handler returns a structured error shape on failure — see the
  `errorCategory` / `isRetryable` pattern in
  `domain-2-tool-mcp/examples/02_structured_mcp_errors.py`. No bare `{"error": "failed"}`.
- New endpoints must be added to the OpenAPI schema in the same change.
- Auth checks happen in middleware, never re-implemented per-handler.
