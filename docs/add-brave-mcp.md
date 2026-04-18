# Adding the Brave Search MCP Server with APM

This guide walks through adding [`brave/brave-search-mcp-server`](https://github.com/brave/brave-search-mcp-server) to this project using **APM**. After this, Claude Code will have access to Brave's web, local, image, video, news, and AI-summarizer tools.

> **Project context:** This repo declares its dependencies in [`apm.yml`](../apm.yml). MCP servers go under `dependencies.mcp`. The existing `parallel-search` and `deepwiki` entries are good templates — Brave will follow the same shape.

---

## TL;DR

```bash
# 1. Get an API key from https://api-dashboard.search.brave.com/app/keys
# 2. Export it
export BRAVE_API_KEY="bsk_..."

# 3. Add the MCP entry to apm.yml (see "Option 1" below), then:
apm install --only=mcp

# 4. Verify
apm config
```

---

## Step 0 — Prerequisites

| Requirement | Why |
|---|---|
| **APM installed** | Already required by this project — see the [setup guides](./README.md) |
| **Node.js 22.x or higher** | Only needed for Option 1 (`npx`) |
| **Docker** | Only needed for Option 2 |
| **A Brave Search API key** | The server is just a wrapper around the Brave Search API |

### Get a Brave Search API key

1. Sign up at <https://brave.com/search/api/>.
2. Pick a plan (the free tier works for testing).
3. Generate a key from the [developer dashboard](https://api-dashboard.search.brave.com/app/keys).
4. Export it in your shell so APM-launched processes inherit it:

   **macOS / Linux**
   ```bash
   echo 'export BRAVE_API_KEY="bsk_your_real_key"' >> ~/.zshrc   # or ~/.bashrc
   source ~/.zshrc
   ```

   **Windows (PowerShell)**
   ```powershell
   [Environment]::SetEnvironmentVariable("BRAVE_API_KEY", "bsk_your_real_key", "User")
   # restart PowerShell so the new env var loads
   ```

   Never commit the API key to the repo.

---

## Background — how APM declares MCP servers

APM (per [Key Concepts](https://microsoft.github.io/apm/introduction/key-concepts/)) treats MCP servers as a first-class dependency type alongside APM packages. They live under `dependencies.mcp` in `apm.yml`.

There are two declaration styles:

1. **Registry shorthand** — a single string referring to a server in the GitHub MCP Registry, e.g. `- io.github.github/github-mcp-server`.
2. **Inline object** — used when the server isn't in the registry, or when you need to pin a transport / command / env. This project's existing entries use the inline form:

   ```yaml
   - name: parallel-search
     registry: false
     transport: http
     url: https://search-mcp.parallel.ai/mcp
   ```

For Brave, the inline form is the right choice — we want to pin the launch command and pass the API key.

---

## Option 1 — `stdio` via `npx` (recommended)

This is the simplest path: APM/Claude launches the server on demand via `npx`, no long-running process to manage.

### 1. Edit `apm.yml`

Add a new entry under `dependencies.mcp`:

```yaml
dependencies:
  apm:
  - anthropics/skills/skills/pdf
  - ./agents
  mcp:
  - name: parallel-search
    registry: false
    transport: http
    url: https://search-mcp.parallel.ai/mcp
  - name: deepwiki
    registry: false
    transport: http
    url: https://mcp.deepwiki.com/mcp
  - name: brave-search
    registry: false
    transport: stdio
    command: npx
    args:
    - "-y"
    - "@brave/brave-search-mcp-server"
    - "--transport"
    - "stdio"
    env:
      BRAVE_API_KEY: ${BRAVE_API_KEY}
```

Notes:
- `${BRAVE_API_KEY}` references the env var you exported in step 0 — no secret ends up in git.
- `-y` makes `npx` skip the install prompt.
- `--transport stdio` is explicit (it's also the default in v2.x of the Brave server, but being explicit avoids surprises if the default changes).

### 2. Install

```bash
apm install --only=mcp
```

`--only=mcp` skips the APM package step and just (re)applies the MCP server config to the target runtime — Claude Code in this project's case (`target: claude` in `apm.yml`).

A full `apm install` works too — APM is diff-aware: existing MCP servers with unchanged config are reported as `already configured`, and changed ones as `updated` (per the [CLI docs](https://microsoft.github.io/apm/reference/cli-commands)).

---

## Option 2 — Docker

If you don't want Node on your host machine.

### 1. Pull the image

```bash
docker pull mcp/brave-search:latest
```

### 2. Edit `apm.yml`

```yaml
  mcp:
  - name: brave-search
    registry: false
    transport: stdio
    command: docker
    args:
    - "run"
    - "-i"
    - "--rm"
    - "-e"
    - "BRAVE_API_KEY"
    - "mcp/brave-search"
    env:
      BRAVE_API_KEY: ${BRAVE_API_KEY}
```

The `-e BRAVE_API_KEY` form (no `=value`) tells Docker to copy the variable from the parent shell. APM populates that parent shell from the `env:` block, which itself reads from your exported `BRAVE_API_KEY`.

### 3. Install

```bash
apm install --only=mcp
```

---

## Verify the install

```bash
apm config
```

You should see Brave Search listed under MCP dependencies. Then in Claude Code, ask the model to "search the web with Brave for X" — Claude will surface tools like `brave_web_search`, `brave_local_search`, `brave_image_search`, `brave_video_search`, `brave_news_search`, and `brave_summarizer`.

You can also list all known MCP servers in the GitHub MCP Registry to confirm Brave is reachable:

```bash
apm mcp search brave
apm mcp show <server-name-or-id>
```

(See [`apm mcp` reference](https://microsoft.github.io/apm/reference/cli-commands).)

---

## Day-to-day commands

| Task | Command |
|---|---|
| Re-apply MCP config after editing `apm.yml` | `apm install --only=mcp` |
| Preview without writing changes | `apm install --only=mcp --dry-run` |
| Force re-apply (bypass diff check) | `apm install --only=mcp --force` |
| Remove Brave from the project | Delete the `brave-search` block in `apm.yml`, then `apm install` |
| Show full project config | `apm config` |

---

## Optional configuration

The Brave server reads several env vars that you can pass in the `env:` block of `apm.yml`:

| Variable | Purpose | Default |
|---|---|---|
| `BRAVE_API_KEY` | API key (required) | — |
| `BRAVE_MCP_TRANSPORT` | `stdio` or `http` | `stdio` |
| `BRAVE_MCP_PORT` | HTTP port | `8000` |
| `BRAVE_MCP_HOST` | HTTP bind host | `0.0.0.0` |
| `BRAVE_MCP_LOG_LEVEL` | `debug` … `emergency` | `info` |
| `BRAVE_MCP_ENABLED_TOOLS` | Comma-separated allowlist | all |
| `BRAVE_MCP_DISABLED_TOOLS` | Comma-separated denylist | none |
| `BRAVE_MCP_STATELESS` | HTTP stateless mode | `true` |

Example — restrict to web and news only, with debug logging:

```yaml
  - name: brave-search
    registry: false
    transport: stdio
    command: npx
    args: ["-y", "@brave/brave-search-mcp-server"]
    env:
      BRAVE_API_KEY: ${BRAVE_API_KEY}
      BRAVE_MCP_ENABLED_TOOLS: "brave_web_search,brave_news_search"
      BRAVE_MCP_LOG_LEVEL: "debug"
```

---

## Troubleshooting

**`BRAVE_API_KEY is not set`**
The env var isn't visible to the process APM spawned. Export it in the shell you launched Claude / `apm install` from, or set it user-wide (see step 0).

**`npx: command not found`**
Node 22+ isn't installed or isn't on PATH. Install Node, or switch to Option C (Docker).

**Old Brave server returning base64 image blobs**
You're on v1.x — upgrade to v2.x. Bumping the `npx` invocation to `@brave/brave-search-mcp-server@latest` is enough.

**`already configured` on install**
Not an error — APM detected the manifest config matches what's already deployed. If you really want to reset, use `apm install --only=mcp --force`.

**MCP server not appearing in Claude**
- Confirm `target: claude` is set in `apm.yml` (it is in this project).
- Re-run `apm install` (no `--only`) to re-deploy local content too.
- Restart Claude Code so it re-reads `.claude/` settings.

**Pro-tier features (local search, extra snippets) not working**
Those require a paid Brave plan. Free-tier keys silently fall back to web search.

---

## References

- Brave Search MCP server: <https://github.com/brave/brave-search-mcp-server>
- APM key concepts: <https://microsoft.github.io/apm/introduction/key-concepts/>
- APM CLI reference: <https://microsoft.github.io/apm/reference/cli-commands>
- This project's manifest: [`../apm.yml`](../apm.yml)
