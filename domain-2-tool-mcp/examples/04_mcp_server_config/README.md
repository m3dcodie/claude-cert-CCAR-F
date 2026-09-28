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

## Beyond the outline: how this actually gets configured

The exam outline collapses scoping to project vs. user, but Claude Code has **three**
scopes, and in practice you rarely hand-edit JSON — the CLI writes it for you:

```bash
claude mcp add --transport http github https://api.githubcopilot.com/mcp/ \
  --header "Authorization: Bearer $GITHUB_TOKEN" --scope project   # writes .mcp.json
claude mcp add --transport stdio scratch-db --scope local -- python server.py  # ~/.claude.json, this project only
claude mcp add --transport http hubspot https://mcp.hubspot.com/anthropic --scope user  # ~/.claude.json, every project
```

| Scope | File | Shared with team | Loads in |
|---|---|---|---|
| `local` (default) | `~/.claude.json` | No | current project only |
| `project` | `.mcp.json` | Yes (git) | current project only |
| `user` | `~/.claude.json` | No | every project |

Both `local` and `user` live in the same `~/.claude.json` file — the difference is
scope, not location. Manage what's connected with `/mcp` (interactive panel) or
`claude mcp list` / `get` / `remove` / `login` / `logout` from the shell.

`${VAR}` expansion also supports a fallback: `${API_BASE_URL:-https://api.example.com}`
— useful for a project server where most of the team can rely on a sane default and
only a few people need to override it locally.

One more practical gotcha: MCP tool output is capped (`MAX_MCP_OUTPUT_TOKENS`, default
25,000 tokens, warning at 10,000) — a resource or tool that can return a lot of data
(e.g. `get_schema` on a big DB) should paginate or filter server-side rather than
relying on the client to truncate for it.
