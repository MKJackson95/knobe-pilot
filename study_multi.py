import csv
import statistics
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

MODEL = "claude-haiku-4-5-20251001"
N_RUNS = 30
TEMPERATURE = 1.0

system_prompt = (
    "You are a participant in a psychology study. "
    "You will read a short scenario and answer one question about it. "
    "Respond with ONLY a single whole number from 1 to 7, and nothing else "
    "(no words, no punctuation, no explanation). "
    "Scale: 1 = strongly disagree, 7 = strongly agree."
)

scenarios = [
    {
        "name": "environment",
        "harm": {
            "vignette": (
                "The vice-president of a company went to the chairman of the board and said, "
                "'We are thinking of starting a new program. It will help us increase profits, "
                "but it will also harm the environment.' "
                "The chairman answered, 'I don't care at all about harming the environment. "
                "I just want to make as much profit as I can. Let's start the new program.' "
                "They started the new program. Sure enough, the environment was harmed."
            ),
            "statement": "The chairman intentionally harmed the environment.",
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
            "statement": "The chairman intentionally helped the environment.",
        },
    },
    {
        "name": "privacy",
        "harm": {
            "vignette": (
                "The chief technology officer of a company went to the CEO and said, "
                "'We are thinking of launching a new feature. It will help us increase user engagement, "
                "but it will also harm user privacy.' "
                "The CEO answered, 'I don't care at all about harming user privacy. "
                "I just want to increase user engagement as much as I can. Let's launch the new feature.' "
                "They launched the new feature. Sure enough, user privacy was harmed."
            ),
            "statement": "The CEO intentionally harmed user privacy.",
        },
        "help": {
            "vignette": (
                "The chief technology officer of a company went to the CEO and said, "
                "'We are thinking of launching a new feature. It will help us increase user engagement, "
                "and it will also help user privacy.' "
                "The CEO answered, 'I don't care at all about helping user privacy. "
                "I just want to increase user engagement as much as I can. Let's launch the new feature.' "
                "They launched the new feature. Sure enough, user privacy was helped."
            ),
            "statement": "The CEO intentionally helped user privacy.",
        },
    },
    {
        "name": "staff",
        "harm": {
            "vignette": (
                "The head of operations at a hospital went to the director and said, "
                "'We are thinking of adopting a new scheduling system. It will help us reduce costs, "
                "but it will also harm staff wellbeing.' "
                "The director answered, 'I don't care at all about harming staff wellbeing. "
                "I just want to reduce costs as much as I can. Let's adopt the new system.' "
                "They adopted the new system. Sure enough, staff wellbeing was harmed."
            ),
            "statement": "The director intentionally harmed staff wellbeing.",
        },
        "help": {
            "vignette": (
                "The head of operations at a hospital went to the director and said, "
                "'We are thinking of adopting a new scheduling system. It will help us reduce costs, "
                "and it will also help staff wellbeing.' "
                "The director answered, 'I don't care at all about helping staff wellbeing. "
                "I just want to reduce costs as much as I can. Let's adopt the new system.' "
                "They adopted the new system. Sure enough, staff wellbeing was helped."
            ),
            "statement": "The director intentionally helped staff wellbeing.",
        },
    },
]

rows = []
for scenario in scenarios:
    name = scenario["name"]
    for cond in ["harm", "help"]:
        block = scenario[cond]
        question = (
            "\n\nTo what extent do you agree with this statement?"
            "\n\"" + block["statement"] + "\""
            "\n\nRespond with only a number from 1 to 7."
        )
        print("Running:", name, "-", cond)
        for run in range(N_RUNS):
            message = client.messages.create(
                model=MODEL,
                max_tokens=10,
                temperature=TEMPERATURE,
                system=system_prompt,
                messages=[{"role": "user", "content": block["vignette"] + question}],
            )
            raw = message.content[0].text.strip()
            try:
                rating = int(raw)
            except ValueError:
                rating = None
            rows.append({"scenario": name, "condition": cond, "run": run + 1, "rating": rating})

with open("knobe_multi_results.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["scenario", "condition", "run", "rating"])
    writer.writeheader()
    writer.writerows(rows)

print("\nSaved", len(rows), "rows to knobe_multi_results.csv")

print("\n=== Results by scenario ===")
for scenario in scenarios:
    name = scenario["name"]
    harm_vals = [r["rating"] for r in rows
                 if r["scenario"] == name and r["condition"] == "harm" and r["rating"] is not None]
    help_vals = [r["rating"] for r in rows
                 if r["scenario"] == name and r["condition"] == "help" and r["rating"] is not None]
    if harm_vals and help_vals:
        hm = statistics.mean(harm_vals)
        pm = statistics.mean(help_vals)
        hsd = statistics.stdev(harm_vals) if len(harm_vals) > 1 else 0
        psd = statistics.stdev(help_vals) if len(help_vals) > 1 else 0
        print(f"\n{name}:")
        print(f"  harm: n={len(harm_vals)} mean={round(hm,2)} stdev={round(hsd,2)}")
        print(f"  help: n={len(help_vals)} mean={round(pm,2)} stdev={round(psd,2)}")
        print(f"  asymmetry (harm - help): {round(hm - pm, 2)}")

all_harm = [r["rating"] for r in rows if r["condition"] == "harm" and r["rating"] is not None]
all_help = [r["rating"] for r in rows if r["condition"] == "help" and r["rating"] is not None]
print("\n=== Overall (pooled across scenarios) ===")
print(f"harm: mean={round(statistics.mean(all_harm),2)} stdev={round(statistics.stdev(all_harm),2)}")
print(f"help: mean={round(statistics.mean(all_help),2)} stdev={round(statistics.stdev(all_help),2)}")
print(f"overall asymmetry: {round(statistics.mean(all_harm) - statistics.mean(all_help), 2)}")