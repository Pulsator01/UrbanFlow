"""Local search heuristics."""

from __future__ import annotations

from typing import Any, Dict


def optimize(
    seed_solution: Dict[str, Any],
    evaluator: Any,
    constraints: Dict[str, Any],
    max_iters: int = 5000,
) -> Dict[str, Any]:
    raise NotImplementedError("Local search not yet implemented")
