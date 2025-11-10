"""Tests for optimizer workflow."""

import pytest

from urbanflow.optimizer import greedy_seed


def test_build_seed_solution_not_implemented():
    with pytest.raises(NotImplementedError):
        greedy_seed.build_seed_solution(None, None, {}, {})
