import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict
import tempfile
import zipfile
import io

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

def _write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _default_constraints() -> Dict[str, Any]:
    return {
        "fleet_size": 40,
        "depots": [{"id": "D1", "lat": 0.0, "lon": 0.0}],
        "max_interline": 2,
        "max_vehicle_km_per_day": 400,
        "vehicle_capacity": 70,
    }


def _default_objective() -> Dict[str, Any]:
    return {
        "weights": {
            "p90_travel_time": 0.5,
            "passenger_weighted_travel_time": 0.3,
            "coverage_within_400m": 0.2,
        },
        "coverage_radius_m": 400,
    }


def _create_sample_gtfs_zip(dst_zip: Path) -> None:
    # Minimal 2-stop, 1-route, 1-trip, 2-stop_times sample feed
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, mode="w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr(
            "stops.txt",
            "stop_id,stop_name,stop_lat,stop_lon\nS1,Stop 1,0.0,0.0\nS2,Stop 2,0.0,0.1\n",
        )
        z.writestr(
            "routes.txt",
            "route_id,route_short_name,route_long_name,route_type\nR1,1,Route 1,3\n",
        )
        z.writestr(
            "trips.txt",
            "trip_id,route_id,service_id,trip_headsign,shape_id\nT1,R1,WEEK,To Stop 2,\n",
        )
        z.writestr(
            "stop_times.txt",
            "trip_id,arrival_time,departure_time,stop_sequence,stop_id\nT1,00:00:00,00:00:00,1,S1\nT1,00:10:00,00:10:00,2,S2\n",
        )
    dst_zip.parent.mkdir(parents=True, exist_ok=True)
    with dst_zip.open("wb") as f:
        f.write(mem.getvalue())


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

def cmd_pipeline(args: argparse.Namespace) -> None:
    # One-shot pipeline: optionally create sample GTFS and default configs, run, and print KPI deltas
    outdir = Path(args.outdir)
    _ensure_outdir(outdir)

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        # Prepare GTFS
        if args.use_sample:
            gtfs_zip = td_path / "sample_gtfs.zip"
            _create_sample_gtfs_zip(gtfs_zip)
        else:
            if not args.gtfs:
                raise SystemExit("Either provide --gtfs or use --use-sample")
            gtfs_zip = Path(args.gtfs)

        # Prepare constraints/objective
        constraints_path = Path(args.constraints) if args.constraints else (td_path / "constraints.json")
        objective_path = Path(args.objective) if args.objective else (td_path / "objective.json")
        if not args.constraints:
            _write_json(constraints_path, _default_constraints())
        if not args.objective:
            _write_json(objective_path, _default_objective())

        # Validate
        report_path = outdir / "validation_report.json"
        feed = read_gtfs_zip(gtfs_zip)
        report = validate_feed(feed)
        _write_json(report_path, report)

        # Run
        run_ns = argparse.Namespace(
            gtfs=str(gtfs_zip),
            constraints=str(constraints_path),
            objective=str(objective_path),
            outdir=str(outdir),
            sample_size=str(args.sample_size),
            seed=str(args.seed) if args.seed is not None else None,
            max_iters=str(args.max_iters),
        )
        cmd_run(run_ns)

        # Print KPI deltas
        kpi_file = outdir / "kpi_report.json"
        if kpi_file.exists():
            kpi = _load_json(kpi_file)
            b = kpi.get("baseline", {})
            o = kpi.get("optimized", {})
            def delta(key: str) -> float:
                return float(o.get(key, 0) - b.get(key, 0))
            print("KPI deltas (optimized - baseline):")
            keys = ["average_travel_time", "passenger_weighted_travel_time", "p50_travel_time", "p90_travel_time", "on_time_percentage", "coverage_ratio"]
            for k in keys:
                print(f" - {k}: {delta(k):.2f}")
        else:
            print("kpi_report.json not found; pipeline completed without KPI summary.")


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

    p_pipe = sub.add_parser("pipeline", help="One-shot pipeline: validate + run + KPI deltas")
    p_pipe.add_argument("--gtfs", help="Path to GTFS zip (omit if using --use-sample)")
    p_pipe.add_argument("--use-sample", action="store_true", help="Generate a minimal sample GTFS and run")
    p_pipe.add_argument("--constraints", help="Path to constraints JSON (defaults will be generated if omitted)")
    p_pipe.add_argument("--objective", help="Path to objective JSON (defaults will be generated if omitted)")
    p_pipe.add_argument("--outdir", required=True, help="Output directory")
    p_pipe.add_argument("--sample-size", default="1000", help="Sampling size for evaluator")
    p_pipe.add_argument("--seed", default="42", help="Random seed")
    p_pipe.add_argument("--max_iters", default="200", help="Max iterations for local search")
    p_pipe.set_defaults(func=cmd_pipeline)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


