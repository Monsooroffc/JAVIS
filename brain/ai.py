import ollama
from config import MODEL

conversation = []

def ask_ai(user_text):
    conversation.append({
        "role": "user",
        "content": user_text
    })

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are JARVIS, a helpful personal AI assistant. "
                    "Keep answers short and natural. "
                    "Call the user bro when appropriate."
                )
            },
            *conversation[-10:]
        ]
    )

    answer = response["message"]["content"]

    conversation.append({
        "role": "assistant",
        "content": answer
    })

    return answer	