import subprocess
import os


def open_app(app):
    app = app.lower().strip()

    if app == "notepad":
        subprocess.Popen(["notepad.exe"])
        return "Opening Notepad, bro."

    if app in ["calculator", "calc"]:
        subprocess.Popen(["calc.exe"])
        return "Opening Calculator, bro."

    if app == "paint":
        subprocess.Popen(["mspaint.exe"])
        return "Opening Paint, bro."

    if app in ["chrome", "google chrome"]:
        chrome_paths = [
            os.path.expandvars(
                r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"
            ),
            os.path.expandvars(
                r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
            ),
            os.path.expandvars(
                r"%LocalAppData%\Google\Chrome\Application\chrome.exe"
            ),
        ]

        for path in chrome_paths:
            if os.path.exists(path):
                subprocess.Popen([path])
                return "Opening Google Chrome, bro."

        return "I couldn't find Google Chrome."

    return None