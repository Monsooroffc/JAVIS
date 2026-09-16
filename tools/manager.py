from tools.apps import open_app

from tools.browser import (
    browser,
    open_website,
    google_search,
    youtube_search,
)

from tools.files import open_jarvis_folder


class ToolManager:

    def open_app(self, app):
        return open_app(app)

    def open_website(self, site):
        return open_website(site)

    def google_search(self, query):
        return google_search(query)

    def youtube_search(self, query):
        return youtube_search(query)

    def type_text(self, text):
        return browser.type_text(text)

    def press(self, key):
        return browser.press(key)

    def click_text(self, text):
        return browser.click_text(text)

    def find_text(self, text):
        return browser.find_text(text)

    def scroll(self):
        return browser.scroll()

    def read_page(self):
        return browser.read()

    def open_jarvis_folder(self):
        return open_jarvis_folder()


tools = ToolManager()