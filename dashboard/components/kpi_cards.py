"""
KPI card components for the Smart City Dashboard.
"""
from __future__ import annotations
from typing import Any, Optional


def render_kpi_card(
    title: str,
    value: Any,
    delta: Optional[str] = None,
    icon: Optional[str] = None,
) -> None:
    """Render a single Streamlit KPI metric card."""
    import streamlit as st

    label = f"{icon} {title}" if icon else title
    st.metric(label=label, value=str(value), delta=delta)


def render_kpi_row(kpis: list[dict]) -> None:
    """Render a horizontal row of KPI cards.

    Each dict should have keys: title, value, delta (optional), icon (optional).
    """
    import streamlit as st

    cols = st.columns(len(kpis))
    for col, kpi in zip(cols, kpis):
        with col:
            render_kpi_card(
                title=kpi.get("title", ""),
                value=kpi.get("value", ""),
                delta=kpi.get("delta"),
                icon=kpi.get("icon"),
            )


def get_sensor_kpis(session: Any) -> list[dict]:
    """Query sensor statistics from the database."""
    try:
        from sqlalchemy import text
        result = session.execute(text(
            "SELECT Statut, COUNT(*) as cnt FROM capteur GROUP BY Statut"
        )).fetchall()
        counts = {row[0]: row[1] for row in result}
        total = sum(counts.values())
        active = counts.get("ACTIVE", 0)
        return [
            {"title": "Total Sensors", "value": total, "icon": "📡"},
            {"title": "Active Sensors", "value": active, "icon": "✅", "delta": f"{active/total*100:.0f}%" if total else "0%"},
            {"title": "In Maintenance", "value": counts.get("MAINTENANCE", 0), "icon": "🔧"},
            {"title": "Faulty Sensors", "value": counts.get("FAULTY", 0), "icon": "⚠️"},
        ]
    except Exception:
        return _demo_sensor_kpis()


def get_intervention_kpis(session: Any) -> list[dict]:
    """Query intervention statistics from the database."""
    try:
        from sqlalchemy import text
        result = session.execute(text(
            "SELECT etat_dfa, COUNT(*) FROM intervention GROUP BY etat_dfa"
        )).fetchall()
        counts = {row[0]: row[1] for row in result}
        total = sum(counts.values())
        return [
            {"title": "Total Interventions", "value": total, "icon": "🔨"},
            {"title": "Pending", "value": counts.get("DEMAND", 0), "icon": "⏳"},
            {"title": "AI Validated", "value": counts.get("AI_VALIDATED", 0), "icon": "🤖"},
            {"title": "Completed", "value": counts.get("COMPLETED", 0), "icon": "✅"},
        ]
    except Exception:
        return _demo_intervention_kpis()


def get_city_health_score(session: Any) -> dict:
    """Calculate overall city health score."""
    try:
        from sqlalchemy import text
        pollution = session.execute(text(
            "SELECT AVG(Indice_Pollution) FROM zone"
        )).scalar() or 50
        active_ratio = session.execute(text(
            "SELECT COUNT(*) FILTER(WHERE Statut='ACTIVE')::float / NULLIF(COUNT(*), 0) FROM capteur"
        )).scalar() or 0.7
        score = max(0, min(100, 100 - float(pollution) * 0.5 + float(active_ratio) * 30))
        return {
            "score": round(score, 1),
            "label": "Excellent" if score > 80 else "Good" if score > 60 else "Fair" if score > 40 else "Poor",
        }
    except Exception:
        return {"score": 72.5, "label": "Good"}


def _demo_sensor_kpis() -> list[dict]:
    return [
        {"title": "Total Sensors", "value": 50, "icon": "📡"},
        {"title": "Active Sensors", "value": 35, "icon": "✅", "delta": "70%"},
        {"title": "In Maintenance", "value": 8, "icon": "🔧"},
        {"title": "Faulty Sensors", "value": 7, "icon": "⚠️"},
    ]


def _demo_intervention_kpis() -> list[dict]:
    return [
        {"title": "Total Interventions", "value": 50, "icon": "🔨"},
        {"title": "Pending", "value": 12, "icon": "⏳"},
        {"title": "AI Validated", "value": 15, "icon": "🤖"},
        {"title": "Completed", "value": 23, "icon": "✅"},
    ]
