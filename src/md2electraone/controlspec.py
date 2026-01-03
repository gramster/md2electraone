import dataclasses


@dataclasses.dataclass
class ControlSpec:
    section: str
    cc: int | list[int]  # Single CC or list of CCs for envelope controls
    label: str
    min_val: int
    max_val: int
    choices: list[tuple[int, str]]  # (value, label)
    description: str
    color: str | None = None  # 6-character hex RGB (e.g., "F45C51")
    is_blank: bool = False  # True if this is a placeholder for a blank row
    envelope_type: str | None = None  # "ADSR" or "ADR" for envelope controls
    msg_type: str = "C"  # "C" for CC (default), "N" for NRPN, "P" for Program, "S" for SysEx (future)
    default_value: int | None = None  # Default/initial value for the control
    mode: str | None = None  # Control mode: "default", "unipolar", "bipolar", "momentary", "toggle"
    is_group: bool = False  # True if this is a group definition row
    group_size: int = 0  # For group rows: number of contiguous controls in the top row of the group
    group_id: str | None = None  # For group rows: internal group identifier; For controls: explicit group membership via "<groupname>:" prefix
    device_id: int | None = None  # Device index (1-based) for multi-device presets
