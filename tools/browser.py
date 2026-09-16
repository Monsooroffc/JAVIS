"""Browser automation for JARVIS V7.2."""

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
LOCATOR_TIMEOUT_MS = 5000

GOOGLE_URL = "https://www.google.com/search?q="
YOUTUBE_URL = "https://www.youtube.com/results?search_query="


# ============================================================
# KNOWN WEBSITES
# ============================================================

WEBSITES: dict[str, str] = {
    "google": "https://www.google.com",
    "google search": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "instagram": "https://www.instagram.com",
    "facebook": "https://www.facebook.com",
    "whatsapp": "https://web.whatsapp.com",
    "spotify": "https://open.spotify.com",
    "discord": "https://discord.com/app",
    "github": "https://github.com",
    "chatgpt": "https://chatgpt.com",
    "chat gpt": "https://chatgpt.com",
    "gmail": "https://mail.google.com",
    "google drive": "https://drive.google.com",
    "google docs": "https://docs.google.com",
    "google sheets": "https://sheets.google.com",
    "linkedin": "https://www.linkedin.com",
    "reddit": "https://www.reddit.com",
    "netflix": "https://www.netflix.com",
    "amazon": "https://www.amazon.in",
    "x": "https://x.com",
    "twitter": "https://x.com",
    "canva": "https://www.canva.com",
    "notebooklm": "https://notebooklm.google.com",
}


def normalize_site(site: str) -> str:
    """Normalize spoken website names."""

    value = (site or "").strip().lower()

    prefixes = (
        "the ",
        "website ",
    )

    for prefix in prefixes:
        if value.startswith(prefix):
            value = value[len(prefix):].strip()

    return value.rstrip(" .")


def to_url(site: str) -> str:
    """Convert a website name into a direct URL."""

    value = normalize_site(site)

    if not value:
        return ""

    if value.startswith(("http://", "https://")):
        return value

    if value in WEBSITES:
        return WEBSITES[value]

    # Common spoken domain forms.
    domain_aliases = {
        "instagram.com": "https://instagram.com",
        "youtube.com": "https://youtube.com",
        "github.com": "https://github.com",
        "google.com": "https://google.com",
        "spotify.com": "https://spotify.com",
        "discord.com": "https://discord.com",
        "chatgpt.com": "https://chatgpt.com",
        "linkedin.com": "https://linkedin.com",
    }

    if value in domain_aliases:
        return domain_aliases[value]

    # If the user supplied a domain, use it directly.
    if "." in value and " " not in value:
        return f"https://{value}"

    # Unknown site names are treated as domains instead of
    # automatically sending the user to Google.
    compact = value.replace(" ", "")

    if compact:
        return f"https://www.{compact}.com"

    return ""


class BrowserAgent:
    """Persistent Playwright browser controlled by JARVIS."""

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
        self._context = None

    # ============================================================
    # LIFECYCLE
    # ============================================================

    @property
    def running(self) -> bool:
        return self.page is not None

    def start(self) -> bool:
        """Start the persistent browser."""

        if self.running:
            return True

        try:
            from playwright.sync_api import sync_playwright

            self._playwright = sync_playwright().start()

            self._browser = self._playwright.chromium.launch(
                channel=self.channel,
                headless=self.headless,
            )

            self._context = self._browser.new_context()

            self.page = self._context.new_page()

            self.page.set_default_timeout(LOCATOR_TIMEOUT_MS)

            log.info("Browser started.")

            return True

        except Exception as error:
            log.error("Browser startup failed: %s", error)
            self.stop()

            return False

    def stop(self) -> None:
        """Close browser."""

        try:
            if self._browser is not None:
                self._browser.close()

        except Exception as error:
            log.debug("Browser close error: %s", error)

        try:
            if self._playwright is not None:
                self._playwright.stop()

        except Exception as error:
            log.debug("Playwright shutdown error: %s", error)

        self.page = None
        self._context = None
        self._browser = None
        self._playwright = None

    # ============================================================
    # NAVIGATION
    # ============================================================

    def _goto(self, url: str) -> str | None:
        """Navigate to a URL."""

        if not self.start():
            return f"I couldn't start the browser, {USER_TITLE}."

        try:
            self.page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=self.timeout_ms,
            )

            return None

        except Exception as error:
            log.error("Navigation failed: %s", error)

            return f"I couldn't open that page, {USER_TITLE}."

    def open(self, site: str) -> str:
        """Open a website directly."""

        value = normalize_site(site)

        if not value:
            return f"Tell me which website to open, {USER_TITLE}."

        url = to_url(value)

        if not url:
            return f"I couldn't understand that website, {USER_TITLE}."

        problem = self._goto(url)

        if problem:
            return problem

        return f"{value.title()} is open, {USER_TITLE}."

    def search(self, query: str) -> str:
        """Explicit Google search."""

        query = (query or "").strip()

        if not query:
            return f"What should I search for, {USER_TITLE}?"

        url = GOOGLE_URL + urllib.parse.quote_plus(query)

        problem = self._goto(url)

        if problem:
            return problem

        return f"I searched Google for {query}, {USER_TITLE}."

    def youtube_search(self, query: str) -> str:
        """Search YouTube directly."""

        query = (query or "").strip()

        if not query:
            return f"What should I search on YouTube, {USER_TITLE}?"

        url = YOUTUBE_URL + urllib.parse.quote_plus(query)

        problem = self._goto(url)

        if problem:
            return problem

        return f"I searched YouTube for {query}, {USER_TITLE}."

    def back(self) -> str:
        """Go back."""

        problem = self._ready()

        if problem:
            return problem

        try:
            self.page.go_back(timeout=self.timeout_ms)

            return f"Going back, {USER_TITLE}."

        except Exception as error:
            log.error("Back failed: %s", error)

            return "I couldn't go back."

    def forward(self) -> str:
        """Go forward."""

        problem = self._ready()

        if problem:
            return problem

        try:
            self.page.go_forward(timeout=self.timeout_ms)

            return f"Going forward, {USER_TITLE}."

        except Exception as error:
            log.error("Forward failed: %s", error)

            return "I couldn't go forward."

    def refresh(self) -> str:
        """Refresh current page."""

        problem = self._ready()

        if problem:
            return problem

        try:
            self.page.reload(
                wait_until="domcontentloaded",
                timeout=self.timeout_ms,
            )

            return f"Page refreshed, {USER_TITLE}."

        except Exception as error:
            log.error("Refresh failed: %s", error)

            return "I couldn't refresh the page."

    # ============================================================
    # INTERACTION
    # ============================================================

    def _ready(self) -> str | None:
        if not self.running:
            return "The browser is not running yet."

        return None

    def type_text(self, text: str) -> str:
        problem = self._ready()

        if problem:
            return problem

        try:
            self.page.keyboard.type(text)

            return f"Typed it, {USER_TITLE}."

        except Exception as error:
            log.error("Typing failed: %s", error)

            return "I couldn't type that."

    def press(self, key: str) -> str:
        problem = self._ready()

        if problem:
            return problem

        try:
            self.page.keyboard.press(key)

            return f"Pressed {key}, {USER_TITLE}."

        except Exception as error:
            log.error("Key press failed: %s", error)

            return f"I couldn't press {key}."

    def click_text(self, text: str) -> str:
        problem = self._ready()

        if problem:
            return problem

        try:
            locator = self.page.get_by_text(
                text,
                exact=False,
            ).first

            locator.click(timeout=LOCATOR_TIMEOUT_MS)

            return f"Clicked {text}, {USER_TITLE}."

        except Exception as error:
            log.error("Click failed for %s: %s", text, error)

            return f"I couldn't click {text}."

    def find_text(self, text: str) -> str:
        problem = self._ready()

        if problem:
            return problem

        try:
            count = self.page.get_by_text(
                text,
                exact=False,
            ).count()

            if count:
                return f"I found {text} on the page, {USER_TITLE}."

            return f"I couldn't find {text}."

        except Exception as error:
            log.error("Find failed: %s", error)

            return f"I couldn't search the page for {text}."

    def scroll(self, amount: int = DEFAULT_SCROLL_PIXELS) -> str:
        problem = self._ready()

        if problem:
            return problem

        try:
            self.page.mouse.wheel(0, amount)

            if amount < 0:
                return f"Scrolled up, {USER_TITLE}."

            return f"Scrolled down, {USER_TITLE}."

        except Exception as error:
            log.error("Scroll failed: %s", error)

            return "I couldn't scroll the page."

    def read(self) -> str:
        problem = self._ready()

        if problem:
            return problem

        try:
            title = self.page.title()

            body = self.page.locator(
                "body"
            ).inner_text(timeout=LOCATOR_TIMEOUT_MS)

            text = " ".join(body.split())

            if len(text) > MAX_PAGE_CHARS:
                text = text[:MAX_PAGE_CHARS] + "..."

            return f"Page title: {title}\n\n{text}"

        except Exception as error:
            log.error("Page reading failed: %s", error)

            return "I couldn't read that page."


browser = BrowserAgent()


def open_website(site: str) -> str:
    return browser.open(site)


def google_search(query: str) -> str:
    return browser.search(query)


def youtube_search(query: str) -> str:
    return browser.youtube_search(query)