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
| N100     | 100      | Filter Cutoff   | 0-127 | | NRPN control |
| C200     | 200      | Fine Tune       | 0-16383 | | 14-bit CC (inferred from range) |

Message Type Prefixes (optional):
- C or c: CC message (default if no prefix)
  - 7-bit (cc7) if range <= 127
  - 14-bit (cc14) if range > 127
- N or n: NRPN message (always 14-bit)
- S or s: SysEx message (future support)

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
from .json2md import convert_json_to_markdown
from .mdcleaner import generate_clean_markdown
from .mdparser import parse_controls_from_md


# -----------------------------
# Electra One layout + JSON
# -----------------------------

def compute_grid_bounds(meta: dict[str, Any]) -> dict[str, int]:
    electra = meta.get("electra", {}) if isinstance(meta.get("electra"), dict) else {}

    cols = int(electra.get("cols", 6))
    rows = int(electra.get("rows", 6))
    top_offset = int(electra.get("top_offset", 28))
    left_offset = int(electra.get("left_offset", 20))
    cell_height = int(electra.get("cell_height", 56))
    cell_width = int(electra.get("cell_width", 146))
    xpadding = int(electra.get("xpadding", 20))
    ypadding = int(electra.get("ypadding", 34))

    # IMPORTANT: Many firmwares appear to have ~800px usable width for controls.
    # We default to 800 unless overridden.
    screen_w = int(electra.get("screen_width_controls", electra.get("screen_width", 800)))


    return {
        "screen_w": screen_w,
        "cols": cols,
        "rows": rows,
        "top_offset": top_offset,
        "left_offset": left_offset,
        "xpadding": xpadding,
        "ypadding": ypadding,
        "cell_w": cell_width,
        "cell_h": cell_height,
    }

def bounds_for_index(idx: int, grid: dict[str, int]) -> list[int]:
    cols = grid["cols"]
    left = grid["left_offset"]
    top_offset = grid["top_offset"]
    cw = grid["cell_w"]
    ch = grid["cell_h"]
    xpadding = grid.get("xpadding", 0)
    ypadding = grid.get("ypadding", 0)

    r = idx // cols
    c = idx % cols
    x = left + c * (cw + xpadding)
    y = top_offset + r * (ch + ypadding)
    return [int(x), int(y), int(cw), int(ch)]

def is_toggle(choices: list[tuple[int, str]]) -> bool:
    """Check if choices represent a 2-valued toggle (on/off).
    
    A control is considered a toggle if it has exactly 2 choices AND the labels
    indicate on/off semantics (e.g., "On"/"Off", "Play"/"Pause", etc.).
    This distinguishes toggles from other 2-value lists like "Red"/"Blue".
    """
    if len(choices) != 2:
        return False
    
    # Get the labels (case-insensitive)
    labels = [lbl.lower().strip() for _, lbl in choices]
    labels_set = set(labels)
    
    # Check for common on/off label patterns
    on_off_patterns = [
        {"on", "off"},
        {"play", "pause"},
        {"enable", "disable"},
        {"enabled", "disabled"},
        {"yes", "no"},
        {"true", "false"},
    ]
    
    return labels_set in on_off_patterns

def control_type(spec: ControlSpec) -> str:
    """Determine the Electra One control type based on the control spec.
    
    Returns:
        - "adsr" for ADSR envelope controls
        - "adr" for ADR envelope controls
        - "pad" for 2-valued toggles (on/off controls)
        - "list" for multi-valued choices
        - "fader" for continuous ranges
    """
    if spec.envelope_type:
        return spec.envelope_type.lower()
    if spec.choices:
        return "pad" if is_toggle(spec.choices) else "list"
    return "fader"

def control_mode(spec: ControlSpec, ctype: str) -> str:
    """Determine the control mode for a given control type.
    
    For pad controls:
        - "toggle" mode: press to turn on, press again to turn off (used for 2-valued settings)
        - "momentary" mode: on while pressed, off when released
    
    For fader controls:
        - "unipolar" mode: 0 to max (default for positive ranges)
        - "bipolar" mode: negative to positive (inferred from negative min value)
    
    Args:
        spec: The control specification
        ctype: The control type (pad, list, fader, adsr, or adr)
    
    Returns:
        The appropriate mode string for the control type
    """
    # Use explicitly inferred mode if available
    if spec.mode is not None:
        return spec.mode
    
    # Default mode logic
    if ctype == "pad":
        return "toggle"  # Use toggle mode for 2-valued settings
    if ctype == "list":
        return "default"
    if ctype in ("adsr", "adr"):
        return "default"  # Envelope controls use default mode
    return "unipolar"

def message_type(spec: ControlSpec) -> str:
    """Determine the Electra One message type based on the control spec.
    
    Returns:
        - "nrpn" for NRPN messages (msg_type="N")
        - "cc14" for 14-bit CC messages (msg_type="C" and range > 127)
        - "cc7" for 7-bit CC messages (msg_type="C" and range <= 127)
        - "sysex" for SysEx messages (msg_type="S", future)
    """
    if spec.msg_type == "N":
        return "nrpn"
    elif spec.msg_type == "S":
        return "sysex"  # Future support
    else:  # msg_type == "C" (default)
        # Infer 7-bit vs 14-bit from range
        if spec.max_val > 127:
            return "cc14"
        else:
            return "cc7"

def message_max_value(spec: ControlSpec, msg_type: str) -> int:
    """Determine the max MIDI value for a message type.
    
    For NRPN, the max is always 16383 regardless of the control's range.
    For CC7/CC14, it's 127 or 16383 based on the message type.
    """
    if msg_type == "nrpn":
        return 16383  # NRPN is always 14-bit
    elif msg_type == "cc14":
        return 16383
    else:  # cc7
        return 127

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
                
                # Envelope controls (ADSR/ADR) have special structure
                if ctype in ("adsr", "adr"):
                    # Validate that we have a list of CCs
                    if not isinstance(spec.cc, list):
                        # Skip invalid envelope control
                        position_idx += 1
                        continue
                    
                    # Define envelope component names
                    if ctype == "adsr":
                        components = ["attack", "decay", "sustain", "release"]
                    else:  # adr
                        components = ["attack", "decay", "release"]
                    
                    # Validate CC count matches envelope type
                    if len(spec.cc) != len(components):
                        # Skip invalid envelope control
                        position_idx += 1
                        continue
                    
                    # Create values array with one entry per component
                    values_array: list[dict[str, Any]] = []
                    inputs_array: list[dict[str, Any]] = []
                    
                    msg_type = message_type(spec)
                    msg_max = message_max_value(spec, msg_type)
                    for idx, (component, cc_num) in enumerate(zip(components, spec.cc), start=1):
                        value_obj: dict[str, Any] = {
                            "id": component,
                            "min": spec.min_val,
                            "max": spec.max_val,
                            "message": {
                                "deviceId": 1,
                                "type": msg_type,
                                "parameterNumber": cc_num,
                                "min": 0,
                                "max": msg_max,
                            }
                        }
                        # Add defaultValue if specified
                        if spec.default_value is not None:
                            value_obj["defaultValue"] = spec.default_value
                        values_array.append(value_obj)
                        inputs_array.append({
                            "potId": idx,
                            "valueId": component
                        })
                    
                    # Calculate bounds for envelope control (wider than normal)
                    # Envelopes typically span 2 columns
                    bounds = bounds_for_index(position_idx, grid)
                    # Double the width for envelope controls
                    bounds[2] = bounds[2] * 2 + grid.get("xpadding", 20)
                    
                    control_obj: dict[str, Any] = {
                        "id": control_id,
                        "type": ctype,
                        "name": spec.label,
                        "bounds": bounds,
                        "pageId": page_id,
                        "controlSetId": 1,
                        "inputs": inputs_array,
                        "values": values_array,
                    }
                    
                    # Add color if specified
                    if spec.color is not None:
                        control_obj["color"] = spec.color
                    
                    controls.append(control_obj)
                    control_id += 1
                    # Envelope controls take up 2 positions
                    position_idx += 2
                    
                # Pad controls use a different value structure with offValue/onValue
                elif ctype == "pad":
                    # Extract off and on values from choices (sorted: [off, on])
                    vals = sorted((v, lbl) for v, lbl in spec.choices)
                    off_val, on_val = vals[0][0], vals[1][0]
                    
                    msg_type = message_type(spec)
                    val: dict[str, Any] = {
                        "id": "value",
                        "message": {
                            "type": msg_type,
                            "deviceId": 1,
                            "parameterNumber": spec.cc,
                            "offValue": off_val,
                            "onValue": on_val,
                        },
                    }
                    
                    control_obj: dict[str, Any] = {
                        "id": control_id,
                        "type": ctype,
                        "name": spec.label,
                        "bounds": bounds_for_index(position_idx, grid),
                        "pageId": page_id,
                        "controlSetId": 1,
                        "values": [val],
                        "mode": control_mode(spec, ctype),
                        "visible": True,
                    }
                    
                    # Add color if specified
                    if spec.color is not None:
                        control_obj["color"] = spec.color
                    
                    controls.append(control_obj)
                    control_id += 1
                    position_idx += 1
                    
                else:
                    # List and fader controls use min/max structure
                    msg_type = message_type(spec)
                    msg_max = message_max_value(spec, msg_type)
                    val = {
                        "id": "value",
                        "min": spec.min_val,
                        "max": spec.max_val,
                        "message": {
                            "deviceId": 1,
                            "type": msg_type,
                            "parameterNumber": spec.cc,
                            "min": 0,
                            "max": msg_max,
                        },
                    }
                    # Add defaultValue if specified
                    if spec.default_value is not None:
                        val["defaultValue"] = spec.default_value
                    # Only non-pad controls use overlays
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
                        "mode": control_mode(spec, ctype),
                        "variant": "thin" if ctype == "fader" else "default",
                    }
                    
                    # Add color if specified
                    if spec.color is not None:
                        control_obj["color"] = spec.color
                    
                    controls.append(control_obj)
                    control_id += 1
                    position_idx += 1

            page_id += 1

    # Generate startup messages: send each control's default value with delays
    # Skip blank rows as they don't have actual controls
    startup_messages: list[dict[str, Any]] = []
    for spec in sections:
        if spec.is_blank:
            continue
        
        # Use default_value if specified, otherwise fall back to min_val
        startup_val = spec.default_value if spec.default_value is not None else spec.min_val
        
        # Envelope controls have multiple CCs
        if isinstance(spec.cc, list):
            for cc_num in spec.cc:
                startup_messages.append({
                    "type": "cc",
                    "ch": channel,
                    "cc": cc_num,
                    "val": startup_val,
                })
                startup_messages.append({
                    "type": "delay",
                    "ms": startup_delay_ms,
                })
        else:
            # Single CC control
            startup_messages.append({
                "type": "cc",
                "ch": channel,
                "cc": spec.cc,
                "val": startup_val,
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
    ap = argparse.ArgumentParser(
        description="Convert between Markdown CC/controls specs and Electra One preset JSON.",
        epilog="Examples:\n"
               "  MD to JSON: %(prog)s specs/ndlr2.md -o preset.json\n"
               "  JSON to MD: %(prog)s preset.json --to-markdown -o spec.md\n",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("input", type=Path, help="Input file (markdown or JSON)")
    ap.add_argument("-o", "--output", type=Path, required=True, help="Output file path")
    ap.add_argument("--to-markdown", action="store_true", help="Convert JSON to Markdown (reverse mode)")
    ap.add_argument("--clean-md", type=Path, default=None, help="Optional: write cleaned markdown to this path (MD→JSON mode only)")
    ap.add_argument("--pretty", action="store_true", help="Format JSON output with indentation for readability (MD→JSON mode only)")
    ap.add_argument("--debug", action="store_true", help="Print parsing/debug info")
    args = ap.parse_args()

    # Determine conversion direction
    if args.to_markdown:
        # JSON → Markdown conversion
        if args.debug:
            print(f"Converting JSON to Markdown: {args.input} → {args.output}")
        
        convert_json_to_markdown(args.input, args.output)
        
        if args.debug:
            print(f"Conversion complete. Check stderr for any warnings about unsupported features.")
        
        return 0
    
    # Markdown → JSON conversion (original behavior)
    md_body = args.input.read_text(encoding="utf-8", errors="replace")
    title, meta, specs, by_section = parse_controls_from_md(md_body)

    if args.debug:
        envelope_count = sum(1 for s in specs if s.envelope_type)
        list_count = sum(1 for s in specs if s.choices and not is_toggle(s.choices) and not s.envelope_type)
        pad_count = sum(1 for s in specs if is_toggle(s.choices) and not s.envelope_type)
        fader_count = sum(1 for s in specs if not s.choices and not s.envelope_type)
        print(f"Title: {title}")
        print(f"Metadata: {meta}")
        print(f"Sections with controls: {len(by_section)}")
        print(f"Controls: {len(specs)} (envelopes={envelope_count}, lists={list_count}, pads={pad_count}, faders={fader_count})")
        grid = compute_grid_bounds(meta)
        print(f"Grid: cols={grid['cols']} rows={grid['rows']} cell={grid['cell_w']}x{grid['cell_h']}")

    preset = generate_preset(title, meta, specs)
    
    # Format JSON output: minified by default, pretty-printed with --pretty
    if args.pretty:
        json_output = json.dumps(preset, ensure_ascii=False, indent=2)
    else:
        json_output = json.dumps(preset, ensure_ascii=False, separators=(",", ":"))
    
    args.output.write_text(json_output, encoding="utf-8")

    if args.clean_md is not None:
        clean_md = generate_clean_markdown(title, meta, by_section)
        args.clean_md.write_text(clean_md, encoding="utf-8")

    return 0



