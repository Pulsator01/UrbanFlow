"""Synthetic AVL data generation."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

import pandas as pd


def generate_synthetic_avl(
    tables: Dict[str, pd.DataFrame],
    params: Optional[Dict[str, float]] = None,
) -> pd.DataFrame:
    raise NotImplementedError("Synthetic AVL generation not yet implemented")


def generate_to_csv(
    tables: Dict[str, pd.DataFrame],
    out_path: Path,
    params: Optional[Dict[str, float]] = None,
) -> None:
    df = generate_synthetic_avl(tables, params)
    df.to_csv(out_path, index=False)
