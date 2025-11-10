"""Graph construction from canonical GTFS tables."""

from __future__ import annotations

from typing import Dict

import networkx as nx
import pandas as pd


def build_graph(tables: Dict[str, pd.DataFrame]) -> nx.DiGraph:
    raise NotImplementedError("Graph construction not yet implemented")
