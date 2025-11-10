from __future__ import annotations

from typing import Dict, Any
import random
import networkx as nx
import pandas as pd


class Evaluator:
    def __init__(self, objective: Dict[str, Any], sample_size: int = 5000, seed: int | None = None) -> None:
        self.objective = objective or {"weights": {}}
        self.sample_size = int(sample_size)
        self.rng = random.Random(seed)

    def _estimate_wait_time(self, canonical: Dict[str, pd.DataFrame]) -> float:
        freqs = canonical.get("frequencies")
        if freqs is None or freqs.empty:
            # fallback average headway: 10 minutes
            return 300.0
        return float(freqs["headway_secs"].mean() / 2.0)

    def _avg_in_vehicle_time(self, graph: nx.DiGraph) -> float:
        # approximate by average edge travel time
        if graph.number_of_edges() == 0:
            return 0.0
        return float(sum(d.get("travel_time", 0) for _, _, d in graph.edges(data=True)) / graph.number_of_edges())

    def compute_kpis(self, graph: nx.DiGraph, canonical: Dict[str, pd.DataFrame]) -> Dict[str, float]:
        wait = self._estimate_wait_time(canonical)
        in_vehicle = self._avg_in_vehicle_time(graph)
        # P90 ~ mean + 1.28*std (rough proxy); assume std ~ 0.5 * mean for MVP
        mean_tt = wait + in_vehicle
        std_tt = 0.5 * mean_tt
        p90 = mean_tt + 1.28 * std_tt
        coverage_ratio = 1.0  # placeholder; compute via radius and stop coverage later
        return {
            "average_travel_time": float(mean_tt),
            "passenger_weighted_travel_time": float(mean_tt),  # proxy
            "p50_travel_time": float(mean_tt),
            "p90_travel_time": float(p90),
            "on_time_percentage": 0.9,  # placeholder
            "coverage_ratio": float(coverage_ratio),
        }


