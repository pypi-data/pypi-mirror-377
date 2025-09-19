"""Color families data loader.

Loads color family definitions from src/color_families.json and exposes
ordered lists and helper mappings for reuse across modules.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


def _load_color_families() -> List[Dict]:
    root = Path(__file__).resolve().parents[1]
    data_path = root / "color_families.json"
    with data_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("color_families.json must contain a list")
    return data


COLOR_FAMILIES: List[Dict] = _load_color_families()
COLOR_FAMILY_ID_ORDER: List[int] = [item["id"] for item in COLOR_FAMILIES]
COLOR_FAMILY_ID_TO_NAME: Dict[int, str] = {
    item["id"]: item["name"] for item in COLOR_FAMILIES
}
