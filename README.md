# UrbanFlow MVP

UrbanFlow is an AI-assisted copilot for city bus network design. This MVP delivers an end-to-end pipeline that ingests GTFS feeds, validates and canonicalizes them, constructs a transit network graph, runs heuristic optimization to produce improved service plans, then exports KPIs, GTFS-like outputs, operational blocks, and before/after visualizations.

## Features
- GTFS ingestion, validation, and canonicalization
- Synthetic AVL generator and demand modeling utilities
- Network graph builder with persistence helpers
- Greedy seed and local search heuristics guided by configurable objectives and constraints
- KPI evaluator with passenger-level simulation
- CLI and optional FastAPI interface for running optimizations, validation, synthetic data generation, and visualization
- Exports for optimized GTFS files, vehicle blocks, KPI reports, scenario diff, and Folium map

## Getting Started

```bash
# create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# install project
pip install -e .
```

## CLI Usage

```bash
urbanflow run \
  --gtfs path/to/feed.zip \
  --constraints path/to/constraints.json \
  --objective path/to/objective.json \
  --outdir ./output \
  --sample-size 5000 \
  --seed 42

urbanflow validate --gtfs path/to/feed.zip --out validation_report.json
urbanflow synth-avl --gtfs path/to/feed.zip --out synthetic_avl.csv --params params.json
urbanflow visualize --before ./output/baseline.json --after ./output/optimized.json --out map.html
```

## Project Layout

```
README.md
pyproject.toml
src/urbanflow/
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
    diff_report.py
  config.py
  logging_utils.py
  exceptions.py

tests/
  test_parser.py
  test_validator.py
  test_optimizer_small_feed.py
notebooks/
  demo_notebook.ipynb
```

## Testing

```bash
pytest
```

## References
- UrbanFlow MVP Technical Specification
- PMF Project Group 10 planning document
