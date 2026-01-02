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
    msg_type: str = "C"  # "C" for CC (default), "N" for NRPN, "S" for SysEx (future)
    default_value: int | None = None  # Default/initial value for the control
    mode: str | None = None  # Control mode: "default", "unipolar", "bipolar", "momentary", "toggle"
