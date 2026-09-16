import ollama

response = ollama.chat(
    model="qwen2.5:1.5b",
    messages=[
        {
            "role": "user",
            "content": "Hello. Introduce yourself as my local JARVIS AI in one short sentence."
        }
    ]
)

print("JARVIS:", response["message"]["content"])