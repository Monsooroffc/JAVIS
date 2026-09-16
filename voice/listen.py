import speech_recognition as sr
from config import LISTEN_TIMEOUT, PHRASE_TIME_LIMIT

recognizer = sr.Recognizer()
microphone = sr.Microphone()

def calibrate():
    print("🎤 Calibrating microphone...")
    
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)

    print("✅ Microphone ready.")

def listen():
    with microphone as source:
        try:
            audio = recognizer.listen(
                source,
                timeout=LISTEN_TIMEOUT,
                phrase_time_limit=PHRASE_TIME_LIMIT
            )
        except sr.WaitTimeoutError:
            return ""

    try:
        text = recognizer.recognize_google(audio)
        print("YOU:", text)
        return text.lower().strip()

    except sr.UnknownValueError:
        return ""

    except sr.RequestError:
        print("❌ Speech recognition service unavailable.")
        return ""