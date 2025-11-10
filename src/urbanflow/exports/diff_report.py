"""Scenario diff report generator."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Any


def write_diff_report(baseline: Dict[str, Any], optimized: Dict[str, Any], out_path: Path) -> None:
    raise NotImplementedError("Diff report not yet implemented")
