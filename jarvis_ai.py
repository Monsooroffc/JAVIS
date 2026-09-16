import pyttsx3
import speech_recognition as sr
import ollama
import subprocess
import webbrowser
import datetime
import os


# =========================================================
# JARVIS CONFIGURATION
# =========================================================

MODEL = "qwen2.5:1.5b"

# Maximum number of previous messages kept in memory
MAX_HISTORY = 10


# =========================================================
# VOICE ENGINE
# =========================================================

engine = pyttsx3.init()

engine.setProperty("rate", 170)
engine.setProperty("volume", 1.0)


def speak(text):
    print("\nJARVIS:", text)

    engine.say(text)
    engine.runAndWait()


# =========================================================
# SPEECH RECOGNITION
# =========================================================

recognizer = sr.Recognizer()

recognizer.pause_threshold = 0.8
recognizer.phrase_threshold = 0.3
recognizer.non_speaking_duration = 0.5


def calibrate_microphone():

    print("\n🎧 Calibrating microphone...")
    print("Please stay quiet for one second...")

    with sr.Microphone() as source:

        recognizer.adjust_for_ambient_noise(
            source,
            duration=1
        )

    print("✅ Microphone ready.")


def listen():

    with sr.Microphone() as source:

        print("\n🎤 JARVIS is listening...")

        try:

            audio = recognizer.listen(
                source,
                timeout=7,
                phrase_time_limit=10
            )

            print("🔄 Processing...")

            text = recognizer.recognize_google(audio)

            print("YOU:", text)

            return text.lower().strip()

        except sr.WaitTimeoutError:

            print("JARVIS: I didn't hear anything.")

            return ""

        except sr.UnknownValueError:

            print("JARVIS: I couldn't understand that.")

            return ""

        except sr.RequestError:

            print("JARVIS: Speech recognition service is unavailable.")

            return ""


# =========================================================
# COMPUTER CONTROL
# =========================================================

def computer_command(command):

    # Open Notepad
    if "open notepad" in command:

        subprocess.Popen("notepad.exe")

        speak("Opening Notepad.")

        return True


    # Open Calculator
    if "open calculator" in command:

        subprocess.Popen("calc.exe")

        speak("Opening Calculator.")

        return True


    # Open Chrome
    if "open chrome" in command:

        chrome_paths = [

            r"C:\Program Files\Google\Chrome\Application\chrome.exe",

            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

        ]

        for path in chrome_paths:

            if os.path.exists(path):

                subprocess.Popen(path)

                speak("Opening Chrome.")

                return True

        speak("Chrome was not found.")

        return True


    # Open YouTube
    if "open youtube" in command:

        webbrowser.open("https://www.youtube.com")

        speak("Opening YouTube.")

        return True


    # Open Google
    if "open google" in command:

        webbrowser.open("https://www.google.com")

        speak("Opening Google.")

        return True


    # Open JARVIS folder
    if "open jarvis folder" in command:

        os.startfile(r"C:\Users\acer\JARVIS")

        speak("Opening your JARVIS folder.")

        return True


    # Search Google
    if command.startswith("search for "):

        query = command.replace(
            "search for ",
            "",
            1
        )

        if query:

            url = (
                "https://www.google.com/search?q="
                + query.replace(" ", "+")
            )

            webbrowser.open(url)

            speak("Searching Google for " + query)

        return True


    return False


# =========================================================
# TIME AND DATE
# =========================================================

def time_date_command(command):

    if "what time" in command or "current time" in command:

        current_time = datetime.datetime.now().strftime(
            "%I:%M %p"
        )

        speak("The current time is " + current_time)

        return True


    if "what date" in command or "today's date" in command:

        current_date = datetime.datetime.now().strftime(
            "%A, %d %B %Y"
        )

        speak("Today is " + current_date)

        return True


    return False


# =========================================================
# LOCAL AI BRAIN
# =========================================================

conversation = [

    {
        "role": "system",
        "content": (
            "You are JARVIS, a personal AI assistant. "
            "You are running locally on the user's computer "
            "using Ollama. "
            "Give useful, accurate and concise answers. "
            "Speak naturally because your answers will be "
            "read aloud using text to speech."
        )
    }

]


def ask_ai(command):

    global conversation

    conversation.append({

        "role": "user",

        "content": command

    })


    # Keep conversation small so the local model stays fast

    if len(conversation) > MAX_HISTORY + 1:

        conversation = (
            [conversation[0]]
            + conversation[-MAX_HISTORY:]
        )


    try:

        response = ollama.chat(

            model=MODEL,

            messages=conversation

        )

        answer = response["message"]["content"]


        conversation.append({

            "role": "assistant",

            "content": answer

        })


        return answer


    except Exception as error:

        print("\nAI ERROR:", error)

        return (
            "Sorry bro. I couldn't connect "
            "to my local AI brain."
        )


# =========================================================
# MAIN JARVIS SYSTEM
# =========================================================

def main():

    print("\n")
    print("=" * 55)
    print("        J A R V I S   A I")
    print("=" * 55)
    print("🧠 Local AI  :", MODEL)
    print("🎤 Voice     : Online")
    print("🔊 Speech    : Online")
    print("💻 Control   : Online")
    print("=" * 55)


    # Microphone calibration

    calibrate_microphone()


    speak(
        "Hello bro. I am JARVIS. "
        "My local AI brain is online."
    )


    while True:

        command = listen()


        if not command:

            continue


        # =================================================
        # SHUTDOWN
        # =================================================

        if command in [

            "exit",

            "quit",

            "shutdown",

            "goodbye",

            "stop jarvis",

            "shutdown jarvis"

        ]:

            speak(
                "Goodbye bro. "
                "JARVIS is shutting down."
            )

            break


        # =================================================
        # COMPUTER COMMANDS
        # =================================================

        if computer_command(command):

            continue


        # =================================================
        # TIME / DATE
        # =================================================

        if time_date_command(command):

            continue


        # =================================================
        # AI
        # =================================================

        answer = ask_ai(command)

        speak(answer)


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    main()