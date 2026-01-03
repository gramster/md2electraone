import re
from typing import Any
from .controlspec import ControlSpec
from .mdutils import clean_cell, pick

# -----------------------------
# YAML-ish frontmatter (minimal)
# -----------------------------

def parse_frontmatter(md: str) -> tuple[dict[str, Any], str]:
    """
    Minimal YAML frontmatter parser.
    Supports only simple key: value, one-level nesting via indentation, and simple lists.
    If you want full YAML, you can add PyYAML, but we keep it dependency-free.

    Returns (meta, remaining_markdown).
    """
    lines = md.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, md

    meta: dict[str, Any] = {}
    i = 1
    stack: list[tuple[int, dict[str, Any] | list[Any]]] = [(0, meta)]
    current_list_key: str | None = None

    def set_kv(container: dict[str, Any], k: str, v: Any) -> None:
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
        
        # Check for list item (starts with "- ")
        list_match = re.match(r'^\s*-\s+(.+)$', line)
        if list_match and current_list_key:
            # This is a list item
            item_content = list_match.group(1).strip()
            # Parse as key: value pairs for list items
            kv_match = re.match(r'^([A-Za-z0-9_\-]+)\s*:\s*(.+)$', item_content)
            if kv_match:
                # List of objects
                key = kv_match.group(1)
                raw_val = kv_match.group(2).strip()
                val: Any = raw_val
                if re.fullmatch(r"-?\d+", raw_val):
                    val = int(raw_val)
                elif raw_val.lower() in {"true", "false"}:
                    val = (raw_val.lower() == "true")
                
                # Get the list from meta
                if current_list_key in meta and isinstance(meta[current_list_key], list):
                    # Check if we need to start a new dict or add to existing
                    if not meta[current_list_key] or not isinstance(meta[current_list_key][-1], dict) or key in meta[current_list_key][-1]:
                        # Start new dict
                        meta[current_list_key].append({key: val})
                    else:
                        # Add to existing dict
                        meta[current_list_key][-1][key] = val
            i += 1
            continue
        
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
        if not isinstance(container, dict):
            i += 1
            continue

        if raw_val == "":
            # Check if next line is a list item
            if i + 1 < len(lines) and re.match(r'^\s*-\s+', lines[i + 1]):
                # Start a list
                new_list: list[Any] = []
                set_kv(container, key, new_list)
                current_list_key = key
            else:
                # start a nested map
                new_map: dict[str, Any] = {}
                set_kv(container, key, new_map)
                stack.append((indent + 2, new_map))
                current_list_key = None
        else:
            val_parsed: Any = raw_val
            # cast ints/bools if possible
            if re.fullmatch(r"-?\d+", raw_val):
                val_parsed = int(raw_val)
            elif raw_val.lower() in {"true", "false"}:
                val_parsed = (raw_val.lower() == "true")
            set_kv(container, key, val_parsed)
            current_list_key = None

        i += 1

    # if unclosed frontmatter, treat as none
    return {}, md

# -----------------------------
# Markdown parsing helpers
# -----------------------------

def split_sections(md: str) -> tuple[str, list[tuple[str, list[str]]]]:
    """
    Returns (title, [(section_title, section_lines), ...]).
    - Title is first H1 (# ...)
    - Sections are H2 (## ...) or H3 (### ...) etc (we treat any heading >=2 as section)
    """
    title = "Untitled Preset"
    sections: list[tuple[str, list[str]]] = []
    cur_title: str | None = None
    cur_lines: list[str] = []

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

def split_row(line: str) -> list[str]:
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [clean_cell(c) for c in s.split("|")]

def parse_tables(lines: list[str]) -> list[list[dict[str, str]]]:
    """
    Parse all pipe tables in a list of lines.
    Robust against:
    - missing trailing pipes
    - ragged rows (pads/merges as needed)
    """
    tables: list[list[dict[str, str]]] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if "|" in line and line.count("|") >= 1 and i + 1 < len(lines) and is_divider_line(lines[i + 1]):
            header = split_row(line)
            i += 2
            rows: list[dict[str, str]] = []
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
                # Include all rows, even blank ones (for layout control)
                rows.append(row)
                i += 1
            if rows:
                tables.append(rows)
            continue
        i += 1
    return tables


# -----------------------------
# Value parsers
# -----------------------------

def parse_cc(s: str) -> tuple[str, int | list[int] | None, int | None]:
    """Parse CC value(s) from a cell with optional message type prefix and device prefix.
    
    Supports prefixes:
        - C or c: CC message (default if no prefix)
        - N or n: NRPN message
        - S or s: SysEx message (future)
        - Device prefix: "1:38" means device 1, CC 38
    
    Returns:
        - tuple[str, int | list[int] | None, int | None]: (msg_type, cc_value, device_id)
          where msg_type is "C", "N", or "S"
          cc_value is int (single), list[int] (envelope), or None (invalid)
          device_id is int (1-based device index) or None (use default device)
    """
    s = clean_cell(s)
    if not s:
        return ("C", None, None)
    
    # Check for device prefix (e.g., "1:38" or "2:42")
    device_id = None
    m = re.match(r"^(\d+):(.+)$", s)
    if m:
        device_id = int(m.group(1))
        s = m.group(2).strip()
    
    # Check for message type prefix (C, N, S)
    msg_type = "C"  # default
    m = re.match(r"^([CNScns])(.+)$", s)
    if m:
        prefix = m.group(1).upper()
        s = m.group(2).strip()
        msg_type = prefix
    
    # Check for comma-separated list (envelope controls)
    if "," in s:
        parts = [p.strip() for p in s.split(",")]
        ccs = []
        for part in parts:
            # hex like 0x1A or 1A
            m = re.match(r"^(0x)?([0-9A-Fa-f]{1,2})$", part)
            if m and (m.group(1) or any(c.isalpha() for c in m.group(2))):
                ccs.append(int(m.group(2), 16))
            # decimal
            elif re.match(r"^\d+$", part):
                ccs.append(int(part))
            else:
                return (msg_type, None, device_id)  # Invalid format in list
        return (msg_type, ccs if ccs else None, device_id)
    
    # Single CC value
    # hex like 0x1A or 1A
    m = re.match(r"^(0x)?([0-9A-Fa-f]{1,2})$", s)
    if m and (m.group(1) or any(c.isalpha() for c in m.group(2))):
        return (msg_type, int(m.group(2), 16), device_id)
    # decimal
    m = re.match(r"^\d+$", s)
    if m:
        return (msg_type, int(s), device_id)
    return (msg_type, None, device_id)

def parse_range(s: str) -> tuple[int, int, int | None]:
    """Parse range string with optional default value.
    
    Supports formats:
        - "0-127" -> (0, 127, None)
        - "-64-63" -> (-64, 63, None)
        - "0-127 (64)" -> (0, 127, 64)
        - "64" -> (64, 64, None)
        - "-10" -> (-10, -10, None)
    
    Returns:
        tuple[int, int, int | None]: (min_val, max_val, default_value)
        If no default is specified, returns None for default_value.
    """
    s = clean_cell(s).replace("–", "-")
    
    # Check for default value in parentheses: "0-127 (64)" or "-64-63 (0)"
    default_val: int | None = None
    m = re.match(r"^(.+?)\s*\(\s*(-?\d+)\s*\)$", s)
    if m:
        s = m.group(1).strip()
        default_val = int(m.group(2))
    
    # Parse range: "0-127" or "-64-63"
    m = re.match(r"^(-?\d+)\s*-\s*(-?\d+)$", s)
    if m:
        return int(m.group(1)), int(m.group(2)), default_val
    
    # Parse single value: "64" or "-10"
    m = re.match(r"^(-?\d+)$", s)
    if m:
        v = int(m.group(1))
        return v, v, default_val
    
    return 0, 127, default_val

def expand_range_label(lhs_a: int, lhs_b: int, rhs: str) -> list[tuple[int, str]]:
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

def parse_choices(s: str, minv: int, maxv: int) -> list[tuple[int, str]]:
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
    items: list[tuple[int, str]] = []

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
    out: list[tuple[int, str]] = []
    for v, lbl in items:
        if v in seen:
            continue
        seen.add(v)
        out.append((int(v), str(lbl)))
    return out

def infer_choices_from_desc(desc: str, minv: int, maxv: int) -> list[tuple[int, str]]:
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


def parse_color(s: str) -> str | None:
    """
    Parse a color value from a cell. Accepts 6-character hex RGB values.
    Returns normalized uppercase hex string without '#' prefix, or None if invalid.
    Examples: "F45C51", "#F45C51", "f45c51" -> "F45C51"
    """
    s = clean_cell(s)
    if not s:
        return None
    # Remove '#' prefix if present
    if s.startswith("#"):
        s = s[1:]
    # Validate 6-character hex
    if re.fullmatch(r"[0-9A-Fa-f]{6}", s):
        return s.upper()
    return None


def infer_mode(minv: int, maxv: int, choices: list[tuple[int, str]]) -> str | None:
    """
    Infer the control mode based on control characteristics.
    
    Rules:
    - bipolar: faders with negative minimum value
    - momentary: 2-choice controls with "Momentary"/"Released" or similar labels
    - toggle: 2-choice controls with "On"/"Off" or similar labels (handled by is_toggle in main.py)
    - None: use default mode determination in main.py
    
    Returns:
        Mode string ("bipolar", "momentary") or None to use default logic
    """
    # Bipolar mode: faders with negative minimum
    if minv < 0 and not choices:
        return "bipolar"
    
    # Momentary mode: 2-choice controls with momentary/released semantics
    if len(choices) == 2:
        labels = [lbl.lower().strip() for _, lbl in choices]
        labels_set = set(labels)
        
        # Check for momentary label patterns
        momentary_patterns = [
            {"momentary", "released"},
            {"press", "release"},
            {"pressed", "released"},
            {"hold", "release"},
        ]
        
        if labels_set in momentary_patterns:
            return "momentary"
    
    # Return None to use default mode logic
    return None


def parse_controls_from_md(md_body: str) -> tuple[str, dict[str, Any], list[ControlSpec], list[tuple[str, list[ControlSpec]]]]:
    meta, md_no_fm = parse_frontmatter(md_body)
    title, sections = split_sections(md_no_fm)

    all_specs: list[ControlSpec] = []
    by_section_out: list[tuple[str, list[ControlSpec]]] = []

    for sec_title, sec_lines in sections:
        tables = parse_tables(sec_lines)
        specs: list[ControlSpec] = []
        # Track current color for persistence across rows
        current_color: str | None = None
        
        for t in tables:
            for row in t:
                cc_s = pick(row, "Control", "Control (Dec)", "Control (Hex)", "CC", "CC (Dec)", "CC (Hex)", "Hex", contains="cc")
                
                # Check if this is a group definition row
                # New format: group name in CC column (e.g., "grp1")
                # Old format: "Group" in CC column (for backward compatibility)
                group_name: str | None = None
                display_label: str | None = None
                
                if cc_s:
                    cc_clean = cc_s.strip()
                    # Check if it's the old "Group" keyword or a group name (alphanumeric identifier)
                    if cc_clean.lower() == "group":
                        # Old format: use label as both group name and display label
                        label = pick(row, "Label", "Target", "Name")
                        if label:
                            group_name = label
                            display_label = label
                    elif re.match(r"^[A-Za-z_][A-Za-z0-9_ ]*$", cc_clean):
                        # New format: CC column contains group name (identifier, may contain spaces)
                        # Label column contains the display label
                        group_name = cc_clean
                        display_label = pick(row, "Label", "Target", "Name")
                
                if group_name and display_label:
                    # Parse range to get group size (number of controls in top row)
                    r = pick(row, "Range")
                    group_size = 0
                    if r:
                        # Try to parse as a single number
                        m = re.match(r"^(\d+)$", clean_cell(r))
                        if m:
                            group_size = int(m.group(1))
                    
                    # Parse color for the group
                    color_s = pick(row, "Color", "Colour")
                    parsed_color = parse_color(color_s)
                    if parsed_color is not None:
                        current_color = parsed_color
                    
                    # Create a group definition spec
                    specs.append(ControlSpec(
                        section=sec_title,
                        cc=0,  # dummy value
                        label=display_label,  # Display label for the group
                        min_val=0,
                        max_val=0,
                        choices=[],
                        description="",
                        color=current_color,
                        is_blank=False,
                        is_group=True,
                        group_size=group_size,
                        envelope_type=None,
                        msg_type="C",
                        default_value=None,
                        mode=None,
                        group_id=group_name,  # Internal group identifier
                    ))
                    continue
                
                msg_type, cc, device_id = parse_cc(cc_s)
                
                # Check if this is a blank row (no CC and no label)
                label = pick(row, "Label", "Target", "Name")
                
                # Parse explicit group membership from label prefix: "groupname: Label"
                group_id: str | None = None
                if label:
                    m = re.match(r"^([^:]+):\s*(.+)$", label)
                    if m:
                        # Check if this looks like a group name (not a time format like "12:30")
                        potential_group = m.group(1).strip()
                        # Group names should be alphabetic/alphanumeric, not purely numeric
                        if not re.match(r"^\d+$", potential_group):
                            group_id = potential_group
                            label = m.group(2).strip()
                
                # Parse color column first (may be present even in blank rows)
                color_s = pick(row, "Color", "Colour")
                parsed_color = parse_color(color_s)
                # Update current_color if a new color is specified
                if parsed_color is not None:
                    current_color = parsed_color
                
                # If no CC and no label, this is a blank row placeholder
                if cc is None and not label:
                    # Create a blank placeholder to preserve grid position
                    specs.append(ControlSpec(
                        section=sec_title,
                        cc=0,  # dummy value
                        label="",
                        min_val=0,
                        max_val=0,
                        choices=[],
                        description="",
                        color=current_color,
                        is_blank=True,
                        envelope_type=None,
                        msg_type=msg_type,
                        default_value=None,
                        mode=None,
                        group_id=None,
                        device_id=None,
                    ))
                    continue
                
                # Skip rows with no CC (but may have label - these are invalid)
                if cc is None:
                    continue
                    
                # Skip rows with no label (but have CC - these are invalid)
                if not label:
                    continue
                
                r = pick(row, "Range")
                minv, maxv, default_val = parse_range(r)
                
                # If no default value specified, use 0 if in range, otherwise min
                if default_val is None:
                    if minv <= 0 <= maxv:
                        default_val = 0
                    else:
                        default_val = minv
                
                desc = pick(row, "Description", "Range Description", contains="desc")
                choices_s = pick(row, "Choices", "Options", "Option(s)", contains="option")
                
                # Check if this is an envelope control
                envelope_type = None
                if choices_s and choices_s.upper() in ("ADSR", "ADR"):
                    envelope_type = choices_s.upper()
                    choices = []  # Envelope controls don't use choices
                else:
                    choices = parse_choices(choices_s, minv, maxv)
                    # If no explicit choices, try inferring from description (optional)
                    if not choices:
                        choices = infer_choices_from_desc(desc, minv, maxv)
                
                # Infer mode from control characteristics
                mode = infer_mode(minv, maxv, choices)

                specs.append(ControlSpec(
                    section=sec_title,
                    cc=cc,
                    label=label,
                    min_val=minv,
                    max_val=maxv,
                    choices=choices,
                    description=desc,
                    color=current_color,
                    is_blank=False,
                    is_group=False,
                    group_size=0,
                    envelope_type=envelope_type,
                    msg_type=msg_type,
                    default_value=default_val,
                    mode=mode,
                    group_id=group_id,
                    device_id=device_id,
                ))
        if specs:
            by_section_out.append((sec_title, specs))
            all_specs.extend(specs)

    return title, meta, all_specs, by_section_out