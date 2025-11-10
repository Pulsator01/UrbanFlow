"""Command-line interface for UrbanFlow."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from .config import UrbanFlowConfig
from .logging_utils import get_logger

app = typer.Typer(help="UrbanFlow transit optimization toolkit")
logger = get_logger(__name__)


@app.command()
def run(
    gtfs: Path = typer.Option(..., exists=True, readable=True, help="Path to GTFS zip feed"),
    constraints: Path = typer.Option(..., exists=True, readable=True, help="Path to constraints JSON/YAML"),
    objective: Path = typer.Option(..., exists=True, readable=True, help="Path to objective weights JSON/YAML"),
    outdir: Path = typer.Option(Path("./output"), help="Output directory for results"),
    sample_size: int = typer.Option(5000, help="Sample size for KPI simulation"),
    seed: Optional[int] = typer.Option(None, help="Random seed"),
) -> None:
    """Run the full UrbanFlow optimization pipeline."""

    config = UrbanFlowConfig(
        gtfs_path=gtfs,
        constraints_path=constraints,
        objective_path=objective,
        output_dir=outdir,
        sample_size=sample_size,
        seed=seed,
    )
    config.ensure_output_dir()
    logger.info("Starting UrbanFlow pipeline")
    # Pipeline orchestration will be implemented in subsequent iterations.
    logger.info("Pipeline orchestration not yet implemented")


@app.command()
def validate(gtfs: Path, out: Path = typer.Option(Path("validation_report.json"))) -> None:
    """Validate the provided GTFS feed and produce a report."""

    logger.info("Validation command not yet implemented")


@app.command(name="synth-avl")
def synth_avl(
    gtfs: Path,
    out: Path = typer.Option(Path("synthetic_avl.csv")),
    params: Optional[Path] = typer.Option(None, help="Path to synthetic generator parameters"),
) -> None:
    """Generate synthetic AVL data for stress tests."""

    logger.info("Synthetic AVL generation not yet implemented")


@app.command()
def visualize(
    before: Path,
    after: Path,
    out: Path = typer.Option(Path("before_after_map.html")),
) -> None:
    """Create a before/after Folium visualization from scenario JSON exports."""

    logger.info("Visualization command not yet implemented")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
