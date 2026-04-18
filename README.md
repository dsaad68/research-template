# research-template

An [APM](https://microsoft.github.io/apm/) project targeting [Claude Code](https://claude.com/claude-code), pre-wired with research agents, the Anthropic PDF skill, and the `parallel-search` and `deepwiki` MCP servers.

## Quick start

```bash
git clone <repo-url> research-template
cd research-template
apm install
```

That's it — `apm install` reads [`apm.yml`](./apm.yml) and pulls in every agent, skill, and MCP server the project needs.

## Prerequisites

You need three tools on your machine:

| Tool | What for |
|------|----------|
| **Git** | Cloning the repo and the dependencies APM pulls in |
| **uv** | Fast Python package & environment manager |
| **APM** | Microsoft's Agent Package Manager — runs the install from `apm.yml` |

Don't have them yet? Follow the per-OS setup guide:

- 🍎 [macOS setup guide](./docs/setup-macos.md)
- 🪟 [Windows setup guide](./docs/setup-windows.md)
- 🐧 [Linux setup guide](./docs/setup-linux.md)

The [`docs/`](./docs/README.md) directory has the full walkthrough including how to install Git itself if you don't have it.

## What's in the box

Configured in [`apm.yml`](./apm.yml):

- **Target:** `claude` — APM configures everything for Claude Code
- **APM dependencies:**
  - `anthropics/skills/skills/pdf` — Anthropic's PDF skill
  - `./agents` — local agents in this repo
- **MCP servers:**
  - `parallel-search` — `https://search-mcp.parallel.ai/mcp`
  - `deepwiki` — `https://mcp.deepwiki.com/mcp`

## Project layout

```
.
├── agents/        # Local agents (registered as an APM dependency)
├── docs/          # Setup guides (macOS / Windows / Linux)
├── research/      # Research artifacts
├── sandbox/       # Scratch space
├── scripts/       # Project scripts
├── apm.yml        # APM manifest — source of truth for deps & MCPs
├── links.md
└── READING-LIST.md
```

## Verify your setup

```bash
git --version
uv --version
apm --version
```

If any of these fail, see the [setup guides](./docs/README.md).

## License

MIT
