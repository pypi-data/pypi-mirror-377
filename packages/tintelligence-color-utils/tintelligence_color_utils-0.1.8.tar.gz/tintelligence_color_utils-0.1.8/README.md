# tintelligence-color-utils

Utility functions for working with colors: conversions, manipulations, family assignment, sorting, and optional Qt helpers.

## Installation

```bash
pip install tintelligence-color-utils
```

### Optional Qt support
If you need `QColor` helpers, install with one of the extras:

- PySide6:
  ```bash
  pip install "tintelligence-color-utils[qt_pyside6]"
  ```
- PyQt6:
  ```bash
  pip install "tintelligence-color-utils[qt_pyqt6]"
  ```

## Quick start

```python
from tintelligence_color_utils import hex_to_hsv, get_color_family
# or
from color_utils import hex_to_hsv, get_color_family

h, s, v = hex_to_hsv("#FF7F00")
print(h, s, v)
print(get_color_family(h, s, v))
```

## API Reference
All functions are available from `color_utils` or `tintelligence_color_utils` top-level import.

### Conversion

#### HEX to RGB

```python
hex_to_rgb(hex_code: str) -> tuple[float, float, float]
```

Convert `#RRGGBB` or `RRGGBB` to an `(r, g, b)` tuple in `[0, 1]`. Raises `ValueError` on invalid input.

#### HEX to HSV

```python
hex_to_hsv(hex_code: str) -> tuple[float, float, float]
```

Convert a hex color to HSV `(h, s, v)` where `h ∈ [0,1]`.

#### Integer RGB to HEX

```python
rgb_to_hex(r: int, g: int, b: int) -> str
```

Convert integer RGB (0-255) to `#RRGGBB`.

#### HEX midpoint

```python
hex_midpoint(c1: str | None, c2: str | None) -> str | None
```

Midpoint between two hex colors as `#RRGGBB`. Returns `None` if inputs are invalid.

#### RGB to LAB

```python
rgb_to_lab(r: int, g: int, b: int) -> tuple[float, float, float]
```

Approximate sRGB (D65) to CIE L*a*b* with `L ∈ [0..100]`.

#### Normalize LAB

```python
normalize_lab(l: float | None, a: float | None, b: float | None) -> tuple[float | None, float | None, float | None]
```

Normalize Lab to `[0,1]` each. `L/100`, and `a,b` via `(v+128)/255` when needed.

#### RGB to HSL

```python
rgb_to_hsl(r: int, g: int, b: int) -> tuple[int, int, int]
```

Convert RGB (0-255) to HSL where `H ∈ [0..360]`, `S,L ∈ [0..100]` (ints).

#### LAB to LCH

```python
lab_to_lch(l: float, a: float, b: float) -> tuple[float, float, float]
```

Convert CIE Lab to LCH(ab) `(L, C, H_deg)`.

#### Get Brigtness from HEX
```python
brightness_from_hex(hex_color: str) -> float | None
```

Perceived brightness (Lab L) from a hex color. Higher means brighter.

### Color families

#### Get color family

```python
get_color_family(hue: float, saturation: float, value: float) -> str
```

Assign a color family based on HSV, with handling for dark and muted tones. Families include e.g. "Black", "Grey", "White / Off-white", "Red", "Pink", "Orange", "Yellow", "Green", "Turquoise / Teal", "Blue", "Purple / Violet", "Brown", "Unknown".

### Shades

#### Get darker shades

```python
get_darker_shades(hex_code: str, steps: int = 2, factor: float = 0.8) -> tuple[str, ...]
```

Generate `steps` darker hex shades by multiplying V by `factor` iteratively.

### Sorting

#### Sort paints by color

```python
sort_paints_by_color(paints: list[dict], mode: str = "hue") -> list[dict]
```

Sort a list of paint dicts by `"hue"`, `"saturation"`, or `"value"`. Expects `hsv_h`, `hsv_s`, `hsv_v` fields.

#### Group paints by color family and sort by hue

```python
sort_paints_by_family_value_hue(
    paints: list[dict],
    order: Literal["bright_to_dark", "dark_to_bright"] = "bright_to_dark",
    color_families: list[dict] | None = None,
) -> list[dict]
```

Group by `color_family_id` (using the provided `color_families` order if given; otherwise numeric id order), then sort by HSV V in the chosen order, tie-breaking by HSV H. Returns items enriched with `_hsv` and `_family` when `color_families` is provided.

#### Group paints by color family and sort by LAB brightness

```python
sort_paints_by_family_lab_brightness(
    paints: list[dict],
    order: Literal["bright_to_dark", "dark_to_bright"] = "bright_to_dark",
    color_families: list[dict] | None = None,
) -> list[dict]
```

Group by `color_family_id` (using the provided `color_families` order if given; otherwise numeric id order), then sort by Lab L in the chosen order, tie-breaking by `hsv_h` if present.

#### Sort HEX colors by brightness

```python
sort_hex_by_brightness(hex_codes: list[str], order: Literal["bright_to_dark", "dark_to_bright"] = "bright_to_dark") -> list[str]
```

Sort a list of hex color codes by perceived brightness (Lab L). Invalid hex codes are placed at the end.

### Qt helper (optional)

#### HEX to QColor

```python
color_utils.qcolor.to_qcolor(color) -> QColor
```

Convert a hex string, `(r, g, b)` tuple, or `QColor` instance to a `QColor`. Requires PySide6, PyQt6, or a `qt_core.QColor` shim. Raises `RuntimeError` if no `QColor` is available.

## Development

- Python 3.9+
- Install dev deps: `pip install -e .[dev]`
- Build: `python -m build`
- Test: `pytest`

## License

MIT
