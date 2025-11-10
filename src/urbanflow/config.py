"""Configuration models for UrbanFlow."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


@dataclass(slots=True)
class UrbanFlowConfig:
    """Configuration container for UrbanFlow runs."""

    gtfs_path: Path
    constraints_path: Path
    objective_path: Path
    output_dir: Path
    sample_size: int = 5000
    seed: Optional[int] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UrbanFlowConfig":
        return cls(
            gtfs_path=Path(data["gtfs_path"]),
            constraints_path=Path(data["constraints_path"]),
            objective_path=Path(data["objective_path"]),
            output_dir=Path(data.get("output_dir", "./output")),
            sample_size=int(data.get("sample_size", 5000)),
            seed=data.get("seed"),
            extra={k: v for k, v in data.items() if k not in {"gtfs_path", "constraints_path", "objective_path", "output_dir", "sample_size", "seed"}},
        )

    @classmethod
    def from_yaml(cls, path: Path) -> "UrbanFlowConfig":
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        return cls.from_dict(data)

    def ensure_output_dir(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
