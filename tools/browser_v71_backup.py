"""Browser automation built on Playwright.

The browser starts on first use and stays open between commands, so a
conversation like *"open google"*, *"type python"*, *"press enter"* keeps
working in the same window. Playwright is imported lazily, so JARVIS still
starts when the browser package is missing.
"""

from __future__ import annotations

import urllib.parse

from config import (
    BROWSER_CHANNEL,
    BROWSER_HEADLESS,
    BROWSER_TIMEOUT_MS,
    USER_TITLE,
)
from core.logger import get_logger

__all__ = [
    "BrowserAgent",
    "browser",
    "google_search",
    "open_website",
    "to_url",
    "youtube_search",
]

log = get_logger(__name__)

MAX_PAGE_CHARS = 3000
DEFAULT_SCROLL_PIXELS = 800
SEARCH_URL = "https://www.google.com/search?q="
LOCATOR_TIMEOUT_MS = 5000


def to_url(site: str) -> str:
    """Turn whatever the user said into a URL."""

    site = (site or "").strip()

    if site.startswith(("http://", "https://")):
        return site

    if "." in site and " " not in site:
        return f"https://{site}"

    return SEARCH_URL + urllib.parse.quote(f"{site} official website")


class BrowserAgent:
    """A Chrome/Chromium window driven by Playwright."""

    def __init__(
        self,
        channel: str = BROWSER_CHANNEL,
        headless: bool = BROWSER_HEADLESS,
        timeout_ms: int = BROWSER_TIMEOUT_MS,
    ) -> None:
        self.channel = channel
        self.headless = headless
        self.timeout_ms = timeout_ms
        self.page = None
        self._playwright = None
        self._browser = None

    # =========================
    # LIFECYCLE
    # =========================

    @property
    def running(self) -> bool:
        """True when a page is available."""

        return self.page is not None

    def start(self) -> bool:
        """Start the browser when it is not running yet."""

        if self.running:
            return True

        try:
            from playwright.sync_api import sync_playwright

            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(
                channel=self.channel,
                headless=self.headless,
            )
            self.page = self._browser.new_context().new_page()

        except Exception as error:  # noqa: BLE001 - Playwright raises many types
            log.error("Browser could not start: %s", error)
            self.stop()
            return False

        log.info("Browser started (%s).", self.channel)

        return True

    def stop(self) -> None:
        """Close the browser and release Playwright."""

        if self._browser is not None:
            try:
                self._browser.close()

            except Exception as error:  # noqa: BLE001 - best effort
                log.debug("Browser close problem: %s", error)

        if self._playwright is not None:
            try:
                self._playwright.stop()

            except Exception as error:  # noqa: BLE001 - best effort
                log.debug("Playwright stop problem: %s", error)

        self.page = None
        self._browser = None
        self._playwright = None

        log.debug("Browser stopped.")

    def __enter__(self) -> BrowserAgent:
        self.start()
        return self

    def __exit__(self, *_exc_info: object) -> None:
        self.stop()

    # =========================
    # NAVIGATION
    # =========================

    def _goto(self, url: str) -> str:
        """Navigate to ``url``, returning an empty string on success."""

        if not self.start():
            return f"I couldn't start the browser, {USER_TITLE}."

        try:
            self.page.goto(  # type: ignore[union-attr]
                url,
                wait_until="domcontentloaded",
                timeout=self.timeout_ms,
            )

        except Exception as error:  # noqa: BLE001 - Playwright raises many types
            log.error("Navigation to %s failed: %s", url, error)
            return "I couldn't open that page."

        return ""

    def open(self, site: str) -> str:
        """Open a website, or search for it when it is not a domain."""

        if not (site or "").strip():
            return f"Tell me the website name, {USER_TITLE}."

        problem = self._goto(to_url(site))

        if problem:
            return problem

        return f"Opened {site.strip()}."

    def search(self, query: str) -> str:
        """Search Google for ``query``."""

        query = (query or "").strip()

        if not query:
            return "What should I search for?"

        problem = self._goto(SEARCH_URL + urllib.parse.quote(query))

        if problem:
            return problem

        return f"Searched Google for {query}."

    # =========================
    # PAGE INTERACTION
    # =========================

    def _ready(self) -> str:
        """Return an error message when there is no page to work with."""

        if not self.running:
            return "The browser is not running."

        return ""

    def type_text(self, text: str) -> str:
        """Type ``text`` into the focused element."""

        problem = self._ready()

        if problem:
            return problem

        try:
            self.page.keyboard.type(text)  # type: ignore[union-attr]

        except Exception as error:  # noqa: BLE001 - Playwright raises many types
            log.error("Typing failed: %s", error)
            return "I couldn't type that."

        return f"Typed: {text}"

    def press(self, key: str) -> str:
        """Press a single key, for example ``enter``."""

        problem = self._ready()

        if problem:
            return problem

        try:
            self.page.keyboard.press(key)  # type: ignore[union-attr]

        except Exception as error:  # noqa: BLE001 - Playwright raises many types
            log.error("Key press failed: %s", error)
            return f"I couldn't press {key}."

        return f"Pressed {key}."

    def click_text(self, text: str) -> str:
        """Click the first element containing ``text``."""

        problem = self._ready()

        if problem:
            return problem

        try:
            self.page.get_by_text(  # type: ignore[union-attr]
                text, exact=False
            ).first.click(timeout=LOCATOR_TIMEOUT_MS)

        except Exception as error:  # noqa: BLE001 - Playwright raises many types
            log.error("Could not click %s: %s", text, error)
            return f"I couldn't click {text}."

        return f"Clicked {text}."

    def find_text(self, text: str) -> str:
        """Report whether ``text`` appears on the current page."""

        problem = self._ready()

        if problem:
            return problem

        try:
            matches = self.page.get_by_text(  # type: ignore[union-attr]
                text, exact=False
            ).count()

        except Exception as error:  # noqa: BLE001 - Playwright raises many types
            log.error("Find failed: %s", error)
            return f"I couldn't search the page for {text}."

        if matches:
            return f"I found {text} on the page."

        return f"I couldn't find {text}."

    def scroll(self, amount: int = DEFAULT_SCROLL_PIXELS) -> str:
        """Scroll the page by ``amount`` pixels."""

        problem = self._ready()

        if problem:
            return problem

        try:
            self.page.mouse.wheel(0, amount)  # type: ignore[union-attr]

        except Exception as error:  # noqa: BLE001 - Playwright raises many types
            log.error("Scrolling failed: %s", error)
            return "I couldn't scroll the page."

        return "Scrolled down."

    def read(self) -> str:
        """Return the title and the visible text of the current page."""

        problem = self._ready()

        if problem:
            return problem

        try:
            title = self.page.title()  # type: ignore[union-attr]
            body = self.page.locator("body").inner_text(  # type: ignore[union-attr]
                timeout=LOCATOR_TIMEOUT_MS
            )

        except Exception as error:  # noqa: BLE001 - Playwright raises many types
            log.error("Reading the page failed: %s", error)
            return "I couldn't read that page."

        text = " ".join(body.split())

        if len(text) > MAX_PAGE_CHARS:
            text = text[:MAX_PAGE_CHARS] + "..."

        return f"Page title: {title}\n\n{text}"


browser = BrowserAgent()


def open_website(site: str) -> str:
    """Open a website with the shared browser."""

    return browser.open(site)


def google_search(query: str) -> str:
    """Search Google with the shared browser."""

    return browser.search(query)


def youtube_search(query: str) -> str:
    """Search YouTube with the shared browser."""

    return browser.search(f"site:youtube.com {query}")