"""Graph serialization utilities."""

from __future__ import annotations

from pathlib import Path

import networkx as nx


def save_graph(graph: nx.DiGraph, path: Path) -> None:
    raise NotImplementedError("Graph save not yet implemented")


def load_graph(path: Path) -> nx.DiGraph:
    raise NotImplementedError("Graph load not yet implemented")
