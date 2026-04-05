"""
Base DFA engine for the Smart City Platform.
Provides a generic Deterministic Finite Automaton implementation.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from datetime import datetime


@dataclass
class DFATransition:
    """Represents a transition between DFA states."""
    from_state: str
    event: str
    to_state: str
    action: Optional[Callable] = None

    def __repr__(self) -> str:
        return f"DFATransition({self.from_state!r} --[{self.event}]--> {self.to_state!r})"


@dataclass
class TransitionRecord:
    """Records a historical state transition."""
    from_state: str
    event: str
    to_state: str
    timestamp: datetime
    context: Optional[dict] = None


class DFAEngine:
    """
    Generic Deterministic Finite Automaton engine.

    Supports:
    - Named states and events
    - Transition actions (callbacks)
    - Transition history logging
    - Accepting states
    - Event sequence validation

    Usage::
        engine = DFAEngine(
            name="MySensor",
            states=["OFF", "ON"],
            initial_state="OFF",
            transitions=[
                DFATransition("OFF", "turn_on", "ON"),
                DFATransition("ON", "turn_off", "OFF"),
            ],
        )
        engine.process_event("turn_on")
    """

    def __init__(
        self,
        name: str,
        states: List[str],
        initial_state: str,
        transitions: List[DFATransition],
        accepting_states: Optional[List[str]] = None,
    ) -> None:
        self.name = name
        self.states: Set[str] = set(states)
        self.initial_state = initial_state
        self.current_state = initial_state
        self.accepting_states: Set[str] = set(accepting_states or [])
        self.history: List[TransitionRecord] = []

        # Build transition table: {(from_state, event): DFATransition}
        self._transition_table: Dict[tuple, DFATransition] = {}
        for trans in transitions:
            key = (trans.from_state, trans.event)
            self._transition_table[key] = trans

        # Validate
        assert initial_state in self.states, f"Initial state {initial_state!r} not in states"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process_event(self, event: str, context: Optional[dict] = None) -> bool:
        """
        Process an event and transition to the next state if valid.

        Returns True if transition occurred, False if invalid event.
        """
        key = (self.current_state, event)
        transition = self._transition_table.get(key)

        if transition is None:
            return False

        old_state = self.current_state
        self.current_state = transition.to_state

        # Record history
        self.history.append(TransitionRecord(
            from_state=old_state,
            event=event,
            to_state=self.current_state,
            timestamp=datetime.now(),
            context=context,
        ))

        # Execute action callback if defined
        if transition.action is not None:
            try:
                transition.action(context)
            except Exception:
                pass  # Don't let callbacks break the DFA

        return True

    def get_current_state(self) -> str:
        """Return the current state name."""
        return self.current_state

    def reset(self) -> None:
        """Reset DFA to initial state."""
        self.current_state = self.initial_state
        self.history.clear()

    def is_in_accepting_state(self) -> bool:
        """Return True if current state is an accepting state."""
        return self.current_state in self.accepting_states

    def get_valid_events(self) -> List[str]:
        """Return list of valid events from the current state."""
        return [
            event
            for (state, event) in self._transition_table
            if state == self.current_state
        ]

    def get_transition_history(self) -> List[dict]:
        """Return transition history as list of dicts."""
        return [
            {
                "from_state": r.from_state,
                "event": r.event,
                "to_state": r.to_state,
                "timestamp": r.timestamp.isoformat(),
                "context": r.context,
            }
            for r in self.history
        ]

    def validate_event_sequence(self, events: List[str]) -> bool:
        """
        Simulate an event sequence from the INITIAL state without modifying real state.
        Returns True if all events are valid in sequence.
        """
        sim_state = self.initial_state
        for event in events:
            key = (sim_state, event)
            transition = self._transition_table.get(key)
            if transition is None:
                return False
            sim_state = transition.to_state
        return True

    def get_all_transitions(self) -> List[dict]:
        """Return all defined transitions as dicts (for visualisation)."""
        return [
            {
                "from": t.from_state,
                "event": t.event,
                "to": t.to_state,
            }
            for t in self._transition_table.values()
        ]

    def __repr__(self) -> str:
        return f"<DFAEngine name={self.name!r} state={self.current_state!r}>"
