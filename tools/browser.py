import urllib.parse
from playwright.sync_api import sync_playwright


class BrowserAgent:

    def __init__(self):
        self.pw = None
        self.browser = None
        self.page = None

    def start(self):

        if self.page:
            return True

        try:
            self.pw = sync_playwright().start()

            self.browser = self.pw.chromium.launch(
                channel="chrome",
                headless=False
            )

            context = self.browser.new_context()
            self.page = context.new_page()

            return True

        except Exception as error:
            print("Browser error:", error)
            self.stop()
            return False

    def stop(self):

        try:
            if self.browser:
                self.browser.close()

            if self.pw:
                self.pw.stop()

        except Exception:
            pass

        self.page = None
        self.browser = None
        self.pw = None

    def open(self, site):

        if not self.start():
            return "Browser could not start."

        site = site.strip()

        if not site:
            return "Tell me the website name, bro."

        try:

            if site.startswith("http://") or site.startswith("https://"):
                url = site

            elif "." in site and " " not in site:
                url = "https://" + site

            else:
                url = (
                    "https://www.google.com/search?q="
                    + urllib.parse.quote(
                        site + " official website"
                    )
                )

            self.page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=15000
            )

            return f"Opened {site}."

        except Exception as error:
            return f"I couldn't open {site}: {error}"

    def search(self, query):

        if not self.start():
            return "Browser could not start."

        try:

            url = (
                "https://www.google.com/search?q="
                + urllib.parse.quote(query)
            )

            self.page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=15000
            )

            return f"Searched Google for {query}."

        except Exception as error:
            return f"Search failed: {error}"

    # =========================
    # TYPE
    # =========================

    def type_text(self, text):

        if not self.page:
            return "Browser is not running."

        try:

            self.page.keyboard.type(text)

            return f"Typed: {text}"

        except Exception as error:

            return f"Typing failed: {error}"

    # =========================
    # PRESS KEY
    # =========================

    def press(self, key):

        if not self.page:
            return "Browser is not running."

        try:

            self.page.keyboard.press(key)

            return f"Pressed {key}."

        except Exception as error:

            return f"Key press failed: {error}"

    # =========================
    # CLICK TEXT
    # =========================

    def click_text(self, text):

        if not self.page:
            return "Browser is not running."

        try:

            locator = self.page.get_by_text(
                text,
                exact=False
            ).first

            locator.click(timeout=5000)

            return f"Clicked {text}."

        except Exception as error:

            return f"I couldn't click {text}: {error}"

    # =========================
    # FIND TEXT
    # =========================

    def find_text(self, text):

        if not self.page:
            return "Browser is not running."

        try:

            locator = self.page.get_by_text(
                text,
                exact=False
            ).first

            if locator.count() > 0:

                return f"I found {text} on the page."

            return f"I couldn't find {text}."

        except Exception as error:

            return f"Find failed: {error}"

    # =========================
    # SCROLL
    # =========================

    def scroll(self, amount=800):

        if not self.page:
            return "Browser is not running."

        try:

            self.page.mouse.wheel(0, amount)

            return "Scrolled down."

        except Exception as error:

            return f"Scrolling failed: {error}"

    # =========================
    # READ PAGE
    # =========================

    def read(self):

        if not self.page:
            return "Browser is not running."

        try:

            title = self.page.title()

            text = self.page.locator(
                "body"
            ).inner_text(timeout=5000)

            text = " ".join(text.split())

            if len(text) > 3000:
                text = text[:3000] + "..."

            return (
                f"Page title: {title}\n\n"
                f"{text}"
            )

        except Exception as error:

            return f"Page reading failed: {error}"


browser = BrowserAgent()


def open_website(site):
    return browser.open(site)


def google_search(query):
    return browser.search(query)


def youtube_search(query):
    return browser.search(
        "site:youtube.com " + query
    )