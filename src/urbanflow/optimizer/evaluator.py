"""KPI evaluation and simulation."""

from __future__ import annotations

from typing import Any, Dict, Tuple

import pandas as pd


def compute_kpis(
    graph: Any,
    demand: pd.DataFrame,
    sample_size: int,
    seed: int | None = None,
) -> Dict[str, float]:
    raise NotImplementedError("KPI computation not yet implemented")


def evaluate_move(
    solution: Dict[str, Any],
    move: Dict[str, Any],
    constraints: Dict[str, Any],
    sample_size: int,
    seed: int | None = None,
) -> Tuple[Dict[str, float], Dict[str, Any]]:
    raise NotImplementedError("Move evaluation not yet implemented")
