"""
Plotly chart components for the Smart City Dashboard.
"""
from __future__ import annotations
from typing import Any


def create_pollution_chart(data: Any) -> Any:
    """Create a bar chart of pollution index by zone."""
    import plotly.graph_objects as go
    import pandas as pd

    if hasattr(data, "to_dict"):
        df = data
    elif isinstance(data, list):
        import pandas as pd
        df = pd.DataFrame(data)
    else:
        df = _demo_zone_data()

    if df.empty:
        df = _demo_zone_data()

    # Use first two columns or defaults
    x_col = "nom_zone" if "nom_zone" in df.columns else (df.columns[0] if len(df.columns) > 0 else "Zone")
    y_col = "indice_pollution" if "indice_pollution" in df.columns else (df.columns[1] if len(df.columns) > 1 else "Pollution")

    colors = [
        "#2ecc71" if v < 25 else "#f39c12" if v < 50 else "#e74c3c"
        for v in df[y_col].fillna(0)
    ] if y_col in df.columns else ["#3498db"] * len(df)

    fig = go.Figure(go.Bar(
        x=df[x_col].astype(str) if x_col in df.columns else list(range(len(df))),
        y=df[y_col] if y_col in df.columns else [0] * len(df),
        marker_color=colors,
        text=df[y_col].round(1) if y_col in df.columns else None,
        textposition="outside",
    ))
    fig.update_layout(
        title="Pollution Index by Zone",
        xaxis_title="Zone",
        yaxis_title="Pollution Index (AQI)",
        xaxis_tickangle=-45,
        height=400,
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def create_sensor_status_pie(data: Any) -> Any:
    """Create a pie chart of sensor status distribution."""
    import plotly.graph_objects as go

    if isinstance(data, dict):
        labels = list(data.keys())
        values = list(data.values())
    elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
        labels = [d.get("statut", d.get("status", "Unknown")) for d in data]
        from collections import Counter
        counter = Counter(labels)
        labels, values = list(counter.keys()), list(counter.values())
    else:
        labels = ["ACTIVE", "INACTIVE", "MAINTENANCE", "FAULTY"]
        values = [35, 5, 6, 4]

    color_map = {
        "ACTIVE": "#2ecc71", "INACTIVE": "#95a5a6",
        "MAINTENANCE": "#f39c12", "FAULTY": "#e74c3c",
    }
    colors = [color_map.get(l, "#3498db") for l in labels]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker_colors=colors,
    ))
    fig.update_layout(
        title="Sensor Status Distribution",
        height=350,
        showlegend=True,
    )
    return fig


def create_intervention_timeline(data: Any) -> Any:
    """Create a timeline chart of interventions."""
    import plotly.graph_objects as go
    import pandas as pd
    from datetime import datetime, timedelta

    if isinstance(data, list) and len(data) > 0:
        df = pd.DataFrame(data)
    elif hasattr(data, "columns"):
        df = data
    else:
        df = _demo_intervention_data()

    if df.empty or len(df) == 0:
        df = _demo_intervention_data()

    priority_colors = {"CRITICAL": "#e74c3c", "HIGH": "#f39c12", "MEDIUM": "#3498db", "LOW": "#2ecc71"}

    fig = go.Figure()

    if "date_demande" in df.columns and "priorite" in df.columns:
        for priority in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            mask = df["priorite"] == priority
            subset = df[mask]
            if not subset.empty:
                fig.add_trace(go.Scatter(
                    x=pd.to_datetime(subset["date_demande"]),
                    y=[priority] * len(subset),
                    mode="markers",
                    name=priority,
                    marker=dict(size=10, color=priority_colors.get(priority, "#3498db")),
                ))
    else:
        now = datetime.now()
        for i, priority in enumerate(["CRITICAL", "HIGH", "MEDIUM", "LOW"]):
            times = [now - timedelta(days=j) for j in range(i * 3, i * 3 + 5)]
            fig.add_trace(go.Scatter(
                x=times, y=[priority] * 5,
                mode="markers", name=priority,
                marker=dict(size=10, color=priority_colors[priority]),
            ))

    fig.update_layout(
        title="Intervention Timeline by Priority",
        xaxis_title="Date",
        yaxis_title="Priority Level",
        height=350,
    )
    return fig


def create_measurement_trend(data: Any, sensor_id: int = 1) -> Any:
    """Create a line chart of sensor measurements over time."""
    import plotly.graph_objects as go
    import pandas as pd

    if isinstance(data, list):
        df = pd.DataFrame(data)
    elif hasattr(data, "columns"):
        df = data
    else:
        df = _demo_measurement_data(sensor_id)

    if df.empty:
        df = _demo_measurement_data(sensor_id)

    t_col = "timestamp_mesure" if "timestamp_mesure" in df.columns else (df.columns[0] if len(df.columns) > 0 else "time")
    v_col = "valeur" if "valeur" in df.columns else (df.columns[1] if len(df.columns) > 1 else "value")

    fig = go.Figure(go.Scatter(
        x=pd.to_datetime(df[t_col]) if t_col in df.columns else list(range(len(df))),
        y=df[v_col] if v_col in df.columns else [0] * len(df),
        mode="lines+markers",
        line=dict(color="#3498db", width=2),
        marker=dict(size=4),
        fill="tozeroy",
        fillcolor="rgba(52, 152, 219, 0.1)",
    ))
    fig.update_layout(
        title=f"Sensor #{sensor_id} — Measurement Trend",
        xaxis_title="Time",
        yaxis_title="Value",
        height=350,
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def create_dfa_state_bar(dfa_data: dict) -> Any:
    """Create a bar chart showing DFA state distribution across entities."""
    import plotly.graph_objects as go

    if not dfa_data:
        dfa_data = {
            "Sensors": {"ACTIVE": 35, "INACTIVE": 5, "MAINTENANCE": 6, "SIGNALED": 4},
            "Interventions": {"DEMAND": 8, "TECH1_ASSIGNED": 12, "COMPLETED": 23, "AI_VALIDATED": 7},
            "Vehicles": {"PARKED": 12, "EN_ROUTE": 5, "ARRIVED": 3},
        }

    fig = go.Figure()
    colors = ["#2ecc71", "#3498db", "#f39c12", "#e74c3c", "#9b59b6", "#1abc9c"]

    for i, (entity, states) in enumerate(dfa_data.items()):
        fig.add_trace(go.Bar(
            name=entity,
            x=list(states.keys()),
            y=list(states.values()),
            marker_color=colors[i % len(colors)],
        ))

    fig.update_layout(
        title="DFA State Distribution",
        barmode="group",
        xaxis_title="State",
        yaxis_title="Count",
        height=400,
    )
    return fig


# ---------------------------------------------------------------------------
# Demo data generators
# ---------------------------------------------------------------------------

def _demo_zone_data():
    import pandas as pd
    return pd.DataFrame({
        "nom_zone": [
            "Médina", "Zone Industrielle", "Corniche", "Erriadh",
            "Hammam Sousse Centre", "Parc Vert Akouda",
        ],
        "indice_pollution": [52.3, 78.4, 44.1, 28.7, 38.2, 8.1],
    })


def _demo_intervention_data():
    import pandas as pd
    from datetime import datetime, timedelta
    now = datetime.now()
    return pd.DataFrame({
        "date_demande": [now - timedelta(days=i) for i in range(10)],
        "priorite": ["HIGH", "CRITICAL", "MEDIUM", "LOW", "HIGH",
                     "MEDIUM", "CRITICAL", "LOW", "HIGH", "MEDIUM"],
        "etat_dfa": ["COMPLETED", "DEMAND", "TECH1_ASSIGNED", "COMPLETED", "AI_VALIDATED",
                     "TECH2_VALIDATED", "DEMAND", "COMPLETED", "TECH1_ASSIGNED", "DEMAND"],
    })


def _demo_measurement_data(sensor_id: int):
    import pandas as pd
    import random
    from datetime import datetime, timedelta
    random.seed(sensor_id)
    now = datetime.now()
    return pd.DataFrame({
        "timestamp_mesure": [now - timedelta(hours=i) for i in range(24, 0, -1)],
        "valeur": [random.uniform(20, 80) for _ in range(24)],
    })
