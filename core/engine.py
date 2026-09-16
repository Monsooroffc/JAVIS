class JarvisEngine:

    def __init__(self):
        self.running = True
        self.conversation_mode = False

    def start_conversation(self):
        self.conversation_mode = True
        print("💬 Conversation mode: ON")

    def stop_conversation(self):
        self.conversation_mode = False
        print("💬 Conversation mode: OFF")

    def should_continue(self):
        return self.running

    def shutdown(self):
        self.running = False
        self.conversation_mode = False
        print("🔴 JARVIS engine stopped.")