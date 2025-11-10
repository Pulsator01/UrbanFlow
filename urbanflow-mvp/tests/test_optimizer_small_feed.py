import pandas as pd
import networkx as nx
from urbanflow.optimizer.evaluator import Evaluator
from urbanflow.optimizer.greedy_seed import GreedySeed
from urbanflow.optimizer.local_search import LocalSearch


def test_optimizer_smoke():
    # minimal canonical feed
    canonical = {
        "stops": pd.DataFrame([
            {"stop_id": "S1", "name": "A", "lat": 0.0, "lon": 0.0, "zone_id": None},
            {"stop_id": "S2", "name": "B", "lat": 0.0, "lon": 0.1, "zone_id": None},
        ]),
        "routes": pd.DataFrame([
            {"route_id": "R1", "short_name": "1", "long_name": "Route 1", "route_type": 3},
        ]),
        "trips": pd.DataFrame([
            {"trip_id": "T1", "route_id": "R1", "service_id": "WEEK", "trip_headsign": "To B", "shape_id": None},
        ]),
        "stop_times": pd.DataFrame([
            {"trip_id": "T1", "arrival_time_sec": 0, "departure_time_sec": 0, "stop_sequence": 1, "stop_id": "S1", "timepoint": 1},
            {"trip_id": "T1", "arrival_time_sec": 600, "departure_time_sec": 600, "stop_sequence": 2, "stop_id": "S2", "timepoint": 1},
        ]),
        "frequencies": pd.DataFrame(),
    }
    G = nx.DiGraph()
    G.add_node("S1", lat=0.0, lon=0.0)
    G.add_node("S2", lat=0.0, lon=0.1)
    G.add_edge("S1", "S2", travel_time=600, distance_m=1000, trip_id="T1")

    evaluator = Evaluator(objective={"weights": {}}, sample_size=1000, seed=42)
    seed = GreedySeed.create(G, canonical, constraints={"fleet_size": 5}, objective={"weights": {}})
    best = LocalSearch.optimize(seed, evaluator=evaluator, constraints={"fleet_size": 5}, max_iters=5)
    assert "graph" in best and "canonical" in best


