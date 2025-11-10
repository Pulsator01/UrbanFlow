"""Tests for GTFS parser."""

import pytest

from urbanflow.gtfs import parser


def test_read_gtfs_not_implemented():
    with pytest.raises(NotImplementedError):
        parser.read_gtfs(__file__)  # type: ignore[arg-type]
