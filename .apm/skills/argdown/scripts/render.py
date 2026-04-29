#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
"""
render.py — Self-contained Argdown → DOT → PNG/SVG renderer.

Requires: uv (https://docs.astral.sh/uv/) + Graphviz system package.

Install Graphviz:
  macOS:   brew install graphviz
  Linux:   apt install graphviz
  Windows: choco install graphviz

Usage:
  uv run render.py input.argdown                  # → input.png
  uv run render.py input.argdown --format svg     # → input.svg
  uv run render.py input.argdown --format dot     # → input.dot (no Graphviz needed)
  uv run render.py input.argdown -o output.png    # custom output path
  uv run render.py input.argdown --dpi 200        # higher resolution PNG
  uv run render.py input.argdown --format all     # → .dot + .svg + .png
"""

import re
import sys
import shutil
import os
import subprocess
import argparse
import textwrap
from typing import Optional


# Import shared parser (same directory)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from argdown_parser import (
    ArgdownModel,
    parse_argdown,
)

# ─── DOT Generation ────────────────────────────────────────────────────────────

def escape_dot(text: str) -> str:
    """Escape text for DOT labels."""
    return (text.replace("\\", "\\\\")
                .replace('"', '\\"')
                .replace("\n", "\\n")
                .replace("<", "\\<")
                .replace(">", "\\>")
                .replace("{", "\\{")
                .replace("}", "\\}"))


def wrap_label(text: str, width: int = 28) -> str:
    """Wrap text for DOT node labels."""
    lines = textwrap.wrap(text, width=width)
    return "\\n".join(lines)


def resolve_color(element, config: dict, element_type: str) -> Optional[str]:
    """Resolve color for an element from config."""
    color_cfg = config.get("color", {})

    # Check inline metadata
    if hasattr(element, 'meta') and element.meta.get("color"):
        return element.meta["color"]

    # Check title-based colors
    title_colors = color_cfg.get(f"{element_type}Colors", {})
    if isinstance(title_colors, dict) and element.title in title_colors:
        return title_colors[element.title]

    # Check tag-based colors
    tag_colors = color_cfg.get("tagColors", {})
    if isinstance(tag_colors, dict) and hasattr(element, 'tags'):
        for tag in element.tags:
            if tag in tag_colors:
                return tag_colors[tag]

    return None


def contrast_fontcolor(bg_hex: str) -> str:
    """Return white or dark text depending on background luminance."""
    bg = bg_hex.lstrip("#")
    if len(bg) != 6:
        return "#FFFFFF"
    r, g, b = int(bg[:2], 16), int(bg[2:4], 16), int(bg[4:6], 16)
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return "#212121" if lum > 140 else "#FFFFFF"


# ─── Themes ────────────────────────────────────────────────────────────────────

THEMES = {
    "light": {
        "graph_bgcolor": "transparent",
        "cluster_border": "#90A4AE",
        "cluster_fontcolor": "#37474F",
        "cluster_bgcolor": "#FAFAFA",
        "default_stmt_color": "#BBDEFB",
        "default_arg_color": "#C8E6C9",
        "edge_support": "#2E7D32",
        "edge_attack": "#C62828",
        "edge_undercut": "#E65100",
        "edge_contradiction": "#6A1B9A",
    },
    "dark": {
        "graph_bgcolor": "#1E1E1E",
        "cluster_border": "#546E7A",
        "cluster_fontcolor": "#B0BEC5",
        "cluster_bgcolor": "#263238",
        "default_stmt_color": "#1565C0",
        "default_arg_color": "#2E7D32",
        "edge_support": "#66BB6A",
        "edge_attack": "#EF5350",
        "edge_undercut": "#FFA726",
        "edge_contradiction": "#AB47BC",
    },
}


# Default color palette (colorbrewer-set3 inspired)
DEFAULT_COLORS = [
    "#8dd3c7", "#ffffb3", "#bebada", "#fb8072", "#80b1d3",
    "#fdb462", "#b3de69", "#fccde5", "#d9d9d9", "#bc80bd",
    "#ccebc5", "#ffed6f",
]


# ─── JSON Export ───────────────────────────────────────────────────────────────

def model_to_json(model: ArgdownModel) -> dict:
    """Convert ArgdownModel to a JSON-serializable dict."""
    return {
        "title": model.title,
        "statements": {
            t: {
                "text": s.text,
                "tags": s.tags,
                "meta": s.meta,
                "section": s.section,
            } for t, s in model.statements.items()
        },
        "arguments": {
            t: {
                "description": a.description,
                "tags": a.tags,
                "meta": a.meta,
                "section": a.section,
            } for t, a in model.arguments.items()
        },
        "relations": [
            {
                "source": r.source,
                "source_type": r.source_type,
                "target": r.target,
                "target_type": r.target_type,
                "relation": r.relation,
            } for r in model.relations
        ],
        "sections": model.sections,
        "section_parent": model.section_parent,
        "config": model.config,
    }


def generate_dot(model: ArgdownModel, theme_name: str = "light",
                 show_legend: bool = False) -> str:
    """Generate Graphviz DOT from an ArgdownModel."""
    theme = THEMES.get(theme_name, THEMES["light"])
    config = model.config
    dot_cfg = config.get("dot", {})
    gv = dot_cfg.get("graphVizSettings", {})
    map_cfg = config.get("map", {})
    stmt_cfg = dot_cfg.get("statement", {})
    arg_cfg = dot_cfg.get("argument", {})

    rankdir = gv.get("rankdir", "BT")
    size = gv.get("size", "")
    ratio = gv.get("ratio", "")
    nodesep = gv.get("nodesep", "0.6")
    ranksep = gv.get("ranksep", "0.8")

    stmt_label_mode = map_cfg.get("statementLabelMode", "hide-untitled")
    arg_label_mode = map_cfg.get("argumentLabelMode", "hide-untitled")

    stmt_shape = stmt_cfg.get("shape", "box")
    arg_shape = arg_cfg.get("shape", "box")
    stmt_min_w = stmt_cfg.get("minWidth", 3)
    arg_min_w = arg_cfg.get("minWidth", 2.5)
    stmt_fontsize = stmt_cfg.get("fontSize", 12)
    arg_fontsize = arg_cfg.get("fontSize", 12)

    lines = ['digraph argument_map {']
    lines.append(f'  rankdir={rankdir};')
    lines.append(f'  graph [bgcolor="{theme["graph_bgcolor"]}", pad=0.5, nodesep={nodesep}, ranksep={ranksep}];')
    if size:
        lines.append(f'  graph [size="{size}"];')
    if ratio:
        lines.append(f'  graph [ratio="{ratio}"];')
    # Pass through any other graphVizSettings not explicitly handled
    skip_keys = {"rankdir", "size", "ratio", "nodesep", "ranksep"}
    extra_gv = {k: v for k, v in gv.items() if k not in skip_keys}
    if extra_gv:
        attrs = ", ".join(f'{k}="{v}"' for k, v in extra_gv.items())
        lines.append(f'  graph [{attrs}];')
    lines.append(f'  node [fontname="Helvetica", fontsize={stmt_fontsize}];')
    lines.append('  edge [fontname="Helvetica"];')
    lines.append('')

    # Collect sections for subgraph grouping
    section_elements = {}  # section -> [(id, type)]
    color_idx = 0

    def next_color():
        nonlocal color_idx
        c = DEFAULT_COLORS[color_idx % len(DEFAULT_COLORS)]
        color_idx += 1
        return c

    def node_id(elem_type: str, title: str) -> str:
        safe = re.sub(r'[^a-zA-Z0-9]', '_', title)
        prefix = "s_" if elem_type == "statement" else "a_"
        return prefix + safe

    def get_label(title: str, text: str, mode: str) -> str:
        if mode == "title":
            return wrap_label(title)
        elif mode == "text":
            return wrap_label(text) if text else wrap_label(title)
        elif mode == "none":
            return ""
        else:  # hide-untitled
            if title and text:
                return wrap_label(f"{title}\\n{text}", 32)
            return wrap_label(title or text)

    # Collect which elements are connected
    connected = set()
    exclude_disconnected = config.get("selection", {}).get("excludeDisconnected", True)
    for rel in model.relations:
        connected.add((rel.source_type, rel.source))
        connected.add((rel.target_type, rel.target))

    # Generate statement nodes
    for title, stmt in model.statements.items():
        if exclude_disconnected and ("statement", title) not in connected:
            # Check isInMap
            if not stmt.meta.get("isInMap", False):
                continue

        nid = node_id("statement", title)
        label = get_label(title, stmt.text, stmt_label_mode)
        color = resolve_color(stmt, config, "statement") or theme["default_stmt_color"]
        fontcolor = contrast_fontcolor(color)

        sec = stmt.section
        if sec:
            section_elements.setdefault(sec, []).append(nid)

        lines.append(f'  {nid} [')
        lines.append(f'    label="{escape_dot(label)}",')
        lines.append(f'    shape={stmt_shape},')
        lines.append('    style="filled,rounded",')
        lines.append(f'    fillcolor="{color}",')
        lines.append(f'    fontcolor="{fontcolor}",')
        lines.append('    penwidth=1.5,')
        lines.append(f'    width={stmt_min_w},')
        lines.append(f'    fontsize={stmt_fontsize}')
        lines.append('  ];')

    # Generate argument nodes
    for title, arg in model.arguments.items():
        if exclude_disconnected and ("argument", title) not in connected:
            if not arg.meta.get("isInMap", False):
                continue

        nid = node_id("argument", title)
        label = get_label(title, arg.description, arg_label_mode)
        color = resolve_color(arg, config, "argument") or theme["default_arg_color"]
        fontcolor = contrast_fontcolor(color)

        sec = arg.section
        if sec:
            section_elements.setdefault(sec, []).append(nid)

        lines.append(f'  {nid} [')
        lines.append(f'    label="{escape_dot(label)}",')
        lines.append(f'    shape={arg_shape},')
        lines.append('    style="filled",')
        lines.append(f'    fillcolor="{color}",')
        lines.append(f'    fontcolor="{fontcolor}",')
        lines.append('    penwidth=1.5,')
        lines.append(f'    width={arg_min_w},')
        lines.append(f'    fontsize={arg_fontsize}')
        lines.append('  ];')

    lines.append('')

    # Generate edges
    edge_styles = {
        "support": {"color": theme["edge_support"], "style": "solid", "arrowhead": "normal", "penwidth": "2.0"},
        "attack": {"color": theme["edge_attack"], "style": "solid", "arrowhead": "normal", "penwidth": "2.0"},
        "undercut": {"color": theme["edge_undercut"], "style": "dashed", "arrowhead": "tee", "penwidth": "1.5"},
        "contradiction": {"color": theme["edge_contradiction"], "style": "bold", "arrowhead": "diamond", "penwidth": "2.0"},
    }

    for rel in model.relations:
        src_id = node_id(rel.source_type, rel.source)
        tgt_id = node_id(rel.target_type, rel.target)
        style = edge_styles.get(rel.relation, edge_styles["support"])

        lines.append(f'  {src_id} -> {tgt_id} [')
        lines.append(f'    color="{style["color"]}",')
        lines.append(f'    style="{style["style"]}",')
        lines.append(f'    arrowhead="{style["arrowhead"]}",')
        lines.append(f'    penwidth={style["penwidth"]}')
        lines.append('  ];')

    lines.append('')

    # Generate nested subgraphs for sections
    # Build full parent→children tree from section_parent
    children_map = {}  # parent -> [child section names]
    for sec, par in model.section_parent.items():
        if par is not None:
            children_map.setdefault(par, []).append(sec)

    def has_content(sec):
        """Check if section or any descendant has elements."""
        if section_elements.get(sec):
            return True
        return any(has_content(c) for c in children_map.get(sec, []))

    # Top-level = sections with no parent that have content
    top_level = []
    seen = set()
    for sec in model.sections:
        if sec in seen:
            continue
        seen.add(sec)
        par = model.section_parent.get(sec)
        if par is None and has_content(sec):
            top_level.append(sec)

    def emit_cluster(section, indent=2):
        """Emit a cluster with nested child clusters."""
        members = section_elements.get(section, [])
        kids = [c for c in children_map.get(section, []) if has_content(c)]
        if not members and not kids:
            return
        prefix = " " * indent
        cluster_id = re.sub(r'[^a-zA-Z0-9]', '_', section)
        lines.append(f'{prefix}subgraph cluster_{cluster_id} {{')
        lines.append(f'{prefix}  label="{escape_dot(section)}";')
        lines.append(f'{prefix}  style="rounded,dashed";')
        lines.append(f'{prefix}  color="{theme["cluster_border"]}";')
        lines.append(f'{prefix}  fontname="Helvetica";')
        lines.append(f'{prefix}  fontsize=14;')
        lines.append(f'{prefix}  fontcolor="{theme["cluster_fontcolor"]}";')
        lines.append(f'{prefix}  bgcolor="{theme["cluster_bgcolor"]}";')
        for m in members:
            lines.append(f'{prefix}  {m};')
        for child in kids:
            emit_cluster(child, indent + 2)
        lines.append(f'{prefix}}}')

    for section in top_level:
        emit_cluster(section)

    # ── sameRank blocks ──
    same_rank_cfg = dot_cfg.get("sameRank", [])
    for rank_group in same_rank_cfg:
        rank_nodes = []
        for st in rank_group.get("statements", []):
            rank_nodes.append(node_id("statement", st))
        for ar in rank_group.get("arguments", []):
            rank_nodes.append(node_id("argument", ar))
        if rank_nodes:
            nodes_str = "; ".join(rank_nodes)
            lines.append(f'  {{rank=same; {nodes_str}}}')

    # ── Legend ──
    if show_legend:
        lines.append('')
        lines.append('  subgraph cluster_legend {')
        lines.append('    label="Legend";')
        lines.append('    style="rounded,solid";')
        lines.append(f'    color="{theme["cluster_border"]}";')
        lines.append('    fontname="Helvetica";')
        lines.append('    fontsize=12;')
        lines.append(f'    fontcolor="{theme["cluster_fontcolor"]}";')
        lines.append(f'    bgcolor="{theme["cluster_bgcolor"]}";')
        lines.append(f'    legend_s [label="Statement", shape=box, style="filled,rounded", fillcolor="{theme["default_stmt_color"]}", fontcolor="{contrast_fontcolor(theme["default_stmt_color"])}", fontsize=10, width=1.2];')
        lines.append(f'    legend_a [label="Argument", shape=box, style="filled", fillcolor="{theme["default_arg_color"]}", fontcolor="{contrast_fontcolor(theme["default_arg_color"])}", fontsize=10, width=1.2];')
        lines.append('    legend_sup_s [label="", shape=point, width=0]; legend_sup_t [label="", shape=point, width=0];')
        lines.append(f'    legend_sup_s -> legend_sup_t [label="  supports", color="{theme["edge_support"]}", style=solid, penwidth=2, fontsize=9, fontcolor="{theme["cluster_fontcolor"]}"];')
        lines.append('    legend_att_s [label="", shape=point, width=0]; legend_att_t [label="", shape=point, width=0];')
        lines.append(f'    legend_att_s -> legend_att_t [label="  attacks", color="{theme["edge_attack"]}", style=solid, penwidth=2, fontsize=9, fontcolor="{theme["cluster_fontcolor"]}"];')
        lines.append('    legend_und_s [label="", shape=point, width=0]; legend_und_t [label="", shape=point, width=0];')
        lines.append(f'    legend_und_s -> legend_und_t [label="  undercuts", color="{theme["edge_undercut"]}", style=dashed, arrowhead=tee, penwidth=1.5, fontsize=9, fontcolor="{theme["cluster_fontcolor"]}"];')
        lines.append('    legend_con_s [label="", shape=point, width=0]; legend_con_t [label="", shape=point, width=0];')
        lines.append(f'    legend_con_s -> legend_con_t [label="  contradicts", color="{theme["edge_contradiction"]}", style=bold, arrowhead=diamond, penwidth=2, fontsize=9, fontcolor="{theme["cluster_fontcolor"]}"];')
        lines.append('  }')

    lines.append('}')
    return "\n".join(lines)


# ─── Rendering ─────────────────────────────────────────────────────────────────

def render_dot(dot_content: str, output_path: str, fmt: str = "png",
               dpi: int = 150, engine: str = "dot"):
    """Render DOT to an image using Graphviz."""
    engine_bin = shutil.which(engine)
    if not engine_bin:
        print(f"ERROR: Graphviz '{engine}' command not found.", file=sys.stderr)
        print("Install Graphviz:", file=sys.stderr)
        print("  macOS:   brew install graphviz", file=sys.stderr)
        print("  Linux:   apt install graphviz", file=sys.stderr)
        print("  Windows: choco install graphviz", file=sys.stderr)
        sys.exit(1)

    cmd = [engine_bin, f"-T{fmt}", f"-Gdpi={dpi}", "-o", output_path]
    result = subprocess.run(
        cmd, input=dot_content, capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"ERROR: Graphviz failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)


# ─── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Render Argdown argument maps to PNG, SVG, DOT, or JSON.",
        epilog="Requires Graphviz for PNG/SVG output (brew install graphviz)."
    )
    parser.add_argument("input", help="Input .argdown file")
    parser.add_argument("-o", "--output", help="Output file path (auto-generated if omitted)")
    parser.add_argument("-f", "--format", choices=["png", "svg", "dot", "json", "all"],
                        default="png", help="Output format (default: png)")
    parser.add_argument("--dpi", type=int, default=150,
                        help="DPI for PNG output (default: 150)")
    parser.add_argument("--engine", choices=["dot", "neato", "fdp", "circo", "twopi", "osage"],
                        default="dot",
                        help="Graphviz layout engine (default: dot)")
    parser.add_argument("--theme", choices=["light", "dark"], default="light",
                        help="Color theme (default: light)")
    parser.add_argument("--legend", action="store_true",
                        help="Add a legend showing edge/node types")
    parser.add_argument("--no-groups", action="store_true",
                        help="Disable section grouping in the map")
    parser.add_argument("--dump-model", action="store_true",
                        help="Print parsed model summary to stderr")

    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"ERROR: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()

    # Parse
    model = parse_argdown(text)

    if args.dump_model:
        print(f"Title: {model.title}", file=sys.stderr)
        print(f"Statements: {len(model.statements)}", file=sys.stderr)
        for t in model.statements:
            print(f"  [{t}]", file=sys.stderr)
        print(f"Arguments: {len(model.arguments)}", file=sys.stderr)
        for t in model.arguments:
            print(f"  <{t}>", file=sys.stderr)
        print(f"Relations: {len(model.relations)}", file=sys.stderr)
        for r in model.relations:
            sym = {"support": "+>", "attack": "->", "undercut": "_>", "contradiction": "><"}
            print(f"  {r.source} {sym.get(r.relation, '??')} {r.target}", file=sys.stderr)
        print(f"Sections: {model.sections}", file=sys.stderr)

    if args.no_groups:
        model.sections = []
        for s in model.statements.values():
            s.section = ""
        for a in model.arguments.values():
            a.section = ""

    base = os.path.splitext(args.input)[0]

    # JSON export (no Graphviz needed)
    if args.format == "json":
        import json
        out = args.output or f"{base}.json"
        data = model_to_json(model)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"JSON → {out}")
        return

    # Generate DOT
    dot = generate_dot(model, theme_name=args.theme, show_legend=args.legend)

    if args.format == "all":
        dot_path = args.output or f"{base}.dot"
        with open(dot_path, "w", encoding="utf-8") as f:
            f.write(dot)
        print(f"DOT  → {dot_path}")

        svg_path = f"{base}.svg"
        render_dot(dot, svg_path, "svg", args.dpi, engine=args.engine)
        print(f"SVG  → {svg_path}")

        png_path = f"{base}.png"
        render_dot(dot, png_path, "png", args.dpi, engine=args.engine)
        print(f"PNG  → {png_path}")

    elif args.format == "dot":
        out = args.output or f"{base}.dot"
        with open(out, "w", encoding="utf-8") as f:
            f.write(dot)
        print(f"DOT → {out}")

    else:
        out = args.output or f"{base}.{args.format}"
        render_dot(dot, out, args.format, args.dpi, engine=args.engine)
        print(f"{args.format.upper()} → {out}")


if __name__ == "__main__":
    main()
