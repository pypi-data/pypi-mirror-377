"""Utilities for sorting paint dictionaries by color properties or family."""

from __future__ import annotations

from typing import Dict, List, Literal, Optional

from .conversion import brightness_from_hex


def _build_family_index(color_families: Optional[List[Dict]]) -> Dict[int, int]:
    """Return mapping from family_id to order index.

    If color_families is None, default to numeric sort order based on family_id.
    """
    if color_families:
        return {item["id"]: idx for idx, item in enumerate(color_families)}
    # Fallback: compute order from ids encountered, sorted ascending
    return {}


def sort_paints_by_color(paints: List[Dict], mode: str = "hue") -> List[Dict]:
    """Sort a list of paint dictionaries by color property (hue, saturation, or value)."""
    if mode not in {"hue", "saturation", "value"}:
        raise ValueError("mode must be 'hue', 'saturation', or 'value'")

    def get_sort_key(paint: Dict):
        h = paint.get("hsv_h")
        s = paint.get("hsv_s")
        v = paint.get("hsv_v")
        if h is None or s is None or v is None:
            raise KeyError("paint must contain 'hsv_h', 'hsv_s', 'hsv_v'")
        return {"hue": h, "saturation": s, "value": v}[mode]

    return sorted(paints, key=get_sort_key)


def sort_paints_by_family_value_hue(
    paints: List[Dict],
    order: Literal["bright_to_dark", "dark_to_bright"] = "bright_to_dark",
    color_families: Optional[List[Dict]] = None,
) -> List[Dict]:
    """Group by color family id, then sort by HSV value and hue.

    - Primary grouping: `color_family_id` using provided `color_families` order. If not provided,
      family ids are grouped by their numeric value ascending.
    - Secondary sort: HSV V (value) by `order`
    - Tertiary sort: HSV H (hue) ascending

    Expects paints to have `color_family_id`, `hsv_h`, `hsv_s`, `hsv_v`.
    Enriches each item with `_hsv` and `_family` if `color_families` provided.
    """
    id_to_index = _build_family_index(color_families)
    value_sign = -1 if order == "bright_to_dark" else 1

    enriched_paints: List[Dict] = []
    for paint in paints:
        fam_id = paint.get("color_family_id")
        h = paint.get("hsv_h")
        s = paint.get("hsv_s")
        v = paint.get("hsv_v")
        if fam_id is None:
            raise KeyError("paint must contain 'color_family_id'")
        if h is None or s is None or v is None:
            raise KeyError("paint must contain 'hsv_h', 'hsv_s', 'hsv_v'")
        if color_families:
            name_map = {
                cf["id"]: cf.get("name", str(cf["id"])) for cf in color_families
            }
            enriched_paints.append(
                {**paint, "_hsv": (h, s, v), "_family": name_map.get(fam_id, "Unknown")}
            )
        else:
            enriched_paints.append(paint)

    def fam_index(pid: int) -> int:
        if id_to_index:
            return id_to_index.get(pid, len(id_to_index))
        return pid  # numeric order if no families provided

    def sort_key(p: Dict):
        return (
            fam_index(p["color_family_id"]),
            value_sign * p["hsv_v"],
            p["hsv_h"],
        )

    return sorted(enriched_paints, key=sort_key)


def sort_paints_by_family_lab_brightness(
    paints: List[Dict],
    order: Literal["bright_to_dark", "dark_to_bright"] = "bright_to_dark",
    color_families: Optional[List[Dict]] = None,
) -> List[Dict]:
    """Group by color family id, then sort by Lab L within each family.

    - Primary grouping: `color_family_id` using provided `color_families` order. If not provided,
      family ids are grouped by their numeric value ascending.
    - Secondary sort: Lab L (`lab_l`) in the specified order
    - Tertiary tie-breaker: hue (`hsv_h`) ascending if present, else 0

    Required fields: `color_family_id`, `lab_l`
    Optional: `hsv_h` (used only as stable tie-breaker)
    """
    id_to_index = _build_family_index(color_families)
    brightness_sign = -1 if order == "bright_to_dark" else 1

    enriched = []
    for paint in paints:
        fam_id = paint.get("color_family_id")
        l = paint.get("lab_l")
        if fam_id is None:
            raise KeyError("paint must contain 'color_family_id'")
        if l is None:
            raise KeyError("paint must contain 'lab_l'")
        enriched.append(paint)

    def fam_index(pid: int) -> int:
        if id_to_index:
            return id_to_index.get(pid, len(id_to_index))
        return pid

    def sort_key(p: Dict):
        hue = p.get("hsv_h") or 0.0
        return (
            fam_index(p["color_family_id"]),
            brightness_sign * p["lab_l"],
            hue,
        )

    return sorted(enriched, key=sort_key)


def sort_hex_by_brightness(
    hex_codes: List[str],
    order: Literal["bright_to_dark", "dark_to_bright"] = "bright_to_dark",
) -> List[str]:
    """Return hex codes sorted by perceived brightness (Lab L).

    Invalid hex codes are ranked last regardless of order.
    """
    brightness_sign = -1 if order == "bright_to_dark" else 1

    def key_fn(code: str):
        l = brightness_from_hex(code)
        return (
            1 if l is None else 0,  # invalids at the end
            brightness_sign * (l or 0.0),
        )

    return sorted(hex_codes, key=key_fn)
