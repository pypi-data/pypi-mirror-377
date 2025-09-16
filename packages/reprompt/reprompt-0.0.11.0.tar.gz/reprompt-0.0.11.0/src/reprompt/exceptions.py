"""Exception classes for Reprompt API."""

from __future__ import annotations


class RepromptAPIError(Exception):
    """Exception raised when API requests fail."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
