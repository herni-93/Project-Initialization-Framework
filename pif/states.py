"""Initialization state machine. Only the Project Orchestrator changes the state."""

from __future__ import annotations

from enum import Enum

from .errors import InvalidTransition


class State(str, Enum):
    WAITING = "waiting"
    BOOTSTRAP = "bootstrap"
    DISCOVERY = "discovery"
    VALIDATION = "validation"
    PRD_GENERATION = "prd_generation"
    PRD_REVIEW = "prd_review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"


TERMINAL = frozenset({State.COMPLETED, State.CANCELLED})

# Regular transitions. CANCELLED and ERROR are reachable from any non-terminal
# state; leaving ERROR is done only by resuming the last valid state.
TRANSITIONS = {
    State.WAITING: frozenset({State.BOOTSTRAP}),
    # Discovery is conditional; validation is never skipped.
    State.BOOTSTRAP: frozenset({State.DISCOVERY, State.VALIDATION}),
    State.DISCOVERY: frozenset({State.VALIDATION}),
    State.VALIDATION: frozenset({State.DISCOVERY, State.PRD_GENERATION}),
    State.PRD_GENERATION: frozenset({State.PRD_REVIEW}),
    State.PRD_REVIEW: frozenset({State.DISCOVERY, State.COMPLETED}),
    State.COMPLETED: frozenset(),
    State.CANCELLED: frozenset(),
    State.ERROR: frozenset(),
}


def can_transition(src: str | State, dst: str | State) -> bool:
    src, dst = State(src), State(dst)
    if src in TERMINAL:
        return False
    if src is State.ERROR:
        return dst is State.CANCELLED
    if dst in (State.CANCELLED, State.ERROR):
        return True
    return dst in TRANSITIONS[src]


def ensure_transition(src: str | State, dst: str | State) -> None:
    if not can_transition(src, dst):
        raise InvalidTransition(
            f"Transition {State(src).value} -> {State(dst).value} is not allowed."
        )
