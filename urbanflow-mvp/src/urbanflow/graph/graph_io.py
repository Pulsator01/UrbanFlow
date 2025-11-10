from __future__ import annotations

from pathlib import Path
import pickle
import networkx as nx


def save_graph(graph: nx.DiGraph, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as f:
        pickle.dump(graph, f)


def load_graph(path: Path) -> nx.DiGraph:
    with path.open("rb") as f:
        return pickle.load(f)


