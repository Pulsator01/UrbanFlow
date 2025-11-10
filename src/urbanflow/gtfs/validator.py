"""GTFS validation routines."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import pandas as pd

from ..logging_utils import get_logger
from ..exceptions import ValidationError

logger = get_logger(__name__)


def validate_feed(tables: Dict[str, pd.DataFrame]) -> Dict[str, List[str]]:
    """Perform validation checks and return report."""

    raise NotImplementedError("Validation not yet implemented")


def validate_from_zip(zip_path: Path) -> Dict[str, List[str]]:
    tables = read_and_canonicalize(zip_path)
    return validate_feed(tables)


def read_and_canonicalize(zip_path: Path) -> Dict[str, pd.DataFrame]:
    raise NotImplementedError("Read and canonicalize not yet implemented")
