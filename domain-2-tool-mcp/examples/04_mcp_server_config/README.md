# Task Statement 2.4 — MCP server scoping, env expansion, and resources

## Project-scoped: `.mcp.json`

[`./.mcp.json`](./.mcp.json) in this folder is a real example. It's committed to the
repo so **the whole team** gets the same servers automatically when they open the
project in Claude Code. Secrets are never hardcoded — `${GITHUB_TOKEN}` and
`${ISSUE_TRACKER_API_KEY}` are expanded from the shell environment at connection time,
so the actual token values never touch git history.

Use project scope for: shared, team-wide integrations everyone doing this work needs
(GitHub, an internal issue tracker, a shared database).

## User-scoped: `~/.claude.json`

Personal or experimental servers go in the user's home config instead, so they don't
leak into the shared project config or get committed. Example entry (illustrative —
not written to the real `~/.claude.json` by this repo):

```json
{
  "mcpServers": {
    "my-local-scratch-db": {
      "command": "python",
      "args": ["/home/me/tools/scratch-db-mcp/server.py"],
      "env": { "DB_PATH": "/home/me/scratch.sqlite" }
    }
  }
}
```

**Both are active simultaneously** — when Claude Code connects, tools from every
configured server (project- and user-scoped) are discovered and become available to
the agent at once. There's no "only load this one for this task" toggle at the config
level; scoping tool access per-agent (Task Statement 2.3) is what does that job.

## Preferring community servers over custom ones

For a standard integration (Jira, GitHub, Slack, Postgres) — use an existing,
maintained community MCP server rather than writing one. Reserve custom MCP servers
for things genuinely specific to this team (e.g., `internal-issue-tracker` above,
which talks to a bespoke internal system with no public server for it).

## Resources: exposing a catalog instead of forcing exploration

Without a resource, an agent that needs "which issues exist" has to call a search
tool speculatively and iterate. An MCP **resource** exposes that catalog directly —
e.g. a list of open issue summaries, a documentation hierarchy, or a DB schema — so
the agent can see what's available up front and go straight to the right tool call
instead of spending exploratory turns discovering it.

Illustrative resource shape from an issue-tracker MCP server:

```json
{
  "uri": "issues://open-summary",
  "name": "Open issue summaries",
  "description": "One-line summary + id + labels for every open issue. Read this before searching individual issues.",
  "mimeType": "application/json"
}
```

An agent that reads this resource first knows immediately whether issue `#4021`
exists and is labeled `billing` — no `search_issues("billing")` call needed just to
find out.
