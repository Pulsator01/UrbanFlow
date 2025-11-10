"""Passenger demand modeling utilities."""

from __future__ import annotations

from typing import Dict, Optional

import pandas as pd


def build_synthetic_od(
    tables: Dict[str, pd.DataFrame],
    params: Optional[Dict[str, float]] = None,
) -> pd.DataFrame:
    raise NotImplementedError("OD generation not yet implemented")
