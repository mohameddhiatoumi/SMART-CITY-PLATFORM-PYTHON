"""
Tests for the Smart City automata module.
All tests run without a database connection.
"""
import pytest
from datetime import datetime, timedelta
from automata.dfa_engine import DFAEngine, DFATransition
from automata.sensor_dfa import SensorDFA, INACTIVE, ACTIVE, SIGNALED, MAINTENANCE, OUT_OF_SERVICE
from automata.intervention_dfa import InterventionDFA, DEMAND, TECH1_ASSIGNED, TECH2_VALIDATED, AI_VALIDATED, COMPLETED
from automata.vehicle_dfa import VehicleDFA, PARKED, EN_ROUTE, BROKEN_DOWN, ARRIVED
from automata.alerts import AlertManager, AlertSeverity, Alert


class TestDFAEngine:
    """Tests for the base DFAEngine class."""

    def _make_simple_engine(self) -> DFAEngine:
        return DFAEngine(
            name="TestDFA",
            states=["OFF", "ON", "STANDBY"],
            initial_state="OFF",
            transitions=[
                DFATransition("OFF", "turn_on", "ON"),
                DFATransition("ON", "turn_off", "OFF"),
                DFATransition("ON", "standby", "STANDBY"),
                DFATransition("STANDBY", "resume", "ON"),
            ],
            accepting_states=["ON"],
        )

    def test_initial_state(self):
        engine = self._make_simple_engine()
        assert engine.get_current_state() == "OFF"

    def test_valid_transition(self):
        engine = self._make_simple_engine()
        assert engine.process_event("turn_on") is True
        assert engine.get_current_state() == "ON"

    def test_invalid_transition(self):
        engine = self._make_simple_engine()
        assert engine.process_event("turn_off") is False  # OFF has no turn_off
        assert engine.get_current_state() == "OFF"  # state unchanged

    def test_multiple_transitions(self):
        engine = self._make_simple_engine()
        engine.process_event("turn_on")
        engine.process_event("standby")
        assert engine.get_current_state() == "STANDBY"

    def test_accepting_state(self):
        engine = self._make_simple_engine()
        engine.process_event("turn_on")
        assert engine.is_in_accepting_state() is True

    def test_not_accepting_state(self):
        engine = self._make_simple_engine()
        assert engine.is_in_accepting_state() is False

    def test_reset(self):
        engine = self._make_simple_engine()
        engine.process_event("turn_on")
        engine.reset()
        assert engine.get_current_state() == "OFF"

    def test_transition_history(self):
        engine = self._make_simple_engine()
        engine.process_event("turn_on")
        engine.process_event("standby")
        history = engine.get_transition_history()
        assert len(history) == 2
        assert history[0]["event"] == "turn_on"
        assert history[1]["event"] == "standby"

    def test_valid_events(self):
        engine = self._make_simple_engine()
        events = engine.get_valid_events()
        assert "turn_on" in events

    def test_validate_event_sequence_valid(self):
        engine = self._make_simple_engine()
        assert engine.validate_event_sequence(["turn_on", "standby", "resume"]) is True

    def test_validate_event_sequence_invalid(self):
        engine = self._make_simple_engine()
        assert engine.validate_event_sequence(["turn_off"]) is False

    def test_get_all_transitions(self):
        engine = self._make_simple_engine()
        transitions = engine.get_all_transitions()
        assert len(transitions) == 4


class TestSensorDFA:
    """Tests for SensorDFA."""

    def test_initial_state_inactive(self):
        dfa = SensorDFA(sensor_id=1)
        assert dfa.get_current_state() == INACTIVE

    def test_activate(self):
        dfa = SensorDFA(sensor_id=1)
        assert dfa.process_event("activate") is True
        assert dfa.get_current_state() == ACTIVE

    def test_active_to_signaled(self):
        dfa = SensorDFA(sensor_id=1)
        dfa.process_event("activate")
        dfa.process_event("signal_fault")
        assert dfa.get_current_state() == SIGNALED

    def test_signaled_to_maintenance(self):
        dfa = SensorDFA(sensor_id=1)
        dfa.process_event("activate")
        dfa.process_event("signal_fault")
        dfa.process_event("assign_maintenance")
        assert dfa.get_current_state() == MAINTENANCE

    def test_maintenance_to_active(self):
        dfa = SensorDFA(sensor_id=1)
        dfa.process_event("activate")
        dfa.process_event("signal_fault")
        dfa.process_event("assign_maintenance")
        dfa.process_event("repair_complete")
        assert dfa.get_current_state() == ACTIVE

    def test_maintenance_to_out_of_service(self):
        dfa = SensorDFA(sensor_id=1)
        dfa.process_event("activate")
        dfa.process_event("signal_fault")
        dfa.process_event("assign_maintenance")
        dfa.process_event("decommission")
        assert dfa.get_current_state() == OUT_OF_SERVICE

    def test_out_of_service_to_inactive(self):
        dfa = SensorDFA(sensor_id=1)
        dfa.process_event("activate")
        dfa.process_event("signal_fault")
        dfa.process_event("deactivate")
        dfa.process_event("replace")
        assert dfa.get_current_state() == INACTIVE

    def test_invalid_event_rejected(self):
        dfa = SensorDFA(sensor_id=1)
        result = dfa.process_event("invalid_event")
        assert result is False

    def test_reset(self):
        dfa = SensorDFA(sensor_id=1)
        dfa.process_event("activate")
        dfa.reset()
        assert dfa.get_current_state() == INACTIVE

    def test_transition_history(self):
        dfa = SensorDFA(sensor_id=1)
        dfa.process_event("activate")
        dfa.process_event("signal_fault")
        history = dfa.get_transition_history()
        assert len(history) == 2

    def test_apply_to_db_without_session(self):
        dfa = SensorDFA(sensor_id=1)
        result = dfa.apply_to_db("activate", None)
        assert result is True
        assert dfa.get_current_state() == ACTIVE

    def test_repr(self):
        dfa = SensorDFA(sensor_id=99)
        assert "99" in repr(dfa)

    def test_all_transitions_defined(self):
        dfa = SensorDFA(sensor_id=1)
        transitions = dfa.get_all_transitions()
        assert len(transitions) >= 8  # at least 8 defined transitions


class TestInterventionDFA:
    """Tests for InterventionDFA."""

    def test_initial_state_demand(self):
        dfa = InterventionDFA(intervention_id=1)
        assert dfa.get_current_state() == DEMAND

    def test_assign_tech1(self):
        dfa = InterventionDFA(intervention_id=1)
        assert dfa.process_event("assign_tech1") is True
        assert dfa.get_current_state() == TECH1_ASSIGNED

    def test_validate_tech2(self):
        dfa = InterventionDFA(intervention_id=1)
        dfa.process_event("assign_tech1")
        dfa.process_event("validate_tech2")
        assert dfa.get_current_state() == TECH2_VALIDATED

    def test_validate_ai(self):
        dfa = InterventionDFA(intervention_id=1)
        dfa.process_event("assign_tech1")
        dfa.process_event("validate_tech2")
        dfa.process_event("validate_ai")
        assert dfa.get_current_state() == AI_VALIDATED

    def test_complete(self):
        dfa = InterventionDFA(intervention_id=1)
        dfa.process_event("assign_tech1")
        dfa.process_event("validate_tech2")
        dfa.process_event("validate_ai")
        dfa.process_event("complete")
        assert dfa.get_current_state() == COMPLETED

    def test_is_completed_accepting_state(self):
        dfa = InterventionDFA(intervention_id=1)
        dfa.process_event("assign_tech1")
        dfa.process_event("validate_tech2")
        dfa.process_event("validate_ai")
        dfa.process_event("complete")
        assert dfa.is_completed() is True

    def test_cancel_resets_to_demand(self):
        dfa = InterventionDFA(intervention_id=1)
        dfa.process_event("assign_tech1")
        dfa.process_event("cancel")
        assert dfa.get_current_state() == DEMAND

    def test_full_workflow(self):
        dfa = InterventionDFA(intervention_id=42)
        events = ["assign_tech1", "validate_tech2", "validate_ai", "complete"]
        for event in events:
            assert dfa.process_event(event) is True
        assert dfa.is_completed()

    def test_apply_to_db_without_session(self):
        dfa = InterventionDFA(intervention_id=1)
        result = dfa.apply_to_db("assign_tech1", None)
        assert result is True

    def test_repr(self):
        dfa = InterventionDFA(intervention_id=77)
        assert "77" in repr(dfa)

    def test_validate_event_sequence(self):
        dfa = InterventionDFA(intervention_id=1)
        assert dfa._engine.validate_event_sequence(
            ["assign_tech1", "validate_tech2", "validate_ai", "complete"]
        ) is True


class TestVehicleDFA:
    """Tests for VehicleDFA."""

    def test_initial_state_parked(self):
        dfa = VehicleDFA(vehicle_id=1)
        assert dfa.get_current_state() == PARKED

    def test_depart(self):
        dfa = VehicleDFA(vehicle_id=1)
        assert dfa.process_event("depart") is True
        assert dfa.get_current_state() == EN_ROUTE

    def test_arrive(self):
        dfa = VehicleDFA(vehicle_id=1)
        dfa.process_event("depart")
        dfa.process_event("arrive")
        assert dfa.get_current_state() == ARRIVED

    def test_return(self):
        dfa = VehicleDFA(vehicle_id=1)
        dfa.process_event("depart")
        dfa.process_event("arrive")
        dfa.process_event("return")
        assert dfa.get_current_state() == PARKED

    def test_breakdown(self):
        dfa = VehicleDFA(vehicle_id=1)
        dfa.process_event("depart")
        dfa.process_event("breakdown")
        assert dfa.get_current_state() == BROKEN_DOWN

    def test_repair_after_breakdown(self):
        dfa = VehicleDFA(vehicle_id=1)
        dfa.process_event("depart")
        dfa.process_event("breakdown")
        dfa.process_event("repair")
        assert dfa.get_current_state() == EN_ROUTE

    def test_tow_after_breakdown(self):
        dfa = VehicleDFA(vehicle_id=1)
        dfa.process_event("depart")
        dfa.process_event("breakdown")
        dfa.process_event("tow")
        assert dfa.get_current_state() == PARKED

    def test_invalid_event(self):
        dfa = VehicleDFA(vehicle_id=1)
        assert dfa.process_event("fly") is False

    def test_reset(self):
        dfa = VehicleDFA(vehicle_id=1)
        dfa.process_event("depart")
        dfa.reset()
        assert dfa.get_current_state() == PARKED

    def test_apply_to_db_without_session(self):
        dfa = VehicleDFA(vehicle_id=1)
        result = dfa.apply_to_db("depart", None)
        assert result is True

    def test_repr(self):
        dfa = VehicleDFA(vehicle_id=55)
        assert "55" in repr(dfa)


class TestAlerts:
    """Tests for the AlertManager class."""

    def test_trigger_alert_returns_alert(self):
        manager = AlertManager()
        alert = manager.trigger_alert("TEST", AlertSeverity.HIGH, "Test message", 1, "Capteur")
        assert isinstance(alert, Alert)
        assert alert.severity == AlertSeverity.HIGH

    def test_alert_starts_unresolved(self):
        manager = AlertManager()
        alert = manager.trigger_alert("TEST", AlertSeverity.LOW, "msg", 1, "Capteur")
        assert alert.resolved is False

    def test_resolve_alert(self):
        manager = AlertManager()
        alert = manager.trigger_alert("TEST", AlertSeverity.MEDIUM, "msg", 1, "Capteur")
        result = manager.resolve_alert(alert.id)
        assert result is True
        assert alert.resolved is True

    def test_resolve_nonexistent_alert(self):
        manager = AlertManager()
        assert manager.resolve_alert("nonexistent-id") is False

    def test_get_active_alerts(self):
        manager = AlertManager()
        manager.trigger_alert("A", AlertSeverity.HIGH, "a", 1, "Capteur")
        manager.trigger_alert("B", AlertSeverity.LOW, "b", 2, "Zone")
        alerts = manager.get_active_alerts()
        assert len(alerts) == 2

    def test_get_active_alerts_sorted_by_severity(self):
        manager = AlertManager()
        manager.trigger_alert("A", AlertSeverity.LOW, "low", 1, "Capteur")
        manager.trigger_alert("B", AlertSeverity.CRITICAL, "critical", 2, "Zone")
        alerts = manager.get_active_alerts()
        assert alerts[0].severity == AlertSeverity.CRITICAL

    def test_get_alerts_by_entity(self):
        manager = AlertManager()
        manager.trigger_alert("A", AlertSeverity.HIGH, "a", 1, "Capteur")
        manager.trigger_alert("B", AlertSeverity.LOW, "b", 2, "Zone")
        alerts = manager.get_alerts_by_entity(1, "Capteur")
        assert len(alerts) == 1
        assert alerts[0].entity_id == 1

    def test_check_sensor_downtime_over_threshold(self):
        manager = AlertManager()
        old_time = datetime.now() - timedelta(hours=25)
        alert = manager.check_sensor_downtime(1, old_time)
        assert alert is not None
        assert alert.type == "SENSOR_DOWNTIME"

    def test_check_sensor_downtime_under_threshold(self):
        manager = AlertManager()
        recent_time = datetime.now() - timedelta(hours=12)
        alert = manager.check_sensor_downtime(1, recent_time)
        assert alert is None

    def test_check_intervention_timeout_over(self):
        manager = AlertManager()
        old_time = datetime.now() - timedelta(hours=25)
        alert = manager.check_intervention_timeout(1, old_time, "DEMAND")
        assert alert is not None

    def test_check_intervention_timeout_under(self):
        manager = AlertManager()
        recent_time = datetime.now() - timedelta(hours=5)
        alert = manager.check_intervention_timeout(1, recent_time, "DEMAND")
        assert alert is None

    def test_check_vehicle_route_over_threshold(self):
        manager = AlertManager()
        old_time = datetime.now() - timedelta(hours=3)
        alert = manager.check_vehicle_route_time(1, old_time)
        assert alert is not None

    def test_alert_to_dict(self):
        manager = AlertManager()
        alert = manager.trigger_alert("TEST", AlertSeverity.HIGH, "msg", 1, "Capteur")
        d = alert.to_dict()
        assert "id" in d
        assert "severity" in d
        assert d["severity"] == "HIGH"

    def test_summary(self):
        manager = AlertManager()
        manager.trigger_alert("A", AlertSeverity.CRITICAL, "c", 1, "Capteur")
        summary = manager.get_summary()
        assert summary["total"] >= 1
        assert summary["active"] >= 1
        assert "by_severity" in summary

    def test_clear_resolved(self):
        manager = AlertManager()
        alert = manager.trigger_alert("A", AlertSeverity.LOW, "a", 1, "Capteur")
        manager.resolve_alert(alert.id)
        n = manager.clear_resolved()
        assert n == 1
        assert len(manager.get_all_alerts()) == 0
