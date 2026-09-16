"""Tool layer: everything JARVIS can actually do on the computer."""

from tools.apps import App, AppRegistry, open_app, registry
from tools.browser import BrowserAgent, browser, google_search, open_website
from tools.browser import youtube_search
from tools.files import open_folder, open_jarvis_folder
from tools.manager import ToolManager, tools

__all__ = [
    "App",
    "AppRegistry",
    "BrowserAgent",
    "ToolManager",
    "browser",
    "google_search",
    "open_app",
    "open_folder",
    "open_jarvis_folder",
    "open_website",
    "registry",
    "tools",
    "youtube_search",
]