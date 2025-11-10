"""GTFS parsing utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd

from ..logging_utils import get_logger

logger = get_logger(__name__)


def read_gtfs(zip_path: Path) -> Dict[str, pd.DataFrame]:
    """Read a GTFS zip into dataframes."""

    raise NotImplementedError("GTFS parsing not yet implemented")
