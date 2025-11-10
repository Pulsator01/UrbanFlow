from __future__ import annotations

from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd


def generate_synthetic_demand(canonical: Dict[str, pd.DataFrame], seed: int | None = None) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    stops = canonical["stops"]
    n = len(stops)
    # simple origin weight proportional to 1, destination proportional to 1,
    # then reduce diagonal to avoid self-travel
    base = rng.random((n, n))
    np.fill_diagonal(base, 0.0)
    # sparsify
    mask = rng.random((n, n)) < 0.1
    od = base * mask
    # normalize to daily total demand ~ n*10
    total = od.sum()
    if total > 0:
        od = od * (n * 10.0 / total)
    df = pd.DataFrame(od, index=stops["stop_id"], columns=stops["stop_id"])
    return df


