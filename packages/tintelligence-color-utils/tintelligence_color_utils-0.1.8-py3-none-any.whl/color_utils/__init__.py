"""Compatibility shim for legacy import path `color_utils`.

Re-exports the public API from `tintelligence_color_utils` to preserve
backwards compatibility with existing code and tests.
"""

from __future__ import annotations

from tintelligence_color_utils import *  # noqa: F401,F403
from tintelligence_color_utils import __version__  # re-export version
