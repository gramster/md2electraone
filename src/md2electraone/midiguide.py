from __future__ import annotations

import csv
import io
import re
from collections import OrderedDict
from typing import Any

from .controlspec import ControlSpec


REQUIRED_COLUMNS = {
    "manufacturer",
    "device",
    "section",
    "parameter_name",
    "parameter_description",
    "cc_msb",
    "cc_lsb",
    "cc_min_value",
    "cc_max_value",
    "cc_default_value",
    "nrpn_msb",
    "nrpn_lsb",
    "nrpn_min_value",
    "nrpn_max_value",
    "nrpn_default_value",
    "orientation",
    "notes",
    "usage",
}


def parse_midiguide_csv(csv_text: str) -> tuple[str, dict[str, Any], list[ControlSpec], list[tuple[str, list[ControlSpec]]]]:
    reader = csv.DictReader(io.StringIO(csv_text))
    if reader.fieldnames is None:
        raise ValueError("CSV is missing a header row")

    reader.fieldnames = [_normalize_header(name) for name in reader.fieldnames]
    missing = REQUIRED_COLUMNS - set(reader.fieldnames)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"CSV is missing required midi.guide columns: {missing_list}")

    manufacturer_name = ""
    device_name = ""
    sections: OrderedDict[str, list[ControlSpec]] = OrderedDict()

    for raw_row in reader:
        row = {_normalize_header(key): (value or "").strip() for key, value in raw_row.items() if key is not None}
        if not any(row.values()):
            continue

        row_manufacturer = row.get("manufacturer", "")
        row_device = row.get("device", "")
        if row_manufacturer:
            if manufacturer_name and manufacturer_name != row_manufacturer:
                raise ValueError("CSV contains more than one manufacturer")
            manufacturer_name = row_manufacturer
        if row_device:
            if device_name and device_name != row_device:
                raise ValueError("CSV contains more than one device")
            device_name = row_device

        label_base = row.get("parameter_name", "")
        if not label_base:
            continue

        section_name = row.get("section", "") or "MAIN"
        usage = row.get("usage", "")
        messages = _extract_messages(row)
        if not messages:
            continue

        # When both CC and NRPN are available, prefer CC and drop the NRPN entry.
        if len(messages) > 1:
            messages = [m for m in messages if m["msg_type"] == "C"][:1]

        allow_choices = _usage_is_discrete(usage)
        for message in messages:
            label = label_base
            specs = sections.setdefault(section_name, [])
            specs.append(
                ControlSpec(
                    section=section_name,
                    cc=message["parameter_number"],
                    label=label,
                    min_val=message["min_value"],
                    max_val=message["max_value"],
                    choices=_usage_to_choices(usage) if allow_choices else [],
                    description=_build_description(row, message["description_note"]),
                    color=None,
                    is_blank=False,
                    envelope_type=None,
                    msg_type=message["msg_type"],
                    default_value=message["default_value"],
                    mode=None,
                    group_id=None,
                    device_id=None,
                )
            )

    title = device_name or "Imported MIDI Guide Device"
    meta: dict[str, Any] = {"name": title}
    if manufacturer_name:
        meta["manufacturer"] = manufacturer_name

    by_section = list(sections.items())
    specs = [spec for _, section_specs in by_section for spec in section_specs]
    return title, meta, specs, by_section


def _normalize_header(name: str) -> str:
    return name.lstrip("\ufeff").strip()


def _parse_int(value: str) -> int | None:
    value = value.strip()
    if not value:
        return None
    return int(value)


def _coalesce_int(*values: str) -> int | None:
    for value in values:
        parsed = _parse_int(value)
        if parsed is not None:
            return parsed
    return None


def _usage_is_discrete(usage: str) -> bool:
    entries = _parse_usage_entries(usage)
    if not entries:
        return False
    return all(entry["kind"] != "continuous" for entry in entries)


def _usage_to_choices(usage: str) -> list[tuple[int, str]]:
    choices: list[tuple[int, str]] = []
    seen_values: set[int] = set()
    for entry in _parse_usage_entries(usage):
        if entry["kind"] == "continuous":
            return []
        value = entry["value"]
        if value in seen_values:
            continue
        seen_values.add(value)
        choices.append((value, entry["label"]))
    return choices


def _parse_usage_entries(usage: str) -> list[dict[str, Any]]:
    pattern = re.compile(r"^(?P<start>-?\d+)(?:(?P<sep>[~-])(?P<end>-?\d+))?$")
    entries: list[dict[str, Any]] = []
    if not usage.strip():
        return entries

    for raw_part in usage.split(";"):
        part = raw_part.strip()
        if not part:
            continue
        if ":" not in part:
            return []
        value_part, label = part.split(":", 1)
        label = label.strip()
        value_part = value_part.strip()

        match = pattern.match(value_part)
        if match is None:
            return []

        start = int(match.group("start"))
        sep = match.group("sep")
        end_text = match.group("end")
        if sep is None or end_text is None:
            entries.append({"kind": "discrete", "value": start, "label": label})
            continue

        end = int(end_text)
        if start == end:
            entries.append({"kind": "discrete", "value": start, "label": label})
        elif sep == "~":
            entries.append({"kind": "continuous", "value": start, "label": label})
        else:
            entries.append({"kind": "equivalent", "value": start, "label": label})
    return entries


def _build_description(row: dict[str, str], message_note: str | None) -> str:
    parts: list[str] = []
    description = row.get("parameter_description", "")
    notes = row.get("notes", "")
    orientation = row.get("orientation", "")
    usage = row.get("usage", "")

    if description:
        parts.append(description)
    if notes:
        parts.append(f"Notes: {notes}")
    if message_note:
        parts.append(message_note)
    if orientation and orientation != "0-based":
        parts.append(f"Orientation: {orientation}")
    if usage:
        parts.append(f"Usage: {usage}")
    return " ".join(parts)


def _extract_messages(row: dict[str, str]) -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = []

    cc_msb = _parse_int(row.get("cc_msb", ""))
    cc_lsb = _parse_int(row.get("cc_lsb", ""))
    if cc_msb is not None:
        note = None
        if cc_lsb is not None and cc_lsb != cc_msb + 32:
            note = f"Imported as best-effort CC14 from CC MSB {cc_msb}; source CSV specifies non-standard CC LSB {cc_lsb}."
        messages.append(
            {
                "msg_type": "C",
                "label_suffix": "CC",
                "parameter_number": cc_msb,
                "min_value": _coalesce_int(row.get("cc_min_value", ""), "0") or 0,
                "max_value": _coalesce_int(row.get("cc_max_value", ""), "16383" if cc_lsb is not None else "127") or 127,
                "default_value": _default_value(
                    row.get("cc_default_value", ""),
                    _coalesce_int(row.get("cc_min_value", ""), "0") or 0,
                    _coalesce_int(row.get("cc_max_value", ""), "16383" if cc_lsb is not None else "127") or 127,
                ),
                "description_note": note,
            }
        )

    nrpn_msb = _parse_int(row.get("nrpn_msb", ""))
    nrpn_lsb = _parse_int(row.get("nrpn_lsb", ""))
    if nrpn_msb is not None or nrpn_lsb is not None:
        if nrpn_msb is None:
            parameter_number = nrpn_lsb or 0
            note = "Imported NRPN with only LSB specified in source CSV."
        elif nrpn_lsb is None:
            parameter_number = nrpn_msb
            note = "Imported NRPN with only MSB specified in source CSV."
        else:
            parameter_number = (nrpn_msb * 128) + nrpn_lsb
            note = None

        messages.append(
            {
                "msg_type": "N",
                "label_suffix": "NRPN",
                "parameter_number": parameter_number,
                "min_value": _coalesce_int(row.get("nrpn_min_value", ""), "0") or 0,
                "max_value": _coalesce_int(row.get("nrpn_max_value", ""), "16383") or 16383,
                "default_value": _default_value(
                    row.get("nrpn_default_value", ""),
                    _coalesce_int(row.get("nrpn_min_value", ""), "0") or 0,
                    _coalesce_int(row.get("nrpn_max_value", ""), "16383") or 16383,
                ),
                "description_note": note,
            }
        )

    return messages


def _default_value(raw_value: str, min_value: int, max_value: int) -> int:
    parsed = _parse_int(raw_value)
    if parsed is not None:
        return parsed
    if min_value <= 0 <= max_value:
        return 0
    return min_value