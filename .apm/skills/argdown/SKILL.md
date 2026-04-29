---
name: argdown
description: Write, validate, and reason about Argdown argument maps. Use when creating argument maps, analyzing debates, reconstructing logical arguments, visualizing reasoning, working with .argdown files, or mapping out premise-conclusion structures. Also use when the user mentions logical arguments, premises, conclusions, support/attack relations, inference trees, argument visualization, debate analysis, or structured argumentation — even if they don't explicitly mention "Argdown." Covers full Argdown syntax, configuration, and export to PDF/SVG/PNG/HTML.
license: MIT
metadata:
  author: Daniel Saad
  email: me@dsaad.com
---

# Argdown — Argument Mapping Skill

Create well-structured Argdown documents that model arguments, debates, and logical analyses as visual argument maps.

## When to use this skill

- Creating or editing `.argdown` files
- Analyzing a debate or discussion with support/attack structure
- Reconstructing logical arguments with premises and conclusions
- Visualizing reasoning or argumentation
- Exporting argument maps to PDF, SVG, PNG, HTML, or JSON

## Choosing the right approach

| Scenario | Recommended approach |
|----------|---------------------|
| Simple pro/con debate | Minimal template: thesis + for/against + `+>` / `->` |
| Complex multi-argument analysis | Full reconstruction: sections, PCS, tags, `statementLabelMode: title` |
| Converting prose → Argdown | Extract claims first, then identify relations, then formalize with PCS |
| Visualizing an existing argument | Start with the conclusion, work backwards through premises |
| Quick sketch for discussion | Untitled statements + basic relations (no frontmatter needed) |

## Core workflow

### 1. Identify the argument structure

Before writing Argdown, identify:
- **Central thesis/claim** — the main proposition being debated
- **Supporting arguments** — reasons in favor
- **Opposing arguments** — reasons against
- **Relations** — which arguments support or attack which claims
- **Premise-conclusion structure** — the internal logic of each argument (if detailed reconstruction is needed)

### 2. Write the Argdown document

Start with optional frontmatter configuration, then define statements, arguments, and their relations.

**Minimal template:**

```argdown
===
title: [Descriptive Title]
===

# [Main Topic]

[Central Thesis]: The main claim being debated.

## Arguments For

<Supporting Argument>: Brief description of why. #pro
  +> [Central Thesis]

## Arguments Against

<Opposing Argument>: Brief description of why not. #con
  -> [Central Thesis]
```

### 3. Add detail as needed

- Add premise-conclusion structures for key arguments
- Use tags for categorization and color coding
- Group arguments into sections with headings
- Configure visualization in frontmatter

### 4. Ask user for rendering preferences

Before exporting, ask the user about these options (don't assume defaults):

- **Theme** — Light (default, transparent background) or dark (for presentations/dark-mode docs)?
- **Layout engine** — Hierarchical `dot` (default), force-directed `fdp` (good for large maps), circular `circo`, or radial `twopi`?
- **Legend** — Include a legend showing what colors/shapes mean?
- **sameRank** — Should any nodes be forced to the same level? (Useful for comparing alternatives side-by-side)
- **concentrate** — Merge parallel edges to reduce clutter? (Helps dense maps with many crossing edges)
- **DPI** — Screen (150), presentation (200), or print (300)?

### 5. Validate

```bash
uv run .claude/skills/argdown/scripts/validate.py <file.argdown>
```

### 6. Export or render

**Primary method — Python + Graphviz (no Node.js needed):**

```bash
# PNG (default, 150 DPI)
uv run .claude/skills/argdown/scripts/render.py <file.argdown>

# SVG
uv run .claude/skills/argdown/scripts/render.py <file.argdown> --format svg

# All formats (DOT + SVG + PNG)
uv run .claude/skills/argdown/scripts/render.py <file.argdown> --format all

# JSON (structured data, no Graphviz needed)
uv run .claude/skills/argdown/scripts/render.py <file.argdown> --format json

# High-DPI PNG
uv run .claude/skills/argdown/scripts/render.py <file.argdown> --dpi 300

# Dark theme
uv run .claude/skills/argdown/scripts/render.py <file.argdown> --theme dark

# With legend
uv run .claude/skills/argdown/scripts/render.py <file.argdown> --legend

# Alternative layout engine
uv run .claude/skills/argdown/scripts/render.py <file.argdown> --engine fdp

# Debug: dump parsed model
uv run .claude/skills/argdown/scripts/render.py <file.argdown> --dump-model
```

**Prerequisites:** Python 3.10+, [uv](https://docs.astral.sh/uv/), and [Graphviz](https://graphviz.org/) (`brew install graphviz` / `apt install graphviz`). Dependencies are auto-resolved by `uv run`.

**Alternative methods:**
- VS Code Argdown extension for live preview
- `@argdown/pandoc-filter` for embedding in PDF/HTML documents (see [publishing-and-export.md](references/publishing-and-export.md))

> **Note:** The `@argdown/cli` npm package has compatibility issues with Node.js ≥ 18. Use the Python scripts above instead.

## Feedback loop

Follow this cycle when building argument maps:

1. **Write** — Draft the Argdown document (start with structure, refine text later)
2. **Validate** — `uv run scripts/validate.py <file.argdown>` to catch syntax errors
3. **Render** — `uv run scripts/render.py <file.argdown>` to visualize
4. **Review** — Check the image: Are relations correct? Missing arguments? Overlapping nodes?
5. **Fix** — Common fixes:
   - Overlapping nodes → add `size: "22,28"` in graphVizSettings
   - Nodes too large → set `statementLabelMode: title`
   - Missing node → check for typo in `[Title]` references
   - Wrong direction → change `rankdir` (try LR for wide maps)
6. **Repeat** from step 2 until the map looks right

## Quick syntax reference

### Statements (propositions)

```argdown
This is an untitled statement.

[Titled Statement]: This statement has a reusable title.
```

Titled statements create **equivalence classes** — use the same `[Title]` anywhere to reference the same proposition.

### Arguments

```argdown
<Argument Name>: Brief informal description of the argument.
```

### Relations

Place relation lines indented below the parent element:

```argdown
[Thesis]: The main claim.
  +> [Supported Claim]      // outgoing support
  -> [Attacked Claim]       // outgoing attack
  <+ [Supporting Evidence]   // incoming support
  <- [Counter Evidence]      // incoming attack
  _> <Undercut Target>       // undercut (targets inference)
```

| Symbol | Meaning |
|--------|---------|
| `+>` | Supports |
| `->` | Attacks |
| `_>` | Undercuts |
| `<+` | Supported by |
| `<-` | Attacked by |
| `<_` | Undercut by |
| `><` | Contradicts (strict mode only) |

### Premise-Conclusion Structures (PCS)

Reconstruct an argument's internal logic:

```argdown
<Modus Ponens>

(1) If it rains, the street is wet.
(2) It rains.
----
(3) The street is wet.
```

- Number premises: `(1)`, `(2)`, etc.
- Inference line: `----` (4+ hyphens)
- Conclusions follow the inference line
- Use titled statements in PCS: `(1) [Premise Title]: text`

### Expanded inferences with metadata

```argdown
<Complex Argument>

(1) All humans are mortal.
(2) Socrates is human.
--
Modus Ponens {uses: [1,2]}
--
(3) Socrates is mortal.
```

### Headings, tags, and metadata

```argdown
# Section Heading        // creates groups in the map

[Statement]: Text. #tag-name #another-tag

<Argument>: Text. {source: "Smith 2020", isInMap: true}
```

### Comments

```argdown
// Single-line comment
/* Multi-line comment */
<!-- HTML comment -->
```

For the **complete syntax reference**, see [syntax-reference.md](references/syntax-reference.md).

## Key configuration options

Configuration goes in YAML frontmatter between `===` markers:

```argdown
===
selection:
  statementSelectionMode: with-title   # with-title | all | with-relations
  excludeDisconnected: true
model:
  mode: loose                          # loose | strict
color:
  colorScheme: colorbrewer-set3
  tagColors:
    pro: "#4CAF50"
    con: "#F44336"
dot:
  graphVizSettings:
    rankdir: BT                        # BT | TB | LR | RL
map:
  statementLabelMode: hide-untitled    # hide-untitled | title | text | none
  argumentLabelMode: hide-untitled
===
```

> **Important:** YAML uses `#` for comments. Do NOT use `//` inside frontmatter — that is Argdown comment syntax, valid only outside `===` blocks.

### Common configurations

**Show all statements as nodes:**
```yaml
selection:
  statementSelectionMode: all
```

**Oldschool inference tree (all steps visible):**
```yaml
selection:
  statementSelectionMode: all
model:
  explodeArguments: true
map:
  argumentLabelMode: none
dot:
  argument:
    shape: circle
    minWidth: 0.2
  graphVizSettings:
    rankdir: TB
```

**Filter by section or tag:**
```yaml
selection:
  selectedSections:
    - "Pro Arguments"
  selectedTags:
    - core
```

### Tips for complex maps (20+ nodes)

- **Always use `statementLabelMode: title`** — default `hide-untitled` shows full statement text, making nodes huge
- **Set explicit size:** Add `dot.graphVizSettings.size: "22,28"` to prevent text overlap
- **Use higher DPI:** Render with `--dpi 200` or `--dpi 300` for crisp output (default Graphviz DPI is 72)
- **Use sections (headings)** — they become visual groups/clusters in the map

For all configuration options, see [configuration-reference.md](references/configuration-reference.md).

## Common patterns

### Simple pro/con debate

```argdown
[Thesis]: Remote work should be the default.

<Productivity>: Fewer interruptions increase output. #pro
  +> [Thesis]

<Collaboration>: In-person brainstorming is harder remotely. #con
  -> [Thesis]
```

### Connecting arguments through shared statements

```argdown
<Arg A>

(1) [Shared Premise]: All humans are mortal.
(2) Socrates is human.
----
(3) [Shared Conclusion]: Socrates is mortal.

<Arg B>

(1) [Shared Conclusion]
(2) Mortality implies impermanence.
----
(3) Socrates is impermanent.
```

### Forcing a statement into the map

```argdown
[Hidden by Default]: This statement. {isInMap: true}
```

### Undercuts (attacking the inference, not the conclusion)

```argdown
<Main Argument>

(1) The sample shows X.
(2) X implies Y.
----
(3) Therefore Y.

<Methodological Critique>: The sample is too small. #con
  _> <Main Argument>
```

For more complete examples, see [examples.md](references/examples.md).

## Reference files

Read these when you need deeper detail:

- **[syntax-reference.md](references/syntax-reference.md)** — Complete Argdown syntax: statements, equivalence classes, arguments, all relation types, PCS structures, tags, metadata, comments, shortcodes, bold/italic, links
- **[configuration-reference.md](references/configuration-reference.md)** — All YAML frontmatter options: selection, model, map, dot/graphviz, color settings
- **[publishing-and-export.md](references/publishing-and-export.md)** — Exporting to PDF, SVG, PNG, HTML via CLI, Pandoc integration, image export, web embedding, slideshows
- **[examples.md](references/examples.md)** — Complete real-world argument map examples at various complexity levels

## Validation

Validate Argdown syntax with the bundled Python validator:

```bash
uv run .claude/skills/argdown/scripts/validate.py <file.argdown>
uv run .claude/skills/argdown/scripts/validate.py <file.argdown> --strict   # warnings = errors
uv run .claude/skills/argdown/scripts/validate.py *.argdown                 # batch validate
```

For quick pattern-based checks (no dependencies):

```bash
bash .claude/skills/argdown/scripts/validate-argdown.sh <file.argdown>
```

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `Graphviz 'dot' command not found` | Graphviz not installed | `brew install graphviz` (macOS) or `apt install graphviz` (Linux) |
| `uv: command not found` | uv not installed | `curl -LsSf https://astral.sh/uv/install.sh \| sh` or `brew install uv` |
| Empty map (0 relations) | No `+>`, `->`, `_>` relations defined | Add relations between statements and arguments |
| Nodes overlap in PNG | Map too large for default canvas | Add `dot.graphVizSettings.size: "22,28"` in frontmatter |
| Nodes show full text (huge) | Default label mode shows full text | Set `map.statementLabelMode: title` |
| YAML parse error in frontmatter | Invalid YAML (wrong indentation, `//` comments) | Use `#` for comments, check indentation (2 spaces) |
| Unclosed bracket `[Title` | Missing `]` or `>` | Close all `[Title]` and `<Argument>` brackets |
| Statement not appearing | Title typo in reference | Check spelling matches exactly between definition and reference |
| `TypeError: isFunction` from CLI | `@argdown/cli` broken on Node.js ≥ 18 | Use Python `render.py` instead |
