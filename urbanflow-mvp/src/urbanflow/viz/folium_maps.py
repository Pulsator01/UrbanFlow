from __future__ import annotations

from pathlib import Path
import json
import folium


def write_before_after_map(before_json: Path, after_json: Path, out_html: Path) -> None:
    before = json.loads(before_json.read_text(encoding="utf-8"))
    after = json.loads(after_json.read_text(encoding="utf-8"))

    # Default center: somewhere neutral if no coordinates are passed. For MVP, fixed center.
    m = folium.Map(location=[0.0, 0.0], zoom_start=2, tiles="cartodbpositron")
    folium.LayerControl().add_to(m)

    # Add KPI markers in a simple popup
    folium.Marker(
        [0.0, 0.0],
        popup=folium.Popup(html=f"<b>Baseline</b><br/>{json.dumps(before.get('kpis', before), indent=2)}", max_width=300),
        icon=folium.Icon(color="blue"),
    ).add_to(m)
    folium.Marker(
        [0.0, 10.0],
        popup=folium.Popup(html=f"<b>Optimized</b><br/>{json.dumps(after.get('kpis', after), indent=2)}", max_width=300),
        icon=folium.Icon(color="green"),
    ).add_to(m)

    out_html.parent.mkdir(parents=True, exist_ok=True)
    m.save(str(out_html))


