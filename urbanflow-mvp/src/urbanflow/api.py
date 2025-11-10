from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil
import tempfile
import json

from .gtfs.parser import read_gtfs_zip
from .gtfs.validator import validate_feed
from .gtfs.canonicalizer import canonicalize_feed
from .graph.build_graph import build_graph_from_canonical
from .optimizer.evaluator import Evaluator
from .optimizer.greedy_seed import GreedySeed
from .optimizer.local_search import LocalSearch

app = FastAPI(title="UrbanFlow API", version="0.1.0")


@app.post("/api/v1/optimize")
async def optimize(
    gtfs_zip: UploadFile = File(...),
    constraints_json: UploadFile = File(...),
    objective_json: UploadFile = File(...),
    sample_size: int = Form(2000),
    seed: int | None = Form(None),
):
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        gtfs_path = td_path / "feed.zip"
        constraints_path = td_path / "constraints.json"
        objective_path = td_path / "objective.json"

        with gtfs_path.open("wb") as f:
            shutil.copyfileobj(gtfs_zip.file, f)
        with constraints_path.open("wb") as f:
            shutil.copyfileobj(constraints_json.file, f)
        with objective_path.open("wb") as f:
            shutil.copyfileobj(objective_json.file, f)

        constraints = json.loads(constraints_path.read_text(encoding="utf-8"))
        objective = json.loads(objective_path.read_text(encoding="utf-8"))

        feed = read_gtfs_zip(gtfs_path)
        _ = validate_feed(feed)
        canonical = canonicalize_feed(feed)
        graph = build_graph_from_canonical(canonical)

        evaluator = Evaluator(objective=objective, sample_size=sample_size, seed=seed)
        baseline = evaluator.compute_kpis(graph, canonical)

        seed_solution = GreedySeed.create(graph, canonical, constraints, objective)
        best_solution = LocalSearch.optimize(seed_solution, evaluator, constraints, max_iters=200)
        optimized = evaluator.compute_kpis(best_solution["graph"], best_solution["canonical"])

        return JSONResponse({
            "baseline": baseline,
            "optimized": optimized,
            "notes": "MVP execution completed synchronously.",
        })


