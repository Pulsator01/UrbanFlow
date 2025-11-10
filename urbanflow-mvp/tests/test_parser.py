import pytest
from pathlib import Path
from urbanflow.gtfs.parser import read_gtfs_zip


def test_parser_missing_file(tmp_path: Path):
    # create empty zip
    z = tmp_path / "empty.zip"
    z.write_bytes(b"")  # invalid zip to trigger error
    with pytest.raises(Exception):
        read_gtfs_zip(z)


