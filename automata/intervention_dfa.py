"""
Intervention validation DFA for the Smart City Platform.
Manages the 5-stage intervention approval workflow.
"""
from __future__ import annotations
from datetime import datetime, timedelta
from typing import Optional, Any

from automata.dfa_engine import DFAEngine, DFATransition
from automata.alerts import AlertManager, AlertSeverity

# State constants
DEMAND = "DEMAND"
TECH1_ASSIGNED = "TECH1_ASSIGNED"
TECH2_VALIDATED = "TECH2_VALIDATED"
AI_VALIDATED = "AI_VALIDATED"
COMPLETED = "COMPLETED"

INTERVENTION_STATES = [DEMAND, TECH1_ASSIGNED, TECH2_VALIDATED, AI_VALIDATED, COMPLETED]

INTERVENTION_TRANSITIONS = [
    DFATransition(DEMAND,          "assign_tech1",  TECH1_ASSIGNED),
    DFATransition(TECH1_ASSIGNED,  "validate_tech2", TECH2_VALIDATED),
    DFATransition(TECH2_VALIDATED, "validate_ai",   AI_VALIDATED),
    DFATransition(AI_VALIDATED,    "complete",      COMPLETED),
    # Cancel (any state → DEMAND)
    DFATransition(TECH1_ASSIGNED,  "cancel",        DEMAND),
    DFATransition(TECH2_VALIDATED, "cancel",        DEMAND),
    DFATransition(AI_VALIDATED,    "cancel",        DEMAND),
]

# Timeout thresholds per state (hours)
STATE_TIMEOUTS = {
    DEMAND: 24,
    TECH1_ASSIGNED: 48,
    TECH2_VALIDATED: 24,
    AI_VALIDATED: 12,
}


class InterventionDFA:
    """
    Intervention validation workflow DFA.

    Workflow::
        DEMAND → TECH1_ASSIGNED → TECH2_VALIDATED → AI_VALIDATED → COMPLETED
        (any intermediate state can be cancelled back to DEMAND)

    Usage::
        dfa = InterventionDFA(intervention_id=42)
        dfa.process_event("assign_tech1")
        dfa.process_event("validate_tech2")
    """

    def __init__(
        self,
        intervention_id: int,
        initial_state: str = DEMAND,
        alert_manager: Optional[AlertManager] = None,
    ) -> None:
        self.intervention_id = intervention_id
        self.alert_manager = alert_manager or AlertManager()
        self._state_entry_times: dict[str, datetime] = {initial_state: datetime.now()}
        self._engine = DFAEngine(
            name=f"InterventionDFA-{intervention_id}",
            states=INTERVENTION_STATES,
            initial_state=initial_state,
            transitions=INTERVENTION_TRANSITIONS,
            accepting_states=[COMPLETED],
        )

    # ------------------------------------------------------------------
    # Delegated DFA methods
    # ------------------------------------------------------------------

    def process_event(self, event: str, context: Optional[dict] = None) -> bool:
        """Process an event and update intervention state."""
        result = self._engine.process_event(event, context)
        if result:
            self._state_entry_times[self._engine.current_state] = datetime.now()
            self._check_timeout_alert()
        return result

    def get_current_state(self) -> str:
        return self._engine.get_current_state()

    def get_valid_events(self) -> list[str]:
        return self._engine.get_valid_events()

    def get_transition_history(self) -> list[dict]:
        return self._engine.get_transition_history()

    def reset(self) -> None:
        self._engine.reset()
        self._state_entry_times = {DEMAND: datetime.now()}

    def get_all_transitions(self) -> list[dict]:
        return self._engine.get_all_transitions()

    def is_completed(self) -> bool:
        return self._engine.is_in_accepting_state()

    # ------------------------------------------------------------------
    # Intervention-specific logic
    # ------------------------------------------------------------------

    def _check_timeout_alert(self) -> None:
        """Trigger alert if intervention has been in current state too long."""
        state = self._engine.current_state
        threshold_hours = STATE_TIMEOUTS.get(state)
        if threshold_hours is None:
            return
        entry_time = self._state_entry_times.get(state)
        if entry_time and (datetime.now() - entry_time) > timedelta(hours=threshold_hours):
            self.alert_manager.trigger_alert(
                alert_type="INTERVENTION_TIMEOUT",
                severity=AlertSeverity.HIGH,
                message=(
                    f"Intervention {self.intervention_id} has been in state {state!r} "
                    f"for more than {threshold_hours} hours"
                ),
                entity_id=self.intervention_id,
                entity_type="Intervention",
            )

    def get_time_in_current_state(self) -> Optional[timedelta]:
        """Return how long the intervention has been in its current state."""
        entry = self._state_entry_times.get(self._engine.current_state)
        return (datetime.now() - entry) if entry else None

    def apply_to_db(self, event: str, session: Any) -> bool:
        """Process event and persist new state to database."""
        result = self.process_event(event)
        if result and session is not None:
            try:
                from models.intervention import Intervention
                obj = session.query(Intervention).filter_by(
                    ID_Intervention=self.intervention_id
                ).first()
                if obj:
                    obj.etat_dfa = self._engine.current_state
                    obj.timestamp_derniere_transition = datetime.now()
                    if self._engine.current_state == COMPLETED:
                        obj.Date_Completion = datetime.now()
                    if self._engine.current_state == AI_VALIDATED:
                        obj.Valide_IA = True
                    session.commit()
            except Exception:
                if session:
                    session.rollback()
        return result

    def __repr__(self) -> str:
        return f"<InterventionDFA id={self.intervention_id} state={self.get_current_state()!r}>"
