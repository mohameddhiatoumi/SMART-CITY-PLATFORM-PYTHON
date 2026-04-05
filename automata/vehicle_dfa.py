"""
Vehicle trajectory DFA for the Smart City Platform.
Manages vehicle state transitions through PARKED, EN_ROUTE, BROKEN_DOWN, ARRIVED.
"""
from __future__ import annotations
from datetime import datetime, timedelta
from typing import Optional, Any

from automata.dfa_engine import DFAEngine, DFATransition
from automata.alerts import AlertManager, AlertSeverity

# State constants
PARKED = "PARKED"
EN_ROUTE = "EN_ROUTE"
BROKEN_DOWN = "BROKEN_DOWN"
ARRIVED = "ARRIVED"

VEHICLE_STATES = [PARKED, EN_ROUTE, BROKEN_DOWN, ARRIVED]

VEHICLE_TRANSITIONS = [
    DFATransition(PARKED,       "depart",    EN_ROUTE),
    DFATransition(EN_ROUTE,     "breakdown", BROKEN_DOWN),
    DFATransition(EN_ROUTE,     "arrive",    ARRIVED),
    DFATransition(BROKEN_DOWN,  "repair",    EN_ROUTE),
    DFATransition(BROKEN_DOWN,  "tow",       PARKED),
    DFATransition(ARRIVED,      "return",    PARKED),
]

# Alert threshold: flag long routes (minutes)
ROUTE_TIME_THRESHOLD_MINUTES = 120


class VehicleDFA:
    """
    Vehicle trajectory Deterministic Finite Automaton.

    States::
        PARKED → EN_ROUTE → ARRIVED → PARKED
                          ↘ BROKEN_DOWN → EN_ROUTE (after repair)
                                        → PARKED (after tow)

    Usage::
        dfa = VehicleDFA(vehicle_id=7)
        dfa.process_event("depart")
        dfa.process_event("arrive")
        dfa.process_event("return")
    """

    def __init__(
        self,
        vehicle_id: int,
        initial_state: str = PARKED,
        alert_manager: Optional[AlertManager] = None,
        route_threshold_minutes: int = ROUTE_TIME_THRESHOLD_MINUTES,
    ) -> None:
        self.vehicle_id = vehicle_id
        self.alert_manager = alert_manager or AlertManager()
        self.route_threshold = timedelta(minutes=route_threshold_minutes)
        self._depart_time: Optional[datetime] = None
        self._engine = DFAEngine(
            name=f"VehicleDFA-{vehicle_id}",
            states=VEHICLE_STATES,
            initial_state=initial_state,
            transitions=VEHICLE_TRANSITIONS,
            accepting_states=[ARRIVED, PARKED],
        )

    # ------------------------------------------------------------------
    # Delegated DFA methods
    # ------------------------------------------------------------------

    def process_event(self, event: str, context: Optional[dict] = None) -> bool:
        """Process an event and update vehicle state."""
        result = self._engine.process_event(event, context)
        if result:
            if event == "depart":
                self._depart_time = datetime.now()
            elif event in ("arrive", "tow"):
                self._check_route_time_alert()
                self._depart_time = None
        return result

    def get_current_state(self) -> str:
        return self._engine.get_current_state()

    def get_valid_events(self) -> list[str]:
        return self._engine.get_valid_events()

    def get_transition_history(self) -> list[dict]:
        return self._engine.get_transition_history()

    def reset(self) -> None:
        self._engine.reset()
        self._depart_time = None

    def get_all_transitions(self) -> list[dict]:
        return self._engine.get_all_transitions()

    # ------------------------------------------------------------------
    # Vehicle-specific logic
    # ------------------------------------------------------------------

    def get_route_duration(self) -> Optional[timedelta]:
        """Return elapsed time since departure."""
        if self._depart_time is None:
            return None
        return datetime.now() - self._depart_time

    def _check_route_time_alert(self) -> None:
        """Trigger alert if route duration exceeds threshold."""
        duration = self.get_route_duration()
        if duration and duration > self.route_threshold:
            self.alert_manager.trigger_alert(
                alert_type="VEHICLE_LONG_ROUTE",
                severity=AlertSeverity.MEDIUM,
                message=(
                    f"Vehicle {self.vehicle_id} has been en route for "
                    f"{duration} (threshold: {self.route_threshold})"
                ),
                entity_id=self.vehicle_id,
                entity_type="Vehicule",
            )

    def apply_to_db(self, event: str, session: Any) -> bool:
        """Process event and persist new state to database."""
        result = self.process_event(event)
        if result and session is not None:
            try:
                from models.trajet import Trajet
                from models.vehicule import Vehicule
                # Update most recent trajet for this vehicle
                trajet = (
                    session.query(Trajet)
                    .filter_by(ID_Vehicule=self.vehicle_id)
                    .order_by(Trajet.Heure_Depart.desc())
                    .first()
                )
                if trajet:
                    trajet.etat_dfa = self._engine.current_state
                    trajet.timestamp_derniere_transition = datetime.now()
                    if event == "arrive":
                        trajet.Heure_Arrivee = datetime.now()
                        trajet.Statut = "COMPLETED"
                    session.commit()
            except Exception:
                if session:
                    session.rollback()
        return result

    def __repr__(self) -> str:
        return f"<VehicleDFA vehicle_id={self.vehicle_id} state={self.get_current_state()!r}>"
