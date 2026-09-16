import pyttsx3
import speech_recognition as sr

# =========================
# JARVIS VOICE
# =========================

jarvis = pyttsx3.init()
jarvis.setProperty("rate", 170)
jarvis.setProperty("volume", 1.0)


def speak(text):
    print("JARVIS:", text)
    jarvis.say(text)
    jarvis.runAndWait()


# =========================
# JARVIS LISTENING
# =========================

recognizer = sr.Recognizer()


def listen():
    with sr.Microphone() as source:
        print("\n🎤 JARVIS is listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)

        try:
            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=8
            )

            print("🔄 Processing...")

            text = recognizer.recognize_google(audio)

            print("YOU:", text)

            return text.lower()

        except sr.WaitTimeoutError:
            print("JARVIS: I didn't hear anything.")
            return ""

        except sr.UnknownValueError:
            print("JARVIS: I couldn't understand that.")
            return ""

        except sr.RequestError:
            print("JARVIS: Speech recognition service is unavailable.")
            return ""


# =========================
# START JARVIS
# =========================

speak("Hello. I am JARVIS. My voice system is online.")

while True:

    command = listen()

    if command in ["exit", "quit", "shutdown", "goodbye"]:
        speak("Goodbye bro. JARVIS is shutting down.")
        break

    if command:
        speak("You said " + command)