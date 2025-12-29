import re


def norm_key(s: str) -> str:
    return re.sub(r"\s+", " ", clean_cell(s).lower())


def pick(row: dict[str, str], *keys: str, contains: str | None = None) -> str:
    norm = {norm_key(k): k for k in row.keys()}
    for k in keys:
        kk = norm_key(k)
        if kk in norm:
            v = clean_cell(row.get(norm[kk], ""))
            if v:
                return v
    if contains:
        c = norm_key(contains)
        for k in row.keys():
            if c in norm_key(k):
                v = clean_cell(row.get(k, ""))
                if v:
                    return v
    return ""



def clean_cell(s: str) -> str:
    s = (s or "").strip()
    # strip common markdown wrappers
    s = re.sub(r"^\*+|\*+$", "", s).strip()
    s = re.sub(r"^`+|`+$", "", s).strip()
    return s


