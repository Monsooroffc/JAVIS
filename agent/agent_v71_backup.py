"""The agent: executes the plan produced by the planner."""

from __future__ import annotations

from collections.abc import Callable

from agent.planner import Planner
from brain.router import Intent, Route
from core.logger import get_logger
from tools.manager import ToolManager, tools

__all__ = ["JarvisAgent", "agent"]

log = get_logger(__name__)

Handler = Callable[[Route], "str | None"]


class JarvisAgent:
    """Maps an :class:`~brain.router.Intent` onto a tool call.

    The agent only knows *how* to perform an action; deciding *what* to do is
    the planner's job, which keeps both pieces easy to test.
    """

    def __init__(
        self,
        tool_manager: ToolManager | None = None,
        planner: Planner | None = None,
    ) -> None:
        self.tools = tool_manager or tools
        self.planner = planner or Planner()

        self._handlers: dict[Intent, Handler] = {
            Intent.OPEN_APP: lambda route: self.tools.open_app(route.query or ""),
            Intent.OPEN_WEBSITE: lambda route: self.tools.open_website(
                route.query or ""
            ),
            Intent.GOOGLE_SEARCH: lambda route: self.tools.google_search(
                route.query or ""
            ),
            Intent.YOUTUBE_SEARCH: lambda route: self.tools.youtube_search(
                route.query or ""
            ),
            Intent.BROWSER_SCROLL: lambda _route: self.tools.scroll(),
            Intent.BROWSER_READ: lambda _route: self.tools.read_page(),
            Intent.BROWSER_TYPE: lambda route: self.tools.type_text(
                route.query or ""
            ),
            Intent.BROWSER_PRESS: lambda route: self.tools.press(route.query or ""),
            Intent.BROWSER_CLICK: lambda route: self.tools.click_text(
                route.query or ""
            ),
            Intent.BROWSER_FIND: lambda route: self.tools.find_text(
                route.query or ""
            ),
            Intent.OPEN_JARVIS_FOLDER: lambda _route: (
                self.tools.open_jarvis_folder()
            ),
        }

    @property
    def intents(self) -> frozenset[Intent]:
        """The intents this agent is able to execute."""

        return frozenset(self._handlers)

    def handles(self, route: Route) -> bool:
        """True when the agent can execute ``route``."""

        return route.intent in self._handlers

    def process(self, text: str) -> str | None:
        """Execute ``text`` and return the sentence JARVIS should speak.

        Returns:
            The spoken reply, or ``None`` when the text is not an agent action
            or the tool could not complete it.
        """

        route = self.planner.plan(text)
        handler = self._handlers.get(route.intent)

        if handler is None:
            log.debug("Agent does not handle %s.", route.intent)
            return None

        log.info("Agent action: %s", route.intent)

        return handler(route)


agent = JarvisAgent()