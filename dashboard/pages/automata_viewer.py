"""
Automata Viewer page for the Smart City Dashboard.
Visualises DFA states and allows event simulation.
"""
from __future__ import annotations


def render() -> None:
    """Render the Automata Viewer page."""
    import streamlit as st

    st.title("⚙️ DFA State Viewer")
    st.markdown(
        "Monitor and simulate state machines for sensors, interventions, and vehicles."
    )

    tab1, tab2, tab3, tab4 = st.tabs([
        "📡 Sensor DFA", "🔨 Intervention DFA", "🚗 Vehicle DFA", "🚨 Alerts"
    ])

    with tab1:
        _render_sensor_dfa()

    with tab2:
        _render_intervention_dfa()

    with tab3:
        _render_vehicle_dfa()

    with tab4:
        _render_alerts()


def _render_sensor_dfa() -> None:
    import streamlit as st
    from automata.sensor_dfa import SensorDFA, SENSOR_STATES, SENSOR_TRANSITIONS

    st.subheader("📡 Sensor Lifecycle DFA")

    # State diagram
    _render_state_diagram(
        states=SENSOR_STATES,
        transitions=[t.__dict__ for t in SENSOR_TRANSITIONS],
        current_state=st.session_state.get("sensor_state", "INACTIVE"),
        title="Sensor State Machine",
    )

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Simulate Sensor Events**")
        sensor_id = st.number_input("Sensor ID", min_value=1, value=1, key="sensor_id_input")

        if "sensor_dfa" not in st.session_state or st.session_state.get("sensor_dfa_id") != sensor_id:
            st.session_state.sensor_dfa = SensorDFA(sensor_id=int(sensor_id))
            st.session_state.sensor_dfa_id = sensor_id

        dfa: SensorDFA = st.session_state.sensor_dfa
        current = dfa.get_current_state()
        st.info(f"**Current State:** `{current}`")

        valid_events = dfa.get_valid_events()
        event = st.selectbox("Select Event", valid_events or ["(no valid events)"], key="sensor_event")

        if st.button("▶️ Process Event", key="sensor_process"):
            if event and event != "(no valid events)":
                success = dfa.process_event(event)
                if success:
                    new_state = dfa.get_current_state()
                    st.success(f"✅ Transitioned: `{current}` → `{new_state}`")
                    st.session_state.sensor_state = new_state
                else:
                    st.error(f"❌ Invalid event `{event}` in state `{current}`")

        if st.button("🔄 Reset DFA", key="sensor_reset"):
            dfa.reset()
            st.session_state.sensor_state = "INACTIVE"
            st.rerun()

    with col2:
        st.markdown("**Transition History**")
        history = dfa.get_transition_history()
        if history:
            import pandas as pd
            df = pd.DataFrame(history)[["from_state", "event", "to_state", "timestamp"]]
            df.columns = ["From", "Event", "To", "Timestamp"]
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No transitions yet.")


def _render_intervention_dfa() -> None:
    import streamlit as st
    from automata.intervention_dfa import InterventionDFA, INTERVENTION_STATES, INTERVENTION_TRANSITIONS

    st.subheader("🔨 Intervention Workflow DFA")

    _render_state_diagram(
        states=INTERVENTION_STATES,
        transitions=[t.__dict__ for t in INTERVENTION_TRANSITIONS],
        current_state=st.session_state.get("intervention_state", "DEMAND"),
        title="Intervention Workflow",
    )

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        int_id = st.number_input("Intervention ID", min_value=1, value=1, key="int_id_input")
        if "intervention_dfa" not in st.session_state or st.session_state.get("int_dfa_id") != int_id:
            st.session_state.intervention_dfa = InterventionDFA(intervention_id=int(int_id))
            st.session_state.int_dfa_id = int_id

        dfa: InterventionDFA = st.session_state.intervention_dfa
        current = dfa.get_current_state()
        st.info(f"**Current State:** `{current}`")

        valid_events = dfa.get_valid_events()
        event = st.selectbox("Select Event", valid_events or ["(no valid events)"], key="int_event")

        if st.button("▶️ Process Event", key="int_process"):
            if event and event != "(no valid events)":
                success = dfa.process_event(event)
                if success:
                    new_state = dfa.get_current_state()
                    st.success(f"✅ `{current}` → `{new_state}`")
                    st.session_state.intervention_state = new_state
                    if dfa.is_completed():
                        st.balloons()
                else:
                    st.error(f"❌ Invalid: `{event}` from `{current}`")

        if st.button("🔄 Reset", key="int_reset"):
            dfa.reset()
            st.rerun()

    with col2:
        st.markdown("**Transition History**")
        history = dfa.get_transition_history()
        if history:
            import pandas as pd
            df = pd.DataFrame(history)[["from_state", "event", "to_state", "timestamp"]]
            df.columns = ["From", "Event", "To", "Time"]
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No transitions yet.")


def _render_vehicle_dfa() -> None:
    import streamlit as st
    from automata.vehicle_dfa import VehicleDFA, VEHICLE_STATES, VEHICLE_TRANSITIONS

    st.subheader("🚗 Vehicle Trajectory DFA")

    _render_state_diagram(
        states=VEHICLE_STATES,
        transitions=[t.__dict__ for t in VEHICLE_TRANSITIONS],
        current_state=st.session_state.get("vehicle_state", "PARKED"),
        title="Vehicle Trajectory",
    )

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        veh_id = st.number_input("Vehicle ID", min_value=1, value=1, key="veh_id_input")
        if "vehicle_dfa" not in st.session_state or st.session_state.get("veh_dfa_id") != veh_id:
            st.session_state.vehicle_dfa = VehicleDFA(vehicle_id=int(veh_id))
            st.session_state.veh_dfa_id = veh_id

        dfa: VehicleDFA = st.session_state.vehicle_dfa
        current = dfa.get_current_state()
        st.info(f"**Current State:** `{current}`")

        valid_events = dfa.get_valid_events()
        event = st.selectbox("Select Event", valid_events or ["(no valid events)"], key="veh_event")

        if st.button("▶️ Process Event", key="veh_process"):
            if event and event != "(no valid events)":
                success = dfa.process_event(event)
                if success:
                    new_state = dfa.get_current_state()
                    st.success(f"✅ `{current}` → `{new_state}`")
                    st.session_state.vehicle_state = new_state
                else:
                    st.error(f"❌ Invalid: `{event}` from `{current}`")

        if st.button("🔄 Reset", key="veh_reset"):
            dfa.reset()
            st.rerun()

    with col2:
        history = dfa.get_transition_history()
        if history:
            import pandas as pd
            df = pd.DataFrame(history)[["from_state", "event", "to_state", "timestamp"]]
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No transitions yet.")


def _render_alerts() -> None:
    import streamlit as st
    from automata.alerts import AlertManager, AlertSeverity

    st.subheader("🚨 Active Alerts")

    if "alert_manager" not in st.session_state:
        st.session_state.alert_manager = AlertManager()

    manager: AlertManager = st.session_state.alert_manager
    summary = manager.get_summary()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Alerts", summary["total"])
    col2.metric("Active", summary["active"])
    col3.metric("Resolved", summary["resolved"])
    col4.metric("Critical", summary["by_severity"].get("CRITICAL", 0))

    active_alerts = manager.get_active_alerts()
    if active_alerts:
        import pandas as pd
        df = pd.DataFrame([a.to_dict() for a in active_alerts])
        st.dataframe(df[["type", "severity", "message", "entity_type", "timestamp"]], use_container_width=True)

        alert_id = st.text_input("Alert ID to resolve")
        if st.button("✅ Resolve Alert") and alert_id:
            if manager.resolve_alert(alert_id):
                st.success("Alert resolved!")
            else:
                st.error("Alert not found.")
    else:
        st.success("✅ No active alerts!")

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🧪 Add Demo Alert"):
            manager.trigger_alert("DEMO", AlertSeverity.MEDIUM, "This is a demo alert", 1, "Capteur")
            st.rerun()
    with col_b:
        if st.button("🧹 Clear Resolved"):
            n = manager.clear_resolved()
            st.info(f"Cleared {n} resolved alerts.")


def _render_state_diagram(states: list, transitions: list, current_state: str, title: str) -> None:
    """Render a simple state machine diagram using Plotly."""
    import streamlit as st
    import plotly.graph_objects as go
    import math

    n = len(states)
    angles = [2 * math.pi * i / n for i in range(n)]
    x = [math.cos(a) * 2 for a in angles]
    y = [math.sin(a) * 2 for a in angles]
    state_pos = {s: (x[i], y[i]) for i, s in enumerate(states)}

    fig = go.Figure()

    # Edges
    for t in transitions:
        fs = t.get("from_state", t.get("from", ""))
        ts = t.get("to_state", t.get("to", ""))
        ev = t.get("event", "")
        if fs in state_pos and ts in state_pos:
            x0, y0 = state_pos[fs]
            x1, y1 = state_pos[ts]
            fig.add_trace(go.Scatter(
                x=[x0, x1, None], y=[y0, y1, None],
                mode="lines",
                line=dict(width=1.5, color="#aaa"),
                hoverinfo="none",
                showlegend=False,
            ))
            fig.add_annotation(
                x=(x0 + x1) / 2, y=(y0 + y1) / 2,
                text=ev, showarrow=False,
                font=dict(size=9, color="#555"),
            )

    # Nodes
    for state, (sx, sy) in state_pos.items():
        is_current = state == current_state
        fig.add_trace(go.Scatter(
            x=[sx], y=[sy],
            mode="markers+text",
            marker=dict(
                size=50 if is_current else 40,
                color="#2ecc71" if is_current else "#3498db",
                line=dict(width=3 if is_current else 1, color="white"),
            ),
            text=state,
            textposition="middle center",
            textfont=dict(size=9, color="white"),
            hoverinfo="text",
            hovertext=f"State: {state}" + (" (CURRENT)" if is_current else ""),
            showlegend=False,
        ))

    fig.update_layout(
        title=title,
        height=320,
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=40, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)
