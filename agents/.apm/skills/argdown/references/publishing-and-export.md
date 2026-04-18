# Publishing & Export Reference

How to export Argdown argument maps to PDF, SVG, PNG, HTML, and other formats.

## Contents

- [Python Export (Recommended)](#python-export-recommended)
- [CLI Export — Legacy](#cli-export-argdowncli--legacy)
- [Pandoc Integration](#pandoc-integration)
- [Creating Slideshows](#creating-slideshows)
- [Embedding in Webpages](#embedding-in-webpages)
- [Syntax Highlighting](#syntax-highlighting)
- [Quick Reference](#quick-reference)

## Python Export (Recommended)

The bundled `render.py` script parses Argdown, generates DOT, and renders via Graphviz. It uses [uv](https://docs.astral.sh/uv/) for zero-setup dependency management (PEP 723 inline script metadata).

### Prerequisites

- **Python 3.10+**
- **uv** — `curl -LsSf https://astral.sh/uv/install.sh | sh` or `brew install uv`
- **Graphviz** — `brew install graphviz` (macOS) or `apt install graphviz` (Debian/Ubuntu)

Dependencies (`pyyaml`) are auto-resolved by `uv run` — no manual install needed.

### Commands

```bash
# PNG (default, 150 DPI)
uv run scripts/render.py input.argdown

# SVG
uv run scripts/render.py input.argdown --format svg

# DOT only (no Graphviz needed)
uv run scripts/render.py input.argdown --format dot

# JSON export (structured data, no Graphviz needed)
uv run scripts/render.py input.argdown --format json

# All formats (DOT + SVG + PNG)
uv run scripts/render.py input.argdown --format all

# Custom output path
uv run scripts/render.py input.argdown -o output.png

# High-DPI for print
uv run scripts/render.py input.argdown --dpi 300

# Dark theme
uv run scripts/render.py input.argdown --theme dark

# Add legend showing edge/node types
uv run scripts/render.py input.argdown --legend

# Alternative layout engine (neato, fdp, circo, twopi, osage)
uv run scripts/render.py input.argdown --engine fdp

# Disable section grouping
uv run scripts/render.py input.argdown --no-groups

# Debug: show parsed model
uv run scripts/render.py input.argdown --dump-model
```

### CLI Flags Reference

| Flag | Values | Default | Description |
|------|--------|---------|-------------|
| `-f, --format` | `png`, `svg`, `dot`, `json`, `all` | `png` | Output format |
| `-o, --output` | path | auto | Output file path |
| `--dpi` | integer | `150` | DPI for PNG output |
| `--engine` | `dot`, `neato`, `fdp`, `circo`, `twopi`, `osage` | `dot` | Graphviz layout engine |
| `--theme` | `light`, `dark` | `light` | Color theme |
| `--legend` | flag | off | Add color/shape legend |
| `--no-groups` | flag | off | Disable section clustering |
| `--dump-model` | flag | off | Print parsed model to stderr |

### Layout Engines

| Engine | Best for |
|--------|----------|
| `dot` | Hierarchical layouts (default, best for argument maps) |
| `neato` | Undirected spring-model layouts |
| `fdp` | Force-directed layouts (good for large maps) |
| `circo` | Circular layouts |
| `twopi` | Radial layouts |
| `osage` | Array-based layouts |

### DPI Guidance

| DPI | Use case |
|-----|----------|
| 72 | Graphviz default — blurry, avoid |
| 150 | Render.py default — good for screen/docs |
| 200 | Presentations and large displays |
| 300 | Print quality |

### How It Works

1. Parses Argdown syntax (statements, arguments, relations, PCS, tags, frontmatter)
2. Builds an internal model (equivalence classes, relation graph, section hierarchy)
3. Generates DOT with: tag-based node colors, section subgraph clusters, styled edges (green=support, red=attack, orange=undercut, purple=contradiction)
4. Invokes `dot` (Graphviz) to render PNG/SVG

### Sizing for Complex Maps

For maps with 20+ nodes, set explicit Graphviz size in frontmatter:

```argdown
===
dot:
  graphVizSettings:
    size: "22,28"
    rankdir: TB
map:
  statementLabelMode: title   # essential — prevents enormous nodes
===
```

Or pass DPI flag: `--dpi 200`

---

## CLI Export (`@argdown/cli`) — Legacy

> **⚠ Compatibility Warning:** The `@argdown/cli` package has known compatibility issues with Node.js ≥ 18 due to a Chevrotain dependency bug (`TypeError: (0, util_1.isFunction) is not a function`). Use the Python scripts above instead.

### Installation

```bash
npm install -g @argdown/cli

# Optional: for PNG/JPG/WebP image export
npm install -g @argdown/image-export
```

Requires Node.js >= 13.7.0.

### Commands

| Command | Output | Description |
|---------|--------|-------------|
| `argdown map <file> [outdir]` | PDF (default) | Visual argument map |
| `argdown map <file> --format svg` | SVG | Scalable vector |
| `argdown map <file> --format dot` | DOT | Graphviz source |
| `argdown map <file> --format png` | PNG* | Raster image |
| `argdown map <file> --format jpg` | JPG* | Raster image |
| `argdown map <file> --format webp` | WebP* | Raster image |
| `argdown map <file> --format graphml` | GraphML | Graph exchange format |
| `argdown html <file> [outdir]` | HTML | Static HTML document |
| `argdown web-component <file> [outdir]` | HTML | Interactive web component |
| `argdown json <file> [outdir]` | JSON | Data export |
| `argdown compile <file> [outdir]` | Argdown | Compiled (includes resolved) |
| `argdown <glob>` | Console | Validate and show diagnostics |

\* Requires `@argdown/image-export` plugin.

### Common Options

```bash
-w, --watch        # Watch for file changes and re-export
--stdout           # Output to stdout instead of file
--silent           # Suppress console output
--config <path>    # Use custom config file
--format <fmt>     # Output format (for map command)
```

### Examples

```bash
# PDF argument map
argdown map debate.argdown ./output

# SVG export
argdown map debate.argdown ./output --format svg

# PNG export (requires @argdown/image-export)
argdown map debate.argdown ./output --format png

# Interactive HTML web component
argdown web-component debate.argdown ./output

# JSON data export
argdown json debate.argdown ./output

# Validate files
argdown "src/**/*.argdown"

# Watch mode
argdown map -w debate.argdown ./output
```

## Pandoc Integration

Use the `@argdown/pandoc-filter` to embed Argdown argument maps in Markdown documents and export via Pandoc to PDF, HTML, LaTeX, and other formats.

### Installation

```bash
# 1. Install Pandoc: https://pandoc.org/installing.html
# 2. Install LaTeX and rsvg-convert (needed by Pandoc)
# 3. Install the Argdown Pandoc filter:
npm install -g @argdown/pandoc-filter

# Optional: for PNG/JPG/WebP in Pandoc output
npm install -g @argdown/image-export
```

### Usage in Markdown

Use `argdown-map` fenced code blocks in your Markdown:

````markdown
This is regular Markdown text. Here comes an argument map:

```argdown-map
[Central Thesis]: The main claim.
  <- <Counter Argument>: An opposing view.
  +> [Supporting Evidence]: Key evidence.
```

And here the Markdown continues.
````

### Exporting to PDF

```bash
# macOS / Linux
pandoc input.md -f markdown -t pdf --filter argdown-filter -o output.pdf

# Windows 10
pandoc input.md -f markdown -t pdf --filter argdown-filter.cmd -o output.pdf
```

### Exporting to HTML

```bash
pandoc input.md -f markdown -t html -s --filter argdown-filter -o output.html
```

### Pandoc Filter Configuration

Configure the filter via Markdown YAML metadata:

```markdown
---
argdown:
  mode: "file"      # "inline" (default), "file", or "web-component"
  format: "png"     # "svg" (default), "png", "jpg", "webp"
---

Your Markdown content with `argdown-map` code blocks...
```

### Export Modes

| Mode | Behavior |
|------|----------|
| `inline` | **(Default)** Argument map embedded as inline image |
| `file` | Argument map saved as separate image file |
| `web-component` | Interactive HTML web component (HTML export only) |

### Image Formats

| Format | Requires |
|--------|----------|
| `svg` | **(Default)** Built-in |
| `png` | `@argdown/image-export` |
| `jpg` | `@argdown/image-export` |
| `webp` | `@argdown/image-export` |

### Per-Block Configuration

Override settings for individual code blocks:

````markdown
```{.argdown-map #fig:first-map caption="First argument map" format="png" width=800}
[Thesis]: The claim.
  <- <Counter>: Against it.
```
````

Supports:
- `caption` — Figure caption
- `#fig:id` — Figure ID for cross-references (use with pandoc-crossref)
- `format` — Image format override
- `width` / `height` — Image dimensions
- `config` — Path to argdown.config.json

### Cross-References with pandoc-crossref

```markdown
See @fig:first-map for the initial analysis and @fig:second-map for the rebuttal.
```

Requires the [pandoc-crossref](https://github.com/lierdakil/pandoc-crossref) filter.

### Using External Config Files

```markdown
---
argdown:
  config: "path/to/argdown.config.json"
  mode: "web-component"
---
```

Config file paths are relative to the directory where you run Pandoc.

Per-block config override:

````markdown
```{.argdown-map config="other-config.json"}
[Thesis]: Claim.
```
````

## Creating Slideshows

Combine Pandoc with Reveal.js to create presentations with argument maps:

```bash
pandoc -s --webtex -i -t revealjs slides.md \
  -V theme=black --filter argdown-filter -o slides.html
```

See the [Pandoc Reveal.js guide](https://github.com/jgm/pandoc/wiki/Using-pandoc-to-produce-reveal.js-slides) for more.

## Embedding in Webpages

### Web Component Export

The `web-component` export creates interactive, embeddable argument maps:

```bash
argdown web-component myfile.argdown ./output
```

This produces an HTML file with an `<argdown-map>` custom element.

### Using in Markdown (Static Site Generators)

Many static site generators support Argdown via plugins. The `argdown-map` code block syntax works in systems that support Argdown rendering.

### Application Integration

For custom applications, use `@argdown/core` directly:

```javascript
const { ArgdownApplication } = require("@argdown/core");

const app = new ArgdownApplication();
// Configure plugins and run processing pipeline
```

## Syntax Highlighting

For Pandoc output with Argdown syntax highlighting:
- Use Sebastian Cacean's [argdown-pandoc-highlighting](https://github.com/xylomorph/argdown-pandoc-highlighting)
- Or use the `web-component` export mode which includes built-in highlighting

## Quick Reference

### Most common export workflows

| Goal | Command |
|------|---------|
| Quick PDF | `argdown map file.argdown` |
| SVG for web | `argdown map file.argdown --format svg` |
| PNG image | `argdown map file.argdown --format png` |
| Interactive HTML | `argdown web-component file.argdown` |
| PDF via Pandoc | `pandoc doc.md -t pdf --filter argdown-filter -o doc.pdf` |
| HTML via Pandoc | `pandoc doc.md -t html -s --filter argdown-filter -o doc.html` |
| JSON data | `argdown json file.argdown` |
