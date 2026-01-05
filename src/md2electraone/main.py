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
---

## GENERAL

| CC (Hex) | CC (Dec) | Label           | Range | Choices | Description |
|---------:|---------:|-----------------|------:|---------|-------------|
| 0x1A     | 26       | Chord Degree    | 1-7   | 1=I,2=II,3=III,4=IV,5=V,6=VI,7=VII | ... |
| 0x39     | 57       | Black Keys Ctrl | 0-127 | 0=On,127=Off | ... |
| N100     | 100      | Filter Cutoff   | 0-127 | | NRPN control |
| C200     | 200      | Fine Tune       | 0-16383 | | 14-bit CC (inferred from range) |

Groups (optional):
- Use "Group" in the CC column to define a group label above controls
- Range specifies the number of controls in the top row of the group
- Example:
  | CC    | Label      | Range | Color  |
  |-------|------------|-------|--------|
  | Group | OSCILLATOR | 3     | FF0000 |
  | 10    | Waveform   | 0-3   |        |
  | 11    | Octave     | -2-2  |        |
  | 12    | Detune     | 0-127 |        |

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
from datetime import datetime
from pathlib import Path
from typing import Any

from .controlspec import ControlSpec
from .json2md import convert_json_to_markdown
from .mdcleaner import generate_clean_markdown
from .mdparser import parse_controls_from_md


# -----------------------------
# Layout constants
# -----------------------------

# Group label layout constants
GROUP_LABEL_HEIGHT = 16  # Height of the group label box
GROUP_LABEL_PADDING = 8  # Vertical padding between group label and controls

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
    xpadding = int(electra.get("xpadding", 21))
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
        - "program" for Program Change messages (msg_type="P")
        - "cc14" for 14-bit CC messages (msg_type="C" and range > 127)
        - "cc7" for 7-bit CC messages (msg_type="C" and range <= 127)
        - "sysex" for SysEx messages (msg_type="S", future)
    """
    if spec.msg_type == "N":
        return "nrpn"
    elif spec.msg_type == "P":
        return "program"
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
    For program, it's always 127.
    """
    if msg_type == "nrpn":
        return 16383  # NRPN is always 14-bit
    elif msg_type == "cc14":
        return 16383
    elif msg_type == "program":
        return 127  # Program change is 7-bit (0-127)
    else:  # cc7
        return 127

def generate_preset(
    title: str,
    meta: dict[str, Any],
    sections: list[ControlSpec],
    verbose: bool = False,
) -> dict[str, Any]:
    grid = compute_grid_bounds(meta)

    midi_meta = meta.get("midi", {}) if isinstance(meta.get("midi"), dict) else {}
    
    # Support both top-level and nested midi metadata
    # Priority: top-level frontmatter > midi.* > defaults
    version = int(meta.get("version", 2))
    rate = int(midi_meta.get("rate", 20))
    
    # Handle multiple devices
    devices_config = meta.get("devices", [])
    if isinstance(devices_config, list) and len(devices_config) > 0:
        # Multiple devices specified in frontmatter
        devices_list = []
        for idx, dev in enumerate(devices_config, start=1):
            if isinstance(dev, dict):
                devices_list.append({
                    "id": idx,
                    "name": str(dev.get("name", "Generic MIDI")),
                    "port": int(dev.get("port", 1)),
                    "channel": int(dev.get("channel", idx)),
                    "rate": int(dev.get("rate", rate)),
                })
        # Build device index to ID mapping (1-based index -> device ID)
        device_index_to_id = {i: dev["id"] for i, dev in enumerate(devices_list, start=1)}
    else:
        # Single device (legacy format)
        device_name = str(meta.get("name", meta.get("device", "Generic MIDI")))
        port = int(meta.get("port", midi_meta.get("port", 1)))
        channel = int(meta.get("channel", midi_meta.get("channel", 1)))
        devices_list = [{
            "id": 1,
            "name": device_name,
            "port": port,
            "channel": channel,
            "rate": rate,
        }]
        device_index_to_id = {1: 1}

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
    
    # Track groups: map of (page_id, group_name) -> list of control_ids in top row
    group_controls: dict[tuple[int, str], list[int]] = {}
    # Track group definitions: map of (page_id, group_name) -> (label, color)
    group_defs: dict[tuple[int, str], tuple[str, str | None]] = {}

    # Group specs by section title in original order
    by_section: dict[str, list[ControlSpec]] = {}
    order: list[str] = []
    for s in sections:
        if s.section not in by_section:
            by_section[s.section] = []
            order.append(s.section)
        by_section[s.section].append(s)

    page_id = 1
    next_control_id = 1  # ID counter for controls (starts at 1)
    next_group_id = 1000  # ID counter for groups (starts at 1000)

    for section_title in order:
        specs = by_section[section_title]
        # Filter out group rows when calculating page capacity, as they don't consume grid positions
        # But keep them in the specs list for processing
        non_group_specs = [s for s in specs if not s.is_group]
        
        # Calculate chunks based on non-group specs only
        if len(non_group_specs) <= page_cap:
            # All fits on one page - keep all specs together (including groups)
            chunks = [specs]
        else:
            # Need multiple pages - chunk by actual control count
            chunks = []
            current_chunk: list[ControlSpec] = []
            control_count = 0
            
            for spec in specs:
                if spec.is_group:
                    # Groups don't consume positions, always add to current chunk
                    current_chunk.append(spec)
                else:
                    # Check if adding this control would exceed page capacity
                    if control_count >= page_cap:
                        # Start new chunk
                        chunks.append(current_chunk)
                        current_chunk = [spec]
                        control_count = 1
                    else:
                        current_chunk.append(spec)
                        control_count += 1
            
            # Add final chunk if not empty
            if current_chunk:
                chunks.append(current_chunk)
        for ci, chunk in enumerate(chunks, start=1):
            page_name = section_title if len(chunks) == 1 else f"{section_title} ({ci}/{len(chunks)})"
            pages.append({"id": page_id, "name": page_name, "defaultControlSetId": 1})

            # Track position index separately to handle blank rows and groups
            position_idx = 0
            # Track current group for contiguous assignment (range-based groups)
            current_group_name: str | None = None
            current_group_remaining = 0
            
            for spec_idx, spec in enumerate(chunk):
                # Handle group definition rows
                if spec.is_group:
                    # Use group_id if available (new format), otherwise fall back to label (old format)
                    internal_name = spec.group_id if spec.group_id else spec.label
                    
                    # Store group definition with label and color
                    group_key = (page_id, internal_name)
                    group_defs[group_key] = (spec.label, spec.color)
                    
                    # Set up contiguous assignment for next N controls (only if Range is specified)
                    if spec.group_size > 0:
                        current_group_name = internal_name
                        current_group_remaining = spec.group_size
                    
                    # Group rows don't consume a position
                    continue
                
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
                    # Determine device ID: use spec.device_id if set, otherwise default to 1
                    device_id_for_control = device_index_to_id.get(spec.device_id, 1) if spec.device_id else 1
                    for idx, (component, cc_num) in enumerate(zip(components, spec.cc), start=1):
                        message_obj: dict[str, Any] = {
                            "deviceId": device_id_for_control,
                            "type": msg_type,
                        }
                        # Program messages use min/max directly, others use parameterNumber
                        if msg_type == "program":
                            message_obj["min"] = spec.min_val
                            message_obj["max"] = spec.max_val
                        else:
                            message_obj["parameterNumber"] = cc_num
                            message_obj["min"] = 0
                            message_obj["max"] = msg_max
                        
                        value_obj: dict[str, Any] = {
                            "id": component,
                            "min": spec.min_val,
                            "max": spec.max_val,
                            "message": message_obj
                        }
                        # Add defaultValue if specified
                        if spec.default_value is not None:
                            value_obj["defaultValue"] = spec.default_value
                        values_array.append(value_obj)
                        inputs_array.append({
                            "potId": idx,
                            "valueId": component
                        })
                    
                    # Calculate bounds for envelope control (same as any other control)
                    bounds = bounds_for_index(position_idx, grid)
                    
                    if verbose:
                        print(f"  Control {next_id} ({ctype}): {spec.label} -> bounds={bounds}")
                    
                    control_obj: dict[str, Any] = {
                        "id": next_control_id,
                        "type": ctype,
                        "name": spec.label,
                        "bounds": bounds,
                        "pageId": page_id,
                        "inputs": inputs_array,
                        "values": values_array,
                    }
                    
                    # Add color if specified
                    if spec.color is not None:
                        control_obj["color"] = spec.color
                    
                    controls.append(control_obj)
                    
                    # Track group assignment
                    # Priority: explicit group_id > contiguous range-based assignment
                    assigned_group = None
                    if spec.group_id:
                        # Explicit group membership via "<groupname>:" prefix
                        assigned_group = spec.group_id
                    elif current_group_remaining > 0:
                        # Range-based contiguous assignment
                        assigned_group = current_group_name
                        current_group_remaining -= 1
                    
                    if assigned_group:
                        group_key = (page_id, assigned_group)
                        if group_key not in group_controls:
                            group_controls[group_key] = []
                        group_controls[group_key].append(next_control_id)
                    
                    next_control_id += 1
                    # Envelope controls take up 1 position like any other control
                    position_idx += 1
                    
                # Pad controls use a different value structure with offValue/onValue
                elif ctype == "pad":
                    # Extract off and on values from choices (sorted: [off, on])
                    vals = sorted((v, lbl) for v, lbl in spec.choices)
                    off_val, on_val = vals[0][0], vals[1][0]
                    
                    msg_type = message_type(spec)
                    # Determine device ID: use spec.device_id if set, otherwise default to 1
                    device_id_for_control = device_index_to_id.get(spec.device_id, 1) if spec.device_id else 1
                    
                    message_obj: dict[str, Any] = {
                        "type": msg_type,
                        "deviceId": device_id_for_control,
                        "offValue": off_val,
                        "onValue": on_val,
                    }
                    # Program messages don't use parameterNumber
                    if msg_type != "program":
                        message_obj["parameterNumber"] = spec.cc
                    
                    val: dict[str, Any] = {
                        "id": "value",
                        "message": message_obj,
                    }
                    
                    bounds = bounds_for_index(position_idx, grid)
                    
                    if verbose:
                        print(f"  Control {next_id} ({ctype}): {spec.label} -> bounds={bounds}")
                    
                    control_obj: dict[str, Any] = {
                        "id": next_control_id,
                        "type": ctype,
                        "name": spec.label,
                        "bounds": bounds,
                        "pageId": page_id,
                        "values": [val],
                        "mode": control_mode(spec, ctype),
                        "visible": True,
                    }
                    
                    # Add color if specified
                    if spec.color is not None:
                        control_obj["color"] = spec.color
                    
                    controls.append(control_obj)
                    
                    # Track group assignment
                    # Priority: explicit group_id > contiguous range-based assignment
                    assigned_group = None
                    if spec.group_id:
                        # Explicit group membership via "<groupname>:" prefix
                        assigned_group = spec.group_id
                    elif current_group_remaining > 0:
                        # Range-based contiguous assignment
                        assigned_group = current_group_name
                        current_group_remaining -= 1
                    
                    if assigned_group:
                        group_key = (page_id, assigned_group)
                        if group_key not in group_controls:
                            group_controls[group_key] = []
                        group_controls[group_key].append(next_control_id)
                    
                    next_control_id += 1
                    position_idx += 1
                    
                else:
                    # List and fader controls use min/max structure
                    msg_type = message_type(spec)
                    msg_max = message_max_value(spec, msg_type)
                    # Determine device ID: use spec.device_id if set, otherwise default to 1
                    device_id_for_control = device_index_to_id.get(spec.device_id, 1) if spec.device_id else 1
                    
                    message_obj: dict[str, Any] = {
                        "deviceId": device_id_for_control,
                        "type": msg_type,
                    }
                    # Program messages use min/max directly, others use parameterNumber
                    if msg_type == "program":
                        message_obj["min"] = spec.min_val
                        message_obj["max"] = spec.max_val
                    else:
                        message_obj["parameterNumber"] = spec.cc
                        message_obj["min"] = 0
                        message_obj["max"] = msg_max
                    
                    val = {
                        "id": "value",
                        "min": spec.min_val,
                        "max": spec.max_val,
                        "message": message_obj,
                    }
                    # Add defaultValue if specified
                    if spec.default_value is not None:
                        val["defaultValue"] = spec.default_value
                    # Only non-pad controls use overlays
                    if spec.choices:
                        val["overlayId"] = overlay_id_for(spec.choices)

                    bounds = bounds_for_index(position_idx, grid)
                    
                    if verbose:
                        print(f"  Control {next_id} ({ctype}): {spec.label} -> bounds={bounds}")
                    
                    control_obj: dict[str, Any] = {
                        "id": next_control_id,
                        "type": ctype,
                        "name": spec.label,
                        "bounds": bounds,
                        "pageId": page_id,
                        "values": [val],
                        "mode": control_mode(spec, ctype),
                        "variant": "thin" if ctype == "fader" else "default",
                    }
                    
                    # Add color if specified
                    if spec.color is not None:
                        control_obj["color"] = spec.color
                    
                    controls.append(control_obj)
                    
                    # Track group assignment
                    # Priority: explicit group_id > contiguous range-based assignment
                    assigned_group = None
                    if spec.group_id:
                        # Explicit group membership via "<groupname>:" prefix
                        assigned_group = spec.group_id
                    elif current_group_remaining > 0:
                        # Range-based contiguous assignment
                        assigned_group = current_group_name
                        current_group_remaining -= 1
                    
                    if assigned_group:
                        group_key = (page_id, assigned_group)
                        if group_key not in group_controls:
                            group_controls[group_key] = []
                        group_controls[group_key].append(next_control_id)
                    
                    next_control_id += 1
                    position_idx += 1

            page_id += 1

    # Generate groups array by calculating bounding boxes that surround all controls in the group
    groups: list[dict[str, Any]] = []
    
    # Get group variant from metadata (e.g., "highlighted")
    group_variant = meta.get("groups")
    
    for group_key, control_ids in group_controls.items():
        page_id_for_group, group_internal_id = group_key
        
        # Get the label and color from group definition
        group_def = group_defs.get(group_key)
        if group_def:
            group_label, group_color = group_def
        else:
            # Fallback if not found (shouldn't happen)
            group_label = group_internal_id
            group_color = None
        
        # Find all controls in this group
        group_control_objs = [c for c in controls if c["id"] in control_ids]
        
        if not group_control_objs:
            continue  # Skip empty groups
        
        # Calculate bounding box that surrounds ALL controls in the group
        min_x = min(c["bounds"][0] for c in group_control_objs)
        min_y = min(c["bounds"][1] for c in group_control_objs)
        max_x = max(c["bounds"][0] + c["bounds"][2] for c in group_control_objs)
        max_y = max(c["bounds"][1] + c["bounds"][3] for c in group_control_objs)
        
        # Group bounding box: includes label above controls and surrounds all controls
        # Label is 22px above the topmost control, with 6px horizontal padding
        group_x = min_x - 6
        group_y = min_y - 22
        group_w = (max_x - min_x) + 12  # 6px padding on each side
        # TODO: seems in some cases a fixed height of 16 is used for groups?
        #group_h = (max_y - min_y) + 25  # From label top to bottom of lowest control + 3px padding
        group_h = 16
        group_bounds = [int(group_x), int(group_y), int(group_w), int(group_h)]
        
        # Check if any controls on this page are inside the group bounds but not in the group
        # This can happen when a group has non-contiguous members
        swallowed_controls = []
        for ctrl in controls:
            if ctrl["pageId"] != page_id_for_group:
                continue
            if ctrl["id"] in control_ids:
                continue  # This control is in the group
            
            # Check if this control is inside the group bounding box
            cx, cy, cw, ch = ctrl["bounds"]
            if (cx >= group_x and
                cx + cw <= group_x + group_w and
                cy >= group_y and
                cy + ch <= group_y + group_h):
                swallowed_controls.append(ctrl["name"])
        
        if swallowed_controls:
            print(f"WARNING: Group '{group_label}' bounding box includes controls that were not tagged as group members: {', '.join(swallowed_controls)}", file=sys.stderr)
            print(f"         When converting back to markdown, these controls will appear to be in the group.", file=sys.stderr)
        
        if verbose:
            print(f"  Group {next_group_id}: {group_label} -> bounds={group_bounds}")
        
        group_obj: dict[str, Any] = {
            "id": next_group_id,
            "pageId": page_id_for_group,
            "name": group_label,  # Use display label, not internal ID
            "bounds": group_bounds,
        }
        
        # Add color if specified
        if group_color:
            group_obj["color"] = group_color
        
        # Add variant if specified in metadata
        if group_variant:
            group_obj["variant"] = group_variant
        
        groups.append(group_obj)
        next_group_id += 1


    # Generate projectID in format: NNNNN-YYYYMMDD-HHMM
    # where NNNNN is first 5 chars of instrument name
    now = datetime.now()
    instrument_prefix = devices_list[0]["name"][:5].upper()
    timestamp = now.strftime("%Y%m%d-%H%M")
    project_id = f"{instrument_prefix}-{timestamp}"
    
    preset = {
        "version": version,
        "name": title,
        "projectId": project_id,
        "pages": pages,
        "devices": devices_list,
        "overlays": overlays,
        "groups": groups,
        "controls": controls,
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
    ap.add_argument("--verbose", action="store_true", help="Print verbose output (use with --debug to show bounding boxes)")
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
        
        if args.verbose:
            print("\nComputed bounding boxes:")

    preset = generate_preset(title, meta, specs, verbose=(args.debug and args.verbose))
    
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

if __name__ == "__main__":
    sys.exit(main())

