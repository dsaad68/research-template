#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
"""
validate.py — Argdown syntax validator with real parsing.

Parses the Argdown file structure and reports actual syntax issues,
not just pattern presence.

Usage:
  uv run validate.py input.argdown
  uv run validate.py input.argdown --strict    # treat warnings as errors
  uv run validate.py *.argdown                 # validate multiple files
"""

import re
import sys
import os
import argparse
from dataclasses import dataclass

import yaml # type: ignore

# Import shared parser for model-based validation
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ─── Diagnostics ───────────────────────────────────────────────────────────────

@dataclass
class Diagnostic:
    level: str    # "error", "warning", "info"
    line: int
    message: str

    def __str__(self):
        icons = {"error": "✗", "warning": "⚠", "info": "ℹ"}
        return f"  {icons.get(self.level, '?')} Line {self.line}: {self.message}"


# ─── Patterns ──────────────────────────────────────────────────────────────────

RE_FRONTMATTER_OPEN = re.compile(r'^===\s*$')
RE_TITLED_STATEMENT = re.compile(r'^\[([^\]]+)\]\s*:\s*(.+)')
RE_STATEMENT_REF = re.compile(r'^\[([^\]]+)\]\s*$')
RE_ARGUMENT_DEF = re.compile(r'^<([^>]+)>\s*:\s*(.+)')
RE_ARGUMENT_REF = re.compile(r'^<([^>]+)>\s*$')
RE_RELATION = re.compile(r'^\s+(\+>|\->|\_>|<\+|<\-|<\_|><)\s+(.+)')
RE_RELATION_TARGET = re.compile(r'[\[<]([^\]>]+)[\]>]')
RE_HEADING = re.compile(r'^(#{1,6})\s+(.+)')
RE_PCS_PREMISE = re.compile(r'^\s*\((\d+)\)\s+(.+)')
RE_PCS_INFERENCE = re.compile(r'^\s*-{2,}\s*$')
RE_COMMENT_SINGLE = re.compile(r'^\s*//')
RE_COMMENT_BLOCK_START = re.compile(r'/\*')
RE_COMMENT_BLOCK_END = re.compile(r'\*/')
RE_HTML_COMMENT_START = re.compile(r'<!--')
RE_HTML_COMMENT_END = re.compile(r'-->')
RE_TAG = re.compile(r'#([a-zA-Z][a-zA-Z0-9_-]*)')
RE_META = re.compile(r'\{[^}]+\}')

VALID_RELATIONS = {"+>", "->", "_>", "<+", "<-", "<_", "><"}


def validate_file(filepath: str) -> list[Diagnostic]:
    """Validate an Argdown file, returning a list of diagnostics."""
    diags: list[Diagnostic] = []

    if not os.path.isfile(filepath):
        return [Diagnostic("error", 0, f"File not found: {filepath}")]

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")
    total_lines = len(lines)

    # Track state
    in_frontmatter = False
    frontmatter_opened = False
    frontmatter_closed = False
    frontmatter_lines = []
    frontmatter_start = 0

    in_block_comment = False
    in_html_comment = False

    statements_defined: dict[str, int] = {}      # title → first line
    statements_referenced: dict[str, list] = {}   # title → [line numbers]
    arguments_defined: dict[str, int] = {}
    arguments_referenced: dict[str, list] = {}
    relation_count = 0
    heading_count = 0
    pcs_premises = 0
    pcs_inferences = 0
    last_pcs_number = 0
    in_pcs = False
    current_parent = None  # (type, title, line)

    for i, line in enumerate(lines, 1):
        stripped = line.rstrip()

        # ── Frontmatter handling ──
        if RE_FRONTMATTER_OPEN.match(stripped):
            if not frontmatter_opened:
                frontmatter_opened = True
                in_frontmatter = True
                frontmatter_start = i
                continue
            elif in_frontmatter:
                in_frontmatter = False
                frontmatter_closed = True
                # Validate YAML
                fm_text = "\n".join(frontmatter_lines)
                try:
                    parsed = yaml.safe_load(fm_text)
                    if parsed and not isinstance(parsed, dict):
                        diags.append(Diagnostic("error", frontmatter_start,
                            "Frontmatter must be a YAML mapping (key: value pairs)"))
                except yaml.YAMLError as e:
                    diags.append(Diagnostic("error", frontmatter_start,
                        f"Invalid YAML in frontmatter: {e}"))
                continue

        if in_frontmatter:
            frontmatter_lines.append(stripped)
            # Check for // comments in YAML (common mistake)
            if "//" in stripped and not stripped.strip().startswith("#"):
                diags.append(Diagnostic("warning", i,
                    "YAML uses # for comments, not //"))
            continue

        # ── Comment handling ──
        if in_block_comment:
            if RE_COMMENT_BLOCK_END.search(stripped):
                in_block_comment = False
            continue

        if in_html_comment:
            if RE_HTML_COMMENT_END.search(stripped):
                in_html_comment = False
            continue

        if RE_COMMENT_BLOCK_START.search(stripped):
            if not RE_COMMENT_BLOCK_END.search(stripped):
                in_block_comment = True
            continue

        if RE_HTML_COMMENT_START.search(stripped):
            if not RE_HTML_COMMENT_END.search(stripped):
                in_html_comment = True
            continue

        if RE_COMMENT_SINGLE.match(stripped):
            continue

        if not stripped:
            in_pcs = False
            last_pcs_number = 0
            continue

        # ── Headings ──
        hm = RE_HEADING.match(stripped)
        if hm:
            heading_count += 1
            current_parent = None
            in_pcs = False
            continue

        # ── Relations ──
        rm = RE_RELATION.match(line)
        if rm:
            symbol = rm.group(1)
            rest = rm.group(2).strip()

            if symbol not in VALID_RELATIONS:
                diags.append(Diagnostic("error", i,
                    f"Unknown relation symbol: {symbol}"))

            # Check target is properly formatted
            tm = RE_RELATION_TARGET.match(rest)
            if not tm:
                diags.append(Diagnostic("error", i,
                    "Relation target must be [Statement Title] or <Argument Title>"))
            else:
                target_title = tm.group(1)
                if rest.startswith("["):
                    statements_referenced.setdefault(target_title, []).append(i)
                elif rest.startswith("<"):
                    arguments_referenced.setdefault(target_title, []).append(i)

            if not current_parent:
                diags.append(Diagnostic("warning", i,
                    "Relation without a preceding statement or argument"))

            relation_count += 1
            continue

        # ── Titled statements ──
        sm = RE_TITLED_STATEMENT.match(stripped)
        if sm:
            title = sm.group(1)
            if title not in statements_defined:
                statements_defined[title] = i
            statements_referenced.setdefault(title, []).append(i)
            current_parent = ("statement", title, i)
            in_pcs = False
            continue

        # ── Statement references ──
        sr = RE_STATEMENT_REF.match(stripped)
        if sr:
            title = sr.group(1)
            statements_referenced.setdefault(title, []).append(i)
            current_parent = ("statement", title, i)
            in_pcs = False
            continue

        # ── Argument definitions ──
        am = RE_ARGUMENT_DEF.match(stripped)
        if am:
            title = am.group(1)
            if title not in arguments_defined:
                arguments_defined[title] = i
            arguments_referenced.setdefault(title, []).append(i)
            current_parent = ("argument", title, i)
            in_pcs = False
            continue

        # ── Argument references ──
        ar = RE_ARGUMENT_REF.match(stripped)
        if ar:
            title = ar.group(1)
            arguments_referenced.setdefault(title, []).append(i)
            current_parent = ("argument", title, i)
            in_pcs = False
            continue

        # ── PCS premises ──
        pm = RE_PCS_PREMISE.match(line)
        if pm:
            num = int(pm.group(1))
            if in_pcs and num != last_pcs_number + 1:
                diags.append(Diagnostic("warning", i,
                    f"PCS numbering gap: expected ({last_pcs_number + 1}), got ({num})"))
            last_pcs_number = num
            in_pcs = True
            pcs_premises += 1

            # Check for titled statement in PCS
            pcs_text = pm.group(2)
            tsm = RE_TITLED_STATEMENT.match(pcs_text)
            if tsm:
                t = tsm.group(1)
                statements_referenced.setdefault(t, []).append(i)
                if t not in statements_defined:
                    statements_defined[t] = i
            continue

        # ── PCS inferences ──
        if RE_PCS_INFERENCE.match(stripped):
            if not in_pcs:
                diags.append(Diagnostic("warning", i,
                    "Inference line (----) outside of a premise-conclusion structure"))
            pcs_inferences += 1
            continue

    # ── Post-parse checks ──

    if frontmatter_opened and not frontmatter_closed:
        diags.append(Diagnostic("error", frontmatter_start,
            "Frontmatter opened with === but never closed"))

    if in_block_comment:
        diags.append(Diagnostic("error", total_lines,
            "Unclosed block comment (/* ... */)"))

    if in_html_comment:
        diags.append(Diagnostic("error", total_lines,
            "Unclosed HTML comment (<!-- ... -->)"))

    # Check for referenced-but-never-defined statements
    for title, ref_lines in statements_referenced.items():
        if title not in statements_defined:
            diags.append(Diagnostic("warning", ref_lines[0],
                f"Statement [{title}] referenced but never defined with text"))

    for title, ref_lines in arguments_referenced.items():
        if title not in arguments_defined:
            diags.append(Diagnostic("warning", ref_lines[0],
                f"Argument <{title}> referenced but never defined with description"))

    # Summary info
    if not statements_defined and not arguments_defined:
        diags.append(Diagnostic("warning", 1,
            "No statements or arguments found in file"))

    return diags


def format_summary(filepath: str, diags: list[Diagnostic],
                   content: str) -> str:
    """Format validation results."""
    lines = content.split("\n")
    out = []
    out.append(f"Validating: {filepath} ({len(lines)} lines)")
    out.append("─" * 50)

    errors = [d for d in diags if d.level == "error"]
    warnings = [d for d in diags if d.level == "warning"]

    if errors:
        out.append("")
        out.append(f"Errors ({len(errors)}):")
        for d in errors:
            out.append(str(d))

    if warnings:
        out.append("")
        out.append(f"Warnings ({len(warnings)}):")
        for d in warnings:
            out.append(str(d))

    out.append("")
    out.append("─" * 50)
    if errors:
        out.append(f"✗ FAILED — {len(errors)} error(s), {len(warnings)} warning(s)")
    elif warnings:
        out.append(f"⚠ PASSED with {len(warnings)} warning(s)")
    else:
        out.append("✓ PASSED — no issues found")

    return "\n".join(out)


# ─── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Validate Argdown files for syntax issues."
    )
    parser.add_argument("files", nargs="+", help="Argdown file(s) to validate")
    parser.add_argument("--strict", action="store_true",
                        help="Treat warnings as errors (non-zero exit)")
    args = parser.parse_args()

    any_failed = False

    for filepath in args.files:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        diags = validate_file(filepath)
        print(format_summary(filepath, diags, content))

        errors = [d for d in diags if d.level == "error"]
        warnings = [d for d in diags if d.level == "warning"]

        if errors or (args.strict and warnings):
            any_failed = True

        print()

    sys.exit(1 if any_failed else 0)


if __name__ == "__main__":
    main()
