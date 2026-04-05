"""
Analytics page for the Smart City Dashboard.
Interactive data visualisations and KPI metrics.
"""
from __future__ import annotations


def render() -> None:
    """Render the Analytics page."""
    import streamlit as st

    st.title("📊 City Analytics")
    st.markdown("Real-time analytics and visualisations for Neo-Sousse 2030.")

    # ── Filters ───────────────────────────────────────────────────────────────
    with st.expander("🔧 Filters", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            zone_filter = st.selectbox("Zone Type", ["All", "RESIDENTIAL", "COMMERCIAL", "INDUSTRIAL", "GREEN", "MIXED"])
        with col2:
            priority_filter = st.selectbox("Intervention Priority", ["All", "CRITICAL", "HIGH", "MEDIUM", "LOW"])
        with col3:
            sensor_filter = st.selectbox("Sensor Type", ["All", "AIR_QUALITY", "TEMPERATURE", "HUMIDITY", "NOISE", "TRAFFIC"])

    # ── KPI Cards ─────────────────────────────────────────────────────────────
    st.subheader("📌 Key Performance Indicators")
    _render_kpis()
    st.divider()

    # ── Charts row 1 ──────────────────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🌍 Pollution by Zone")
        _render_pollution_chart(zone_filter)

    with col2:
        st.subheader("📡 Sensor Status")
        _render_sensor_pie()

    st.divider()

    # ── Charts row 2 ──────────────────────────────────────────────────────────
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("🔨 Intervention Timeline")
        _render_intervention_timeline()

    with col4:
        st.subheader("⚙️ DFA State Distribution")
        _render_dfa_states()

    st.divider()

    # ── Measurement trend ─────────────────────────────────────────────────────
    st.subheader("📈 Sensor Measurement Trend")
    sensor_id = st.number_input("Sensor ID", min_value=1, value=1, key="trend_sensor_id")
    _render_measurement_trend(int(sensor_id))


def _render_kpis() -> None:
    import streamlit as st
    from dashboard.components.kpi_cards import render_kpi_row, get_city_health_score

    session = _get_session()
    kpis = [
        {"title": "Active Sensors", "value": _query_scalar("SELECT COUNT(*) FROM capteur WHERE Statut='ACTIVE'", 35), "icon": "📡"},
        {"title": "Avg Pollution", "value": f"{_query_scalar('SELECT AVG(Indice_Pollution) FROM zone', 42.3):.1f}", "icon": "🌫️"},
        {"title": "Pending Interventions", "value": _query_scalar("SELECT COUNT(*) FROM intervention WHERE etat_dfa != 'COMPLETED'", 7), "icon": "🔨"},
        {"title": "Registered Citizens", "value": _query_scalar("SELECT COUNT(*) FROM citoyen", 30), "icon": "👥"},
        {"title": "Vehicles Active", "value": _query_scalar("SELECT COUNT(*) FROM vehicule WHERE Statut='IN_USE'", 5), "icon": "🚗"},
    ]
    render_kpi_row(kpis)


def _render_pollution_chart(zone_filter: str = "All") -> None:
    import streamlit as st
    from dashboard.components.charts import create_pollution_chart
    import pandas as pd

    try:
        from config.settings import DATABASE_URL
        from sqlalchemy import create_engine, text
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            q = "SELECT Nom_Zone, Indice_Pollution, Type_Zone FROM zone"
            if zone_filter != "All":
                q += f" WHERE Type_Zone = '{zone_filter}'"
            q += " ORDER BY Indice_Pollution DESC"
            rows = conn.execute(text(q)).fetchall()
            df = pd.DataFrame(rows, columns=["nom_zone", "indice_pollution", "type_zone"])
    except Exception:
        df = pd.DataFrame()

    fig = create_pollution_chart(df)
    st.plotly_chart(fig, use_container_width=True)


def _render_sensor_pie() -> None:
    import streamlit as st
    from dashboard.components.charts import create_sensor_status_pie

    try:
        from config.settings import DATABASE_URL
        from sqlalchemy import create_engine, text
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            rows = conn.execute(text("SELECT Statut, COUNT(*) FROM capteur GROUP BY Statut")).fetchall()
            data = {r[0]: r[1] for r in rows}
    except Exception:
        data = {"ACTIVE": 35, "INACTIVE": 5, "MAINTENANCE": 6, "FAULTY": 4}

    fig = create_sensor_status_pie(data)
    st.plotly_chart(fig, use_container_width=True)


def _render_intervention_timeline() -> None:
    import streamlit as st
    from dashboard.components.charts import create_intervention_timeline
    import pandas as pd

    try:
        from config.settings import DATABASE_URL
        from sqlalchemy import create_engine, text
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            rows = conn.execute(text(
                "SELECT Date_Demande, Priorite, etat_dfa FROM intervention LIMIT 50"
            )).fetchall()
            df = pd.DataFrame(rows, columns=["date_demande", "priorite", "etat_dfa"])
    except Exception:
        df = pd.DataFrame()

    fig = create_intervention_timeline(df)
    st.plotly_chart(fig, use_container_width=True)


def _render_dfa_states() -> None:
    import streamlit as st
    from dashboard.components.charts import create_dfa_state_bar

    try:
        from config.settings import DATABASE_URL
        from sqlalchemy import create_engine, text
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            sensor_rows = conn.execute(text("SELECT etat_dfa, COUNT(*) FROM capteur GROUP BY etat_dfa")).fetchall()
            int_rows = conn.execute(text("SELECT etat_dfa, COUNT(*) FROM intervention GROUP BY etat_dfa")).fetchall()
            veh_rows = conn.execute(text("SELECT etat_dfa, COUNT(*) FROM trajet GROUP BY etat_dfa")).fetchall()
            dfa_data = {
                "Sensors": {r[0]: r[1] for r in sensor_rows},
                "Interventions": {r[0]: r[1] for r in int_rows},
                "Vehicles": {r[0]: r[1] for r in veh_rows},
            }
    except Exception:
        dfa_data = {}

    fig = create_dfa_state_bar(dfa_data)
    st.plotly_chart(fig, use_container_width=True)


def _render_measurement_trend(sensor_id: int) -> None:
    import streamlit as st
    from dashboard.components.charts import create_measurement_trend
    import pandas as pd

    try:
        from config.settings import DATABASE_URL
        from sqlalchemy import create_engine, text
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            rows = conn.execute(text(
                f"SELECT Timestamp_Mesure, Valeur FROM mesure_capteur "
                f"WHERE ID_Capteur = {sensor_id} ORDER BY Timestamp_Mesure DESC LIMIT 100"
            )).fetchall()
            df = pd.DataFrame(rows, columns=["timestamp_mesure", "valeur"])
    except Exception:
        df = pd.DataFrame()

    fig = create_measurement_trend(df, sensor_id)
    st.plotly_chart(fig, use_container_width=True)


def _get_session():
    try:
        from models.base import get_session
        return get_session()
    except Exception:
        return None


def _query_scalar(sql: str, default):
    try:
        from config.settings import DATABASE_URL
        from sqlalchemy import create_engine, text
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            val = conn.execute(text(sql)).scalar()
            if val is None:
                return default
            try:
                return round(float(val), 1) if isinstance(val, float) else int(val)
            except Exception:
                return val
    except Exception:
        return default
