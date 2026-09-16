import pyttsx3


def speak(text):
    if not text:
        return

    print("JARVIS:", text)

    try:
        engine = pyttsx3.init()

        engine.setProperty("rate", 175)
        engine.setProperty("volume", 1.0)

        engine.say(str(text))
        engine.runAndWait()

        engine.stop()

    except Exception as e:
        print("Speech error:", e)