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
    }
    
    # Extract from values array (should have exactly one value with id="value")
    values = control.get("values", [])
    if not values:
        warn(f"Control '{info['label']}' has no values array")
        return info
    
    if len(values) > 1:
        warn(f"Control '{info['label']}' has multiple values. Only the first will be converted.")
    
    value = values[0]
    message = value.get("message", {})
    
    # Extract CC number
    info["cc"] = message.get("parameterNumber")
    
    # Handle pad controls (toggle with offValue/onValue)
    if info["type"] == "pad":
        off_val = message.get("offValue", 0)
        on_val = message.get("onValue", 127)
        # Determine labels from overlay if present, otherwise use Off/On
        overlay_id = value.get("overlayId")
        if overlay_id is not None and overlay_id in overlay_map:
            # Use overlay labels for pad
            overlay_choices = overlay_map[overlay_id]
            if len(overlay_choices) == 2:
                info["choices"] = overlay_choices
            else:
                warn(f"Pad control '{info['label']}' has overlay with {len(overlay_choices)} items (expected 2)")
                info["choices"] = [(off_val, "Off"), (on_val, "On")]
        else:
            info["choices"] = [(off_val, "Off"), (on_val, "On")]
        info["min_val"] = min(off_val, on_val)
        info["max_val"] = max(off_val, on_val)
    else:
        # List and fader controls use min/max
        info["min_val"] = value.get("min", 0)
        info["max_val"] = value.get("max", 127)
        
        # Check for overlay (choices)
        overlay_id = value.get("overlayId")
        if overlay_id is not None and overlay_id in overlay_map:
            info["choices"] = overlay_map[overlay_id]
    
    return info


def group_controls_by_page(preset: dict[str, Any], overlay_map: dict[int, list[tuple[int, str]]]) -> list[tuple[str, list[dict[str, Any]]]]:
    """Group controls by page, maintaining order."""
    pages_map = {page["id"]: page["name"] for page in preset.get("pages", [])}
    
    # Group controls by page ID
    controls_by_page: dict[int, list[dict[str, Any]]] = {}
    for control in preset.get("controls", []):
        page_id = control.get("pageId")
        if page_id is None:
            warn(f"Control '{control.get('name', 'unknown')}' has no pageId")
            continue
        
        if page_id not in controls_by_page:
            controls_by_page[page_id] = []
        
        controls_by_page[page_id].append(extract_control_info(control, overlay_map))
    
    # Build ordered list of (page_name, controls)
    sections: list[tuple[str, list[dict[str, Any]]]] = []
    for page_id in sorted(controls_by_page.keys()):
        page_name = pages_map.get(page_id, f"Page {page_id}")
        sections.append((page_name, controls_by_page[page_id]))
    
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
    
    # Check for unsupported features
    if preset.get("groups"):
        warn("Groups are not supported and will be dropped")
    
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
            cc = ctrl["cc"]
            label = ctrl["label"]
            min_val = ctrl["min_val"]
            max_val = ctrl["max_val"]
            choices = ctrl["choices"]
            color = ctrl["color"]
            
            # Format range
            if min_val == max_val:
                range_str = str(min_val)
            else:
                range_str = f"{min_val}-{max_val}"
            
            # Format choices
            choices_str = format_choices(choices)
            
            # Add color column if color changed
            if color != current_color:
                current_color = color
                if color:
                    # Add color to this row
                    lines.append(f"| {cc} | {label} | {range_str} | {choices_str} | #{color} |")
                    # Update header if needed (add Color column)
                    if "Color" not in lines[-3]:
                        lines[-3] = "| CC (Dec) | Label | Range | Choices | Color |"
                        lines[-2] = "|----------|-------|-------|---------|-------|"
                else:
                    lines.append(f"| {cc} | {label} | {range_str} | {choices_str} |")
            else:
                # Color unchanged, use current column count
                if current_color:
                    lines.append(f"| {cc} | {label} | {range_str} | {choices_str} | |")
                else:
                    lines.append(f"| {cc} | {label} | {range_str} | {choices_str} |")
        
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
