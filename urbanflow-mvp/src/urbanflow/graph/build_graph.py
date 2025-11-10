from __future__ import annotations

from typing import Dict, Tuple
import math
import networkx as nx
import pandas as pd


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000.0
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def build_graph_from_canonical(canonical: Dict[str, pd.DataFrame]) -> nx.DiGraph:
    stops = canonical["stops"]
    stop_times = canonical["stop_times"]
    trips = canonical["trips"]

    stop_lookup = stops.set_index("stop_id")[["lat", "lon"]].to_dict("index")

    G = nx.DiGraph()
    for _, s in stops.iterrows():
        G.add_node(str(s["stop_id"]), lat=float(s["lat"]), lon=float(s["lon"]))

    # edges from sequential stops on each trip
    st_sorted = stop_times.sort_values(["trip_id", "stop_sequence"])
    for trip_id, group in st_sorted.groupby("trip_id"):
        prev_row = None
        for _, r in group.iterrows():
            if prev_row is not None:
                u = str(prev_row["stop_id"])
                v = str(r["stop_id"])
                t = max(1, int(r["arrival_time_sec"] - prev_row["departure_time_sec"]))
                s_u = stop_lookup.get(u)
                s_v = stop_lookup.get(v)
                if s_u and s_v:
                    d = _haversine(s_u["lat"], s_u["lon"], s_v["lat"], s_v["lon"])
                else:
                    d = 0.0
                G.add_edge(u, v, travel_time=t, distance_m=d, trip_id=str(trip_id))
            prev_row = r

    return G


