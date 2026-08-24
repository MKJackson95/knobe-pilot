import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

prompts = [
    "In two sentences, what is the Knobe effect?",
    "In two sentences, what is the true-self effect in moral psychology?",
    "In two sentences, what is experimental philosophy?",
]

for prompt in prompts:
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    print("PROMPT:", prompt)
    print(message.content[0].text)
    print("-" * 40)