from __future__ import annotations

from typing import Dict, Any
from pathlib import Path
import math
import random
import csv
import time

import pandas as pd


def synthesize_avl(canonical: Dict[str, pd.DataFrame], out_csv: Path, params: Dict[str, Any]) -> None:
    rng = random.Random(int(params.get("seed", 42)))
    mean_dwell = float(params.get("mean_dwell", 20.0))  # seconds
    delay_std = float(params.get("delay_std", 30.0))    # seconds
    delayed_frac = float(params.get("percent_of_trips_delayed", 0.2))

    stops = canonical["stops"]
    stop_times = canonical["stop_times"]

    rows = []
    now = int(time.time())
    for trip_id, group in stop_times.groupby("trip_id"):
        base_delay = rng.gauss(0, delay_std) if rng.random() < delayed_frac else 0.0
        for _, r in group.sort_values("stop_sequence").iterrows():
            dwell = rng.expovariate(1.0 / mean_dwell)
            ts = now + int(r["arrival_time_sec"] + base_delay + dwell)
            stop_id = str(r["stop_id"])
            # crude position: use stop lat/lon
            stop_row = stops.loc[stops["stop_id"] == stop_id].head(1)
            if stop_row.empty:
                continue
            lat = float(stop_row["lat"].values[0])
            lon = float(stop_row["lon"].values[0])
            rows.append({
                "trip_id": str(trip_id),
                "timestamp_iso": pd.to_datetime(ts, unit="s").isoformat(),
                "lat": lat,
                "lon": lon,
                "vehicle_id": f"veh_{hash(trip_id) % 1000}",
            })

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["trip_id", "timestamp_iso", "lat", "lon", "vehicle_id"])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


