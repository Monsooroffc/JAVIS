import subprocess
import os


JARVIS_FOLDER = r"C:\Users\acer\JARVIS"


def open_jarvis_folder():
    if os.path.exists(JARVIS_FOLDER):
        subprocess.Popen(["explorer.exe", JARVIS_FOLDER])
        return "Opening the JARVIS folder, bro."

    return "I couldn't find the JARVIS folder."