from __future__ import annotations

from typing import Dict, Any
from pathlib import Path
import pandas as pd


def write_gtfs_like(solution: Dict[str, Any], outdir: Path) -> None:
    canonical = solution["canonical"]
    outdir.mkdir(parents=True, exist_ok=True)
    # Write minimal GTFS-like CSVs
    canonical["stops"].rename(columns={"name": "stop_name", "lat": "stop_lat", "lon": "stop_lon"})[
        ["stop_id", "stop_name", "stop_lat", "stop_lon", "zone_id"]
    ].to_csv(outdir / "stops.txt", index=False)
    canonical["routes"].rename(columns={"short_name": "route_short_name", "long_name": "route_long_name"})[
        ["route_id", "route_short_name", "route_long_name", "route_type"]
    ].to_csv(outdir / "routes.txt", index=False)

    trips = canonical["trips"].copy()
    if "trip_headsign" not in trips.columns:
        trips["trip_headsign"] = ""
    if "shape_id" not in trips.columns:
        trips["shape_id"] = ""
    trips[
        ["trip_id", "route_id", "service_id", "trip_headsign", "shape_id"]
    ].to_csv(outdir / "trips.txt", index=False)

    st = canonical["stop_times"].copy()
    def sec_to_hms(sec: int) -> str:
        h = sec // 3600
        m = (sec % 3600) // 60
        s = sec % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    st["arrival_time"] = st["arrival_time_sec"].apply(sec_to_hms)
    st["departure_time"] = st["departure_time_sec"].apply(sec_to_hms)
    st[
        ["trip_id", "arrival_time", "departure_time", "stop_sequence", "stop_id", "timepoint"]
    ].to_csv(outdir / "stop_times.txt", index=False)


