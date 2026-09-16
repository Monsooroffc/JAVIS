import re


FILLER_WORDS = [
    "please",
    "could you",
    "can you",
    "would you",
    "will you",
    "i want you to",
    "i need you to",
    "hey jarvis",
    "jarvis",
    "bro",
]


def normalize(text):

    text = text.lower().strip()

    for phrase in FILLER_WORDS:
        text = text.replace(phrase, " ")

    return re.sub(r"\s+", " ", text).strip()


def route_command(text):

    command = normalize(text)

    # EXIT
    if command in [
        "exit",
        "quit",
        "goodbye",
        "shutdown jarvis",
    ]:
        return {
            "type": "exit",
            "command": command,
            "query": None,
        }

    # MEMORY
    if (
        "what do you remember" in command
        or "show my memory" in command
        or "what do you know about me" in command
    ):
        return {
            "type": "memory",
            "command": command,
            "query": None,
        }

    if command.startswith("remember "):
        return {
            "type": "remember",
            "command": command,
            "query": command[9:].strip(),
        }

    # APPS
    apps = [
        "notepad",
        "calculator",
        "calc",
        "paint",
        "chrome",
        "google chrome",
    ]

    for app in apps:

        if command in [
            app,
            f"open {app}",
            f"start {app}",
            f"launch {app}",
        ]:
            return {
                "type": "open_app",
                "command": command,
                "query": app,
            }

    # SCROLL
    if command in [
        "scroll",
        "scroll down",
        "scroll up",
        "scroll the page",
    ]:
        return {
            "type": "browser_scroll",
            "command": command,
            "query": None,
        }

    # READ
    if command in [
        "read page",
        "read this page",
        "read the page",
        "read website",
        "read this website",
        "what is on this page",
        "what's on this page",
    ]:
        return {
            "type": "browser_read",
            "command": command,
            "query": None,
        }

    # TYPE
    if command.startswith("type "):

        return {
            "type": "browser_type",
            "command": command,
            "query": command[5:].strip(),
        }

    # PRESS
    if command.startswith("press "):

        return {
            "type": "browser_press",
            "command": command,
            "query": command[6:].strip(),
        }

    # CLICK
    if command.startswith("click "):

        return {
            "type": "browser_click",
            "command": command,
            "query": command[6:].strip(),
        }

    # FIND
    if command.startswith("find "):

        return {
            "type": "browser_find",
            "command": command,
            "query": command[5:].strip(),
        }

    # WEBSITE
    website_patterns = [
        "open website ",
        "go to website ",
        "visit website ",
        "launch website ",
        "open ",
        "go to ",
        "visit ",
        "launch ",
    ]

    for pattern in website_patterns:

        if command.startswith(pattern):

            site = command[len(pattern):].strip()

            if site.endswith(" website"):
                site = site[:-8].strip()

            if site:

                return {
                    "type": "open_website",
                    "command": command,
                    "query": site,
                }

    # GOOGLE SEARCH
    search_patterns = [
        "search for ",
        "search ",
        "google ",
        "look up ",
    ]

    for pattern in search_patterns:

        if command.startswith(pattern):

            query = command[len(pattern):].strip()

            if query:

                return {
                    "type": "google_search",
                    "command": command,
                    "query": query,
                }

    # YOUTUBE
    if command.startswith("play "):

        query = command[5:].strip()

        if query:

            return {
                "type": "youtube_search",
                "command": command,
                "query": query,
            }

    # CLOSE APP
    if command.startswith("close "):

        return {
            "type": "close_app",
            "command": command,
            "query": command[6:].strip(),
        }

    # SYSTEM
    if command in [
        "time",
        "what time is it",
        "what is the time",
        "date",
        "what date is it",
        "what is today's date",
        "what day is it",
    ]:
        return {
            "type": "system",
            "command": command,
            "query": None,
        }

    # JARVIS FOLDER
    if "open jarvis folder" in command:
        return {
            "type": "open_jarvis_folder",
            "command": command,
            "query": None,
        }

    # AI
    return {
        "type": "ai",
        "command": command,
        "query": command,
    }