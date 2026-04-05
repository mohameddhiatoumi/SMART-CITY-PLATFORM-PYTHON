"""
Map components using Folium for the Smart City Dashboard.
"""
from __future__ import annotations
from typing import Any, Optional

# Sousse city centre coordinates
SOUSSE_CENTER = [35.8256, 10.6369]
SOUSSE_ZOOM = 12


def create_city_map(zones: Optional[list] = None, sensors: Optional[list] = None) -> Any:
    """
    Create a Folium map of Sousse with zone and sensor markers.

    Args:
        zones: list of zone dicts with keys: nom_zone, coordonnees_gps, indice_pollution
        sensors: optional list of sensor dicts

    Returns:
        folium.Map object
    """
    import folium

    m = folium.Map(
        location=SOUSSE_CENTER,
        zoom_start=SOUSSE_ZOOM,
        tiles="CartoDB positron",
    )

    # Demo zones if none provided
    if not zones:
        zones = _demo_zones()

    for zone in zones:
        coords = _parse_gps(zone.get("coordonnees_gps", ""))
        if coords is None:
            continue

        pollution = float(zone.get("indice_pollution", 0))
        color = _pollution_color(pollution)
        name = zone.get("nom_zone", zone.get("name", "Zone"))

        folium.CircleMarker(
            location=coords,
            radius=max(8, pollution / 8),
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.5,
            popup=folium.Popup(
                f"""<b>{name}</b><br>
                Pollution: {pollution:.1f}<br>
                Type: {zone.get("type_zone", "N/A")}""",
                max_width=200,
            ),
            tooltip=f"{name}: {pollution:.1f} AQI",
        ).add_to(m)

    if sensors:
        add_sensor_markers(m, sensors)

    # Add legend
    legend_html = """
    <div style="position: fixed; bottom: 30px; left: 30px; z-index: 1000;
                background: white; padding: 10px; border-radius: 5px;
                border: 2px solid grey; font-size: 12px;">
        <b>Pollution Index</b><br>
        <span style="color:#2ecc71">●</span> Good (&lt;25)<br>
        <span style="color:#f39c12">●</span> Moderate (25-50)<br>
        <span style="color:#e67e22">●</span> Poor (50-75)<br>
        <span style="color:#e74c3c">●</span> Critical (&gt;75)
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    return m


def add_sensor_markers(map_obj: Any, sensors: list) -> None:
    """Add sensor location markers to an existing Folium map."""
    import folium

    icon_map = {
        "AIR_QUALITY": ("cloud", "blue"),
        "TEMPERATURE": ("thermometer", "orange"),
        "HUMIDITY": ("tint", "lightblue"),
        "NOISE": ("volume-up", "purple"),
        "TRAFFIC": ("car", "red"),
        "WATER_QUALITY": ("water", "darkblue"),
    }

    for sensor in sensors:
        coords = _parse_gps(sensor.get("coordonnees_gps", ""))
        if coords is None:
            # Use zone coordinates with slight offset
            base = SOUSSE_CENTER
            import random
            coords = [base[0] + random.uniform(-0.02, 0.02), base[1] + random.uniform(-0.02, 0.02)]

        stype = sensor.get("type_capteur", "AIR_QUALITY")
        icon_name, icon_color = icon_map.get(stype, ("circle", "gray"))

        status = sensor.get("statut", sensor.get("etat_dfa", "UNKNOWN"))
        marker_color = "green" if status == "ACTIVE" else "orange" if status == "MAINTENANCE" else "red"

        folium.Marker(
            location=coords,
            popup=folium.Popup(
                f"""<b>Sensor #{sensor.get("id_capteur", "?")}</b><br>
                Type: {stype}<br>
                Status: {status}<br>
                Model: {sensor.get("modele", "N/A")}""",
                max_width=200,
            ),
            tooltip=f"Sensor {stype}",
            icon=folium.Icon(color=marker_color, icon="circle", prefix="fa"),
        ).add_to(map_obj)


def render_map_in_streamlit(map_obj: Any) -> None:
    """Render a Folium map inside a Streamlit app."""
    try:
        from streamlit_folium import st_folium
        st_folium(map_obj, width=700, height=450)
    except ImportError:
        import streamlit as st
        import folium
        from io import BytesIO
        st.warning("streamlit-folium not installed. Showing static map info.")
        st.info("Map centre: Sousse, Tunisia (35.8256°N, 10.6369°E)")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_gps(gps_str: str) -> Optional[list[float]]:
    """Parse 'lat,lon' string into [lat, lon] list."""
    if not gps_str:
        return None
    try:
        parts = gps_str.split(",")
        if len(parts) == 2:
            return [float(parts[0].strip()), float(parts[1].strip())]
    except (ValueError, AttributeError):
        pass
    return None


def _pollution_color(value: float) -> str:
    """Return a hex color based on pollution level."""
    if value < 25:
        return "#2ecc71"
    elif value < 50:
        return "#f39c12"
    elif value < 75:
        return "#e67e22"
    else:
        return "#e74c3c"


def _demo_zones() -> list[dict]:
    return [
        {"nom_zone": "Médina de Sousse", "coordonnees_gps": "35.8256,10.6369", "indice_pollution": 52.3, "type_zone": "MIXED"},
        {"nom_zone": "Zone Industrielle Nord", "coordonnees_gps": "35.8421,10.6201", "indice_pollution": 78.4, "type_zone": "INDUSTRIAL"},
        {"nom_zone": "Corniche", "coordonnees_gps": "35.8312,10.6445", "indice_pollution": 44.1, "type_zone": "COMMERCIAL"},
        {"nom_zone": "Erriadh", "coordonnees_gps": "35.8189,10.6312", "indice_pollution": 28.7, "type_zone": "RESIDENTIAL"},
        {"nom_zone": "Hammam Sousse Centre", "coordonnees_gps": "35.8591,10.5975", "indice_pollution": 38.2, "type_zone": "COMMERCIAL"},
        {"nom_zone": "Parc Vert Akouda", "coordonnees_gps": "35.8823,10.5612", "indice_pollution": 8.1, "type_zone": "GREEN"},
        {"nom_zone": "Zone Industrielle Kalaa", "coordonnees_gps": "35.8987,10.5312", "indice_pollution": 71.2, "type_zone": "INDUSTRIAL"},
        {"nom_zone": "Parc Industriel Msaken", "coordonnees_gps": "35.7189,10.5623", "indice_pollution": 82.1, "type_zone": "INDUSTRIAL"},
        {"nom_zone": "Quartier Résidentiel Msaken", "coordonnees_gps": "35.7345,10.5912", "indice_pollution": 21.7, "type_zone": "RESIDENTIAL"},
        {"nom_zone": "Espace Vert Oued Msaken", "coordonnees_gps": "35.7423,10.5845", "indice_pollution": 9.4, "type_zone": "GREEN"},
    ]
