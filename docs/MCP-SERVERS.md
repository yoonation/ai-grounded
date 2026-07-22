<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# MCP Servers

This document explains how to add MCP (Model Context Protocol) servers to your project's `.mcp.json` configuration file. MCP servers extend Claude Code with capabilities like GitHub access, web search, database queries, and more.

## Why this is a separate doc

JSON does not support comments. The `.mcp.json` file ships empty (`{"mcpServers": {}}`) so it parses cleanly on every project start. Examples live here in markdown where comments and explanations are first-class.

When you need a server, copy the relevant block from this document into `.mcp.json` and fill in your environment variables.

## File location

`.mcp.json` lives at the repo root. Claude Code reads it automatically on session start. The format is standard JSON.

## Security: environment variables only

Never hardcode API keys, tokens, or credentials in `.mcp.json`. The file is committed to git, so any secret in it leaks. Use `${VARIABLE_NAME}` references which Claude Code resolves at runtime from your shell environment.

Per Myoung's convention, set the actual values in `~/.config/credentials/<provider>.env` and source them in your shell, or use 1Password CLI (`op read op://Technical/<item>/<field>`).

## Common MCP servers

### GitHub

For repo browsing, issue management, PR review.

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

Setup:

```bash
# In ~/.zshrc or ~/.config/credentials/github.env
export GITHUB_TOKEN="$(op read op://Technical/github-pat/token)"
```

### Brave Search

For web search from within Claude Code sessions.

```json
{
  "mcpServers": {
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "${BRAVE_API_KEY}"
      }
    }
  }
}
```

Get an API key at brave.com/search/api/.

### Filesystem (read-only)

For browsing a directory tree outside the current repo.

```json
{
  "mcpServers": {
    "filesystem-readonly": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/YOURNAME/obsidian"
      ]
    }
  }
}
```

Restrict the allowed paths tightly. Don't expose `/` or `$HOME` unless you mean to.

### PostgreSQL

For ad-hoc queries against a database. Useful for ops and debugging.

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "${POSTGRES_CONNECTION_STRING}"
      }
    }
  }
}
```

Use a read-only role unless you specifically need write access.

### AWS

For AWS resource inspection (S3, EC2, IAM, etc.). This is the community AWS MCP server; check the upstream project for current status and security model before adopting.

```json
{
  "mcpServers": {
    "aws": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-aws"],
      "env": {
        "AWS_PROFILE": "${AWS_PROFILE}",
        "AWS_REGION": "${AWS_REGION:-us-east-1}"
      }
    }
  }
}
```

Use a profile with minimum required permissions. Never use a profile with `AdministratorAccess` for ad-hoc MCP use.

## Multiple servers

You can configure several servers at once:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "${BRAVE_API_KEY}"
      }
    }
  }
}
```

Claude Code starts each server on session start. Slow-to-initialize servers can delay session startup; configure only what you need per project.

## Disabling temporarily

To temporarily disable a server without removing its config, rename it (e.g., prefix with `_disabled_`):

```json
{
  "mcpServers": {
    "_disabled_github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

Claude Code only starts servers whose key matches its registry. A prefixed name won't match and stays dormant. Restore by removing the prefix.

## Incident response

If you suspect an MCP server is compromised (returning suspicious results, leaking data, etc.), see `governance-commons/playbooks/compromised-mcp-server.md` for the response playbook. Short version: stop Claude Code, remove the server entry from `.mcp.json`, rotate any credentials the server had access to, then restart.

## Finding more servers

- Official catalog: https://github.com/modelcontextprotocol/servers
- Community-maintained list: https://github.com/punkpeye/awesome-mcp-servers
- Build your own: https://modelcontextprotocol.io/quickstart/server

Vet community servers carefully. An MCP server runs with the credentials you give it; a malicious server with your `GITHUB_TOKEN` can do anything your GitHub user can do.

## Per-project vs global

`.mcp.json` is per-project. Servers configured here apply only to Claude Code sessions started from this repo's root.

For servers you want available across all projects, see Claude Code's global config (`~/.claude/settings.json` or platform equivalent). Global servers run for every session; project-scoped servers apply only when needed.

## Troubleshooting

**"Failed to start MCP server"**: usually a missing API key or wrong env var name. Check `echo $GITHUB_TOKEN` etc. in the shell that started Claude Code.

**"MCP server not found"**: the `command` field's binary isn't on PATH, or the npm package name is misspelled. Run the `command args` line directly in your terminal to debug.

**"JSON parse error"**: `.mcp.json` has a syntax error. Validate with `python3 -m json.tool < .mcp.json` or `jq . .mcp.json`. JSON does NOT support comments; that's why this template ships an empty file with examples in this markdown doc.

**Server starts but Claude Code can't see it**: restart Claude Code. MCP servers are loaded once at session start; mid-session config changes don't apply.
