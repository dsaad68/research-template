---
description: Schema and conventions for maintaining the LLM wiki under research/wiki/. Auto-loads when editing any wiki page.
applyTo: "research/wiki/**/*.md"
---

# LLM Wiki Schema

These rules apply whenever you are reading, creating, or updating files under
`research/wiki/`. Follow them exactly — the wiki's long-term usefulness depends
on consistency.

## Hard rules

1. **Raw inputs are immutable.** Files under `research/input/` are read-only.
   Never edit them. If content is wrong, flag it on the wiki page — don't fix
   the source.
2. **Every ingest touches `index.md` and `log.md`.** If you updated a page
   without updating these two, the ingest is incomplete.
3. **Every entity or concept gets its own page**, even if it is a 3-line stub.
   Stubs create anchor points for future links.
4. **Every non-trivial claim cites its source page.** Use
   `[[YYYY-MM-DD-source-slug]]` at the end of the sentence or bullet.
5. **Flag contradictions; do not silently overwrite.** Use the `⚠️ Conflict:`
   callout (below). When in doubt, ask the user which version is authoritative.
6. **Prefer update over replace.** When re-ingesting a source that touches an
   existing page, merge new material into the existing structure — only
   restructure when the user asks.

## Page types

Four page types. The `type` frontmatter field is required.

| Type | Path | Purpose |
|---|---|---|
| `source` | `research/wiki/sources/YYYY-MM-DD-<slug>.md` | One per ingested source. Summary + key claims + outbound links. |
| `entity` | `research/wiki/entities/<slug>.md` | A person, organization, tool, dataset, model, paper, or product. |
| `concept` | `research/wiki/concepts/<slug>.md` | A topic, method, idea, theory, or phenomenon. |
| `overview` | `research/wiki/overview.md` | A single synthesis page across the whole wiki. |

## Required frontmatter (all page types)

```yaml
---
title: <Human-readable title>
type: source | entity | concept | overview
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [YYYY-MM-DD-source-a, YYYY-MM-DD-source-b]   # source slugs that contributed
aliases: [Alt Name, Abbreviation]                      # optional
---
```

`sources` on a source page is `[]` (it is itself the source).
`updated` must be bumped on every edit.

## Page templates

### Source page

```markdown
---
title: <Original title of the source>
type: source
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: []
origin: <URL or path/to/research/input/file>
author: <Author or org, if known>
date: <Publication date, if known>
aliases: []
---

# <Title>

**One-sentence summary.**

## Key takeaways
- Bullet 1
- Bullet 2
- Bullet 3

## Claims
- Concrete, citable claim 1.
- Concrete, citable claim 2.

## Entities mentioned
- [[entity-slug-a]]
- [[entity-slug-b]]

## Concepts mentioned
- [[concept-slug-a]]
- [[concept-slug-b]]

## Notes
Free-form reading notes, quotes worth preserving, open questions.
```

### Entity page

```markdown
---
title: <Canonical entity name>
type: entity
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [YYYY-MM-DD-source-a]
aliases: [Alt spelling]
entity_kind: person | org | tool | dataset | model | paper | product
---

# <Entity name>

**One-line descriptor.** What this thing is, in one sentence.

## Overview
Two to four paragraphs synthesizing what the wiki knows about this entity.
Cite sources inline with `[[YYYY-MM-DD-source-slug]]`.

## Key facts
- Fact 1 [[source]]
- Fact 2 [[source]]

## Related
- [[related-entity]] — relationship in one phrase
- [[related-concept]] — relationship in one phrase

## Open questions
- Things the wiki does not yet answer.
```

### Concept page

```markdown
---
title: <Canonical concept name>
type: concept
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [YYYY-MM-DD-source-a, YYYY-MM-DD-source-b]
aliases: []
---

# <Concept name>

**One-sentence definition.**

## Summary
Two to four paragraphs. Cite sources inline.

## Variations / sub-concepts
- [[sub-concept-a]]
- [[sub-concept-b]]

## Key claims across sources
- Claim 1 [[source-a]]
- Claim 2 [[source-b]]

## Related
- [[related-concept]]
- [[related-entity]]

## Open questions
```

## Linking

- **Primary link style: `[[slug]]`** (Obsidian-style wiki links). The slug is
  the filename without the `.md` extension. Example: `[[wiki-ingest]]` or
  `[[2026-04-18-karpathy-llm-wiki]]`.
- Use aliases via `[[slug|Display Text]]` when the inline phrasing differs
  from the canonical title.
- For external references, use standard markdown: `[text](https://url)`.
- Every page should link **outward** to at least one other wiki page unless
  it is genuinely a leaf. Orphan pages will be flagged by `wiki-lint`.

## Contradiction marker

When a new source disagrees with something already on a page, do **not**
overwrite. Insert a blockquote callout:

```markdown
> ⚠️ Conflict: [[source-a]] reports X, but [[source-b]] reports Y. Unresolved.
```

Place it in the relevant section. If the user resolves it, replace the
callout with the resolved claim and append a note to `log.md`.

## `index.md` format

Grouped catalog, one line per page. Keep entries in alphabetical order within
each group.

```markdown
# Wiki Index

## Sources
- [[YYYY-MM-DD-source-slug]] — One-line summary.

## Entities
- [[entity-slug]] — One-line descriptor.

## Concepts
- [[concept-slug]] — One-line definition.
```

On every ingest: add new entries, update one-line summaries that changed.
Never delete an entry without explicit user approval.

## `log.md` format

Append-only. Every operation adds one entry, most recent at the bottom. Entry
header uses a consistent prefix so the log stays `grep`-parseable with
`grep "^## \[" log.md`.

```markdown
# Wiki Log

## [2026-04-18 14:30] ingest | Karpathy — LLM Wiki
- Source: [[2026-04-18-karpathy-llm-wiki]]
- New: [[concept/llm-wiki]], [[entity/andrej-karpathy]]
- Updated: [[concept/rag]], [[index]]
- Contradictions flagged: none

## [2026-04-18 15:02] query | how does ingest differ from RAG?
- Pages consulted: [[concept/llm-wiki]], [[concept/rag]]
- Gaps: none

## [2026-04-19 09:10] lint
- Orphans: 1 ([[entity/obsidian]])
- Unresolved conflicts: 0
- Stubs flagged: 2
```

Valid `<op>` values: `ingest`, `query`, `lint`, `resolve` (after resolving a
flagged conflict), `refactor` (structural changes across many pages).

## Slug rules

- Lowercase
- Words separated by single hyphens
- Alphanumeric + hyphens only
- No trailing or leading hyphens
- Source pages are prefixed with the ingest date: `YYYY-MM-DD-<slug>`
- Entity and concept pages are unprefixed
