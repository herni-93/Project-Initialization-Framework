"""Errors raised by the reference implementation."""


class PifError(Exception):
    """Base class for framework errors."""


class GuardError(PifError):
    """A framework rule blocks the requested action. The project state is unchanged."""


class InvalidTransition(PifError):
    """The requested state transition is not part of the state machine."""
