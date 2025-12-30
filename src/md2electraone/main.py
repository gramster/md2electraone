#!/usr/bin/env python3
"""
ndlr_electra_presetgen.py

Generate an Electra One preset JSON from a Markdown spec containing sections and tables.

Input markdown format (suggested):

# Preset Title

Optional YAML frontmatter:

---
# Top-level metadata (used in preset JSON)
name: Moog Subsequent 37        # Device name (also used in devices array)
version: 2                       # Preset version (default: 2)
port: 1                          # MIDI port (default: 1)
channel: 5                       # MIDI channel (default: 1)
manufacturer: Conductive Labs    # Manufacturer (informational)
device: NDLR                     # Alternative to 'name' (deprecated, use 'name')

# Electra One layout configuration
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

# MIDI configuration (can also be set at top level)
midi:
  port: 1                        # MIDI port (overridden by top-level 'port')
  channel: 1                     # MIDI channel (overridden by top-level 'channel')
  startup_delay_ms: 20           # delay between startup CC messages (default: 20ms)
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
import json
import re
import sys
from pathlib import Path
from typing import Any

from .controlspec import ControlSpec
from .mdcleaner import generate_clean_markdown
from .mdparser import parse_controls_from_md


# -----------------------------
# Electra One layout + JSON
# -----------------------------

def compute_grid_bounds(meta: dict[str, Any]) -> dict[str, int]:
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

def bounds_for_index(idx: int, grid: dict[str, int]) -> list[int]:
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

def is_toggle(choices: list[tuple[int, str]]) -> bool:
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
    meta: dict[str, Any],
    sections: list[ControlSpec],
) -> dict[str, Any]:
    grid = compute_grid_bounds(meta)

    midi_meta = meta.get("midi", {}) if isinstance(meta.get("midi"), dict) else {}
    
    # Support both top-level and nested midi metadata
    # Priority: top-level frontmatter > midi.* > defaults
    device_name = str(meta.get("name", meta.get("device", "NDLR")))
    port = int(meta.get("port", midi_meta.get("port", 1)))
    channel = int(meta.get("channel", midi_meta.get("channel", 1)))
    version = int(meta.get("version", 2))
    rate = int(midi_meta.get("rate", 20))
    startup_delay_ms = int(midi_meta.get("startup_delay_ms", 20))

    # Overlay reuse
    overlays: list[dict[str, Any]] = []
    overlay_key_to_id: dict[tuple[tuple[int, str], ...], int] = {}
    next_overlay_id = 1

    def overlay_id_for(choices: list[tuple[int, str]]) -> int:
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

    pages: list[dict[str, Any]] = []
    controls: list[dict[str, Any]] = []

    # Group specs by section title in original order
    by_section: dict[str, list[ControlSpec]] = {}
    order: list[str] = []
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

            # Track position index separately to handle blank rows
            position_idx = 0
            for spec in chunk:
                # Skip blank rows - they reserve a position but don't create a control
                if spec.is_blank:
                    position_idx += 1
                    continue
                    
                ctype = control_type(spec)
                val: dict[str, Any] = {
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

                control_obj: dict[str, Any] = {
                    "id": control_id,
                    "type": ctype,
                    "name": spec.label,
                    "bounds": bounds_for_index(position_idx, grid),
                    "pageId": page_id,
                    "controlSetId": 1,
                    "values": [val],
                    "variant": "thin" if ctype == "fader" else "default",
                    "mode": control_mode(spec, ctype),
                }
                # Add color if specified
                if spec.color is not None:
                    control_obj["color"] = spec.color
                
                controls.append(control_obj)

                control_id += 1
                position_idx += 1

            page_id += 1

    # Generate startup messages: send each control's minimum value (default) with delays
    # Skip blank rows as they don't have actual controls
    startup_messages: list[dict[str, Any]] = []
    for spec in sections:
        if spec.is_blank:
            continue
        startup_messages.append({
            "type": "cc",
            "ch": channel,
            "cc": spec.cc,
            "val": spec.min_val,
        })
        startup_messages.append({
            "type": "delay",
            "ms": startup_delay_ms,
        })

    preset = {
        "version": version,
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
        "startup": {
            "messages": startup_messages,
        },
    }
    return preset


# -----------------------------
# Main: read -> parse -> emit
# -----------------------------

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
        pad_count = sum(1 for s in specs if is_toggle(s.choices))
        fader_count = sum(1 for s in specs if not s.choices)
        print(f"Title: {title}")
        print(f"Metadata: {meta}")
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



