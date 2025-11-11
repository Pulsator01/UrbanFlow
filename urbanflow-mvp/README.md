## UrbanFlow MVP

UrbanFlow is a minimal, development-ready MVP that ingests a GTFS static feed, validates and canonicalizes inputs, builds a stop/route/trip graph, runs a heuristic optimizer, and exports optimized service plans, KPI deltas, and before/after maps.

### Features (MVP)
- CLI:
  - `urbanflow run --gtfs feed.zip --constraints constraints.json --objective objective.json --outdir ./output`
  - `urbanflow validate --gtfs feed.zip --out validation_report.json`
  - `urbanflow synth_avl --gtfs feed.zip --out synthetic_avl.csv --params synth.json`
  - `urbanflow visualize --before ./output/baseline.json --after ./output/optimized.json --out map.html`
  - `urbanflow pipeline --use-sample --outdir ./output_pipeline` (one-shot run with sample GTFS and defaults)
- Optional FastAPI endpoints for demo: `POST /api/v1/optimize`, `GET /api/v1/status/{job_id}`

### Quickstart
1. Create a virtual environment (Python 3.11).
2. Install dependencies:
   - `pip install -e .` (from the `urbanflow-mvp` root)
3. Run a validation:
   - `urbanflow validate --gtfs path/to/feed.zip --out ./output/validation_report.json`
4. End-to-end run:
   - `urbanflow run --gtfs path/to/feed.zip --constraints constraints.json --objective objective.json --outdir ./output --sample-size 5000 --seed 42`
5. One-shot pipeline (auto sample + defaults):
   - `urbanflow pipeline --use-sample --outdir ./output_pipeline`

### Repository Layout
```
urbanflow-mvp/
  README.md
  pyproject.toml
  src/urbanflow/
    __init__.py
    cli.py
    api.py
    gtfs/
      parser.py
      validator.py
      canonicalizer.py
    data/
      synthetic_avl.py
      od_generator.py
    graph/
      build_graph.py
      graph_io.py
    optimizer/
      greedy_seed.py
      local_search.py
      evaluator.py
    viz/
      folium_maps.py
    exports/
      gtfs_writer.py
      vehicle_block_writer.py
  tests/
    test_parser.py
    test_validator.py
    test_optimizer_small_feed.py
  notebooks/
    demo_notebook.ipynb
```

### Notes
- This MVP prioritizes clarity and reproducibility. Heavy optimizations and advanced models can be added after establishing the baseline pipeline.
*** End Patch

