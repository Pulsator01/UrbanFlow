from __future__ import annotations

from typing import Dict, Any
from pathlib import Path
import csv
import pandas as pd


def write_vehicle_blocks(solution: Dict[str, Any], out_csv: Path) -> None:
    canonical = solution["canonical"]
    st = canonical["stop_times"]
    trips = canonical["trips"]

    # naive blocks: one trip per block for MVP
    rows = []
    for trip_id, group in st.groupby("trip_id"):
        start_time = int(group["departure_time_sec"].min())
        end_time = int(group["arrival_time_sec"].max())
        rows.append({
            "block_id": f"block_{trip_id}",
            "route_sequence": ",".join(sorted(set(trips.loc[trips['trip_id'] == trip_id, 'route_id'].astype(str)))),
            "trip_start_time": start_time,
            "trip_end_time": end_time,
            "vehicle_id": "",
        })

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["block_id", "route_sequence", "trip_start_time", "trip_end_time", "vehicle_id"])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


