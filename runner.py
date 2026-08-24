import csv
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

MODEL = "claude-haiku-4-5-20251001"

prompts = [
    "In two sentences, what is the Knobe effect?",
    "In two sentences, what is the true-self effect in moral psychology?",
    "In two sentences, what is experimental philosophy?",
]

rows = []
for prompt in prompts:
    message = client.messages.create(
        model=MODEL,
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    answer = message.content[0].text
    rows.append({"model": MODEL, "prompt": prompt, "response": answer})
    print("Got response for:", prompt)

with open("results.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["model", "prompt", "response"])
    writer.writeheader()
    writer.writerows(rows)

print("Saved", len(rows), "rows to results.csv")