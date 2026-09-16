from agent.planner import Planner

from tools.manager import tools


class JarvisAgent:

    def __init__(self):
        self.planner = Planner()

    def process(self, user_text):

        plan = self.planner.plan(user_text)

        command_type = plan["type"]
        query = plan["query"]

        print("🤖 Agent:", command_type)

        # =========================
        # APPLICATION
        # =========================

        if command_type == "open_app":
            return tools.open_app(query)

        # =========================
        # WEBSITE
        # =========================

        if command_type == "open_website":
            return tools.open_website(query)

        # =========================
        # GOOGLE
        # =========================

        if command_type == "google_search":
            return tools.google_search(query)

        # =========================
        # YOUTUBE
        # =========================

        if command_type == "youtube_search":
            return tools.youtube_search(query)

        # =========================
        # SCROLL
        # =========================

        if command_type == "browser_scroll":
            return tools.scroll()

        # =========================
        # READ
        # =========================

        if command_type == "browser_read":
            return tools.read_page()

        # =========================
        # TYPE
        # =========================

        if command_type == "browser_type":
            return tools.type_text(query)

        # =========================
        # PRESS KEY
        # =========================

        if command_type == "browser_press":
            return tools.press(query)

        # =========================
        # CLICK
        # =========================

        if command_type == "browser_click":
            return tools.click_text(query)

        # =========================
        # FIND
        # =========================

        if command_type == "browser_find":
            return tools.find_text(query)

        # =========================
        # JARVIS FOLDER
        # =========================

        if command_type == "open_jarvis_folder":
            return tools.open_jarvis_folder()

        # =========================
        # AI
        # =========================

        if command_type == "ai":
            return None

        return None


agent = JarvisAgent()