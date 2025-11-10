"""Folium visualization helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import folium


def build_before_after_map(before_geojson: Dict, after_geojson: Dict, out_path: Path) -> None:
    raise NotImplementedError("Map generation not yet implemented")
