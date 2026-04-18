# Argdown Configuration Reference

All configuration options for customizing Argdown parser behavior via YAML frontmatter or config files.

## Contents

- [Configuration Methods](#configuration-methods)
- [Selection Settings](#selection-settings)
- [Model Settings](#model-settings)
- [Map Settings](#map-settings)
- [Group Settings](#group-settings)
- [Dot / Graphviz Settings](#dot--graphviz-settings)
- [Color Settings](#color-settings)
- [Common Configuration Recipes](#common-configuration-recipes)

## Configuration Methods

1. **Frontmatter** — YAML between `===` markers at the top of `.argdown` files
2. **Config file** — `argdown.config.json` or `argdown.config.js` in the project directory

Frontmatter is good for per-document settings; config files are reusable across documents.

## Selection Settings

Control which statements and arguments appear in the argument map.

```yaml
selection:
  statementSelectionMode: with-title
  excludeDisconnected: true
  selectedSections: []
  selectedTags: []
  selectElementsWithoutTag: false
  selectElementsWithoutSection: false
  includeStatements: []
  excludeStatements: []
  excludeArguments: []
  ignoreIsInMap: false
```

### `statementSelectionMode`

| Value | Behavior |
|-------|----------|
| `with-title` | **(Default)** Only titled statements become nodes |
| `all` | All statements become nodes |
| `with-relations` | Statements with at least one relation become nodes |
| `with-more-than-one-relation` | Statements with 2+ relations become nodes |
| `not-used-in-argument` | Statements not used in any PCS become nodes |

### `excludeDisconnected`

Default: `true`. When enabled, nodes not connected to any other node are excluded.

**An element counts as "connected" if:**
- *Statement*: Used in a preselected argument's PCS, or has a relation to a preselected element
- *Argument*: Directly related to another element, or a premise is supported/attacked, or main conclusion supports/attacks another element

### Section and Tag Filtering

```yaml
selection:
  selectedSections:
    - "Pro Arguments"
    - "Con Arguments"
  selectElementsWithoutSection: false

  selectedTags:
    - pro
    - con
    - core
  selectElementsWithoutTag: true
```

### Explicit Include/Exclude

```yaml
selection:
  includeStatements:
    - "Main Thesis"
    - "Key Evidence"
  excludeStatements:
    - "Tangential Point"
  excludeArguments:
    - "Weak Argument"
```

### The `isInMap` Data Flag

Override selection per-element directly in the Argdown source:

```argdown
[Always Shown]: This appears in the map. {isInMap: true}
[Never Shown]: This is excluded. {isInMap: false}
```

To ignore these flags globally:
```yaml
selection:
  ignoreIsInMap: true
```

## Model Settings

Control how the argument model is built from the parsed AST.

```yaml
model:
  mode: loose
  explodeArguments: false
  removeTagsFromText: false
```

### `mode`

| Mode | `+`/`<+` | `-`/`<-` | `><` |
|------|----------|----------|------|
| `loose` **(default)** | Support | Attack | N/A |
| `strict` | Entailment | Contrariness | Contradiction |

### `explodeArguments`

When `true`, multi-step arguments are split into separate argument nodes — one per inferential step. Essential for "oldschool" argument maps.

```yaml
model:
  explodeArguments: true
```

### `removeTagsFromText`

When `true`, `#tags` are stripped from displayed statement and description text.

## Map Settings

Control visual representation of nodes and labels.

```yaml
map:
  statementLabelMode: hide-untitled
  argumentLabelMode: hide-untitled
  addTags: false
```

### Label Modes

| Value | Behavior |
|-------|----------|
| `hide-untitled` | **(Default)** Title + text; hidden if no title |
| `title` | Title only |
| `text` | Text content only |
| `none` | No text in nodes |

### `addTags`

When `true`, tags are displayed in node labels.

## Group Settings

Control how headings create groups in the map.

```yaml
group:
  groupDepth: 2
  regroup:
    - title: "Custom Group"
      statements: ["Statement A"]
      arguments: ["Argument B"]
```

- `groupDepth`: How many heading levels create groups (default: all)
- `regroup`: Manually reassign elements to named groups

## Dot / Graphviz Settings

Control the Graphviz DOT output for graph rendering.

```yaml
dot:
  graphVizSettings:
    rankdir: BT
    ratio: auto
    size: "10,10"
  argument:
    shape: box
    minWidth: 3
    fontSize: 12
    font: "Arial"
    bold: true
  statement:
    shape: box
    minWidth: 5
    fontSize: 12
    font: "Arial"
    bold: true
```

### `rankdir` — Graph Flow Direction

| Value | Direction | Best For |
|-------|-----------|----------|
| `BT` | Bottom → Top **(default)** | Standard argument maps |
| `TB` | Top → Bottom | Inference trees |
| `LR` | Left → Right | Horizontal layouts |
| `RL` | Right → Left | Right-to-left layouts |

### Node Shapes

Common Graphviz shapes: `box` (default), `circle`, `diamond`, `ellipse`, `record`, `plaintext`

### Image Settings

```yaml
dot:
  statement:
    images:
      "#earth": "https://example.com/earth.png"
      position: top
      padding: 10
```

## Color Settings

```yaml
color:
  colorScheme: colorbrewer-set3
  tagColors:
    pro: "#4CAF50"
    con: "#F44336"
    neutral: "#9E9E9E"
  statementColors:
    "Main Thesis": "#2196F3"
  argumentColors:
    "Key Argument": "#FF9800"
  groupColors:
    "Section A": "#E0E0E0"
```

### Built-in Color Schemes

ColorBrewer schemes: `colorbrewer-set1`, `colorbrewer-set2`, `colorbrewer-set3`, `colorbrewer-paired`

iwanthue schemes: `iwanthue-red-roses`, `iwanthue-fluo`, and others

### Color Assignment Priority

1. **Inline metadata** `{color: "#hex"}` — highest priority
2. **Title colors** (`statementColors` / `argumentColors`)
3. **Tag colors** (`tagColors`)
4. **Group colors** (`groupColors`)
5. **Color scheme** — automatic assignment

## Common Configuration Recipes

### Standard debate map

```yaml
===
selection:
  statementSelectionMode: with-title
color:
  tagColors:
    pro: "#4CAF50"
    con: "#F44336"
===
```

### Oldschool inference tree

```yaml
===
selection:
  statementSelectionMode: all
model:
  explodeArguments: true
map:
  argumentLabelMode: none
  statementLabelMode: text
dot:
  argument:
    shape: circle
    minWidth: 0.2
  graphVizSettings:
    rankdir: TB
===
```

### Focused view (specific sections only)

```yaml
===
selection:
  selectedSections:
    - "Core Arguments"
  selectElementsWithoutSection: false
  excludeDisconnected: true
===
```

### Title-only compact map

```yaml
===
map:
  statementLabelMode: title
  argumentLabelMode: title
dot:
  statement:
    minWidth: 2
  argument:
    minWidth: 2
  graphVizSettings:
    rankdir: LR
===
```

### Same-rank alignment

Force specific nodes to align at the same rank (useful for comparing alternatives):

```yaml
===
dot:
  sameRank:
    - statements: ["Option A", "Option B", "Option C"]
    - arguments: ["Pro A", "Pro B"]
===
```

This generates `{rank=same; ...}` blocks in the DOT output, aligning the listed nodes horizontally (in TB/BT layouts) or vertically (in LR/RL layouts).

### Strict mode with contradiction

```yaml
===
model:
  mode: strict
color:
  colorScheme: colorbrewer-set1
===
```
