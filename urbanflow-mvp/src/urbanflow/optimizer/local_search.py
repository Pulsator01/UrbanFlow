from __future__ import annotations

from typing import Dict, Any
import random
import copy
import networkx as nx
import pandas as pd


class LocalSearch:
    @staticmethod
    def optimize(
        solution: Dict[str, Any],
        evaluator,
        constraints: Dict[str, Any],
        max_iters: int = 500,
    ) -> Dict[str, Any]:
        # MVP: perform a few random tweaks with hill-climb acceptance on proxy objective
        rng = random.Random(42)
        best = copy.deepcopy(solution)
        best_score = LocalSearch._score(evaluator.compute_kpis(best["graph"], best["canonical"]), evaluator.objective)
        for _ in range(int(max_iters)):
            cand = LocalSearch._propose_move(best, rng)
            cand_score = LocalSearch._score(evaluator.compute_kpis(cand["graph"], cand["canonical"]), evaluator.objective)
            if cand_score < best_score:
                best = cand
                best_score = cand_score
        return best

    @staticmethod
    def _propose_move(solution: Dict[str, Any], rng: random.Random) -> Dict[str, Any]:
        # Very simple move: randomly drop a low-degree stop and then restore (simulates exploration)
        graph: nx.DiGraph = solution["graph"]
        canonical = solution["canonical"]
        degrees = {n: graph.degree(n) for n in graph.nodes}
        if not degrees:
            return copy.deepcopy(solution)
        sorted_nodes = sorted(degrees.items(), key=lambda x: x[1])
        node_to_remove = sorted_nodes[0][0]
        cand_graph = graph.copy()
        if cand_graph.has_node(node_to_remove) and cand_graph.degree(node_to_remove) < 2:
            cand_graph.remove_node(node_to_remove)
            removed = solution.get("removed_stops", []) + [node_to_remove]
        else:
            removed = solution.get("removed_stops", [])
        cand = {
            "graph": cand_graph,
            "canonical": canonical,
            "changed_routes": solution.get("changed_routes", []),
            "removed_stops": removed,
        }
        return cand

    @staticmethod
    def _score(kpis: Dict[str, float], objective: Dict[str, Any]) -> float:
        weights = (objective or {}).get("weights", {})
        return (
            float(weights.get("p90_travel_time", 0.5)) * kpis["p90_travel_time"]
            + float(weights.get("passenger_weighted_travel_time", 0.3)) * kpis["passenger_weighted_travel_time"]
            + float(weights.get("coverage_within_400m", 0.2)) * (1.0 - kpis.get("coverage_ratio", 1.0))
        )


