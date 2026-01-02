#!/usr/bin/env python3
"""
json2md.py

Convert Electra One preset JSON back to Markdown format.
Supports the subset of features that md2electraone can generate.
Warns about unsupported features that will be dropped.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def warn(message: str) -> None:
    """Print a warning message to stderr."""
    print(f"WARNING: {message}", file=sys.stderr)


def extract_metadata(preset: dict[str, Any]) -> dict[str, Any]:
    """Extract metadata from preset JSON for frontmatter."""
    meta: dict[str, Any] = {}
    
    # Basic preset info
    if "version" in preset and preset["version"] != 2:
        meta["version"] = preset["version"]
    
    # Device info (from first device)
    devices = preset.get("devices", [])
    if devices:
        device = devices[0]
        if "name" in device:
            meta["name"] = device["name"]
        if "port" in device and device["port"] != 1:
            meta["port"] = device["port"]
        if "channel" in device and device["channel"] != 1:
            meta["channel"] = device["channel"]
        
        # MIDI rate in nested midi section
        if "rate" in device and device["rate"] != 20:
            if "midi" not in meta:
                meta["midi"] = {}
            meta["midi"]["rate"] = device["rate"]
    
    # Warn about multiple devices
    if len(devices) > 1:
        warn(f"Multiple devices found ({len(devices)}). Only the first device will be preserved in metadata.")
    
    # Extract group variant from first group (if any)
    groups = preset.get("groups", [])
    if groups:
        first_group = groups[0]
        if "variant" in first_group:
            meta["groups"] = first_group["variant"]
    
    return meta


def build_overlay_map(preset: dict[str, Any]) -> dict[int, list[tuple[int, str]]]:
    """Build a map of overlay ID to choices list."""
    overlay_map: dict[int, list[tuple[int, str]]] = {}
    
    for overlay in preset.get("overlays", []):
        overlay_id = overlay.get("id")
        if overlay_id is None:
            continue
        
        items = overlay.get("items", [])
        choices = [(item["value"], item["label"]) for item in items if "value" in item and "label" in item]
        overlay_map[overlay_id] = choices
    
    return overlay_map


def extract_control_info(control: dict[str, Any], overlay_map: dict[int, list[tuple[int, str]]]) -> dict[str, Any]:
    """Extract control information for markdown table row."""
    info: dict[str, Any] = {
        "label": control.get("name", ""),
        "cc": None,
        "min_val": None,
        "max_val": None,
        "choices": [],
        "type": control.get("type", "fader"),
        "color": control.get("color"),
        "envelope_type": None,
        "default_value": None,
        "mode": control.get("mode"),
    }
    
    # Extract from values array
    values = control.get("values", [])
    if not values:
        warn(f"Control '{info['label']}' has no values array")
        return info
    
    # Handle envelope controls (ADSR/ADR)
    if info["type"] in ("adsr", "adr"):
        # Extract CC numbers from all values
        cc_list = []
        for val in values:
            message = val.get("message", {})
            cc_num = message.get("parameterNumber")
            if cc_num is not None:
                cc_list.append(cc_num)
        
        if cc_list:
            info["cc"] = cc_list
            # Use first value for min/max and default (all should be the same)
            info["min_val"] = values[0].get("min", 0)
            info["max_val"] = values[0].get("max", 127)
            info["default_value"] = values[0].get("defaultValue")
            info["envelope_type"] = info["type"].upper()
        else:
            warn(f"Envelope control '{info['label']}' has no valid CC numbers")
        
        return info
    
    # Non-envelope controls should have exactly one value with id="value"
    if len(values) > 1:
        warn(f"Control '{info['label']}' has multiple values. Only the first will be converted.")
    
    value = values[0]
    message = value.get("message", {})
    
    # Extract CC number
    info["cc"] = message.get("parameterNumber")
    
    # Handle pad controls (toggle/momentary with offValue/onValue)
    if info["type"] == "pad":
        off_val = message.get("offValue", 0)
        on_val = message.get("onValue", 127)
        # Determine labels from overlay if present, otherwise use mode-appropriate defaults
        overlay_id = value.get("overlayId")
        if overlay_id is not None and overlay_id in overlay_map:
            # Use overlay labels for pad
            overlay_choices = overlay_map[overlay_id]
            if len(overlay_choices) == 2:
                info["choices"] = overlay_choices
            else:
                warn(f"Pad control '{info['label']}' has overlay with {len(overlay_choices)} items (expected 2)")
                # Use mode-appropriate default labels
                if info["mode"] == "momentary":
                    info["choices"] = [(off_val, "Released"), (on_val, "Momentary")]
                else:
                    info["choices"] = [(off_val, "Off"), (on_val, "On")]
        else:
            # Use mode-appropriate default labels
            if info["mode"] == "momentary":
                info["choices"] = [(off_val, "Released"), (on_val, "Momentary")]
            else:
                info["choices"] = [(off_val, "Off"), (on_val, "On")]
        info["min_val"] = min(off_val, on_val)
        info["max_val"] = max(off_val, on_val)
        # Pad controls don't typically have defaultValue in the same way
    else:
        # List and fader controls use min/max
        info["min_val"] = value.get("min", 0)
        info["max_val"] = value.get("max", 127)
        info["default_value"] = value.get("defaultValue")
        
        # Check for overlay (choices)
        overlay_id = value.get("overlayId")
        if overlay_id is not None and overlay_id in overlay_map:
            info["choices"] = overlay_map[overlay_id]
    
    return info


def group_controls_by_page(preset: dict[str, Any], overlay_map: dict[int, list[tuple[int, str]]]) -> list[tuple[str, list[dict[str, Any]]]]:
    """Group controls by page, maintaining order and inserting group definitions."""
    pages_map = {page["id"]: page["name"] for page in preset.get("pages", [])}
    
    # Build map of groups by page
    groups_by_page: dict[int, list[dict[str, Any]]] = {}
    for group in preset.get("groups", []):
        page_id = group.get("pageId")
        if page_id is None:
            continue
        if page_id not in groups_by_page:
            groups_by_page[page_id] = []
        groups_by_page[page_id].append(group)
    
    # Group controls by page ID, with position info and control ID
    controls_by_page: dict[int, list[tuple[dict[str, Any], list[int], int]]] = {}
    for control in preset.get("controls", []):
        page_id = control.get("pageId")
        if page_id is None:
            warn(f"Control '{control.get('name', 'unknown')}' has no pageId")
            continue
        
        if page_id not in controls_by_page:
            controls_by_page[page_id] = []
        
        # Extract bounds for position calculation and control ID
        bounds = control.get("bounds", [0, 0, 0, 0])
        control_id = control.get("id", 0)
        controls_by_page[page_id].append((extract_control_info(control, overlay_map), bounds, control_id))
    
    # Build ordered list of (page_name, controls_with_groups)
    sections: list[tuple[str, list[dict[str, Any]]]] = []
    for page_id in sorted(controls_by_page.keys()):
        page_name = pages_map.get(page_id, f"Page {page_id}")
        
        # Get controls and groups for this page
        controls_with_bounds = controls_by_page.get(page_id, [])
        groups = groups_by_page.get(page_id, [])
        
        # Extract controls list
        controls_only = [ctrl for ctrl, _, _ in controls_with_bounds]
        
        # Map control index to group name (for explicit group membership)
        # This must be done BEFORE inserting group definitions
        control_to_group: dict[int, str] = {}
        
        if groups:
            # For each group, find which controls belong to it based on position
            for group in groups:
                group_bounds = group.get("bounds", [0, 0, 0, 0])
                group_x, group_y, group_w, group_h = group_bounds
                group_name = group.get("name", "")
                
                # Find ALL controls within the group's bounding box
                # Group label is above controls, so controls have y > group_y
                matching_controls = []
                for i, (ctrl, ctrl_bounds, ctrl_id) in enumerate(controls_with_bounds):
                    ctrl_x, ctrl_y, ctrl_w, ctrl_h = ctrl_bounds
                    # Check if control is within the group's bounding box
                    if (ctrl_x >= group_x and
                        ctrl_x < group_x + group_w and
                        ctrl_y > group_y):
                        matching_controls.append((i, ctrl, ctrl_y, ctrl_x))
                
                if matching_controls:
                    # Find the minimum y (top row)
                    min_y = min(y for _, _, y, _ in matching_controls)
                    # Get controls in the top row (sorted by x position)
                    top_row_controls = sorted([(i, x) for i, _, y, x in matching_controls if y == min_y], key=lambda t: t[1])
                    top_row_indices = [i for i, _ in top_row_controls]
                    
                    # Check if top row controls are contiguous in the control list
                    is_contiguous = False
                    if top_row_indices:
                        min_idx = min(top_row_indices)
                        max_idx = max(top_row_indices)
                        expected_indices = list(range(min_idx, max_idx + 1))
                        is_contiguous = (top_row_indices == expected_indices)
                    
                    # Check if ALL controls in the group are in the top row
                    all_in_top_row = len(matching_controls) == len(top_row_indices)
                    
                    # Determine if we should use Range (contiguous top row only) or explicit group IDs
                    if is_contiguous and len(top_row_indices) > 0 and all_in_top_row:
                        # Use Range-based group definition (all controls are contiguous in top row)
                        group_size = len(top_row_indices)
                        insert_idx = min(top_row_indices)
                        
                        # Create group definition with Range
                        group_def = {
                            "is_group": True,
                            "label": group_name,
                            "group_size": group_size,
                            "color": group.get("color"),
                        }
                        
                        # Insert group before its first control
                        controls_only.insert(insert_idx, group_def)
                    else:
                        # Use explicit group membership (no Range)
                        # Either controls span multiple rows or are non-contiguous
                        # Mark all controls in this group for explicit prefix (BEFORE inserting group def)
                        for i, _, _, _ in matching_controls:
                            control_to_group[i] = group_name
                        
                        # Now insert group definition
                        if matching_controls:
                            insert_idx = min(i for i, _, _, _ in matching_controls)
                            group_def = {
                                "is_group": True,
                                "label": group_name,
                                "group_size": 0,  # No Range specified
                                "color": group.get("color"),
                            }
                            controls_only.insert(insert_idx, group_def)
        
            result = controls_only
        else:
            result = controls_only
        
        # Add group_id to controls that need explicit membership
        # Note: control_to_group uses original indices (before group insertions)
        # We need to map back to original control objects
        for original_idx, group_name in control_to_group.items():
            if original_idx < len(controls_with_bounds):
                ctrl_obj, _, _ = controls_with_bounds[original_idx]
                ctrl_obj["group_id"] = group_name
        
        sections.append((page_name, result))
    
    return sections


def format_choices(choices: list[tuple[int, str]]) -> str:
    """Format choices list for markdown table."""
    if not choices:
        return ""
    
    # Check if it's a simple sequential mapping starting at 0 or 1
    if len(choices) > 0:
        first_val = choices[0][0]
        is_sequential = all(choices[i][0] == first_val + i for i in range(len(choices)))
        
        # Only use simple comma-separated format if sequential AND starting at 0 or 1
        # AND the values match the expected pattern (no gaps)
        if is_sequential and first_val in (0, 1) and len(choices) > 2:
            # Simple comma-separated list for sequential choices
            return ", ".join(label for _, label in choices)
    
    # Use explicit value=label format for non-sequential or 2-item lists
    return ", ".join(f"{val}={label}" for val, label in choices)


def generate_markdown(preset: dict[str, Any]) -> str:
    """Generate markdown from Electra One preset JSON."""
    lines: list[str] = []
    
    # Extract metadata
    meta = extract_metadata(preset)
    
    # Generate frontmatter if we have metadata
    if meta:
        lines.append("---")
        for key, value in meta.items():
            if isinstance(value, dict):
                lines.append(f"{key}:")
                for subkey, subval in value.items():
                    lines.append(f"  {subkey}: {subval}")
            else:
                lines.append(f"{key}: {value}")
        lines.append("---")
        lines.append("")
    
    # Title
    title = preset.get("name", "Untitled Preset")
    lines.append(f"# {title}")
    lines.append("")
    
    # Build overlay map
    overlay_map = build_overlay_map(preset)
    
    # Group controls by page
    sections = group_controls_by_page(preset, overlay_map)
    
    # Generate sections
    for section_name, controls in sections:
        lines.append(f"## {section_name}")
        lines.append("")
        
        # Table header
        lines.append("| CC (Dec) | Label | Range | Choices |")
        lines.append("|----------|-------|-------|---------|")
        
        # Track current color for persistence
        current_color: str | None = None
        
        # Table rows
        for ctrl in controls:
            # Handle group definition rows
            if ctrl.get("is_group"):
                label = ctrl["label"]
                group_size = ctrl.get("group_size", 0)
                color = ctrl.get("color")
                
                # Update current color if group has one
                if color != current_color:
                    current_color = color
                    if color:
                        # Add Color column header if not present
                        if "Color" not in lines[-2]:
                            lines[-2] = "| CC (Dec) | Label | Range | Choices | Color |"
                            lines[-1] = "|----------|-------|-------|---------|-------|"
                
                # Generate group row
                if current_color:
                    lines.append(f"| Group | {label} | {group_size} | | #{current_color} |" if current_color else f"| Group | {label} | {group_size} | | |")
                else:
                    lines.append(f"| Group | {label} | {group_size} | |")
                continue
            
            cc = ctrl["cc"]
            label = ctrl["label"]
            min_val = ctrl["min_val"]
            max_val = ctrl["max_val"]
            choices = ctrl["choices"]
            color = ctrl["color"]
            envelope_type = ctrl.get("envelope_type")
            default_value = ctrl.get("default_value")
            group_id = ctrl.get("group_id")
            
            # Add group prefix if this control has explicit group membership
            if group_id:
                label = f"{group_id}: {label}"
            
            # Format CC (may be a list for envelope controls)
            if isinstance(cc, list):
                cc_str = ",".join(str(c) for c in cc)
            else:
                cc_str = str(cc) if cc is not None else ""
            
            # Format range with optional default value
            if min_val == max_val:
                range_str = str(min_val)
            else:
                range_str = f"{min_val}-{max_val}"
            
            # Add default value if present and not the auto-default (0 or min)
            if default_value is not None:
                # Only include default if it's not the automatic default
                # (0 if in range, otherwise min)
                auto_default = 0 if min_val <= 0 <= max_val else min_val
                if default_value != auto_default:
                    range_str += f" ({default_value})"
            
            # Format choices (or envelope type)
            if envelope_type:
                choices_str = envelope_type
            else:
                choices_str = format_choices(choices)
            
            # Add color column if color changed
            if color != current_color:
                current_color = color
                if color:
                    # Add color to this row
                    lines.append(f"| {cc_str} | {label} | {range_str} | {choices_str} | #{color} |")
                    # Update header if needed (add Color column)
                    if "Color" not in lines[-3]:
                        lines[-3] = "| CC (Dec) | Label | Range | Choices | Color |"
                        lines[-2] = "|----------|-------|-------|---------|-------|"
                else:
                    lines.append(f"| {cc_str} | {label} | {range_str} | {choices_str} |")
            else:
                # Color unchanged, use current column count
                if current_color:
                    lines.append(f"| {cc_str} | {label} | {range_str} | {choices_str} | |")
                else:
                    lines.append(f"| {cc_str} | {label} | {range_str} | {choices_str} |")
        
        lines.append("")
    
    return "\n".join(lines)


def convert_json_to_markdown(json_path: Path, output_md: Path) -> None:
    """Convert Electra One JSON preset to Markdown."""
    # Read JSON
    with open(json_path, "r", encoding="utf-8") as f:
        preset = json.load(f)
    
    # Generate markdown
    markdown = generate_markdown(preset)
    
    # Write output
    output_md.write_text(markdown, encoding="utf-8")
