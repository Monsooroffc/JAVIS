"""JARVIS V7.2 agent execution layer."""

from __future__ import annotations

from collections.abc import Callable

from agent.planner import Planner
from brain.router import Intent, Route
from core.logger import get_logger
from tools.manager import ToolManager, tools

__all__ = ["JarvisAgent", "agent"]

log = get_logger(__name__)

Handler = Callable[[Route], str | None]


class JarvisAgent:
    """Execute deterministic JARVIS commands through ToolManager."""

    def __init__(
        self,
        tool_manager: ToolManager | None = None,
        planner: Planner | None = None,
    ) -> None:
        self.tools = tool_manager or tools
        self.planner = planner or Planner()

        self._handlers: dict[Intent, Handler] = {
            # =========================
            # APPLICATIONS
            # =========================

            Intent.OPEN_APP: lambda route: self.tools.open_app(
                route.query or ""
            ),

            Intent.CLOSE_APP: lambda route: (
                f"I can't close {route.query} yet."
                if route.query
                else "Tell me which application to close."
            ),

            # =========================
            # WEBSITES
            # =========================

            Intent.OPEN_WEBSITE: lambda route: self.tools.open_website(
                route.query or ""
            ),

            Intent.GOOGLE_SEARCH: lambda route: self.tools.google_search(
                route.query or ""
            ),

            Intent.YOUTUBE_SEARCH: lambda route: self.tools.youtube_search(
                route.query or ""
            ),

            # =========================
            # BROWSER CONTROL
            # =========================

            Intent.BROWSER_SCROLL: self._scroll,

            Intent.BROWSER_READ: lambda _route: (
                self.tools.read_page()
            ),

            Intent.BROWSER_TYPE: lambda route: self.tools.type_text(
                route.query or ""
            ),

            Intent.BROWSER_PRESS: lambda route: self.tools.press(
                route.query or ""
            ),

            Intent.BROWSER_CLICK: lambda route: self.tools.click_text(
                route.query or ""
            ),

            Intent.BROWSER_FIND: lambda route: self.tools.find_text(
                route.query or ""
            ),

            Intent.BROWSER_BACK: lambda _route: self.tools.browser_agent.back(),

            Intent.BROWSER_FORWARD: lambda _route: (
                self.tools.browser_agent.forward()
            ),

            Intent.BROWSER_REFRESH: lambda _route: (
                self.tools.browser_agent.refresh()
            ),

            # =========================
            # FILES
            # =========================

            Intent.OPEN_JARVIS_FOLDER: lambda _route: (
                self.tools.open_jarvis_folder()
            ),
        }

    # ============================================================
    # BROWSER HELPERS
    # ============================================================

    def _scroll(self, route: Route) -> str:
        """Handle scroll direction."""

        direction = (route.query or "down").lower()

        if direction == "up":
            return self.tools.scroll(-800)

        return self.tools.scroll(800)

    # ============================================================
    # PUBLIC API
    # ============================================================

    @property
    def intents(self) -> frozenset[Intent]:
        """Return all intents handled by this agent."""

        return frozenset(self._handlers)

    def handles(self, route: Route) -> bool:
        """Return True when this agent can execute the route."""

        return route.intent in self._handlers

    def process(self, text: str) -> str | None:
        """Plan and execute a user command."""

        route = self.planner.plan(text)

        log.info(
            "JARVIS route: %s | command=%s | query=%s",
            route.intent,
            route.command,
            route.query,
        )

        handler = self._handlers.get(route.intent)

        if handler is None:
            log.debug(
                "Agent does not handle intent: %s",
                route.intent,
            )
            return None

        try:
            result = handler(route)

            if result is None:
                return "Done."

            return str(result)

        except Exception as error:
            log.exception(
                "Agent execution failed for %s: %s",
                route.intent,
                error,
            )

            return "Something went wrong while doing that."


agent = JarvisAgent()