#!/usr/bin/env python3
"""
ndlr_electra_presetgen.py

Generate an Electra One preset JSON from a Markdown spec containing sections and tables.

Input markdown format (suggested):

# Preset Title

Optional YAML frontmatter:

---
manufacturer: Conductive Labs
device: NDLR
electra:
  screen_width: 1024
  screen_height_usable: 550
  cols: 6
  rows: 6
  padding: 10
  top_offset: 25
  left_offset: 10
  right_padding: 30
  cell_width: auto   # or integer
  cell_height: 83
midi:
  port: 1
  channel: 1
---

## GENERAL

| CC (Hex) | CC (Dec) | Label           | Range | Choices | Description |
|---------:|---------:|-----------------|------:|---------|-------------|
| 0x1A     | 26       | Chord Degree    | 1-7   | 1=I,2=II,3=III,4=IV,5=V,6=VI,7=VII | ... |
| 0x39     | 57       | Black Keys Ctrl | 0-127 | 0=On,127=Off | ... |

Choices/Options syntax supported:
- "A,B,C" -> sequential mapping starting at min (or 0/1 if range ambiguous)
- "A(1), B(2)" or "1=A,2=B"
- "2-5=USB1-USB4" expands ranges
- "Off(0), On(127)" etc.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# -----------------------------
# Data models
# -----------------------------

@dataclasses.dataclass
class ControlSpec:
    section: str
    cc: int
    label: str
    min_val: int
    max_val: int
    choices: List[Tuple[int, str]]  # (value, label)
    description: str

# -----------------------------
# YAML-ish frontmatter (minimal)
# -----------------------------

def parse_frontmatter(md: str) -> Tuple[Dict[str, Any], str]:
    """
    Minimal YAML frontmatter parser.
    Supports only simple key: value and one-level nesting via indentation.
    If you want full YAML, you can add PyYAML, but we keep it dependency-free.

    Returns (meta, remaining_markdown).
    """
    lines = md.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, md

    meta: Dict[str, Any] = {}
    i = 1
    stack: List[Tuple[int, Dict[str, Any]]] = [(0, meta)]

    def set_kv(container: Dict[str, Any], k: str, v: Any) -> None:
        container[k] = v

    while i < len(lines):
        line = lines[i]
        if line.strip() == "---":
            # end frontmatter
            rest = "\n".join(lines[i+1:])
            return meta, rest

        # ignore empty/comment
        if not line.strip() or line.strip().startswith("#"):
            i += 1
            continue

        indent = len(line) - len(line.lstrip(" "))
        m = re.match(r'^\s*([A-Za-z0-9_\-]+)\s*:\s*(.*?)\s*$', line)
        if not m:
            i += 1
            continue

        key = m.group(1)
        raw_val = m.group(2)

        # adjust stack based on indentation
        while stack and indent < stack[-1][0]:
            stack.pop()
        if not stack:
            stack = [(0, meta)]

        container = stack[-1][1]

        if raw_val == "":
            # start a nested map
            new_map: Dict[str, Any] = {}
            set_kv(container, key, new_map)
            stack.append((indent + 2, new_map))
        else:
            val: Any = raw_val
            # cast ints/bools if possible
            if re.fullmatch(r"-?\d+", raw_val):
                val = int(raw_val)
            elif raw_val.lower() in {"true", "false"}:
                val = (raw_val.lower() == "true")
            set_kv(container, key, val)

        i += 1

    # if unclosed frontmatter, treat as none
    return {}, md

# -----------------------------
# Markdown parsing helpers
# -----------------------------

def clean_cell(s: str) -> str:
    s = (s or "").strip()
    # strip common markdown wrappers
    s = re.sub(r"^\*+|\*+$", "", s).strip()
    s = re.sub(r"^`+|`+$", "", s).strip()
    return s

def norm_key(s: str) -> str:
    return re.sub(r"\s+", " ", clean_cell(s).lower())

def split_sections(md: str) -> Tuple[str, List[Tuple[str, List[str]]]]:
    """
    Returns (title, [(section_title, section_lines), ...]).
    - Title is first H1 (# ...)
    - Sections are H2 (## ...) or H3 (### ...) etc (we treat any heading >=2 as section)
    """
    title = "Untitled Preset"
    sections: List[Tuple[str, List[str]]] = []
    cur_title: Optional[str] = None
    cur_lines: List[str] = []

    for line in md.splitlines():
        h1 = re.match(r"^\s*#\s+(.*?)\s*$", line)
        if h1 and title == "Untitled Preset":
            title = clean_cell(h1.group(1))
            continue

        h = re.match(r"^\s*(#{2,6})\s+(.*?)\s*$", line)
        if h:
            # flush previous section
            if cur_title is not None:
                sections.append((cur_title, cur_lines))
            cur_title = clean_cell(h.group(2))
            cur_lines = []
            continue

        if cur_title is not None:
            cur_lines.append(line)

    if cur_title is not None:
        sections.append((cur_title, cur_lines))

    # If no explicit sections, treat whole doc as one section.
    if not sections:
        sections = [("MAIN", md.splitlines())]

    return title, sections

def is_divider_line(line: str) -> bool:
    # Accept GFM divider with or without leading/trailing pipe.
    return bool(re.match(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)+\|?\s*$", line.strip()))

def split_row(line: str) -> List[str]:
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [clean_cell(c) for c in s.split("|")]

def parse_tables(lines: List[str]) -> List[List[Dict[str, str]]]:
    """
    Parse all pipe tables in a list of lines.
    Robust against:
    - missing trailing pipes
    - ragged rows (pads/merges as needed)
    """
    tables: List[List[Dict[str, str]]] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if "|" in line and line.count("|") >= 1 and i + 1 < len(lines) and is_divider_line(lines[i + 1]):
            header = split_row(line)
            i += 2
            rows: List[Dict[str, str]] = []
            while i < len(lines):
                rowline = lines[i]
                if "|" not in rowline or is_divider_line(rowline):
                    break
                parts = split_row(rowline)
                # normalize length
                if len(parts) < len(header):
                    parts += [""] * (len(header) - len(parts))
                elif len(parts) > len(header):
                    parts = parts[: len(header) - 1] + [" | ".join(parts[len(header) - 1 :])]
                row = {header[j]: parts[j] for j in range(len(header))}
                if any(v.strip() for v in row.values()):
                    rows.append(row)
                i += 1
            if rows:
                tables.append(rows)
            continue
        i += 1
    return tables

def pick(row: Dict[str, str], *keys: str, contains: Optional[str] = None) -> str:
    norm = {norm_key(k): k for k in row.keys()}
    for k in keys:
        kk = norm_key(k)
        if kk in norm:
            v = clean_cell(row.get(norm[kk], ""))
            if v:
                return v
    if contains:
        c = norm_key(contains)
        for k in row.keys():
            if c in norm_key(k):
                v = clean_cell(row.get(k, ""))
                if v:
                    return v
    return ""

# -----------------------------
# Value parsers
# -----------------------------

def parse_cc(s: str) -> Optional[int]:
    s = clean_cell(s)
    if not s:
        return None
    # hex like 0x1A or 1A
    m = re.match(r"^(0x)?([0-9A-Fa-f]{1,2})$", s)
    if m and (m.group(1) or any(c.isalpha() for c in m.group(2))):
        return int(m.group(2), 16)
    # decimal
    m = re.match(r"^\d+$", s)
    if m:
        return int(s)
    return None

def parse_range(s: str) -> Tuple[int, int]:
    s = clean_cell(s).replace("–", "-")
    m = re.match(r"^(\d+)\s*-\s*(\d+)$", s)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.match(r"^(\d+)$", s)
    if m:
        v = int(m.group(1))
        return v, v
    return 0, 127

def expand_range_label(lhs_a: int, lhs_b: int, rhs: str) -> List[Tuple[int, str]]:
    """
    Expand '2-5=USB1-USB4' style mapping:
    - If rhs contains a '1-4' pattern, replace with appropriate index.
    - Otherwise label is the rhs unchanged for all values.
    """
    rhs = clean_cell(rhs)
    out = []
    for i, v in enumerate(range(lhs_a, lhs_b + 1), start=1):
        lbl = rhs
        # common pattern replacement "1-4" -> i
        lbl = lbl.replace("1-4", str(i))
        out.append((v, lbl))
    return out

def parse_choices(s: str, minv: int, maxv: int) -> List[Tuple[int, str]]:
    """
    Parse choices/options cell into [(value,label),...].
    Supported forms:
      - "Off(0), On(127)"
      - "0=Off, 127=On"
      - "2-5=USB1-USB4"
      - "USB1, USB2, USB3" -> sequential from minv if reasonable
    """
    s = clean_cell(s)
    if not s or s.lower() in {"n/a", "na", "none", "no"}:
        return []

    parts = re.split(r"[;\n,]+", s)
    items: List[Tuple[int, str]] = []

    for p in parts:
        p = clean_cell(p)
        if not p:
            continue

        # 2-5=USB1-USB4
        m = re.match(r"^(\d+)\s*-\s*(\d+)\s*[:=]\s*(.+)$", p)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            rhs = m.group(3)
            items.extend(expand_range_label(a, b, rhs))
            continue

        # 1=All or 1:All
        m = re.match(r"^(\d+)\s*[:=]\s*(.+)$", p)
        if m:
            items.append((int(m.group(1)), clean_cell(m.group(2))))
            continue

        # Label(3) or Label (3-5)
        m = re.match(r"^(.+?)\s*\(\s*(\d+)\s*-\s*(\d+)\s*\)\s*$", p)
        if m:
            lbl = clean_cell(m.group(1))
            a, b = int(m.group(2)), int(m.group(3))
            for v in range(a, b + 1):
                items.append((v, lbl))
            continue

        m = re.match(r"^(.+?)\s*\(\s*(\d+)\s*\)\s*$", p)
        if m:
            items.append((int(m.group(2)), clean_cell(m.group(1))))
            continue

        # Bare label -> sequential
        items.append((-1, p))

    # If we got bare labels (-1), assign sequential values.
    if any(v == -1 for v, _ in items):
        labels = [lbl for v, lbl in items if v == -1]
        # choose start value
        start = minv
        # if range looks like 0-... but minv missing, keep minv anyway
        assigned = [(start + i, labels[i]) for i in range(len(labels))]
        items = [(v, lbl) for v, lbl in items if v != -1] + assigned

    # de-dupe by value, keep first
    seen = set()
    out: List[Tuple[int, str]] = []
    for v, lbl in items:
        if v in seen:
            continue
        seen.add(v)
        out.append((int(v), str(lbl)))
    return out

def infer_choices_from_desc(desc: str, minv: int, maxv: int) -> List[Tuple[int, str]]:
    """
    Optional: if no explicit choices column, try to infer from description if it's
    a comma-separated enumeration matching the range size.
    """
    desc = clean_cell(desc)
    if not desc:
        return []
    if maxv - minv > 31:
        return []
    # if it already contains explicit numeric mappings, skip
    if re.search(r"\d+\s*[:=]\s*\w+", desc) or re.search(r"\d+\s*-\s*\d+", desc):
        return []
    tmp = desc.replace("&", ",")
    tmp = re.sub(r"\band\b", ",", tmp, flags=re.I)
    labels = [clean_cell(p) for p in tmp.split(",") if clean_cell(p)]
    labels = [re.sub(r"\s*\(.*?\)\s*$", "", l).strip() for l in labels]
    n = maxv - minv + 1
    if len(labels) == n:
        return [(minv + i, labels[i]) for i in range(n)]
    return []

# -----------------------------
# Electra One layout + JSON
# -----------------------------

def compute_grid_bounds(meta: Dict[str, Any]) -> Dict[str, int]:
    electra = meta.get("electra", {}) if isinstance(meta.get("electra"), dict) else {}

    cols = int(electra.get("cols", 6))
    rows = int(electra.get("rows", 6))
    padding = int(electra.get("padding", 10))
    top_offset = int(electra.get("top_offset", 25))
    left_offset = int(electra.get("left_offset", 10))
    right_padding = int(electra.get("right_padding", 30))
    cell_height = int(electra.get("cell_height", 83))

    # IMPORTANT: Many firmwares appear to have ~800px usable width for controls.
    # We default to 800 unless overridden.
    screen_w = int(electra.get("screen_width_controls", electra.get("screen_width", 800)))

    if electra.get("cell_width", "auto") != "auto":
        cell_width = int(electra["cell_width"])
    else:
        cell_width = (screen_w - left_offset - right_padding - (cols - 1) * padding) // cols
        cell_width = int(cell_width)

    return {
        "screen_w": screen_w,
        "cols": cols,
        "rows": rows,
        "padding": padding,
        "top_offset": top_offset,
        "left_offset": left_offset,
        "right_padding": right_padding,
        "cell_w": cell_width,
        "cell_h": cell_height,
    }

def bounds_for_index(idx: int, grid: Dict[str, int]) -> List[int]:
    cols = grid["cols"]
    padding = grid["padding"]
    left = grid["left_offset"]
    top_offset = grid["top_offset"]
    cw = grid["cell_w"]
    ch = grid["cell_h"]

    r = idx // cols
    c = idx % cols
    x = left + c * (cw + padding)
    y = top_offset + (padding + r * (ch + padding))
    return [int(x), int(y), int(cw), int(ch)]

def is_toggle(choices: List[Tuple[int, str]]) -> bool:
    if len(choices) != 2:
        return False
    vals = sorted(v for v, _ in choices)
    return vals == [0, 127] or vals == [0, 1]

def control_type(spec: ControlSpec) -> str:
    if spec.choices:
        return "pad" if is_toggle(spec.choices) else "list"
    return "fader"

def control_mode(spec: ControlSpec, ctype: str) -> str:
    if ctype == "pad":
        return "toggle" if is_toggle(spec.choices) else "momentary"
    if ctype == "list":
        return "default"
    return "unipolar"

def generate_preset(
    title: str,
    meta: Dict[str, Any],
    sections: List[ControlSpec],
) -> Dict[str, Any]:
    grid = compute_grid_bounds(meta)

    midi_meta = meta.get("midi", {}) if isinstance(meta.get("midi"), dict) else {}
    device_name = str(meta.get("device", meta.get("name", "NDLR")))
    port = int(midi_meta.get("port", 1))
    channel = int(midi_meta.get("channel", 1))
    rate = int(midi_meta.get("rate", 20))

    # Overlay reuse
    overlays: List[Dict[str, Any]] = []
    overlay_key_to_id: Dict[Tuple[Tuple[int, str], ...], int] = {}
    next_overlay_id = 1

    def overlay_id_for(choices: List[Tuple[int, str]]) -> int:
        nonlocal next_overlay_id
        key = tuple((int(v), str(lbl)) for v, lbl in choices)
        if key in overlay_key_to_id:
            return overlay_key_to_id[key]
        oid = next_overlay_id
        overlays.append({
            "id": oid,
            "items": [{"value": int(v), "label": str(lbl)} for v, lbl in choices],
        })
        overlay_key_to_id[key] = oid
        next_overlay_id += 1
        return oid

    # Pages + controls
    cols = grid["cols"]
    rows = grid["rows"]
    page_cap = cols * rows

    pages: List[Dict[str, Any]] = []
    controls: List[Dict[str, Any]] = []

    # Group specs by section title in original order
    by_section: Dict[str, List[ControlSpec]] = {}
    order: List[str] = []
    for s in sections:
        if s.section not in by_section:
            by_section[s.section] = []
            order.append(s.section)
        by_section[s.section].append(s)

    page_id = 1
    control_id = 1

    for section_title in order:
        specs = by_section[section_title]
        chunks = [specs[i:i+page_cap] for i in range(0, len(specs), page_cap)]
        for ci, chunk in enumerate(chunks, start=1):
            page_name = section_title if len(chunks) == 1 else f"{section_title} ({ci}/{len(chunks)})"
            pages.append({"id": page_id, "name": page_name, "defaultControlSetId": 1})

            for idx, spec in enumerate(chunk):
                ctype = control_type(spec)
                val: Dict[str, Any] = {
                    "id": "value",
                    "min": spec.min_val,
                    "max": spec.max_val,
                    "message": {
                        "deviceId": 1,
                        "type": "cc7",
                        "parameterNumber": spec.cc,
                        "min": 0,
                        "max": 127,
                    },
                }
                if spec.choices:
                    val["overlayId"] = overlay_id_for(spec.choices)

                controls.append({
                    "id": control_id,
                    "type": ctype,
                    "name": spec.label,
                    "bounds": bounds_for_index(idx, grid),
                    "pageId": page_id,
                    "controlSetId": 1,
                    "values": [val],
                    "variant": "thin" if ctype == "fader" else "default",
                    "mode": control_mode(spec, ctype),
                })

                control_id += 1

            page_id += 1

    preset = {
        "version": 2,
        "name": title,
        "projectId": re.sub(r"[^a-z0-9\-]+", "-", title.lower()).strip("-")[:40] or "preset",
        "pages": pages,
        "devices": [{
            "id": 1,
            "name": device_name,
            "port": port,
            "channel": channel,
            "rate": rate,
        }],
        "overlays": overlays,
        "groups": [],
        "controls": controls,
    }
    return preset

# -----------------------------
# Clean Markdown output
# -----------------------------

CANON_HEADERS = ["CC", "Label", "Range", "Choices", "Description"]

def render_table(rows: List[Dict[str, str]]) -> str:
    # Build header + divider + rows with consistent pipes
    # Ensure we output canonical columns if present
    cols = CANON_HEADERS
    # Compute widths
    widths = {c: len(c) for c in cols}
    norm_rows: List[Dict[str, str]] = []
    for r in rows:
        rr = {c: "" for c in cols}
        # map incoming keys
        cc = pick(r, "CC", "CC (Dec)", "CC (Hex)", "Hex")
        label = pick(r, "Label", "Target", "Name")
        rng = pick(r, "Range")
        choices = pick(r, "Choices", "Options", "Option(s)", contains="option")
        desc = pick(r, "Description", "Range Description", contains="desc")
        rr["CC"] = cc
        rr["Label"] = label
        rr["Range"] = rng
        rr["Choices"] = choices
        rr["Description"] = desc
        for c in cols:
            widths[c] = max(widths[c], len(clean_cell(rr[c])))
        norm_rows.append(rr)

    def fmt_row(rr: Dict[str, str]) -> str:
        return "| " + " | ".join(clean_cell(rr[c]).ljust(widths[c]) for c in cols) + " |"

    header = "| " + " | ".join(c.ljust(widths[c]) for c in cols) + " |"
    divider = "| " + " | ".join(("-" * widths[c]) for c in cols) + " |"
    body = "\n".join(fmt_row(rr) for rr in norm_rows)
    return "\n".join([header, divider, body])

def generate_clean_markdown(title: str, meta: Dict[str, Any], sections: List[Tuple[str, List[ControlSpec]]]) -> str:
    out: List[str] = []
    out.append(f"# {title}")
    out.append("")
    if meta:
        # Write minimal frontmatter back out (stable)
        out.append("---")
        if "manufacturer" in meta:
            out.append(f"manufacturer: {meta['manufacturer']}")
        if "device" in meta:
            out.append(f"device: {meta['device']}")
        if "midi" in meta and isinstance(meta["midi"], dict):
            out.append("midi:")
            for k in ["port", "channel", "rate"]:
                if k in meta["midi"]:
                    out.append(f"  {k}: {meta['midi'][k]}")
        if "electra" in meta and isinstance(meta["electra"], dict):
            out.append("electra:")
            # keep a small subset
            for k in ["cols", "rows", "padding", "top_offset", "left_offset", "right_padding", "screen_width_controls", "cell_width", "cell_height"]:
                if k in meta["electra"]:
                    out.append(f"  {k}: {meta['electra'][k]}")
        out.append("---")
        out.append("")

    for sec_title, specs in sections:
        out.append(f"## {sec_title}")
        out.append("")
        # convert specs back into canonical rows
        rows: List[Dict[str, str]] = []
        for s in specs:
            choice_str = ""
            if s.choices:
                # stable "label(value)" format
                choice_str = ", ".join(f"{lbl}({v})" for v, lbl in s.choices)
            rows.append({
                "CC": f"{s.cc}",
                "Label": s.label,
                "Range": f"{s.min_val}-{s.max_val}" if s.min_val != s.max_val else f"{s.min_val}",
                "Choices": choice_str,
                "Description": s.description,
            })
        out.append(render_table(rows))
        out.append("")

    return "\n".join(out).rstrip() + "\n"

# -----------------------------
# Main: read -> parse -> emit
# -----------------------------

def parse_controls_from_md(md_body: str) -> Tuple[str, Dict[str, Any], List[ControlSpec], List[Tuple[str, List[ControlSpec]]]]:
    meta, md_no_fm = parse_frontmatter(md_body)
    title, sections = split_sections(md_no_fm)

    all_specs: List[ControlSpec] = []
    by_section_out: List[Tuple[str, List[ControlSpec]]] = []

    for sec_title, sec_lines in sections:
        tables = parse_tables(sec_lines)
        specs: List[ControlSpec] = []
        for t in tables:
            for row in t:
                cc_s = pick(row, "CC", "CC (Dec)", "CC (Hex)", "Hex", contains="cc")
                cc = parse_cc(cc_s)
                if cc is None:
                    continue
                label = pick(row, "Label", "Target", "Name")
                if not label:
                    continue
                r = pick(row, "Range")
                minv, maxv = parse_range(r)
                desc = pick(row, "Description", "Range Description", contains="desc")
                choices_s = pick(row, "Choices", "Options", "Option(s)", contains="option")
                choices = parse_choices(choices_s, minv, maxv)
                # If no explicit choices, try inferring from description (optional)
                if not choices:
                    choices = infer_choices_from_desc(desc, minv, maxv)

                specs.append(ControlSpec(
                    section=sec_title,
                    cc=cc,
                    label=label,
                    min_val=minv,
                    max_val=maxv,
                    choices=choices,
                    description=desc,
                ))
        if specs:
            by_section_out.append((sec_title, specs))
            all_specs.extend(specs)

    return title, meta, all_specs, by_section_out

def main() -> int:
    ap = argparse.ArgumentParser(description="Generate Electra One preset JSON from a Markdown CC/controls spec.")
    ap.add_argument("input_md", type=Path, help="Input markdown file")
    ap.add_argument("-o", "--output-json", type=Path, required=True, help="Output preset JSON path")
    ap.add_argument("--clean-md", type=Path, default=None, help="Optional: write cleaned markdown to this path")
    ap.add_argument("--debug", action="store_true", help="Print parsing/debug info")
    args = ap.parse_args()

    md_body = args.input_md.read_text(encoding="utf-8", errors="replace")
    title, meta, specs, by_section = parse_controls_from_md(md_body)

    if args.debug:
        list_count = sum(1 for s in specs if s.choices and not is_toggle(s.choices))
        pad_count =_unlock = sum(1 for s in specs if is_toggle(s.choices))
        fader_count = sum(1 for s in specs if not s.choices)
        print(f"Title: {title}")
        print(f"Sections with controls: {len(by_section)}")
        print(f"Controls: {len(specs)} (lists={list_count}, pads={pad_count}, faders={fader_count})")
        grid = compute_grid_bounds(meta)
        last_edge = grid["left_offset"] + (grid["cols"] - 1) * (grid["cell_w"] + grid["padding"]) + grid["cell_w"]
        print(f"Grid: cols={grid['cols']} rows={grid['rows']} cell={grid['cell_w']}x{grid['cell_h']} screen_w={grid['screen_w']} last_edge={last_edge}")

    preset = generate_preset(title, meta, specs)
    args.output_json.write_text(json.dumps(preset, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    if args.clean_md is not None:
        clean_md = generate_clean_markdown(title, meta, by_section)
        args.clean_md.write_text(clean_md, encoding="utf-8")

    return 0



