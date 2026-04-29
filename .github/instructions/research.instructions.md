---
description: Project-wide conventions for the research-template repo. Points at the LLM-wiki schema, the verify/reference report locations, and MCP usage.
applyTo: "**/*.md"
---

# Research Template Conventions

This repo is an APM-managed research workspace. Three workflows coexist:

## Workflows

| Workflow | Agent(s) | Output |
|---|---|---|
| **LLM wiki** — persistent, compounding knowledge base | `wiki-ingest`, `wiki-query`, `wiki-lint` | `research/wiki/` |
| **Claim verification** — fact-check a paragraph | `verify-claims` | `research/verify/` |
| **Reference finding** — strengthen a paragraph with citations | `find-references` | `research/references/` |

The three workflows write to **separate directories** and do not step on
each other. The wiki is the canonical knowledge store; verify and
find-references are ad-hoc helpers that produce standalone reports.

## Wiki schema

When editing any file under `research/wiki/`, the full schema in
`.apm/instructions/wiki.instructions.md` applies. Follow it exactly —
page formats, frontmatter, `[[WikiLink]]` style, `index.md` / `log.md`
conventions.

## Raw inputs

User-curated input material lives under `research/input/` and is
**immutable**. Agents may read from it but never edit it.

## MCP servers

Two MCP servers are available (configured in `.mcp.json`):

- **parallel-search** — web search and fetch (`web_search_preview`, `web_fetch`)
- **deepwiki** — GitHub repo Q&A (`read_wiki_contents`, `ask_question`)

Prefer these over raw `WebFetch` when the use case fits.
