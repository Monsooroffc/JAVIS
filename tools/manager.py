"""A single facade that the agent uses to reach every tool."""

from __future__ import annotations

from tools.apps import open_app
from tools.browser import (
    BrowserAgent,
    browser,
    google_search,
    open_website,
    youtube_search,
)
from tools.files import open_jarvis_folder

__all__ = ["ToolManager", "tools"]


class ToolManager:
    """Convenience wrapper around the individual tool modules."""

    def __init__(self, browser_agent: BrowserAgent | None = None) -> None:
        self.browser_agent = browser_agent or browser

    # =========================
    # APPLICATIONS
    # =========================

    def open_app(self, app: str) -> str | None:
        """Open a desktop application."""

        return open_app(app)

    # =========================
    # BROWSER
    # =========================

    def open_website(self, site: str) -> str:
        """Open a website."""

        return open_website(site)

    def google_search(self, query: str) -> str:
        """Search Google."""

        return google_search(query)

    def youtube_search(self, query: str) -> str:
        """Search YouTube."""

        return youtube_search(query)

    def type_text(self, text: str) -> str:
        """Type into the open page."""

        return self.browser_agent.type_text(text)

    def press(self, key: str) -> str:
        """Press a key in the open page."""

        return self.browser_agent.press(key)

    def click_text(self, text: str) -> str:
        """Click text in the open page."""

        return self.browser_agent.click_text(text)

    def find_text(self, text: str) -> str:
        """Look for text in the open page."""

        return self.browser_agent.find_text(text)

    def scroll(self, amount: int = 800) -> str:
        """Scroll the open page."""

        return self.browser_agent.scroll(amount)

    def read_page(self) -> str:
        """Read the open page."""

        return self.browser_agent.read()

    def close_browser(self) -> None:
        """Close the automated browser."""

        self.browser_agent.stop()

    # =========================
    # FILES
    # =========================

    def open_jarvis_folder(self) -> str | None:
        """Show the JARVIS folder in Explorer."""

        return open_jarvis_folder()


tools = ToolManager()