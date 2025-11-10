from __future__ import annotations

from typing import Dict, Any
import pandas as pd


def canonicalize_feed(feed: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    stops = feed["stops.txt"].copy()
    routes = feed["routes.txt"].copy()
    trips = feed["trips.txt"].copy()
    stop_times = feed["stop_times.txt"].copy()
    frequencies = feed.get("frequencies.txt", pd.DataFrame())

    # enforce basic schemas and types
    stops = stops.rename(columns={"stop_lat": "lat", "stop_lon": "lon"})
    if "zone_id" not in stops.columns:
        stops["zone_id"] = None
    stops = stops[["stop_id", "stop_name", "lat", "lon", "zone_id"]]
    stops.columns = ["stop_id", "name", "lat", "lon", "zone_id"]

    routes = routes[["route_id", "route_short_name", "route_long_name", "route_type"]]
    routes.columns = ["route_id", "short_name", "long_name", "route_type"]

    core_trip_cols = ["trip_id", "route_id", "service_id"]
    if "trip_headsign" in trips.columns:
        core_trip_cols.append("trip_headsign")
    if "shape_id" in trips.columns:
        core_trip_cols.append("shape_id")
    trips = trips[core_trip_cols]
    # pad optional cols
    if "trip_headsign" not in trips.columns:
        trips["trip_headsign"] = None
    if "shape_id" not in trips.columns:
        trips["shape_id"] = None

    # normalize times to seconds
    def to_sec(t: str) -> int:
        if pd.isna(t):
            return 0
        h, m, s = [int(x) for x in str(t).split(":")]
        return h * 3600 + m * 60 + s

    st = stop_times.copy()
    st["arrival_time_sec"] = st["arrival_time"].apply(to_sec)
    st["departure_time_sec"] = st["departure_time"].apply(to_sec)
    if "timepoint" not in st.columns:
        st["timepoint"] = 1
    st = st[
        ["trip_id", "arrival_time_sec", "departure_time_sec", "stop_sequence", "stop_id", "timepoint"]
    ].sort_values(["trip_id", "stop_sequence"])

    frequencies = frequencies.copy()
    if not frequencies.empty:
        # keep core fields if exists
        freq_cols = [c for c in ["trip_id", "start_time", "end_time", "headway_secs"] if c in frequencies.columns]
        frequencies = frequencies[freq_cols]

    return {
        "stops": stops.reset_index(drop=True),
        "routes": routes.reset_index(drop=True),
        "trips": trips.reset_index(drop=True),
        "stop_times": st.reset_index(drop=True),
        "frequencies": frequencies.reset_index(drop=True),
    }


