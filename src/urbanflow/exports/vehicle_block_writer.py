"""Vehicle block export helpers."""

from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Any

import pandas as pd


def build_vehicle_blocks(solution: Dict[str, Any]) -> pd.DataFrame:
    raise NotImplementedError("Vehicle block construction not yet implemented")


def write_vehicle_blocks(solution: Dict[str, Any], out_path: Path) -> None:
    df = build_vehicle_blocks(solution)
    df.to_csv(out_path, index=False)
