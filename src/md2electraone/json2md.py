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
    
    # Device info
    devices = preset.get("devices", [])
    if len(devices) > 1:
        # Multiple devices - output as list
        devices_list = []
        for device in devices:
            dev_dict: dict[str, Any] = {}
            if "name" in device:
                dev_dict["name"] = device["name"]
            if "port" in device:
                dev_dict["port"] = device["port"]
            if "channel" in device:
                dev_dict["channel"] = device["channel"]
            if "rate" in device and device["rate"] != 20:
                dev_dict["rate"] = device["rate"]
            devices_list.append(dev_dict)
        meta["devices"] = devices_list
    elif devices:
        # Single device (legacy format)
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
        "device_id": None,
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
        # Extract CC numbers and device ID from all values
        cc_list = []
        device_id = None
        for val in values:
            message = val.get("message", {})
            cc_num = message.get("parameterNumber")
            if cc_num is not None:
                cc_list.append(cc_num)
            if device_id is None:
                device_id = message.get("deviceId")
        
        if cc_list:
            info["cc"] = cc_list
            info["device_id"] = device_id
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
    
    # Extract CC number and device ID
    info["cc"] = message.get("parameterNumber")
    info["device_id"] = message.get("deviceId")
    
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
    
    # Track group name occurrences across all pages to ensure uniqueness
    group_name_counts: dict[str, int] = {}
    for groups in groups_by_page.values():
        for group in groups:
            name = group.get("name", "")
            group_name_counts[name] = group_name_counts.get(name, 0) + 1
    
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
        ctrl_info = extract_control_info(control, overlay_map)
        # Preserve bounds in the control info for later use
        ctrl_info["_bounds"] = bounds
        controls_by_page[page_id].append((ctrl_info, bounds, control_id))
    
    # Build ordered list of (page_name, controls_with_groups)
    sections: list[tuple[str, list[dict[str, Any]]]] = []
    
    # Track group name usage to make them unique with letter suffixes
    group_name_usage: dict[str, int] = {}
    
    def get_unique_group_name(base_name: str) -> str:
        """Generate a unique group name by appending letters if needed."""
        # Check if this name appears multiple times
        if group_name_counts.get(base_name, 0) <= 1:
            # Only one occurrence, no suffix needed
            return base_name
        
        # Multiple occurrences - track usage and append letter
        count = group_name_usage.get(base_name, 0)
        group_name_usage[base_name] = count + 1
        
        if count == 0:
            # First occurrence - no suffix
            return base_name
        else:
            # Subsequent occurrences - append letter (A, B, C, ...)
            # count=1 -> A, count=2 -> B, etc.
            letter = chr(ord('A') + count - 1)
            return f"{base_name} {letter}"
    
    for page_id in sorted(controls_by_page.keys()):
        page_name = pages_map.get(page_id, f"Page {page_id}")
        
        # Get controls and groups for this page
        controls_with_bounds = controls_by_page.get(page_id, [])
        groups = groups_by_page.get(page_id, [])
        
        # Sort controls by position: row-by-row (Y), then column-by-column (X)
        # bounds format is [x, y, width, height]
        controls_with_bounds.sort(key=lambda item: (item[1][1], item[1][0]))  # Sort by Y, then X
        
        # Build the ordered list of controls
        ordered_controls: list[dict[str, Any]] = []
        control_index_map: dict[int, int] = {}  # old index -> new index in ordered_controls
        
        for i, (ctrl, _, _) in enumerate(controls_with_bounds):
            control_index_map[i] = len(ordered_controls)
            ordered_controls.append(ctrl)
        
        # Map control index to group name (for explicit group membership)
        control_to_group: dict[int, str] = {}
        
        if groups:
            # For each group, find which controls belong to it based on bounding box
            for group in groups:
                group_bounds = group.get("bounds", [0, 0, 0, 0])
                group_x, group_y, group_w, group_h = group_bounds
                base_group_name = group.get("name", "")
                # Get unique name for this group occurrence
                group_name = get_unique_group_name(base_group_name)
                
                # Detect if this is a header-only group (small height, typically 16-20px)
                is_header_only = group_h <= 20
                
                # Find ALL controls within or below the group's bounding box
                matching_controls = []
                for i, (ctrl, ctrl_bounds, ctrl_id) in enumerate(controls_with_bounds):
                    ctrl_x, ctrl_y, ctrl_w, ctrl_h = ctrl_bounds
                    
                    if is_header_only:
                        # For header-only groups, find controls positioned directly below
                        # Controls should be horizontally aligned with the group header
                        # and positioned within a reasonable distance below it (e.g., within 100px)
                        if (ctrl_x >= group_x and
                            ctrl_x + ctrl_w <= group_x + group_w + 20 and  # Allow slight horizontal tolerance
                            ctrl_y > group_y and
                            ctrl_y < group_y + 100):  # Within 100px below the header
                            matching_controls.append((i, ctrl, ctrl_y, ctrl_x))
                    else:
                        # For full-size groups, check if control is inside the group's bounding box
                        # Control must be within the group bounds
                        if (ctrl_x >= group_x and
                            ctrl_x + ctrl_w <= group_x + group_w and
                            ctrl_y >= group_y and
                            ctrl_y + ctrl_h <= group_y + group_h):
                            matching_controls.append((i, ctrl, ctrl_y, ctrl_x))
                
                if matching_controls:
                    # Find the minimum y (top row)
                    min_y = min(y for _, _, y, _ in matching_controls)
                    # Get controls in the top row (sorted by x position)
                    top_row_controls = sorted([(i, x) for i, _, y, x in matching_controls if y == min_y], key=lambda t: t[1])
                    top_row_indices = [i for i, _ in top_row_controls]
                    
                    # Check if ALL controls in the group are in the top row
                    all_in_top_row = len(matching_controls) == len(top_row_indices)
                    
                    # Check if top row controls are contiguous (no gaps AND consecutive in sorted list)
                    is_contiguous_in_row = False
                    if all_in_top_row and len(top_row_indices) > 0:
                        # Check if they appear consecutively in the sorted control list
                        sorted_indices = sorted(top_row_indices)
                        consecutive_in_list = all(
                            sorted_indices[i] + 1 == sorted_indices[i + 1]
                            for i in range(len(sorted_indices) - 1)
                        )
                        # Also check that they are ALL controls in that row (no gaps)
                        # Get all controls in the same row
                        all_controls_in_row = [i for i, (_, bounds, _) in enumerate(controls_with_bounds) if bounds[1] == min_y]
                        # Check if the group controls are all consecutive controls in that row
                        if consecutive_in_list and sorted_indices == all_controls_in_row:
                            is_contiguous_in_row = True
                        elif consecutive_in_list:
                            # They're consecutive in the list, but check if there are any controls between them
                            # that are NOT in the group (which would make them non-contiguous)
                            min_idx = min(sorted_indices)
                            max_idx = max(sorted_indices)
                            all_in_range = set(range(min_idx, max_idx + 1))
                            group_set = set(sorted_indices)
                            # If there are controls in the range that aren't in the group, it's non-contiguous
                            is_contiguous_in_row = (all_in_range == group_set)
                    
                    # Determine if we should use Range (contiguous top row only) or explicit group IDs
                    if is_contiguous_in_row and all_in_top_row:
                        # Use Range-based group definition (all controls are contiguous in top row)
                        group_size = len(top_row_indices)
                        first_control_idx = min(top_row_indices)
                        insert_position = control_index_map[first_control_idx]
                        
                        # Create group definition with Range using unique name
                        group_def = {
                            "is_group": True,
                            "label": group_name,
                            "group_size": group_size,
                            "color": group.get("color"),
                            "_bounds": group_bounds,
                        }
                        
                        # Insert group before its first control
                        ordered_controls.insert(insert_position, group_def)
                        # Update all subsequent indices in the map
                        for idx in control_index_map:
                            if control_index_map[idx] >= insert_position:
                                control_index_map[idx] += 1
                    else:
                        # Use explicit group membership (no Range)
                        # Either controls span multiple rows or are non-contiguous
                        # Mark all controls in this group for explicit prefix using unique name
                        for i, _, _, _ in matching_controls:
                            control_to_group[i] = group_name
                        
                        # Insert group definition before first control
                        first_control_idx = min(i for i, _, _, _ in matching_controls)
                        insert_position = control_index_map[first_control_idx]
                        
                        group_def = {
                            "is_group": True,
                            "label": group_name,
                            "group_size": 0,  # No Range specified
                            "color": group.get("color"),
                            "_bounds": group_bounds,
                        }
                        
                        # Insert group before its first control
                        ordered_controls.insert(insert_position, group_def)
                        # Update all subsequent indices in the map
                        for idx in control_index_map:
                            if control_index_map[idx] >= insert_position:
                                control_index_map[idx] += 1
        
        # Add group_id to controls that need explicit membership
        for original_idx, group_name in control_to_group.items():
            if original_idx < len(controls_with_bounds):
                ctrl_obj, _, _ = controls_with_bounds[original_idx]
                ctrl_obj["group_id"] = group_name
        
        sections.append((page_name, ordered_controls))
    
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
    
    # Build device ID to index mapping for multi-device presets
    devices = preset.get("devices", [])
    device_id_to_index: dict[int, int] = {}
    for idx, device in enumerate(devices, start=1):
        device_id = device.get("id")
        if device_id is not None:
            device_id_to_index[device_id] = idx
    
    # Determine if we need device prefixes (only if multiple devices)
    use_device_prefix = len(devices) > 1
    
    # Generate frontmatter if we have metadata
    if meta:
        lines.append("---")
        for key, value in meta.items():
            if isinstance(value, list):
                # Handle list values (e.g., devices)
                lines.append(f"{key}:")
                for item in value:
                    if isinstance(item, dict):
                        for subkey, subval in item.items():
                            lines.append(f"  - {subkey}: {subval}")
                    else:
                        lines.append(f"  - {item}")
            elif isinstance(value, dict):
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
        
        # Table header - always include Color column
        lines.append("| Control (Dec) | Label | Range | Choices | Color |")
        lines.append("|---------------|-------|-------|---------|-------|")
        
        # Track current color for persistence
        current_color: str | None = None
        
        # Detect grid layout and insert blank rows for gaps
        # Collect all unique Y and X positions to determine grid structure
        y_positions: set[int] = set()
        x_positions: set[int] = set()
        
        for ctrl in controls:
            if ctrl.get("is_group"):
                continue
            bounds = ctrl.get("_bounds")
            if bounds:
                y_positions.add(bounds[1])
                x_positions.add(bounds[0])
        
        # Sort positions
        sorted_y = sorted(y_positions)
        sorted_x = sorted(x_positions)
        
        # Infer grid spacing from positions
        # Calculate spacing between consecutive positions
        x_spacing = None
        if len(sorted_x) > 1:
            spacings = [sorted_x[i+1] - sorted_x[i] for i in range(len(sorted_x)-1)]
            # Use the minimum spacing as the grid spacing (most common case)
            x_spacing = min(spacings) if spacings else None
        
        y_spacing = None
        if len(sorted_y) > 1:
            spacings = [sorted_y[i+1] - sorted_y[i] for i in range(len(sorted_y)-1)]
            y_spacing = min(spacings) if spacings else None
        
        # Build complete grid including missing positions
        # Assume standard 6-column Electra One grid
        complete_x = set(sorted_x)
        if x_spacing and len(sorted_x) > 1:
            # Fill in missing X positions based on spacing
            # Extend to 6 columns (standard Electra One grid)
            min_x = min(sorted_x)
            for i in range(6):
                complete_x.add(min_x + i * x_spacing)
        
        complete_y = set(sorted_y)
        if y_spacing and len(sorted_y) > 1:
            # Fill in missing Y positions based on spacing
            min_y, max_y = min(sorted_y), max(sorted_y)
            y = min_y
            while y <= max_y:
                complete_y.add(y)
                y += y_spacing
        
        # Create index mappings with complete grid
        sorted_complete_x = sorted(complete_x)
        sorted_complete_y = sorted(complete_y)
        y_to_row = {y: i for i, y in enumerate(sorted_complete_y)}
        x_to_col = {x: i for i, x in enumerate(sorted_complete_x)}
        max_col = len(sorted_complete_x) - 1
        
        # Build a grid: (row_idx, col_idx) -> control or None
        # Also track groups - map each group to the row it should appear before
        grid_map: dict[tuple[int, int], dict[str, Any]] = {}
        groups_by_row: dict[int, list[dict[str, Any]]] = {}  # row_idx -> list of groups
        
        for ctrl in controls:
            if ctrl.get("is_group"):
                # Groups appear before the row containing their controls
                # Find the first control row that comes after the group's y position
                bounds = ctrl.get("_bounds")
                if bounds:
                    group_y = bounds[1]
                    # Find the first control row with y > group_y
                    target_row = None
                    for row_idx, row_y in enumerate(sorted_complete_y):
                        if row_y > group_y:
                            target_row = row_idx
                            break
                    
                    if target_row is not None:
                        if target_row not in groups_by_row:
                            groups_by_row[target_row] = []
                        groups_by_row[target_row].append(ctrl)
                continue
            
            bounds = ctrl.get("_bounds")
            if bounds:
                curr_y, curr_x = bounds[1], bounds[0]
                curr_row_idx = y_to_row.get(curr_y, -1)
                curr_col_idx = x_to_col.get(curr_x, -1)
                if curr_row_idx >= 0 and curr_col_idx >= 0:
                    grid_map[(curr_row_idx, curr_col_idx)] = ctrl
        
        # Output the grid row by row, column by column
        num_rows = len(sorted_complete_y)
        num_cols = len(sorted_complete_x)
        
        # Find the last non-empty cell in the grid to avoid trailing blanks
        last_row = -1
        last_col = -1
        for row_idx in range(num_rows):
            for col_idx in range(num_cols):
                if (row_idx, col_idx) in grid_map:
                    last_row = row_idx
                    last_col = max(last_col, col_idx)
        
        for row_idx in range(num_rows):
            # Output any groups that should appear before this row
            if row_idx in groups_by_row:
                for group_ctrl in groups_by_row[row_idx]:
                    label = group_ctrl["label"]
                    group_size = group_ctrl.get("group_size", 0)
                    color = group_ctrl.get("color")
                    
                    if color != current_color:
                        current_color = color
                    
                    range_val = str(group_size) if group_size > 0 else ""
                    color_val = f"#{current_color}" if current_color else ""
                    lines.append(f"| {label} | {label.upper()} | {range_val} | | {color_val} |")
            
            # Output each column in this row
            for col_idx in range(num_cols):
                ctrl = grid_map.get((row_idx, col_idx))
                
                # Skip trailing blanks (blanks after the last control)
                if ctrl is None:
                    # Only output blank if it's not a trailing blank
                    # Trailing blanks are those after the last control in the entire grid
                    if row_idx < last_row or (row_idx == last_row and col_idx <= last_col):
                        lines.append("|  |  |  |  |  |")
                else:
                    # Output control
                    cc = ctrl["cc"]
                    device_id = ctrl.get("device_id")
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
                    
                    # Add device prefix if multiple devices and device_id is set
                    if use_device_prefix and device_id is not None:
                        device_index = device_id_to_index.get(device_id)
                        if device_index is not None:
                            cc_str = f"{device_index}:{cc_str}"
                    
                    # Format range with optional default value
                    if min_val == max_val:
                        range_str = str(min_val)
                    else:
                        range_str = f"{min_val}-{max_val}"
                    
                    # Add default value if present and not the auto-default (0 or min)
                    if default_value is not None:
                        auto_default = 0 if min_val <= 0 <= max_val else min_val
                        if default_value != auto_default:
                            range_str += f" ({default_value})"
                    
                    # Format choices (or envelope type)
                    if envelope_type:
                        choices_str = envelope_type
                    else:
                        choices_str = format_choices(choices)
                    
                    # Update current color if changed
                    if color != current_color:
                        current_color = color
                    
                    # Generate row with color column
                    color_val = f"#{current_color}" if current_color else ""
                    lines.append(f"| {cc_str} | {label} | {range_str} | {choices_str} | {color_val} |")
        
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
