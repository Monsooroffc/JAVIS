import subprocess
import webbrowser
import urllib.parse
import os


def execute_command(text):

    text = text.lower().strip()

    # =========================
    # OPEN APPLICATIONS
    # =========================

    if (
        "open notepad" in text
        or text == "notepad"
        or "start notepad" in text
    ):
        subprocess.Popen(["notepad.exe"])
        return "Opening Notepad, bro."

    if (
        "open calculator" in text
        or "open calc" in text
        or text == "calculator"
        or text == "calc"
    ):
        subprocess.Popen(["calc.exe"])
        return "Opening Calculator, bro."

    if "open paint" in text or text == "paint":
        subprocess.Popen(["mspaint.exe"])
        return "Opening Paint, bro."

    # =========================
    # OPEN WEBSITES
    # =========================

    if "open youtube" in text or text == "youtube":
        webbrowser.open("https://www.youtube.com")
        return "Opening YouTube, bro."

    if "open google" in text or text == "google":
        webbrowser.open("https://www.google.com")
        return "Opening Google."

    if "open github" in text or text == "github":
        webbrowser.open("https://github.com")
        return "Opening GitHub."

    if "open chatgpt" in text or text == "chatgpt":
        webbrowser.open("https://chatgpt.com")
        return "Opening ChatGPT."

    # =========================
    # SEARCH GOOGLE
    # =========================

    if text.startswith("search for "):

        query = text.replace("search for ", "", 1).strip()

        if query:
            url = (
                "https://www.google.com/search?q="
                + urllib.parse.quote(query)
            )

            webbrowser.open(url)

            return f"Searching Google for {query}."

    # =========================
    # PLAY / SEARCH YOUTUBE
    # =========================

    if text.startswith("play "):

        query = text.replace("play ", "", 1).strip()

        if query:

            url = (
                "https://www.youtube.com/results?search_query="
                + urllib.parse.quote(query)
            )

            webbrowser.open(url)

            return f"Searching YouTube for {query}."

    # =========================
    # OPEN JARVIS FOLDER
    # =========================

    if "open jarvis folder" in text:

        path = r"C:\Users\acer\JARVIS"

        if os.path.exists(path):
            subprocess.Popen(["explorer.exe", path])
            return "Opening the JARVIS folder, bro."

    # =========================
    # CLOSE APPLICATIONS
    # =========================

    if "close notepad" in text or "close the notepad" in text:

        subprocess.run(
            ["taskkill", "/IM", "notepad.exe", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        return "Closing Notepad, bro."

    if "close calculator" in text or "close the calculator" in text:

        subprocess.run(
            ["taskkill", "/IM", "CalculatorApp.exe", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        return "Closing Calculator, bro."

    if "close chrome" in text or "close google chrome" in text:

        subprocess.run(
            ["taskkill", "/IM", "chrome.exe", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        return "Closing Chrome, bro."

    return None