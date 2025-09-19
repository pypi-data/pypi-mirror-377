"""Color space conversion utilities."""

from __future__ import annotations

import colorsys
import math
from typing import Optional, Tuple


def hex_to_rgb(hex_code: str) -> Tuple[float, float, float]:
    """Convert #RRGGBB or RRGGBB to RGB tuple in [0,1].

    Raises ValueError on invalid input.
    """
    s = hex_code.lstrip("#").strip()
    if len(s) != 6:
        raise ValueError(f"Invalid hex color: {hex_code}")
    try:
        return tuple(int(s[i : i + 2], 16) / 255.0 for i in (0, 2, 4))  # type: ignore[return-value]
    except ValueError as exc:
        raise ValueError(f"Invalid hex color: {hex_code}") from exc


def hex_to_hsv(hex_code: str) -> Tuple[float, float, float]:
    """Convert a hex color code to HSV tuple (h, s, v), with h in [0, 1]."""
    rgb = hex_to_rgb(hex_code)
    return colorsys.rgb_to_hsv(*rgb)


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert integer RGB (0-255) to #RRGGBB."""
    r = max(0, min(255, int(r)))
    g = max(0, min(255, int(g)))
    b = max(0, min(255, int(b)))
    return f"#{r:02X}{g:02X}{b:02X}"


def rgb_to_xyz(r: float, g: float, b: float) -> tuple[float, float, float]:
    """
    Convert normalized RGB (0-1) to CIE XYZ (D65).
    """

    def pivot_rgb(c):
        return ((c + 0.055) / 1.055) ** 2.4 if c > 0.04045 else c / 12.92

    r, g, b = pivot_rgb(r), pivot_rgb(g), pivot_rgb(b)
    r *= 100
    g *= 100
    b *= 100

    # sRGB D65
    x = r * 0.4124 + g * 0.3576 + b * 0.1805
    y = r * 0.2126 + g * 0.7152 + b * 0.0722
    z = r * 0.0193 + g * 0.1192 + b * 0.9505
    return x, y, z


def xyz_to_lab(x: float, y: float, z: float) -> tuple[float, float, float]:
    """
    Convert CIE XYZ to CIE Lab (D65).
    """
    # Reference white (D65)
    ref_x, ref_y, ref_z = 95.047, 100.000, 108.883
    x, y, z = x / ref_x, y / ref_y, z / ref_z

    def pivot_xyz(c):
        return c ** (1 / 3) if c > 0.008856 else (7.787 * c) + (16 / 116)

    x, y, z = pivot_xyz(x), pivot_xyz(y), pivot_xyz(z)

    l = (116 * y) - 16
    a = 500 * (x - y)
    b = 200 * (y - z)
    return l, a, b


def hex_midpoint(c1: Optional[str], c2: Optional[str]) -> Optional[str]:
    """Midpoint of two hex colors as #RRGGBB. Returns None if invalid input."""
    if not c1 or not c2:
        return None
    try:
        r1, g1, b1 = (int(x * 255) for x in hex_to_rgb(c1))
        r2, g2, b2 = (int(x * 255) for x in hex_to_rgb(c2))
    except ValueError:
        return None
    r = (r1 + r2) // 2
    g = (g1 + g2) // 2
    b = (b1 + b2) // 2
    return rgb_to_hex(r, g, b)


def rgb_to_lab(r: float, g: float, b: float) -> tuple[float, float, float]:
    """
    Convert normalized RGB (0-1) to Lab (L* in 0-100).
    """
    x, y, z = rgb_to_xyz(r, g, b)
    return xyz_to_lab(x, y, z)


def lab_to_lch(l: float, a: float, b: float) -> tuple[float, float, float]:
    """
    Convert Lab to LCH (L in 0-100, C >=0, H in degrees).
    """
    c = math.sqrt(a * a + b * b)
    h = math.degrees(math.atan2(b, a)) if c > 1e-6 else 0.0
    if h < 0:
        h += 360
    return l, c, h


def normalize_lab(
    l_value: Optional[float], a_value: Optional[float], b_value: Optional[float]
) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """Normalize Lab to 0..1 each. L in 0..100 -> /100; a,b in ~[-128,127] -> (v+128)/255."""

    def norm_l(v: Optional[float]) -> Optional[float]:
        if v is None:
            return None
        # if already normalized, keep within [0,1]; else divide by 100 and cap
        vv = v if v <= 1.0 else v / 100.0
        return min(1.0, max(0.0, vv))

    def norm_ab(v: Optional[float]) -> Optional[float]:
        if v is None:
            return None
        if 0.0 <= v <= 1.0:
            return v
        return (v + 128.0) / 255.0

    return norm_l(l_value), norm_ab(a_value), norm_ab(b_value)


def rgb255_to_hsl_percent(r: int, g: int, b: int) -> Tuple[int, int, int]:
    """Convert RGB (0-255) to HSL where H in 0..360, S,L in 0..100 (ints)."""
    rs, gs, bs = r / 255.0, g / 255.0, b / 255.0
    cmax, cmin = max(rs, gs, bs), min(rs, gs, bs)
    delta = cmax - cmin
    if delta == 0:
        h = 0
    elif cmax == rs:
        h = 60 * (((gs - bs) / delta) % 6)
    elif cmax == gs:
        h = 60 * (((bs - rs) / delta) + 2)
    else:
        h = 60 * (((rs - gs) / delta) + 4)
    l = (cmax - cmin) / 2 + cmin
    if delta == 0:
        s = 0
    else:
        s = delta / (1 - abs(2 * l - 1))
    return int(round(h) % 360), int(round(s * 100)), int(round(l * 100))


def rgb01_to_hsl(r: float, g: float, b: float) -> tuple[float, float, float]:
    """
    Convert normalized RGB (0-1) to HSL.
    """
    maxc = max(r, g, b)
    minc = min(r, g, b)
    l = (minc + maxc) / 2.0
    if minc == maxc:
        return 0.0, 0.0, l
    if l <= 0.5:
        s = (maxc - minc) / (maxc + minc)
    else:
        s = (maxc - minc) / (2.0 - maxc - minc)
    rc = (maxc - r) / (maxc - minc)
    gc = (maxc - g) / (maxc - minc)
    bc = (maxc - b) / (maxc - minc)
    if r == maxc:
        h = bc - gc
    elif g == maxc:
        h = 2.0 + rc - bc
    else:
        h = 4.0 + gc - rc
    h = (h / 6.0) % 1.0
    return h * 360.0, s, l


def brightness_from_hex(hex_color: str) -> Optional[float]:
    """Perceived brightness (Lab L) from a hex color. Higher means brighter."""
    try:
        r, g, b = (int(x * 255) for x in hex_to_rgb(hex_color))
    except ValueError:
        return None
    l_value, _a, _b = rgb_to_lab(r, g, b)
    return l_value
