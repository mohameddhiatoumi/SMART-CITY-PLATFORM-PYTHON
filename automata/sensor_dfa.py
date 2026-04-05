"""
Sensor lifecycle DFA for the Smart City Platform.
Manages sensor state transitions from INACTIVE through ACTIVE, SIGNALED, MAINTENANCE, OUT_OF_SERVICE.
"""
from __future__ import annotations
from datetime import datetime, timedelta
from typing import Optional, Any

from automata.dfa_engine import DFAEngine, DFATransition
from automata.alerts import AlertManager, AlertSeverity

# State constants
INACTIVE = "INACTIVE"
ACTIVE = "ACTIVE"
SIGNALED = "SIGNALED"
MAINTENANCE = "MAINTENANCE"
OUT_OF_SERVICE = "OUT_OF_SERVICE"

SENSOR_STATES = [INACTIVE, ACTIVE, SIGNALED, MAINTENANCE, OUT_OF_SERVICE]

SENSOR_TRANSITIONS = [
    DFATransition(INACTIVE,      "activate",           ACTIVE),
    DFATransition(ACTIVE,        "signal_fault",       SIGNALED),
    DFATransition(ACTIVE,        "deactivate",         INACTIVE),
    DFATransition(ACTIVE,        "schedule_maintenance", MAINTENANCE),
    DFATransition(SIGNALED,      "assign_maintenance", MAINTENANCE),
    DFATransition(SIGNALED,      "deactivate",         OUT_OF_SERVICE),
    DFATransition(MAINTENANCE,   "repair_complete",    ACTIVE),
    DFATransition(MAINTENANCE,   "decommission",       OUT_OF_SERVICE),
    DFATransition(OUT_OF_SERVICE,"replace",            INACTIVE),
]


class SensorDFA:
    """
    Sensor lifecycle Deterministic Finite Automaton.

    Wraps DFAEngine with sensor-specific logic including
    downtime monitoring and database state persistence.

    States: INACTIVE → ACTIVE ↔ SIGNALED → MAINTENANCE → ACTIVE
                                          ↘ OUT_OF_SERVICE → INACTIVE

    Usage::
        dfa = SensorDFA(sensor_id=1)
        dfa.process_event("activate")
        dfa.process_event("signal_fault")
    """

    def __init__(
        self,
        sensor_id: int,
        initial_state: str = INACTIVE,
        alert_manager: Optional[AlertManager] = None,
    ) -> None:
        self.sensor_id = sensor_id
        self.alert_manager = alert_manager or AlertManager()
        self._engine = DFAEngine(
            name=f"SensorDFA-{sensor_id}",
            states=SENSOR_STATES,
            initial_state=initial_state,
            transitions=SENSOR_TRANSITIONS,
            accepting_states=[ACTIVE],
        )
        self._last_active_time: Optional[datetime] = None

    # ------------------------------------------------------------------
    # Delegated DFA methods
    # ------------------------------------------------------------------

    def process_event(self, event: str, context: Optional[dict] = None) -> bool:
        """Process an event and update sensor state."""
        result = self._engine.process_event(event, context)
        if result:
            if self._engine.current_state == ACTIVE:
                self._last_active_time = datetime.now()
            self._check_downtime_alert()
        return result

    def get_current_state(self) -> str:
        return self._engine.get_current_state()

    def get_valid_events(self) -> list[str]:
        return self._engine.get_valid_events()

    def get_transition_history(self) -> list[dict]:
        return self._engine.get_transition_history()

    def reset(self) -> None:
        self._engine.reset()
        self._last_active_time = None

    def get_all_transitions(self) -> list[dict]:
        return self._engine.get_all_transitions()

    # ------------------------------------------------------------------
    # Sensor-specific logic
    # ------------------------------------------------------------------

    def _check_downtime_alert(self) -> None:
        """Trigger alert if sensor has been non-active for > 24 hours."""
        if self._last_active_time is None:
            return
        downtime = datetime.now() - self._last_active_time
        state = self._engine.current_state
        if state in (INACTIVE, OUT_OF_SERVICE, MAINTENANCE) and downtime > timedelta(hours=24):
            self.alert_manager.trigger_alert(
                alert_type="SENSOR_DOWN",
                severity=AlertSeverity.HIGH,
                message=f"Sensor {self.sensor_id} has been {state} for {downtime}",
                entity_id=self.sensor_id,
                entity_type="Capteur",
            )

    def apply_to_db(self, event: str, session: Any) -> bool:
        """
        Process event and persist new state to database.

        Args:
            event: DFA event string
            session: SQLAlchemy session

        Returns:
            True if transition succeeded
        """
        result = self.process_event(event)
        if result and session is not None:
            try:
                from models.capteur import Capteur
                sensor = session.query(Capteur).filter_by(ID_Capteur=self.sensor_id).first()
                if sensor:
                    sensor.etat_dfa = self._engine.current_state
                    sensor.timestamp_derniere_transition = datetime.now()
                    session.commit()
            except Exception:
                if session:
                    session.rollback()
        return result

    def __repr__(self) -> str:
        return f"<SensorDFA sensor_id={self.sensor_id} state={self.get_current_state()!r}>"
