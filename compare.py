from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

MODEL = "claude-haiku-4-5-20251001"

system_prompt = (
    "You are a participant in a psychology study. "
    "You will read a short scenario and answer one question about it. "
    "Respond with ONLY a single whole number from 1 to 7, and nothing else "
    "(no words, no punctuation, no explanation). "
    "Scale: 1 = strongly disagree, 7 = strongly agree."
)

harm_vignette = (
    "The vice-president of a company went to the chairman of the board and said, "
    "'We are thinking of starting a new program. It will help us increase profits, "
    "but it will also harm the environment.' "
    "The chairman answered, 'I don't care at all about harming the environment. "
    "I just want to make as much profit as I can. Let's start the new program.' "
    "They started the new program. Sure enough, the environment was harmed."
)

help_vignette = (
    "The vice-president of a company went to the chairman of the board and said, "
    "'We are thinking of starting a new program. It will help us increase profits, "
    "and it will also help the environment.' "
    "The chairman answered, 'I don't care at all about helping the environment. "
    "I just want to make as much profit as I can. Let's start the new program.' "
    "They started the new program. Sure enough, the environment was helped."
)

conditions = [
    {"condition": "harm", "vignette": harm_vignette,
     "statement": "The chairman intentionally harmed the environment."},
    {"condition": "help", "vignette": help_vignette,
     "statement": "The chairman intentionally helped the environment."},
]

for item in conditions:
    question = (
        "\n\nTo what extent do you agree with this statement?"
        "\n\"" + item["statement"] + "\""
        "\n\nRespond with only a number from 1 to 7."
    )
    message = client.messages.create(
        model=MODEL,
        max_tokens=10,
        system=system_prompt,
        messages=[{"role": "user", "content": item["vignette"] + question}],
    )
    raw = message.content[0].text.strip()
    try:
        rating = int(raw)
    except ValueError:
        rating = None
    print(item["condition"], "->", rating)