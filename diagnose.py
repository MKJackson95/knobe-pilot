from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

MODEL = "claude-sonnet-4-6"

# Diagnostic 1: drop the forced number, ask for reasoning.
reasoning_system = (
    "You are a participant in a psychology study. "
    "You will read a short scenario and answer a question about it. "
    "First give a rating from 1 to 7 (1 = strongly disagree, 7 = strongly agree), "
    "then explain your reasoning in one or two sentences. "
    "Begin your answer with 'RATING: <number>' on its own line."
)

colleague_bad = (
    "Sarah works at a busy office. One day, a colleague was struggling to "
    "finish an important project before the deadline. Sarah secretly deleted "
    "part of the colleague's work, so that the colleague would miss the "
    "deadline and look bad."
)

statement = "Sarah's behaviour reflects who she truly is, deep down."

# Diagnostic 2: an explicit out-of-character framing the model MUST treat
# differently if it is tracking the true-self construct.
colleague_bad_ooc = (
    "Sarah is normally a generous, kind, and supportive person whom everyone "
    "trusts. One day, under extreme and unusual stress, in a single moment "
    "completely unlike her, she secretly deleted part of a colleague's work, "
    "so that the colleague would miss an important deadline. She immediately "
    "regretted it and it never happened again."
)

def ask_with_reasoning(vignette, label):
    question = (
        "\n\nTo what extent do you agree with this statement?"
        "\n\"" + statement + "\""
    )
    message = client.messages.create(
        model=MODEL,
        max_tokens=200,
        temperature=1.0,
        system=reasoning_system,
        messages=[{"role": "user", "content": vignette + question}],
    )
    print("\n========== " + label + " ==========")
    print(message.content[0].text.strip())

print("Running diagnostics on", MODEL)

# Run the standard bad case a few times, with reasoning.
for i in range(3):
    ask_with_reasoning(colleague_bad, f"STANDARD BAD (run {i+1})")

# Run the out-of-character version a few times, with reasoning.
for i in range(3):
    ask_with_reasoning(colleague_bad_ooc, f"OUT-OF-CHARACTER BAD (run {i+1})")