from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional
from pathlib import Path
import io
import zipfile

import pandas as pd


REQUIRED_FILES = [
    "stops.txt",
    "routes.txt",
    "trips.txt",
    "stop_times.txt",
]

OPTIONAL_FILES = [
    "agency.txt",
    "calendar.txt",
    "calendar_dates.txt",
    "shapes.txt",
    "frequencies.txt",
    "transfers.txt",
]


def _read_csv_from_zip(zf: zipfile.ZipFile, member: str) -> Optional[pd.DataFrame]:
    try:
        with zf.open(member) as f:
            # pandas infers types; keep strings where necessary
            return pd.read_csv(io.TextIOWrapper(f, encoding="utf-8"))
    except KeyError:
        return None


def read_gtfs_zip(path: Path) -> Dict[str, pd.DataFrame]:
    if not path.exists():
        raise FileNotFoundError(f"GTFS path not found: {path}")
    with zipfile.ZipFile(path, "r") as zf:
        data: Dict[str, pd.DataFrame] = {}
        for name in REQUIRED_FILES + OPTIONAL_FILES:
            df = _read_csv_from_zip(zf, name)
            if df is not None:
                data[name] = df
        missing = [f for f in REQUIRED_FILES if f not in data]
        if missing:
            raise ValueError(f"Missing required GTFS files: {missing}")
        return data


