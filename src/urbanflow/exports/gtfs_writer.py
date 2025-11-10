"""Write optimized GTFS-like outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd


def write_gtfs_like(outputs: Dict[str, pd.DataFrame], out_dir: Path) -> None:
    raise NotImplementedError("GTFS writer not yet implemented")
