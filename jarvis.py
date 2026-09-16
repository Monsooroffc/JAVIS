from config import WAKE_WORD

from voice.speak import speak
from voice.listen import listen, calibrate

from brain.ai import ask_ai
from brain.router import route_command

from memory.memory import (
    remember,
    get_memory,
    memory_count,
)

from commands.system import system_command

from agent.agent import agent


def handle_command(text):
    """Process one JARVIS command."""

    if not text:
        return True

    print()
    print("🔄 Processing:", text)

    route = route_command(text)

    command_type = route["type"]
    query = route["query"]

    print("🧭 Route:", command_type)

    # =========================
    # EXIT JARVIS
    # =========================

    if command_type == "exit":

        speak("Goodbye bro. JARVIS is going offline.")

        return False

    # =========================
    # MEMORY
    # =========================

    if command_type == "memory":

        memories = get_memory()

        if not memories:

            speak("My memory is currently empty, bro.")

        else:

            speak(
                f"I have {memory_count()} memories saved, bro."
            )

            print()
            print("🧠 JARVIS MEMORY")
            print("=" * 40)

            for index, item in enumerate(memories, 1):

                if isinstance(item, dict):

                    memory_text = item.get("text", "")
                    created = item.get("created", "")

                else:

                    memory_text = str(item)
                    created = ""

                print(f"{index}. {memory_text}")

                if created:
                    print(f"   Saved: {created}")

            print("=" * 40)

        return True

    # =========================
    # REMEMBER
    # =========================

    if command_type == "remember":

        if not query:

            speak("What should I remember, bro?")

            return True

        if remember(query):

            speak(
                "Got it bro. I saved that to my memory."
            )

        else:

            speak(
                "I already remember that."
            )

        return True

    # =========================
    # AGENT TOOLS
    # =========================

    agent_commands = [
        "open_app",
        "open_website",
        "google_search",
        "youtube_search",
        "open_jarvis_folder",
    ]

    if command_type in agent_commands:

        result = agent.process(text)

        if result:

            speak(result)

        else:

            speak(
                "I couldn't complete that action, bro."
            )

        return True

    # =========================
    # CLOSE APP
    # =========================

    if command_type == "close_app":

        from commands.computer import execute_command

        result = execute_command(text)

        if result:
            speak(result)
        else:
            speak("I couldn't close that application, bro.")

        return True

    # =========================
    # SYSTEM
    # =========================

    if command_type == "system":

        result = system_command(text)

        if result:

            speak(result)

        else:

            speak(
                "I couldn't get that system information, bro."
            )

        return True

    # =========================
    # AI
    # =========================

    if command_type == "ai":

        speak("Let me think, bro.")

        answer = ask_ai(query)

        if answer:

            speak(answer)

        else:

            speak(
                "I couldn't get a response from my AI brain."
            )

        return True

    return True


def main():

    print()
    print("=" * 60)
    print("                 J A R V I S")
    print("                   V 6.0")
    print("=" * 60)
    print()

    print("🧠 AI          : ONLINE")
    print("💾 MEMORY      : ONLINE")
    print("🎤 VOICE       : ONLINE")
    print("🔊 SPEECH      : ONLINE")
    print("🤖 AGENT       : ONLINE")
    print("🧭 ROUTER      : ONLINE")
    print("💻 TOOLS       : ONLINE")
    print("💬 CONVERSATION: CONTINUOUS")
    print("⚡ WAKE WORD   : JARVIS")

    print()
    print("=" * 60)

    # =========================
    # MICROPHONE
    # =========================

    try:

        calibrate()

    except Exception as error:

        print("❌ Microphone error:", error)

        return

    # =========================
    # START JARVIS
    # =========================

    speak(
        "Hello bro. JARVIS version six is online."
    )

    # =========================
    # MAIN LOOP
    # =========================

    while True:

        print()
        print("💤 Waiting for wake word...")

        wake = listen()

        if not wake:
            continue

        print("👂 Heard:", wake)

        if WAKE_WORD.lower() not in wake.lower():

            continue

        speak(
            "Yes bro. I'm listening."
        )

        # =========================
        # CONTINUOUS CONVERSATION
        # =========================

        while True:

            print()
            print("🎤 Listening...")

            command = listen()

            if not command:

                speak(
                    "I didn't hear you bro."
                )

                continue

            print("YOU:", command)

            command_lower = command.lower().strip()

            # =========================
            # SLEEP
            # =========================

            sleep_commands = [
                "goodbye",
                "go to sleep",
                "sleep",
                "stop listening",
                "that's all",
                "thats all",
                "exit conversation",
                "stop conversation",
            ]

            if any(
                word in command_lower
                for word in sleep_commands
            ):

                speak(
                    "Okay bro. I'll wait for you."
                )

                break

            # =========================
            # PROCESS
            # =========================

            running = handle_command(command)

            if running is False:

                return


if __name__ == "__main__":

    main()