"""Turns the user's sentence into a route the agent can execute.

The planner is deliberately thin: it exists so the agent depends on a
*decision*, not on the router implementation.
"""

from __future__ import annotations

from brain.router import Route, route_command

__all__ = ["Planner"]


class Planner:
    """Decides what JARVIS should do next."""

    def plan(self, user_text: str) -> Route:
        """Return the route describing what ``user_text`` asks for."""

        return route_command(user_text)