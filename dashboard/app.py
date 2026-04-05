"""
Main Streamlit application for Smart City Analytics Platform.
Neo-Sousse 2030 — Smart City Dashboard.
"""
import streamlit as st

st.set_page_config(
    page_title="Smart City Platform - Neo-Sousse 2030",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Sidebar styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
}
[data-testid="stSidebar"] * {
    color: #e0e0e0 !important;
}

/* Main area */
.main .block-container { padding-top: 1rem; }

/* KPI cards */
[data-testid="metric-container"] {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 1rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

/* Title */
h1 { color: #1a1a2e !important; }

/* Buttons */
.stButton > button {
    border-radius: 6px;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)


def _init_session_state() -> None:
    """Initialise Streamlit session state defaults."""
    defaults = {
        "current_page": "Home",
        "sensor_state": "INACTIVE",
        "intervention_state": "DEMAND",
        "vehicle_state": "PARKED",
        "nl_query": "Show the 5 most polluted zones",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def _render_sidebar() -> str:
    """Render navigation sidebar. Returns selected page name."""
    with st.sidebar:
        st.markdown(
            "<h2 style='text-align: center; color: #4fc3f7;'>🏙️ Neo-Sousse 2030</h2>",
            unsafe_allow_html=True,
        )
        st.markdown("<p style='text-align: center; font-size: 0.8em;'>Smart City Analytics Platform</p>", unsafe_allow_html=True)
        st.divider()

        pages = {
            "🏠 Home": "Home",
            "📊 Analytics": "Analytics",
            "🔍 Query Builder": "Query Builder",
            "⚙️ Automata Viewer": "Automata Viewer",
            "🤖 AI Reports": "AI Reports",
        }

        for label, page_key in pages.items():
            if st.sidebar.button(label, key=f"nav_{page_key}", use_container_width=True):
                st.session_state.current_page = page_key

        st.sidebar.divider()
        st.sidebar.markdown("### 📡 System Status")

        # Quick DB status
        try:
            from config.settings import DATABASE_URL
            from sqlalchemy import create_engine, text
            engine = create_engine(DATABASE_URL, connect_args={"connect_timeout": 2})
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            st.sidebar.success("✅ Database Connected")
        except Exception:
            st.sidebar.warning("⚠️ DB Offline (Demo Mode)")

        st.sidebar.markdown(
            "<p style='font-size: 0.7em; text-align: center;'>v1.0.0 · Neo-Sousse 2030</p>",
            unsafe_allow_html=True,
        )

    return st.session_state.get("current_page", "Home")


def _render_home() -> None:
    """Render the Home page with overview and map."""
    st.title("🏙️ Smart City Analytics Platform")
    st.markdown("**Neo-Sousse 2030** — Real-time city monitoring and analytics")

    # KPI row
    from dashboard.components.kpi_cards import render_kpi_row
    kpis = [
        {"title": "Active Sensors", "value": "35 / 50", "icon": "📡", "delta": "+3"},
        {"title": "Avg Pollution", "value": "42.3 AQI", "icon": "🌫️", "delta": "-2.1"},
        {"title": "Interventions", "value": "7 pending", "icon": "🔨"},
        {"title": "Citizens", "value": "30", "icon": "👥"},
        {"title": "Vehicles Active", "value": "5", "icon": "🚗"},
    ]
    render_kpi_row(kpis)

    st.divider()

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("🗺️ City Overview Map")
        from dashboard.components.maps import create_city_map, render_map_in_streamlit
        m = create_city_map()
        render_map_in_streamlit(m)

    with col2:
        st.subheader("📋 Quick Stats")

        from dashboard.components.charts import create_sensor_status_pie
        fig = create_sensor_status_pie({"ACTIVE": 35, "INACTIVE": 5, "MAINTENANCE": 6, "FAULTY": 4})
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Architecture overview
    with st.expander("ℹ️ Platform Architecture"):
        st.markdown("""
        ```
        ┌─────────────────────────────────────────────────────────────────┐
        │              Smart City Platform — Neo-Sousse 2030              │
        ├─────────────────────────────────────────────────────────────────┤
        │  Dashboard (Streamlit)  │  Compiler (NL→SQL)  │  Automata DFA  │
        │  - Analytics            │  - Lexer             │  - Sensor DFA  │
        │  - Query Builder        │  - Parser            │  - Intervention│
        │  - AI Reports           │  - Code Generator    │  - Vehicle DFA │
        │  - Automata Viewer      │  - Query Builder     │  - Alerts      │
        ├─────────────────────────────────────────────────────────────────┤
        │              AI Module (LangChain + Fallback)                   │
        ├─────────────────────────────────────────────────────────────────┤
        │              PostgreSQL Database (SQLAlchemy ORM)               │
        └─────────────────────────────────────────────────────────────────┘
        ```
        """)


def main() -> None:
    """Main application entry point."""
    _init_session_state()
    current_page = _render_sidebar()

    if current_page == "Home":
        _render_home()
    elif current_page == "Analytics":
        from dashboard.pages.analytics import render
        render()
    elif current_page == "Query Builder":
        from dashboard.pages.query_builder import render
        render()
    elif current_page == "Automata Viewer":
        from dashboard.pages.automata_viewer import render
        render()
    elif current_page == "AI Reports":
        from dashboard.pages.reports import render
        render()
    else:
        _render_home()


if __name__ == "__main__":
    main()
