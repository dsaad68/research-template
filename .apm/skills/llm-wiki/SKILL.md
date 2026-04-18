---
name: llm-wiki
description: Persistent, LLM-maintained markdown knowledge base that grows as you drop in sources — ingest, query, and lint operations keep it synthesized and cross-linked.
license: MIT
metadata:
  author: Daniel Saad
  email: me@dsaad.com
---

# LLM Wiki

This package turns the repo into a Karpathy-style **LLM wiki**: a persistent,
compounding markdown knowledge base that the coding agent writes and maintains
on the user's behalf. The human curates sources and asks questions; the agent
does the reading, summarizing, cross-referencing, and bookkeeping.

## Architecture

Three layers — **never** conflate them:

1. **Raw sources** — `research/sources/` (immutable; user drops files here)
2. **The wiki** — `research/wiki/` (LLM-owned markdown; agent reads + writes)
3. **The schema** — `.apm/instructions/wiki.instructions.md` (rules for page
   formats, linking, index/log conventions; auto-loaded when editing wiki files)

## Wiki layout

```
research/
├── sources/                     # Raw, immutable user-supplied files
└── wiki/
    ├── index.md                 # Content catalog (grouped by type)
    ├── log.md                   # Append-only chronological ledger
    ├── overview.md              # High-level synthesis across the wiki
    ├── sources/                 # One page per ingested source
    ├── entities/                # People, orgs, tools, datasets, models, papers
    └── concepts/                # Topics, methods, ideas, theories
```

## Operations

Three agents implement the wiki lifecycle. Pick the right one:

| Intent | Agent | Typical trigger |
|---|---|---|
| Add a new source to the wiki | `wiki-ingest` | "ingest this paper", "add this URL to the wiki", "process research/sources/foo.md" |
| Ask a question against the wiki | `wiki-query` | "what does the wiki say about X?", "summarize our current thinking on Y" |
| Health-check the wiki | `wiki-lint` | "lint the wiki", "find orphan pages", "are there contradictions?" |

Each operation appends an entry to `log.md` with the prefix
`## [YYYY-MM-DD HH:MM] <op> | <title>` so the log stays `grep`-parseable.

## How to use

### Ingesting a new source

The user provides a file path, URL, or pasted text. Invoke the `wiki-ingest`
agent. It will:

1. Read or fetch the source
2. Extract key takeaways
3. Identify entities and concepts
4. Write a source page
5. Create or update entity/concept pages (flagging contradictions inline)
6. Update `index.md`
7. Append to `log.md`
8. Report what was touched and suggest follow-ups

A single ingest typically touches 5–15 wiki pages.

### Querying the wiki

Invoke the `wiki-query` agent with a question. It reads `index.md` first, then
drills into the most relevant entity/concept pages, synthesizes an answer with
inline `[[WikiLinks]]`, and appends a query entry to the log. If the wiki has
gaps, it will suggest sources to ingest.

### Linting

Periodically (or on demand) invoke `wiki-lint`. It surfaces:

- Flagged but unresolved contradictions
- Orphan pages (no inbound links)
- Missing cross-references (entity mentioned but not linked)
- Stub pages that need expansion
- Concepts referenced but lacking their own page

Output is a prioritized markdown report; the agent does not auto-fix without
explicit instruction.

## Composition with other agents

This repo has two additional research agents that compose well with the wiki:

- **`verify-claims`** — run on a freshly written wiki synthesis page to
  fact-check its claims. Report lands in `research/verify/`.
- **`find-references`** — run after drafting a concept page to attach the
  strongest supporting literature. Report lands in `research/references/`.

Both write to separate directories and leave the wiki untouched.

## Guidelines

- **Never modify raw sources** in `research/sources/`. Read-only.
- **Always update both `index.md` and `log.md`** on an ingest. Consistency of
  these two files is the single most important invariant.
- **One entity/concept per page**, even if the page is a stub. Stubs are
  better than missing pages because they create anchor points for future
  ingests to link to.
- **Preserve provenance**: every non-trivial claim on a wiki page should cite
  the `[[source-*]]` page it came from.
- **Flag contradictions, don't silently overwrite**. Use the `⚠️ Conflict:`
  callout defined in the schema.
- **Ask the user** when a source contains material that meaningfully changes
  an existing entity/concept page — don't guess which version to keep.

## References

- Schema and page formats: `.apm/instructions/wiki.instructions.md`
- Ingest agent: `.apm/agents/wiki-ingest.agent.md`
- Query agent: `.apm/agents/wiki-query.agent.md`
- Lint agent: `.apm/agents/wiki-lint.agent.md`
- Original concept: Andrej Karpathy's *LLM Wiki* gist
