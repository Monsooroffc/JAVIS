"""JARVIS V7.2 - Continuous Voice Assistant."""

from __future__ import annotations

from agent.agent import agent
from core.logger import get_logger
from voice.listen import calibrate, listen
from voice.speak import speak

log = get_logger(__name__)


def main() -> None:
    """Run JARVIS in continuous voice mode."""

    print("=" * 55)
    print("              JARVIS V7.2")
    print("          VOICE SYSTEM ONLINE")
    print("=" * 55)

    speak("JARVIS is online, bro. I am listening.")

    # Calibrate microphone once at startup.
    print("\nCalibrating microphone...")
    if not calibrate():
        speak("I cannot access the microphone, bro.")
        print("ERROR: Microphone calibration failed.")
        return

    speak("Microphone ready, bro.")

    while True:
        try:
            print("\n🎤 Listening...")

            text = listen()

            if not text:
                continue

            print(f"YOU: {text}")

            # Exit commands
            if text in {
                "exit",
                "quit",
                "shutdown",
                "goodbye",
                "stop listening",
            }:
                speak("Shutting down JARVIS. Goodbye, bro.")
                break

            # Send speech to the agent.
            reply = agent.process(text)

            if reply:
                print(f"JARVIS: {reply}")
                speak(reply)

            else:
                reply = "I don't know how to do that yet, bro."
                print(f"JARVIS: {reply}")
                speak(reply)

        except KeyboardInterrupt:
            print("\n")
            speak("JARVIS shutting down, bro.")
            break

        except Exception as error:
            log.error("Main loop error: %s", error)
            speak("Something went wrong, bro.")


if __name__ == "__main__":
    main()