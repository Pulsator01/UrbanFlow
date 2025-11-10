"""Canonicalization of GTFS tables."""

from __future__ import annotations

from typing import Dict

import pandas as pd


def canonicalize(tables: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    raise NotImplementedError("Canonicalization not yet implemented")
