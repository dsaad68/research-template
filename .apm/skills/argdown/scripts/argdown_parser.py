"""
argdown_parser.py — Shared Argdown parser and data model.

This module is imported by render.py and validate.py. It is NOT a uv script
itself — it's a plain Python module that lives alongside the scripts.

Requires: pyyaml (provided by the importing uv scripts' dependency declarations)
"""

import re
from dataclasses import dataclass, field

import yaml # type: ignore

# ─── Data Model ────────────────────────────────────────────────────────────────

@dataclass
class Statement:
    title: str
    text: str = ""
    tags: list = field(default_factory=list)
    meta: dict = field(default_factory=dict)
    section: str = ""

@dataclass
class Argument:
    title: str
    description: str = ""
    tags: list = field(default_factory=list)
    meta: dict = field(default_factory=dict)
    section: str = ""
    pcs: list = field(default_factory=list)  # list of PCS steps

@dataclass
class Relation:
    source: str        # title
    source_type: str   # "statement" or "argument"
    target: str        # title
    target_type: str   # "statement" or "argument"
    relation: str      # "support", "attack", "undercut", "contradiction"

@dataclass
class ArgdownModel:
    title: str = "Argument Map"
    statements: dict = field(default_factory=dict)
    arguments: dict = field(default_factory=dict)
    relations: list = field(default_factory=list)
    sections: list = field(default_factory=list)
    section_parent: dict = field(default_factory=dict)  # section -> parent section
    config: dict = field(default_factory=dict)

# ─── Helpers ───────────────────────────────────────────────────────────────────

def parse_yaml_simple(text: str) -> dict:
    """Parse YAML frontmatter using PyYAML."""
    return yaml.safe_load(text) or {}


def extract_tags(text: str) -> list:
    """Extract #tags from text."""
    return re.findall(r'#([a-zA-Z][a-zA-Z0-9_-]*)', text)


def extract_meta(text: str) -> tuple:
    """Extract {key: value} metadata, return (cleaned_text, meta_dict)."""
    m = re.search(r'\{([^}]+)\}', text)
    if not m:
        return text, {}

    meta_str = m.group(1)
    cleaned = text[:m.start()] + text[m.end():]
    meta = {}
    for pair in re.findall(r'([\w-]+)\s*:\s*(".*?"|\'.*?\'|[^,}]+)', meta_str):
        k, v = pair
        v = v.strip().strip('"').strip("'")
        if v.lower() == "true":
            meta[k] = True
        elif v.lower() == "false":
            meta[k] = False
        else:
            meta[k] = v
    return cleaned.strip(), meta


# ─── Regex Patterns ────────────────────────────────────────────────────────────

RELATION_MAP = {
    "+>": ("outgoing", "support"),
    "->": ("outgoing", "attack"),
    "_>": ("outgoing", "undercut"),
    "<+": ("incoming", "support"),
    "<-": ("incoming", "attack"),
    "<_": ("incoming", "undercut"),
    "><": ("symmetric", "contradiction"),
}

RE_TITLED_STATEMENT = re.compile(r'^\[([^\]]+)\]\s*:\s*(.+)', re.DOTALL)
RE_STATEMENT_REF = re.compile(r'^\[([^\]]+)\]\s*$')
RE_ARGUMENT_DEF = re.compile(r'^<([^>]+)>\s*:\s*(.+)', re.DOTALL)
RE_ARGUMENT_REF = re.compile(r'^<([^>]+)>\s*$')
RE_RELATION = re.compile(r'^\s+(\+>|\->|\_>|<\+|<\-|<\_|><)\s+[\[<]([^\]>]+)[\]>]')
RE_HEADING = re.compile(r'^(#{1,6})\s+(.+)')
RE_PCS_PREMISE = re.compile(r'^\s*\((\d+)\)\s+(.+)')
RE_PCS_INFERENCE = re.compile(r'^\s*-{4,}\s*$')
RE_PCS_INFERENCE_EXPANDED_START = re.compile(r'^\s*-{2,}\s*$')
RE_COMMENT_SINGLE = re.compile(r'^\s*//')
RE_COMMENT_BLOCK_START = re.compile(r'/\*')
RE_COMMENT_BLOCK_END = re.compile(r'\*/')
RE_HTML_COMMENT_START = re.compile(r'<!--')
RE_HTML_COMMENT_END = re.compile(r'-->')


# ─── Parser ────────────────────────────────────────────────────────────────────

def parse_argdown(text: str) -> ArgdownModel:
    """Parse Argdown text into an ArgdownModel."""
    model = ArgdownModel()

    # Extract frontmatter
    fm_match = re.match(r'^===\s*\n(.*?)\n===', text, re.DOTALL)
    if fm_match:
        model.config = parse_yaml_simple(fm_match.group(1))
        model.title = model.config.get("title", "Argument Map")
        text = text[fm_match.end():]

    lines = text.split("\n")
    current_section = ""
    section_hierarchy = []    # stack of (level, name)
    section_parent = {}       # section_name -> parent_section_name or None
    current_parent = None     # (type, title)
    in_block_comment = False
    in_html_comment = False
    i = 0

    while i < len(lines):
        line = lines[i]

        # Handle block comments
        if in_block_comment:
            if RE_COMMENT_BLOCK_END.search(line):
                in_block_comment = False
            i += 1
            continue

        if in_html_comment:
            if RE_HTML_COMMENT_END.search(line):
                in_html_comment = False
            i += 1
            continue

        if RE_COMMENT_BLOCK_START.search(line) and not RE_COMMENT_BLOCK_END.search(line):
            in_block_comment = True
            i += 1
            continue

        if RE_HTML_COMMENT_START.search(line) and not RE_HTML_COMMENT_END.search(line):
            in_html_comment = True
            i += 1
            continue

        # Skip single-line comments
        if RE_COMMENT_SINGLE.match(line):
            i += 1
            continue

        stripped = line.strip()
        if not stripped:
            i += 1
            continue

        # Headings
        hm = RE_HEADING.match(stripped)
        if hm:
            level = len(hm.group(1))
            current_section = hm.group(2).strip()
            model.sections.append(current_section)

            # Pop stack to find parent at a higher level
            while section_hierarchy and section_hierarchy[-1][0] >= level:
                section_hierarchy.pop()
            parent = section_hierarchy[-1][1] if section_hierarchy else None
            section_parent[current_section] = parent
            section_hierarchy.append((level, current_section))

            current_parent = None
            i += 1
            continue

        # Relations (must check before statements/arguments — they're indented)
        rm = RE_RELATION.match(line)
        if rm and current_parent:
            symbol = rm.group(1)
            target_title = rm.group(2)
            direction, rel_type = RELATION_MAP.get(symbol, ("outgoing", "support"))

            # Determine target type
            target_char = line.strip()[len(symbol):].strip()[0]
            target_type = "argument" if target_char == "<" else "statement"

            # Ensure target exists in model
            if target_type == "statement" and target_title not in model.statements:
                model.statements[target_title] = Statement(title=target_title, section=current_section)
            elif target_type == "argument" and target_title not in model.arguments:
                model.arguments[target_title] = Argument(title=target_title, section=current_section)

            parent_type, parent_title = current_parent

            if direction == "outgoing":
                model.relations.append(Relation(
                    source=parent_title, source_type=parent_type,
                    target=target_title, target_type=target_type,
                    relation=rel_type
                ))
            elif direction == "incoming":
                model.relations.append(Relation(
                    source=target_title, source_type=target_type,
                    target=parent_title, target_type=parent_type,
                    relation=rel_type
                ))
            elif direction == "symmetric":
                model.relations.append(Relation(
                    source=parent_title, source_type=parent_type,
                    target=target_title, target_type=target_type,
                    relation=rel_type
                ))
            i += 1
            continue

        # Titled statement definition
        sm = RE_TITLED_STATEMENT.match(stripped)
        if sm:
            title = sm.group(1)
            raw_text = sm.group(2)

            # Collect continuation lines
            while i + 1 < len(lines) and lines[i + 1].strip() and \
                  not RE_RELATION.match(lines[i + 1]) and \
                  not RE_TITLED_STATEMENT.match(lines[i + 1].strip()) and \
                  not RE_ARGUMENT_DEF.match(lines[i + 1].strip()) and \
                  not RE_ARGUMENT_REF.match(lines[i + 1].strip()) and \
                  not RE_STATEMENT_REF.match(lines[i + 1].strip()) and \
                  not RE_HEADING.match(lines[i + 1].strip()) and \
                  not RE_PCS_PREMISE.match(lines[i + 1]) and \
                  not RE_PCS_INFERENCE.match(lines[i + 1].strip()) and \
                  not RE_COMMENT_SINGLE.match(lines[i + 1]):
                i += 1
                raw_text += " " + lines[i].strip()

            raw_text, meta = extract_meta(raw_text)
            tags = extract_tags(raw_text)

            if title not in model.statements:
                model.statements[title] = Statement(
                    title=title, text=raw_text.strip(),
                    tags=tags, meta=meta, section=current_section
                )
            else:
                s = model.statements[title]
                if not s.text:
                    s.text = raw_text.strip()
                s.tags = list(set(s.tags + tags))
                s.meta.update(meta)
                if not s.section:
                    s.section = current_section

            current_parent = ("statement", title)
            i += 1
            continue

        # Statement reference
        sr = RE_STATEMENT_REF.match(stripped)
        if sr:
            title = sr.group(1)
            if title not in model.statements:
                model.statements[title] = Statement(title=title, section=current_section)
            current_parent = ("statement", title)
            i += 1
            continue

        # Argument definition
        am = RE_ARGUMENT_DEF.match(stripped)
        if am:
            title = am.group(1)
            raw_desc = am.group(2)

            # Collect continuation lines
            while i + 1 < len(lines) and lines[i + 1].strip() and \
                  not RE_RELATION.match(lines[i + 1]) and \
                  not RE_TITLED_STATEMENT.match(lines[i + 1].strip()) and \
                  not RE_ARGUMENT_DEF.match(lines[i + 1].strip()) and \
                  not RE_ARGUMENT_REF.match(lines[i + 1].strip()) and \
                  not RE_STATEMENT_REF.match(lines[i + 1].strip()) and \
                  not RE_HEADING.match(lines[i + 1].strip()) and \
                  not RE_PCS_PREMISE.match(lines[i + 1]) and \
                  not RE_PCS_INFERENCE.match(lines[i + 1].strip()) and \
                  not RE_COMMENT_SINGLE.match(lines[i + 1]):
                i += 1
                raw_desc += " " + lines[i].strip()

            raw_desc, meta = extract_meta(raw_desc)
            tags = extract_tags(raw_desc)

            if title not in model.arguments:
                model.arguments[title] = Argument(
                    title=title, description=raw_desc.strip(),
                    tags=tags, meta=meta, section=current_section
                )
            else:
                a = model.arguments[title]
                if not a.description:
                    a.description = raw_desc.strip()
                a.tags = list(set(a.tags + tags))
                a.meta.update(meta)
                if not a.section:
                    a.section = current_section

            current_parent = ("argument", title)
            i += 1
            continue

        # Argument reference (standalone)
        ar = RE_ARGUMENT_REF.match(stripped)
        if ar:
            title = ar.group(1)
            if title not in model.arguments:
                model.arguments[title] = Argument(title=title, section=current_section)
            current_parent = ("argument", title)
            i += 1
            continue

        # PCS premises (inside an argument context)
        pm = RE_PCS_PREMISE.match(line)
        if pm and current_parent and current_parent[0] == "argument":
            raw_pcs_text = pm.group(2).strip()
            pcs_text, _ = extract_meta(raw_pcs_text)
            # Check if PCS references a titled statement
            tsm = RE_TITLED_STATEMENT.match(pcs_text)
            if tsm:
                pcs_title = tsm.group(1)
                if pcs_title not in model.statements:
                    model.statements[pcs_title] = Statement(
                        title=pcs_title, text=tsm.group(2).strip(),
                        section=current_section
                    )
            i += 1
            continue

        # PCS inference lines
        if RE_PCS_INFERENCE.match(stripped):
            i += 1
            continue

        # Expanded inference start
        if RE_PCS_INFERENCE_EXPANDED_START.match(stripped):
            # Skip until closing --
            i += 1
            while i < len(lines):
                if RE_PCS_INFERENCE_EXPANDED_START.match(lines[i].strip()):
                    break
                i += 1
            i += 1
            continue

        i += 1

    model.section_parent = section_parent
    return model
