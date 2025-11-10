"""Tests for GTFS validator."""

import pandas as pd
import pytest

from urbanflow.gtfs import validator


def test_validate_feed_not_implemented():
    with pytest.raises(NotImplementedError):
        validator.validate_feed({"stops": pd.DataFrame()})
