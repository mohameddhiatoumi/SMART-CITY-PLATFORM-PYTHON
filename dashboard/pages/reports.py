"""
Reports page for the Smart City Dashboard.
AI-generated insights and report management.
"""
from __future__ import annotations


def render() -> None:
    """Render the AI Reports page."""
    import streamlit as st

    st.title("🤖 AI-Generated Reports")
    st.markdown("Generate intelligent reports using AI analysis of city data.")

    # ── Sidebar config ────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### Report Settings")
        use_openai = st.checkbox("Use OpenAI API", value=False, help="Requires OPENAI_API_KEY in .env")
        if use_openai:
            import os
            key = os.getenv("OPENAI_API_KEY", "")
            if not key or key == "your_openai_api_key_here":
                st.warning("⚠️ OPENAI_API_KEY not set. Using templates.")
                use_openai = False

    from ai.report_generator import ReportGenerator
    generator = ReportGenerator(use_openai=use_openai)

    mode_label = "🤖 OpenAI" if use_openai else "📄 Template"
    st.info(f"Report mode: **{mode_label}**")

    tab1, tab2, tab3, tab4 = st.tabs([
        "🌍 City Dashboard", "🌫️ Air Quality", "🔧 Maintenance", "🔨 Interventions"
    ])

    # ── City Dashboard Report ─────────────────────────────────────────────────
    with tab1:
        st.subheader("City Health Dashboard Report")
        metrics = _get_city_metrics()
        col1, col2 = st.columns([3, 1])
        with col2:
            st.json(metrics)
        with col1:
            if st.button("📊 Generate City Report", type="primary", key="city_report"):
                with st.spinner("Generating..."):
                    report = generator.generate_city_dashboard_report(metrics)
                st.session_state["city_report_text"] = report

        if "city_report_text" in st.session_state:
            st.markdown(st.session_state["city_report_text"])
            st.download_button(
                "⬇️ Download Report",
                st.session_state["city_report_text"],
                file_name="city_health_report.md",
                mime="text/markdown",
            )

    # ── Air Quality Report ────────────────────────────────────────────────────
    with tab2:
        st.subheader("Air Quality Analysis")
        zone_data = _get_zone_data()
        zone_name = st.selectbox("Select Zone", [z["zone_name"] for z in zone_data], key="aq_zone")
        selected = next((z for z in zone_data if z["zone_name"] == zone_name), zone_data[0])

        if st.button("🌫️ Generate Air Quality Report", type="primary", key="aq_report"):
            with st.spinner("Generating..."):
                report = generator.generate_air_quality_report(selected)
            st.session_state["aq_report_text"] = report

        if "aq_report_text" in st.session_state:
            st.markdown(st.session_state["aq_report_text"])
            st.download_button(
                "⬇️ Download", st.session_state["aq_report_text"],
                file_name="air_quality_report.md", mime="text/markdown",
            )

    # ── Maintenance Report ────────────────────────────────────────────────────
    with tab3:
        st.subheader("Sensor Maintenance Report")
        sensor_data = _get_sensor_data()
        if st.button("🔧 Generate Maintenance Report", type="primary", key="maint_report"):
            with st.spinner("Generating..."):
                report = generator.generate_maintenance_report(sensor_data)
            st.session_state["maint_report_text"] = report

        if "maint_report_text" in st.session_state:
            st.markdown(st.session_state["maint_report_text"])

    # ── Interventions Report ──────────────────────────────────────────────────
    with tab4:
        st.subheader("Intervention Summary Report")
        int_data = _get_intervention_data()
        if st.button("🔨 Generate Intervention Report", type="primary", key="int_report"):
            with st.spinner("Generating..."):
                report = generator.generate_intervention_summary(int_data)
            st.session_state["int_report_text"] = report

        if "int_report_text" in st.session_state:
            st.markdown(st.session_state["int_report_text"])

    # ── Report History ────────────────────────────────────────────────────────
    with st.expander("📚 Report History"):
        history = generator.get_report_history()
        if history:
            import pandas as pd
            st.dataframe(pd.DataFrame(history), use_container_width=True)
        else:
            st.info("No reports generated yet.")


def _get_city_metrics() -> dict:
    try:
        from config.settings import DATABASE_URL
        from sqlalchemy import create_engine, text
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            active_sensors = conn.execute(text("SELECT COUNT(*) FROM capteur WHERE Statut='ACTIVE'")).scalar()
            pending = conn.execute(text("SELECT COUNT(*) FROM intervention WHERE etat_dfa != 'COMPLETED'")).scalar()
            avg_pollution = float(conn.execute(text("SELECT AVG(Indice_Pollution) FROM zone")).scalar() or 50)
            citizens = conn.execute(text("SELECT COUNT(*) FROM citoyen")).scalar()
            return {"active_sensors": active_sensors, "interventions_pending": pending,
                    "avg_pollution": avg_pollution, "citizens": citizens}
    except Exception:
        return {"active_sensors": 35, "interventions_pending": 7, "avg_pollution": 42.3, "citizens": 30}


def _get_zone_data() -> list[dict]:
    try:
        from config.settings import DATABASE_URL
        from sqlalchemy import create_engine, text
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            rows = conn.execute(text("SELECT Nom_Zone, Indice_Pollution FROM zone ORDER BY Indice_Pollution DESC LIMIT 10")).fetchall()
            return [{"zone_name": r[0], "pollution_index": float(r[1])} for r in rows]
    except Exception:
        return [
            {"zone_name": "Médina de Sousse", "pollution_index": 52.3},
            {"zone_name": "Zone Industrielle", "pollution_index": 78.4},
            {"zone_name": "Corniche", "pollution_index": 44.1},
            {"zone_name": "Parc Vert Akouda", "pollution_index": 8.1},
        ]


def _get_sensor_data() -> list[dict]:
    try:
        from config.settings import DATABASE_URL
        from sqlalchemy import create_engine, text
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            rows = conn.execute(text("SELECT ID_Capteur, Type_Capteur, Statut, etat_dfa FROM capteur LIMIT 20")).fetchall()
            return [{"id_capteur": r[0], "type_capteur": r[1], "statut": r[2], "etat_dfa": r[3]} for r in rows]
    except Exception:
        return [{"id_capteur": i, "type_capteur": t, "statut": s, "etat_dfa": s}
                for i, t, s in [(1, "AIR_QUALITY", "ACTIVE"), (2, "TEMPERATURE", "MAINTENANCE"),
                                (3, "NOISE", "FAULTY"), (4, "TRAFFIC", "ACTIVE")]]


def _get_intervention_data() -> list[dict]:
    try:
        from config.settings import DATABASE_URL
        from sqlalchemy import create_engine, text
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            rows = conn.execute(text("SELECT ID_Intervention, Priorite, etat_dfa, Valide_IA FROM intervention LIMIT 30")).fetchall()
            return [{"id": r[0], "priorite": r[1], "etat_dfa": r[2], "valide_ia": r[3]} for r in rows]
    except Exception:
        return [{"id": i, "priorite": p, "etat_dfa": e, "valide_ia": v}
                for i, p, e, v in [
                    (1, "HIGH", "COMPLETED", True), (2, "CRITICAL", "DEMAND", False),
                    (3, "MEDIUM", "AI_VALIDATED", True), (4, "LOW", "TECH1_ASSIGNED", False)]]
