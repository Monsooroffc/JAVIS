from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-luna",
    input="Say hello to my JARVIS project in one short sentence."
)

print("JARVIS:", response.output_text)