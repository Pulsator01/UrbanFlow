from __future__ import annotations

from typing import Dict, Any, List
import pandas as pd


def _ref_integrity(feed: Dict[str, pd.DataFrame]) -> List[str]:
    errors: List[str] = []
    stops = feed["stops.txt"]
    trips = feed["trips.txt"]
    routes = feed["routes.txt"]
    stop_times = feed["stop_times.txt"]
    shapes = feed.get("shapes.txt")

    stop_ids = set(stops["stop_id"].astype(str))
    trip_ids = set(trips["trip_id"].astype(str))
    route_ids = set(routes["route_id"].astype(str))
    if shapes is not None and not shapes.empty:
        shape_ids = set(shapes["shape_id"].astype(str))
    else:
        shape_ids = set()

    # stop_times -> stop_id, trip_id
    for col, valid in [("stop_id", stop_ids), ("trip_id", trip_ids)]:
        bad = set(stop_times[col].astype(str)) - valid
        if bad:
            errors.append(f"stop_times.{col} references missing ids: {list(bad)[:5]}...")

    # trips -> route_id, shape_id
    bad_routes = set(trips["route_id"].astype(str)) - route_ids
    if bad_routes:
        errors.append(f"trips.route_id references missing ids: {list(bad_routes)[:5]}...")
    if "shape_id" in trips.columns and shape_ids:
        missing_shapes = set(trips["shape_id"].dropna().astype(str)) - shape_ids
        if missing_shapes:
            errors.append(f"trips.shape_id references missing ids: {list(missing_shapes)[:5]}...")

    return errors


def _normalize_times(stop_times: pd.DataFrame) -> pd.DataFrame:
    def to_seconds(t: str) -> int:
        if pd.isna(t):
            return 0
        parts = str(t).split(":")
        h, m, s = [int(p) for p in parts] if len(parts) == 3 else (0, 0, 0)
        return h * 3600 + m * 60 + s

    st = stop_times.copy()
    st["arrival_time_sec"] = st["arrival_time"].apply(to_seconds)
    st["departure_time_sec"] = st["departure_time"].apply(to_seconds)
    # naive overnight handling: ensure sequence non-decreasing by adding 24h when needed
    st.sort_values(["trip_id", "stop_sequence"], inplace=True)
    for trip_id, group in st.groupby("trip_id"):
        prev = None
        add = 0
        idx = group.index
        for i in idx:
            if prev is not None and st.at[i, "arrival_time_sec"] + add < prev:
                add += 24 * 3600
            st.at[i, "arrival_time_sec"] += add
            st.at[i, "departure_time_sec"] += add
            prev = st.at[i, "arrival_time_sec"]
    return st


def validate_feed(feed: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    errors = []
    warnings = []

    # required files present
    required = ["stops.txt", "routes.txt", "trips.txt", "stop_times.txt"]
    missing = [f for f in required if f not in feed]
    if missing:
        errors.append(f"Missing required files: {missing}")

    errors.extend(_ref_integrity(feed))

    # duplicates
    for name in ["stops.txt", "routes.txt", "trips.txt"]:
        df = feed[name]
        key = name.split(".")[0][:-1] + "_id"
        if key in df.columns:
            dups = df[df.duplicated([key])]
            if not dups.empty:
                warnings.append(f"{name} has duplicate IDs: {len(dups)}")

    # times normalized preview
    st_norm = _normalize_times(feed["stop_times.txt"])
    # lightweight heuristic for non-revenue trips (deadhead) - flag headsigns like NOT IN SERVICE
    trips = feed["trips.txt"]
    if "trip_headsign" in trips.columns:
        deadhead = trips["trip_headsign"].astype(str).str.contains("NOT IN SERVICE|DEADHEAD", case=False, na=False)
        if deadhead.any():
            warnings.append(f"Detected {int(deadhead.sum())} potential non-revenue trips by headsign pattern")

    return {
        "status": "ok" if not errors else "error",
        "errors": errors,
        "warnings": warnings,
        "canonicalized_feed_hint": "Use canonicalizer.canonicalize_feed() to produce normalized tables.",
    }


