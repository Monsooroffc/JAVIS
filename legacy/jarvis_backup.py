import pyttsx3
import speech_recognition as sr
import ollama
import subprocess
import webbrowser
import datetime
import os
import json
import time

# =========================================================
# SETTINGS
# =========================================================

MODEL = "qwen2.5:1.5b"
MEMORY_FILE = "memory.json"
MAX_HISTORY = 10

# =========================================================
# TEXT TO SPEECH
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


def listen(timeout=5, phrase_time_limit=7):

    with sr.Microphone() as source:

        try:

            print("🎤 Listening...")

            audio = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit
            )

            print("🔄 Processing...")

            text = recognizer.recognize_google(audio)

            print("YOU:", text)

            return text.lower().strip()

        except sr.WaitTimeoutError:

            return ""

        except sr.UnknownValueError:

            return ""

        except sr.RequestError:

            print("❌ Speech recognition service unavailable.")

            return ""


# =========================================================
# MEMORY
# =========================================================

def load_memory():

    if not os.path.exists(MEMORY_FILE):
        return []

    try:

        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:

        return []


def save_memory():

    with open(
        MEMORY_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            memories,
            file,
            indent=4,
            ensure_ascii=False
        )


def add_memory(text):

    if text not in memories:

        memories.append(text)

        if len(memories) > 50:
            memories.pop(0)

        save_memory()


def show_memory():

    if not memories:

        speak(
            "I don't have any saved memories yet, bro."
        )

        return

    print("\n========== JARVIS MEMORY ==========")

    for i, memory in enumerate(memories, 1):

        print(f"{i}. {memory}")

    print("===================================\n")

    speak(
        "Here is what I remember, bro. "
        + ". ".join(memories)
    )


memories = load_memory()


# =========================================================
# COMPUTER CONTROL
# =========================================================

def computer_command(command):

    if "open notepad" in command:

        subprocess.Popen("notepad.exe")

        speak("Opening Notepad.")

        return True


    if "open calculator" in command:

        subprocess.Popen("calc.exe")

        speak("Opening Calculator.")

        return True


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


    if "open youtube" in command:

        webbrowser.open(
            "https://www.youtube.com"
        )

        speak("Opening YouTube.")

        return True


    if "open google" in command:

        webbrowser.open(
            "https://www.google.com"
        )

        speak("Opening Google.")

        return True


    if "open jarvis folder" in command:

        os.startfile(
            r"C:\Users\acer\JARVIS"
        )

        speak(
            "Opening your JARVIS folder."
        )

        return True


    if command.startswith("search for "):

        query = command.replace(
            "search for ",
            "",
            1
        ).strip()

        if query:

            url = (
                "https://www.google.com/search?q="
                + query.replace(" ", "+")
            )

            webbrowser.open(url)

            speak(
                "Searching Google for "
                + query
            )

        return True


    return False


# =========================================================
# TIME / DATE
# =========================================================

def time_date_command(command):

    if (
        "what time" in command
        or "current time" in command
    ):

        current_time = datetime.datetime.now().strftime(
            "%I:%M %p"
        )

        speak(
            "The current time is "
            + current_time
        )

        return True


    if (
        "what date" in command
        or "today's date" in command
    ):

        current_date = datetime.datetime.now().strftime(
            "%A, %d %B %Y"
        )

        speak(
            "Today is "
            + current_date
        )

        return True


    return False


# =========================================================
# AI BRAIN
# =========================================================

conversation = [

    {
        "role": "system",

        "content":
        (
            "You are JARVIS, a personal AI assistant. "
            "You run locally using Ollama and Qwen. "
            "Give useful, accurate and concise answers. "
            "Speak naturally because your answers are "
            "read aloud."
        )
    }

]


def ask_ai(command):

    global conversation

    conversation.append(
        {
            "role": "user",
            "content": command
        }
    )

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

        answer = response[
            "message"
        ][
            "content"
        ]

        conversation.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        return answer

    except Exception as error:

        print(
            "\nAI ERROR:",
            error
        )

        return (
            "Sorry bro. "
            "I couldn't connect to my local AI brain."
        )


# =========================================================
# COMMAND PROCESSOR
# =========================================================

def process_command(command):

    # EXIT

    if command in [
        "exit",
        "quit",
        "shutdown",
        "goodbye",
        "stop jarvis"
    ]:

        speak(
            "Goodbye bro. "
            "JARVIS is shutting down."
        )

        return False


    # MEMORY

    if (
        "what do you remember" in command
        or "show my memory" in command
        or "show memories" in command
    ):

        show_memory()

        return True


    # REMEMBER THAT

    if command.startswith(
        "remember that "
    ):

        memory = command.replace(
            "remember that ",
            "",
            1
        ).strip()

        if memory:

            add_memory(memory)

            speak(
                "Okay bro. "
                "I'll remember that."
            )

        return True


    # FAVORITE

    if (
        (
            "my favorite" in command
            or
            "my favourite" in command
        )
        and
        " is " in command
    ):

        add_memory(command)

        speak(
            "Okay bro. "
            "I'll remember that."
        )

        return True


    # COMPUTER

    if computer_command(command):

        return True


    # TIME / DATE

    if time_date_command(command):

        return True


    # AI

    answer = ask_ai(command)

    speak(answer)

    return True


# =========================================================
# WAKE WORD
# =========================================================

def wait_for_wake_word():

    print(
        "\n💤 Waiting for wake word: JARVIS..."
    )

    while True:

        command = listen(
            timeout=10,
            phrase_time_limit=5
        )

        if not command:

            continue

        print(
            "👂 Heard:",
            command
        )

        # Check several common recognition variations

        wake_words = [
            "jarvis",
            "jarvis.",
            "jarvis!",
            "jarvis?"
        ]

        if any(
            word in command
            for word in wake_words
        ):

            print(
                "⚡ WAKE WORD DETECTED!"
            )

            speak(
                "Yes bro?"
            )

            return True

        # If speech recognition hears
        # "hello jarvis", "hey jarvis", etc.

        if (
            "jarv" in command
            or
            "jarvis" in command
        ):

            print(
                "⚡ WAKE WORD DETECTED!"
            )

            speak(
                "Yes bro?"
            )

            return True


# =========================================================
# MAIN
# =========================================================

def main():

    print("\n")
    print("=" * 55)
    print(
        "              J A R V I S   V 2"
    )
    print("=" * 55)

    print(
        "🧠 AI        :",
        MODEL
    )

    print(
        "💾 Memory    : Online"
    )

    print(
        "🎤 Voice     : Online"
    )

    print(
        "🔊 Speech    : Online"
    )

    print(
        "💻 Control   : Online"
    )

    print(
        "⚡ Wake Word : JARVIS"
    )

    print("=" * 55)

    calibrate_microphone()

    speak(
        "Hello bro. "
        "I am JARVIS. "
        "My local AI brain and memory are online."
    )

    while True:

        # WAIT FOR JARVIS

        wait_for_wake_word()

        # LISTEN FOR COMMAND

        command = listen(
            timeout=7,
            phrase_time_limit=10
        )

        if not command:

            speak(
                "I didn't hear you, bro."
            )

            continue

        print(
            "⚡ COMMAND:",
            command
        )

        # EXECUTE COMMAND

        if not process_command(command):

            break

        # Small pause before listening again

        time.sleep(0.3)


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    main()