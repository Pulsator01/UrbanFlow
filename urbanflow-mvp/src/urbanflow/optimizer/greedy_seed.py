from __future__ import annotations

from typing import Dict, Any
import copy
import networkx as nx
import pandas as pd


class GreedySeed:
    @staticmethod
    def create(
        graph: nx.DiGraph,
        canonical: Dict[str, pd.DataFrame],
        constraints: Dict[str, Any],
        objective: Dict[str, Any],
    ) -> Dict[str, Any]:
        # MVP seed: copy baseline as starting point
        seed_solution = {
            "graph": graph,
            "canonical": canonical,
            "changed_routes": [],
            "removed_stops": [],
        }
        return copy.deepcopy(seed_solution)


