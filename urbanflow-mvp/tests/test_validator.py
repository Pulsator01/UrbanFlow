import pandas as pd
from urbanflow.gtfs.validator import validate_feed


def test_validator_minimal():
    feed = {
        "stops.txt": pd.DataFrame([{"stop_id": "S1", "stop_name": "Stop 1", "stop_lat": 0.0, "stop_lon": 0.0}]),
        "routes.txt": pd.DataFrame([{"route_id": "R1", "route_short_name": "1", "route_long_name": "Route 1", "route_type": 3}]),
        "trips.txt": pd.DataFrame([{"trip_id": "T1", "route_id": "R1", "service_id": "WEEK"}]),
        "stop_times.txt": pd.DataFrame([
            {"trip_id": "T1", "arrival_time": "00:00:00", "departure_time": "00:00:00", "stop_sequence": 1, "stop_id": "S1"}
        ]),
    }
    report = validate_feed(feed)
    assert "status" in report


