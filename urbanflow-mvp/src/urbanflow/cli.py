import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

from .gtfs.parser import read_gtfs_zip
from .gtfs.validator import validate_feed
from .gtfs.canonicalizer import canonicalize_feed
from .graph.build_graph import build_graph_from_canonical
from .optimizer.evaluator import Evaluator
from .optimizer.greedy_seed import GreedySeed
from .optimizer.local_search import LocalSearch
from .exports.gtfs_writer import write_gtfs_like
from .exports.vehicle_block_writer import write_vehicle_blocks
from .viz.folium_maps import write_before_after_map


def _ensure_outdir(outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def cmd_validate(args: argparse.Namespace) -> None:
    gtfs_path = Path(args.gtfs)
    out_path = Path(args.out)
    feed = read_gtfs_zip(gtfs_path)
    report = validate_feed(feed)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote validation report to {out_path}")


def cmd_synth_avl(args: argparse.Namespace) -> None:
    from .data.synthetic_avl import synthesize_avl

    gtfs_path = Path(args.gtfs)
    out_path = Path(args.out)
    params = _load_json(Path(args.params)) if args.params else {}

    feed = read_gtfs_zip(gtfs_path)
    canonical = canonicalize_feed(feed)
    synthesize_avl(canonical, out_path, params)
    print(f"Wrote synthetic AVL to {out_path}")


def cmd_visualize(args: argparse.Namespace) -> None:
    before = Path(args.before)
    after = Path(args.after)
    out_path = Path(args.out)
    write_before_after_map(before, after, out_path)
    print(f"Wrote before/after map to {out_path}")


def cmd_run(args: argparse.Namespace) -> None:
    gtfs_path = Path(args.gtfs)
    constraints = _load_json(Path(args.constraints))
    objective = _load_json(Path(args.objective))
    outdir = Path(args.outdir)
    sample_size = int(args.sample_size)
    seed = int(args.seed) if args.seed is not None else None

    _ensure_outdir(outdir)

    # 1) Load and validate
    feed = read_gtfs_zip(gtfs_path)
    report = validate_feed(feed)
    (outdir / "validation_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    # 2) Canonicalize and build graph
    canonical = canonicalize_feed(feed)
    graph = build_graph_from_canonical(canonical)

    # 3) Baseline evaluation (simple)
    evaluator = Evaluator(objective=objective, sample_size=sample_size, seed=seed)
    baseline = evaluator.compute_kpis(graph, canonical)
    (outdir / "baseline_kpi_report.json").write_text(json.dumps(baseline, indent=2), encoding="utf-8")

    # 4) Greedy seed + local search
    seed_solution = GreedySeed.create(graph, canonical, constraints, objective)
    best_solution = LocalSearch.optimize(
        seed_solution,
        evaluator=evaluator,
        constraints=constraints,
        max_iters=int(args.max_iters),
    )

    # 5) Exports
    export_dir = outdir / "optimized_gtfs"
    export_dir.mkdir(parents=True, exist_ok=True)
    write_gtfs_like(best_solution, export_dir)
    write_vehicle_blocks(best_solution, outdir / "vehicle_blocks.csv")

    # 6) KPI report + diff + map
    optimized_kpis = evaluator.compute_kpis(best_solution["graph"], best_solution["canonical"])
    (outdir / "kpi_report.json").write_text(json.dumps({
        "baseline": baseline, "optimized": optimized_kpis
    }, indent=2), encoding="utf-8")

    # Minimal scenario diff
    diff_md = outdir / "scenario_diff.md"
    diff_md.write_text(
        "# Scenario Diff\n\n"
        f"- Routes changed: {len(best_solution.get('changed_routes', []))}\n"
        f"- Stops removed: {len(best_solution.get('removed_stops', []))}\n"
        f"- Fleet size constraint: {constraints.get('fleet_size')}\n",
        encoding="utf-8",
    )

    # Before/After map placeholder (uses exported json placeholders)
    before_json = outdir / "baseline.json"
    after_json = outdir / "optimized.json"
    before_json.write_text(json.dumps({"kpis": baseline}, indent=2), encoding="utf-8")
    after_json.write_text(json.dumps({"kpis": optimized_kpis}, indent=2), encoding="utf-8")
    write_before_after_map(before_json, after_json, outdir / "before_after_map.html")

    print(f"Run completed. Outputs in: {outdir}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="urbanflow", description="UrbanFlow CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_validate = sub.add_parser("validate", help="Validate a GTFS feed and write a report")
    p_validate.add_argument("--gtfs", required=True, help="Path to GTFS zip")
    p_validate.add_argument("--out", required=True, help="Path to write validation_report.json")
    p_validate.set_defaults(func=cmd_validate)

    p_synth = sub.add_parser("synth_avl", help="Generate synthetic AVL CSV")
    p_synth.add_argument("--gtfs", required=True, help="Path to GTFS zip")
    p_synth.add_argument("--out", required=True, help="Path to write synthetic_avl.csv")
    p_synth.add_argument("--params", required=False, help="Path to synthetic params JSON")
    p_synth.set_defaults(func=cmd_synth_avl)

    p_viz = sub.add_parser("visualize", help="Create a before/after map HTML")
    p_viz.add_argument("--before", required=True, help="Path to baseline json")
    p_viz.add_argument("--after", required=True, help="Path to optimized json")
    p_viz.add_argument("--out", required=True, help="Path to write map.html")
    p_viz.set_defaults(func=cmd_visualize)

    p_run = sub.add_parser("run", help="Run end-to-end optimization pipeline")
    p_run.add_argument("--gtfs", required=True, help="Path to GTFS zip")
    p_run.add_argument("--constraints", required=True, help="Path to constraints JSON")
    p_run.add_argument("--objective", required=True, help="Path to objective JSON")
    p_run.add_argument("--outdir", required=True, help="Output directory")
    p_run.add_argument("--sample-size", default="5000", help="Sampling size for evaluator")
    p_run.add_argument("--seed", default=None, help="Random seed")
    p_run.add_argument("--max_iters", default="500", help="Max iterations for local search")
    p_run.set_defaults(func=cmd_run)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


