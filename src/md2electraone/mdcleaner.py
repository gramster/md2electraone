from typing import Any

from .controlspec import ControlSpec
from .mdutils import clean_cell, pick

# -----------------------------
# Clean Markdown output
# -----------------------------

CANON_HEADERS = ["CC", "Label", "Range", "Choices", "Description"]


def render_table(rows: list[dict[str, str]]) -> str:
    # Build header + divider + rows with consistent pipes
    # Ensure we output canonical columns if present
    cols = CANON_HEADERS
    # Compute widths
    widths = {c: len(c) for c in cols}
    norm_rows: list[dict[str, str]] = []
    for r in rows:
        rr = {c: "" for c in cols}
        # map incoming keys
        cc = pick(r, "CC", "CC (Dec)", "CC (Hex)", "Hex")
        label = pick(r, "Label", "Target", "Name")
        rng = pick(r, "Range")
        choices = pick(r, "Choices", "Options", "Option(s)", contains="option")
        desc = pick(r, "Description", "Range Description", contains="desc")
        rr["CC"] = cc
        rr["Label"] = label
        rr["Range"] = rng
        rr["Choices"] = choices
        rr["Description"] = desc
        for c in cols:
            widths[c] = max(widths[c], len(clean_cell(rr[c])))
        norm_rows.append(rr)

    def fmt_row(rr: dict[str, str]) -> str:
        return "| " + " | ".join(clean_cell(rr[c]).ljust(widths[c]) for c in cols) + " |"

    header = "| " + " | ".join(c.ljust(widths[c]) for c in cols) + " |"
    divider = "| " + " | ".join(("-" * widths[c]) for c in cols) + " |"
    body = "\n".join(fmt_row(rr) for rr in norm_rows)
    return "\n".join([header, divider, body])

def generate_clean_markdown(title: str, meta: dict[str, Any], sections: list[tuple[str, list[ControlSpec]]]) -> str:
    out: list[str] = []
    out.append(f"# {title}")
    out.append("")
    if meta:
        # Write minimal frontmatter back out (stable)
        out.append("---")
        if "manufacturer" in meta:
            out.append(f"manufacturer: {meta['manufacturer']}")
        if "device" in meta:
            out.append(f"device: {meta['device']}")
        if "midi" in meta and isinstance(meta["midi"], dict):
            out.append("midi:")
            for k in ["port", "channel", "rate"]:
                if k in meta["midi"]:
                    out.append(f"  {k}: {meta['midi'][k]}")
        if "electra" in meta and isinstance(meta["electra"], dict):
            out.append("electra:")
            # keep a small subset
            for k in ["cols", "rows", "padding", "top_offset", "left_offset", "right_padding", "screen_width_controls", "cell_width", "cell_height"]:
                if k in meta["electra"]:
                    out.append(f"  {k}: {meta['electra'][k]}")
        out.append("---")
        out.append("")

    for sec_title, specs in sections:
        out.append(f"## {sec_title}")
        out.append("")
        # convert specs back into canonical rows
        rows: list[dict[str, str]] = []
        for s in specs:
            choice_str = ""
            if s.choices:
                # stable "label(value)" format
                choice_str = ", ".join(f"{lbl}({v})" for v, lbl in s.choices)
            rows.append({
                "CC": f"{s.cc}",
                "Label": s.label,
                "Range": f"{s.min_val}-{s.max_val}" if s.min_val != s.max_val else f"{s.min_val}",
                "Choices": choice_str,
                "Description": s.description,
            })
        out.append(render_table(rows))
        out.append("")

    return "\n".join(out).rstrip() + "\n"

