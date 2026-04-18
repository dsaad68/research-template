# Project Setup Guide

This directory contains step-by-step setup instructions for the **research-template** project.

The project relies on three tools:

| Tool | Purpose | Required |
|------|---------|----------|
| **Git** | Cloning the repository and pulling APM dependencies | Yes |
| **uv** | Fast Python package & environment manager (used by APM and project scripts) | Yes |
| **APM** | Microsoft's Agent Package Manager — installs the agents, skills, and MCP servers declared in `apm.yml` | Yes |

## Pick your platform

- [macOS setup guide](./setup-macos.md)
- [Windows setup guide](./setup-windows.md)
- [Linux setup guide](./setup-linux.md)

## How-to guides

- [Add the Brave Search MCP server](./add-brave-mcp.md) — declare it in `apm.yml` (stdio / http / Docker) and install with `apm install`.

## What gets installed for this project

After completing the OS-specific guide, running `apm install` from the project root will install everything declared in [`apm.yml`](../apm.yml):

- **APM dependencies**
  - `anthropics/skills/skills/pdf` — PDF skill from Anthropic's skills repo
  - `./agents` — local agents folder
- **MCP servers**
  - `parallel-search` — `https://search-mcp.parallel.ai/mcp`
  - `deepwiki` — `https://mcp.deepwiki.com/mcp`

The `target: claude` line in `apm.yml` means APM will configure these for Claude Code automatically.

## Quick reference (after install)

```bash
# Clone
git clone <repo-url> research-template
cd research-template

# Install all APM dependencies (agents, skills, MCP servers)
apm install

# Verify
git --version
uv --version
apm --version
```

## Troubleshooting

If a command is "not found" after install, your shell can't see the binary's directory on `PATH`. Open a **new** terminal window first — installers usually update your shell profile, but the change only takes effect in new sessions. If it still fails, see the troubleshooting section in the OS-specific guide.
