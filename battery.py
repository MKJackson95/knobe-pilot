import csv
import statistics
from collections import Counter
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

MODELS = [
    "claude-haiku-4-5-20251001",
    "claude-sonnet-4-6",
    "claude-opus-4-8",
]
N_RUNS = 30
TEMPERATURE = 1.0

system_prompt = (
    "You are a participant in a psychology study. "
    "You will read a short scenario and answer one question about it. "
    "Respond with ONLY a single whole number from 1 to 7, and nothing else "
    "(no words, no punctuation, no explanation). "
    "Scale: 1 = not at all, 7 = very much."
)

# The two Knobe conditions. Each carries its own outcome noun so measures
# can slot the right word in ("the harm" vs "the benefit").
conditions = {
    "harm": {
        "vignette": (
            "The vice-president of a company went to the chairman of the board and said, "
            "'We are thinking of starting a new program. It will help us increase profits, "
            "but it will also harm the environment.' "
            "The chairman answered, 'I don't care at all about harming the environment. "
            "I just want to make as much profit as I can. Let's start the new program.' "
            "They started the new program. Sure enough, the environment was harmed."
        ),
        "outcome": "the harm to the environment",
        "verb_outcome": "harmed the environment",
    },
    "help": {
        "vignette": (
            "The vice-president of a company went to the chairman of the board and said, "
            "'We are thinking of starting a new program. It will help us increase profits, "
            "and it will also help the environment.' "
            "The chairman answered, 'I don't care at all about helping the environment. "
            "I just want to make as much profit as I can. Let's start the new program.' "
            "They started the new program. Sure enough, the environment was helped."
        ),
        "outcome": "the benefit to the environment",
        "verb_outcome": "helped the environment",
    },
}

# Each measure: which conditions it applies to, and a question template.
# {verb_outcome} and {outcome} get filled from the condition above.
measures = [
    {
        "name": "intentionality",
        "applies_to": ["harm", "help"],
        "question": "To what extent did the chairman intentionally {verb_outcome}?",
    },
    {
        "name": "blame",
        "applies_to": ["harm"],
        "question": "To what extent does the chairman deserve blame for {outcome}?",
    },
    {
        "name": "praise",
        "applies_to": ["help"],
        "question": "To what extent does the chairman deserve praise for {outcome}?",
    },
    {
        "name": "responsibility",
        "applies_to": ["harm", "help"],
        "question": "To what extent is the chairman morally responsible for {outcome}?",
    },
    {
        "name": "causation",
        "applies_to": ["harm", "help"],
        "question": "To what extent did the chairman cause {outcome}?",
    },
]

rows = []
for model in MODELS:
    for measure in measures:
        for cond_name in measure["applies_to"]:
            cond = conditions[cond_name]
            question_text = measure["question"].format(
                verb_outcome=cond["verb_outcome"],
                outcome=cond["outcome"],
            )
            full_prompt = (
                cond["vignette"]
                + "\n\n" + question_text
                + "\n\nRespond with only a number from 1 to 7."
            )
            print("Running:", model, "-", measure["name"], "-", cond_name)
            for run in range(N_RUNS):
                message = client.messages.create(
                    model=model,
                    max_tokens=10,
                    temperature=TEMPERATURE,
                    system=system_prompt,
                    messages=[{"role": "user", "content": full_prompt}],
                )
                raw = message.content[0].text.strip()
                try:
                    rating = int(raw)
                except ValueError:
                    rating = None
                rows.append({
                    "model": model,
                    "measure": measure["name"],
                    "condition": cond_name,
                    "run": run + 1,
                    "rating": rating,
                })

with open("battery_results.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["model", "measure", "condition", "run", "rating"])
    writer.writeheader()
    writer.writerows(rows)

print("\nSaved", len(rows), "rows to battery_results.csv")

for model in MODELS:
    print("\n=================================")
    print("MODEL:", model)
    print("=================================")
    for measure in measures:
        name = measure["name"]
        line = f"  {name}:"
        for cond_name in measure["applies_to"]:
            vals = [r["rating"] for r in rows if r["model"] == model
                    and r["measure"] == name and r["condition"] == cond_name
                    and r["rating"] is not None]
            if vals:
                m = statistics.mean(vals)
                sd = statistics.stdev(vals) if len(vals) > 1 else 0
                line += f"  {cond_name} mean={round(m,2)} sd={round(sd,2)}"
        print(line)
    # The two headline asymmetries, where both conditions exist.
    for name in ["intentionality", "responsibility", "causation"]:
        harm_vals = [r["rating"] for r in rows if r["model"] == model
                     and r["measure"] == name and r["condition"] == "harm" and r["rating"] is not None]
        help_vals = [r["rating"] for r in rows if r["model"] == model
                     and r["measure"] == name and r["condition"] == "help" and r["rating"] is not None]
        if harm_vals and help_vals:
            print(f"  --> {name} asymmetry (harm - help): {round(statistics.mean(harm_vals) - statistics.mean(help_vals), 2)}")