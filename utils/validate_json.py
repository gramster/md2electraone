#!/usr/bin/env python3
"""
Electra One layout diagnostics

Usage:
  python electra_layout_diag.py <preset.json> [--include-cross-type-overlaps]
                                [--overlaps-across-pages] [--max-overlap-report N]
                                [--show-all-elements]

What it does:
- Prints a per-element table for groups + controls: id, pageId, label, bounds, (row,col)
- Validates global numeric ID uniqueness across the whole JSON tree
- Validates bounding box disjointness (default: within same page only)
- Emits summary stats + grid diagnostics
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Iterable, DefaultDict
from collections import defaultdict


@dataclass(frozen=True)
class Elem:
    kind: str          # "group" or "control"
    id: int
    page_id: Optional[int]
    name: str
    bounds: Tuple[int, int, int, int]  # x,y,w,h
    path: str          # JSON path for debugging


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def iter_numeric_ids(obj: Any, path: str = "$") -> Iterable[Tuple[int, str]]:
    """
    Traverse the JSON tree and yield (id_value, path_to_id) for every numeric 'id' field.
    This catches collisions across pages/devices/groups/controls/etc.
    """
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}"
            if k == "id" and isinstance(v, int):
                yield (v, p)
            yield from iter_numeric_ids(v, p)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from iter_numeric_ids(v, f"{path}[{i}]")
    # primitives ignored


def extract_elems(data: Dict[str, Any]) -> List[Elem]:
    elems: List[Elem] = []

    def add(kind: str, item: Dict[str, Any], idx: int) -> None:
        if "id" not in item or not isinstance(item["id"], int):
            return
        b = item.get("bounds")
        if not (isinstance(b, list) and len(b) == 4 and all(isinstance(n, int) for n in b)):
            return
        name = str(item.get("name", ""))
        page_id = item.get("pageId")
        if not isinstance(page_id, int):
            page_id = None
        elems.append(
            Elem(
                kind=kind,
                id=item["id"],
                page_id=page_id,
                name=name,
                bounds=(b[0], b[1], b[2], b[3]),
                path=f"$.{kind}s[{idx}]",
            )
        )

    for i, g in enumerate(data.get("groups", []) if isinstance(data.get("groups"), list) else []):
        if isinstance(g, dict):
            add("group", g, i)

    for i, c in enumerate(data.get("controls", []) if isinstance(data.get("controls"), list) else []):
        if isinstance(c, dict):
            add("control", c, i)

    return elems


def rect_intersect(a: Tuple[int,int,int,int], b: Tuple[int,int,int,int]) -> bool:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    # Treat touching edges as NON-overlapping (common UI convention).
    return not (ax + aw <= bx or bx + bw <= ax or ay + ah <= by or by + bh <= ay)


def build_grid(values: List[int], target: int = 6) -> List[int]:
    """
    Build a sorted list of representative grid positions from observed values.
    If <= target unique values: return them.
    If > target: compress by picking evenly spaced quantiles of the unique sorted list.
    """
    uniq = sorted(set(values))
    if len(uniq) <= target:
        return uniq
    # choose target quantile anchors
    grid = []
    for i in range(target):
        # i in [0..target-1]
        q = i / (target - 1) if target > 1 else 0
        idx = int(round(q * (len(uniq) - 1)))
        grid.append(uniq[idx])
    # ensure strictly non-decreasing unique-ish
    return sorted(set(grid))


def nearest_index(grid: List[int], v: int) -> int:
    """
    Return 1-based index of the nearest grid value.
    If grid is empty, return 0.
    """
    if not grid:
        return 0
    best_i = 0
    best_d = abs(v - grid[0])
    for i in range(1, len(grid)):
        d = abs(v - grid[i])
        if d < best_d:
            best_d = d
            best_i = i
    return best_i + 1


def format_bounds(b: Tuple[int,int,int,int]) -> str:
    return f"[{b[0]},{b[1]},{b[2]},{b[3]}]"


def summarize_extents(elems: List[Elem]) -> Dict[str, Any]:
    xs = [e.bounds[0] for e in elems]
    ys = [e.bounds[1] for e in elems]
    rights = [e.bounds[0] + e.bounds[2] for e in elems]
    bottoms = [e.bounds[1] + e.bounds[3] for e in elems]

    return {
        "min_x": min(xs) if xs else None,
        "min_y": min(ys) if ys else None,
        "max_x": max(xs) if xs else None,
        "max_y": max(ys) if ys else None,
        "max_x_plus_w": max(rights) if rights else None,
        "max_y_plus_h": max(bottoms) if bottoms else None,
    }


def longest_label(elems: List[Elem]) -> Tuple[str, int, Optional[int], str]:
    # returns (label, length, id, kind)
    best = ("", 0, None, "")
    for e in elems:
        if len(e.name) > best[1]:
            best = (e.name, len(e.name), e.id, e.kind)
    return best


def validate_id_uniqueness(data: Dict[str, Any]) -> List[str]:
    seen: Dict[int, List[str]] = defaultdict(list)
    for idv, p in iter_numeric_ids(data):
        seen[idv].append(p)

    problems = []
    for idv, paths in sorted(seen.items()):
        if len(paths) > 1:
            problems.append(f"ID COLLISION: id={idv} appears {len(paths)} times:\n  " + "\n  ".join(paths))
    return problems


def find_overlaps(
    elems: List[Elem],
    include_cross_type: bool,
    overlaps_across_pages: bool,
    max_report: int,
) -> List[str]:
    overlaps: List[str] = []

    # group elems by page if we only check within page
    if overlaps_across_pages:
        buckets = {"ALL": elems}
    else:
        buckets: Dict[str, List[Elem]] = defaultdict(list)
        for e in elems:
            buckets[str(e.page_id)].append(e)

    for bucket_name, bucket in buckets.items():
        # naive O(n^2) is fine for typical preset sizes
        n = len(bucket)
        for i in range(n):
            for j in range(i + 1, n):
                a, b = bucket[i], bucket[j]

                if not include_cross_type and a.kind != b.kind:
                    continue

                if rect_intersect(a.bounds, b.bounds):
                    overlaps.append(
                        f"OVERLAP ({'page='+bucket_name if not overlaps_across_pages else 'across-pages'}): "
                        f"{a.kind} id={a.id} '{a.name}' {format_bounds(a.bounds)} "
                        f"<-> {b.kind} id={b.id} '{b.name}' {format_bounds(b.bounds)}"
                    )
                    if len(overlaps) >= max_report:
                        return overlaps
    return overlaps


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("json_file", type=Path)
    ap.add_argument("--include-cross-type-overlaps", action="store_true",
                    help="Also check group<->control overlaps. Default checks within same kind only.")
    ap.add_argument("--overlaps-across-pages", action="store_true",
                    help="Check overlaps across different pages too. Default is within each page only.")
    ap.add_argument("--max-overlap-report", type=int, default=50,
                    help="Max number of overlaps to print.")
    ap.add_argument("--show-all-elements", action="store_true",
                    help="Print full element listing (otherwise prints a compact listing).")
    args = ap.parse_args()

    data = load_json(args.json_file)
    elems = extract_elems(data)

    groups = [e for e in elems if e.kind == "group"]
    controls = [e for e in elems if e.kind == "control"]

    # Build separate grids for groups/controls (usually what you want for Electra)
    group_x_grid = build_grid([e.bounds[0] for e in groups], 6)
    group_y_grid = build_grid([e.bounds[1] for e in groups], 6)
    control_x_grid = build_grid([e.bounds[0] for e in controls], 6)
    control_y_grid = build_grid([e.bounds[1] for e in controls], 6)

    # Also build an overall grid (sometimes useful if group+control share a coordinate system)
    all_x_grid = build_grid([e.bounds[0] for e in elems], 6)
    all_y_grid = build_grid([e.bounds[1] for e in elems], 6)

    # Summary
    print(f"FILE: {args.json_file}")
    print(f"Elements: groups={len(groups)}, controls={len(controls)}")
    print()

    print("GRID (groups):")
    print(f"  x_grid={group_x_grid}")
    print(f"  y_grid={group_y_grid}")
    print("GRID (controls):")
    print(f"  x_grid={control_x_grid}")
    print(f"  y_grid={control_y_grid}")
    print("GRID (overall):")
    print(f"  x_grid={all_x_grid}")
    print(f"  y_grid={all_y_grid}")
    print()

    # Extents
    ext = summarize_extents(elems)
    print("EXTENTS (across groups+controls):")
    print(f"  min x={ext['min_x']}, min y={ext['min_y']}")
    print(f"  max x={ext['max_x']}, max y={ext['max_y']}")
    print(f"  max (x+w)={ext['max_x_plus_w']}, max (y+h)={ext['max_y_plus_h']}")
    print()

    lbl, ln, best_id, best_kind = longest_label(elems)
    print("LONGEST LABEL:")
    print(f"  len={ln}  kind={best_kind}  id={best_id}  label={lbl!r}")
    print()

    # ID uniqueness across the whole JSON tree
    id_problems = validate_id_uniqueness(data)
    if id_problems:
        print("ID UNIQUENESS: FAIL")
        for p in id_problems:
            print(p)
    else:
        print("ID UNIQUENESS: OK")
    print()

    # Overlaps
    overlaps = find_overlaps(
        elems,
        include_cross_type=args.include_cross_type_overlaps,
        overlaps_across_pages=args.overlaps_across_pages,
        max_report=args.max_overlap_report,
    )
    if overlaps:
        print(f"BOUNDS DISJOINTNESS: FAIL  (showing up to {args.max_overlap_report})")
        for o in overlaps:
            print(o)
    else:
        print("BOUNDS DISJOINTNESS: OK")
    print()

    # Element listing
    def rowcol(e: Elem) -> Tuple[int, int, int, int]:
        # Use type-specific grids; fall back to overall if missing
        if e.kind == "group":
            gx = group_x_grid or all_x_grid
            gy = group_y_grid or all_y_grid
        else:
            gx = control_x_grid or all_x_grid
            gy = control_y_grid or all_y_grid

        col = nearest_index(gx, e.bounds[0])
        row = nearest_index(gy, e.bounds[1])
        # also show "distance" to nearest for diagnosing drift
        dx = min((abs(e.bounds[0] - v) for v in gx), default=0)
        dy = min((abs(e.bounds[1] - v) for v in gy), default=0)
        return row, col, dx, dy

    # Sort in a stable, editor-like way: page, y, x, kind, id
    elems_sorted = sorted(
        elems,
        key=lambda e: (e.page_id if e.page_id is not None else 10**9, e.bounds[1], e.bounds[0], e.kind, e.id),
    )

    print("ELEMENTS (groups + controls):")
    print("  kind   id    page  (r,c)  dxy   name                          bounds")
    print("  -----  ----  ----  -----  ----  ----------------------------  ----------------")
    for e in elems_sorted:
        r, c, dx, dy = rowcol(e)
        name = (e.name if e.name else "<BLANK>").replace("\n", " ")
        name_disp = (name[:28] + "…") if len(name) > 29 else name
        print(f"  {e.kind:<5}  {e.id:>4}  {str(e.page_id):>4}  ({r},{c})  {dx:>2},{dy:<2}  {name_disp:<28}  {format_bounds(e.bounds)}")

        if args.show_all_elements:
            # show JSON path if requested
            print(f"        path={e.path}")

    print()
    # Additional diagnostics: off-grid elements (non-zero dx/dy)
    off = []
    for e in elems_sorted:
        r, c, dx, dy = rowcol(e)
        if dx != 0 or dy != 0:
            off.append((dx + dy, dx, dy, e))
    if off:
        off.sort(key=lambda t: (t[0], t[1], t[2]))
        print("OFF-GRID (non-zero distance to nearest gridline):")
        for total, dx, dy, e in off[:50]:
            print(f"  {e.kind} id={e.id} page={e.page_id} name={e.name!r} bounds={format_bounds(e.bounds)}  dx={dx} dy={dy}")
        if len(off) > 50:
            print(f"  ... {len(off)-50} more")
    else:
        print("OFF-GRID: none (all x/y match inferred grid values exactly)")

    # Duplicate labels (sometimes editor merges/behaves oddly if name collisions exist)
    name_map: DefaultDict[Tuple[str, Optional[int]], List[Elem]] = defaultdict(list)
    for e in elems:
        name_map[(e.name.strip(), e.page_id)].append(e)

    dups = [(k, v) for k, v in name_map.items() if k[0] and len(v) > 1]
    if dups:
        print()
        print("DUPLICATE LABELS (same page, same trimmed name):")
        for (nm, pid), items in sorted(dups, key=lambda t: (t[0][1] if t[0][1] is not None else 10**9, t[0][0])):
            ids = ", ".join(str(it.id) for it in sorted(items, key=lambda x: x.id))
            print(f"  page={pid} name={nm!r} ids=[{ids}]")

    print("\nDone.")


if __name__ == "__main__":
    main()


