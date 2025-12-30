import dataclasses


@dataclasses.dataclass
class ControlSpec:
    section: str
    cc: int
    label: str
    min_val: int
    max_val: int
    choices: list[tuple[int, str]]  # (value, label)
    description: str
    color: str | None = None  # 6-character hex RGB (e.g., "F45C51")
    is_blank: bool = False  # True if this is a placeholder for a blank row
