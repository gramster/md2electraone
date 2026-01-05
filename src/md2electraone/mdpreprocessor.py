"""
Markdown preprocessor for device expansion.

This module handles the <device> token expansion in markdown specifications,
allowing a single template to be expanded into multiple devices/pages.

The preprocessing happens in two phases:
1. Extract device count from frontmatter
2. Expand <device> tokens in frontmatter and body
3. Process "device: name" declarations and convert to device IDs
"""

import re
from typing import Any


class DeviceExpansionError(Exception):
    """Raised when there's an error during device expansion."""
    pass


def extract_device_count_from_raw(md: str) -> int:
    """Extract device count from raw markdown frontmatter.
    
    Args:
        md: Raw markdown with frontmatter
        
    Returns:
        Device count (default: 1 if not specified)
    """
    # Look for "device count: N" in the frontmatter
    lines = md.splitlines()
    in_frontmatter = False
    for line in lines:
        if line.strip() == "---":
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                break  # End of frontmatter
        
        if in_frontmatter:
            m = re.match(r'^\s*device count\s*:\s*(\d+)', line)
            if m:
                return int(m.group(1))
    
    return 1


def expand_frontmatter_devices(md: str, device_count: int) -> str:
    """Expand <device> tokens in the frontmatter devices list.
    
    This function:
    1. Finds device template entries with <device> tokens
    2. Expands them to multiple device entries (one per device number)
    3. Removes the "device count" line
    4. Handles explicit "id:" fields and detects conflicts
    
    Args:
        md: Raw markdown with frontmatter
        device_count: Number of devices to expand to
        
    Returns:
        Markdown with expanded device entries
        
    Raises:
        DeviceExpansionError: If there are ID conflicts
    """
    if device_count <= 1:
        return md
    
    lines = md.splitlines()
    result_lines: list[str] = []
    i = 0
    in_frontmatter = False
    in_devices_section = False
    devices_indent = 0
    used_ids: set[int] = set()
    
    while i < len(lines):
        line = lines[i]
        
        # Track frontmatter boundaries
        if line.strip() == "---":
            result_lines.append(line)
            if not in_frontmatter:
                in_frontmatter = True
            else:
                in_frontmatter = False
                in_devices_section = False
            i += 1
            continue
        
        if not in_frontmatter:
            result_lines.append(line)
            i += 1
            continue
        
        # Check if we're entering devices section
        if re.match(r'^\s*devices\s*:', line):
            in_devices_section = True
            devices_indent = len(line) - len(line.lstrip())
            result_lines.append(line)
            i += 1
            continue
        
        # Skip "device count" line
        if in_devices_section and re.match(r'^\s*device count\s*:', line):
            i += 1
            continue
        
        # Check if we're leaving devices section (dedent or new top-level key)
        if in_devices_section:
            indent = len(line) - len(line.lstrip())
            if line.strip() and indent <= devices_indent and not line.strip().startswith('-'):
                in_devices_section = False
        
        # Check for device list item with <device> token
        if in_devices_section and re.match(r'^\s*-\s+', line):
            # Collect this device entry (all lines until next list item or dedent)
            device_lines: list[str] = [line]
            list_indent = len(line) - len(line.lstrip())
            i += 1
            
            while i < len(lines):
                next_line = lines[i]
                next_indent = len(next_line) - len(next_line.lstrip())
                
                # Stop if we hit another list item at same level or dedent
                if next_line.strip().startswith('-') and next_indent <= list_indent:
                    break
                if next_line.strip() and next_indent <= list_indent:
                    break
                
                device_lines.append(next_line)
                i += 1
            
            # Check if this device entry contains <device> token
            device_text = '\n'.join(device_lines)
            if '<device>' in device_text:
                # Expand this device entry for each device number
                for dev_num in range(1, device_count + 1):
                    expanded_text = device_text.replace('<device>', str(dev_num))
                    expanded_lines = expanded_text.splitlines()
                    
                    # Check for explicit ID and detect conflicts
                    for exp_line in expanded_lines:
                        id_match = re.match(r'^\s*id\s*:\s*(\d+)', exp_line)
                        if id_match:
                            explicit_id = int(id_match.group(1))
                            if explicit_id in used_ids:
                                raise DeviceExpansionError(
                                    f"Device ID conflict: ID {explicit_id} is used multiple times"
                                )
                            used_ids.add(explicit_id)
                    
                    # If no explicit ID, track the auto-assigned ID
                    has_explicit_id = any(re.match(r'^\s*id\s*:', l) for l in expanded_lines)
                    if not has_explicit_id:
                        auto_id = dev_num
                        if auto_id in used_ids:
                            raise DeviceExpansionError(
                                f"Device ID conflict: Auto-assigned ID {auto_id} conflicts with explicit ID"
                            )
                        used_ids.add(auto_id)
                    
                    result_lines.extend(expanded_lines)
            else:
                # No <device> token, keep as-is
                # Check for explicit ID
                for dev_line in device_lines:
                    id_match = re.match(r'^\s*id\s*:\s*(\d+)', dev_line)
                    if id_match:
                        explicit_id = int(id_match.group(1))
                        if explicit_id in used_ids:
                            raise DeviceExpansionError(
                                f"Device ID conflict: ID {explicit_id} is used multiple times"
                            )
                        used_ids.add(explicit_id)
                
                result_lines.extend(device_lines)
            
            continue
        
        # Regular line
        result_lines.append(line)
        i += 1
    
    return '\n'.join(result_lines)


def expand_sections_with_device_token(md: str, device_count: int) -> str:
    """Expand sections with <device> tokens into multiple sections.
    
    This function:
    1. Identifies sections (## headers) that contain <device> tokens
    2. Groups consecutive sections with <device> tokens
    3. Duplicates each group for each device number (1 to device_count)
    4. Replaces <device> tokens with actual device numbers
    
    Args:
        md: Markdown body (after frontmatter)
        device_count: Number of devices to expand to
        
    Returns:
        Expanded markdown with <device> tokens replaced
    """
    if device_count <= 1:
        return md
    
    lines = md.splitlines()
    result_lines: list[str] = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check if this is a section header (## or more) with <device> token
        header_match = re.match(r'^(#{2,})\s+(.+)$', line)
        
        if header_match and '<device>' in header_match.group(2):
            # Found a section with <device> token
            # Collect this section and any consecutive sections with <device>
            section_group: list[tuple[str, list[str]]] = []
            
            while i < len(lines):
                line = lines[i]
                header_match = re.match(r'^(#{2,})\s+(.+)$', line)
                
                if not header_match:
                    i += 1
                    if i >= len(lines):
                        break
                    continue
                
                header_level = header_match.group(1)
                header_text = header_match.group(2)
                
                if '<device>' not in header_text:
                    # This section doesn't have <device>, stop collecting
                    break
                
                # Collect section content until next header
                section_lines: list[str] = []
                i += 1
                while i < len(lines):
                    next_line = lines[i]
                    # Check if this is another header at the same or higher level
                    next_header = re.match(r'^(#{2,})\s+', next_line)
                    if next_header:
                        break
                    section_lines.append(next_line)
                    i += 1
                
                section_group.append((f"{header_level} {header_text}", section_lines))
            
            # Now expand this group for each device
            for device_num in range(1, device_count + 1):
                for header_line, content_lines in section_group:
                    # Expand header
                    expanded_header = header_line.replace('<device>', str(device_num))
                    result_lines.append(expanded_header)
                    
                    # Expand content
                    for content_line in content_lines:
                        expanded_line = content_line.replace('<device>', str(device_num))
                        result_lines.append(expanded_line)
        else:
            # Regular line, keep as-is
            result_lines.append(line)
            i += 1
    
    return '\n'.join(result_lines)


def preprocess_markdown(md: str) -> str:
    """Main preprocessing function for device expansion.
    
    This function only expands <device> tokens in:
    1. Frontmatter device list entries
    2. Section headers and their content
    
    It does NOT process "device: name" declarations - those are handled
    later during parsing when we have access to the full device mapping.
    
    Args:
        md: Raw markdown with frontmatter
        
    Returns:
        Preprocessed markdown with <device> tokens expanded
        
    Raises:
        DeviceExpansionError: If there are errors during expansion
    """
    # Extract device count
    device_count = extract_device_count_from_raw(md)
    
    if device_count <= 1:
        # No expansion needed
        return md
    
    # Expand devices in frontmatter
    md = expand_frontmatter_devices(md, device_count)
    
    # Split frontmatter and body
    lines = md.splitlines()
    frontmatter_lines: list[str] = []
    body_lines: list[str] = []
    in_frontmatter = False
    frontmatter_ended = False
    
    for line in lines:
        if line.strip() == "---":
            frontmatter_lines.append(line)
            if not in_frontmatter:
                in_frontmatter = True
            else:
                in_frontmatter = False
                frontmatter_ended = True
            continue
        
        if not frontmatter_ended:
            frontmatter_lines.append(line)
        else:
            body_lines.append(line)
    
    body = '\n'.join(body_lines)
    
    # Expand sections with <device> tokens
    body = expand_sections_with_device_token(body, device_count)
    
    # Reconstruct markdown
    return '\n'.join(frontmatter_lines) + '\n' + body
