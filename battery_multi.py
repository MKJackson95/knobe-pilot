import csv
import statistics
from datetime import datetime
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
    "You will read a short scenario, then a statement about it. "
    "Respond with ONLY a single whole number from 1 to 7, and nothing else "
    "(no words, no punctuation, no explanation). "
    "Scale: 1 = strongly disagree, 7 = strongly agree."
)

scenarios = [
    {
        "name": "chairman",
        "agent": "the chairman",
        "harm": {
            "vignette": (
                "The vice-president of a company went to the chairman of the board and said, "
                "'We are thinking of starting a new program. It will help us increase profits, "
                "but it will also harm the environment.' "
                "The chairman answered, 'I don't care at all about harming the environment. "
                "I just want to make as much profit as I can. Let's start the new program.' "
                "They started the new program. Sure enough, the environment was harmed."
            ),
            "verb": "harmed the environment",
            "outcome": "the harm to the environment",
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
            "verb": "helped the environment",
            "outcome": "the benefit to the environment",
        },
    },
    {
        "name": "lieutenant",
        "agent": "the lieutenant",
        "harm": {
            "vignette": (
                "A lieutenant was talking with a sergeant. The lieutenant gave the order: "
                "'Send your squad to the top of Thompson Hill.' "
                "The sergeant said, 'But if I send my squad to the top of Thompson Hill, "
                "we'll be moving the men directly into the enemy's line of fire. Some of them "
                "will surely be killed!' "
                "The lieutenant answered, 'Look, I know that they'll be in the line of fire, "
                "and I know that some of them will be killed. But I don't care at all about "
                "what happens to our soldiers. All I care about is taking control of Thompson Hill.' "
                "The squad was sent to the top of Thompson Hill. As expected, the soldiers were "
                "moved into the enemy's line of fire, and some of them were killed."
            ),
            "verb": "put the soldiers in the line of fire",
            "outcome": "the harm to the soldiers",
        },
        "help": {
            "vignette": (
                "A lieutenant was talking with a sergeant. The lieutenant gave the order: "
                "'Send your squad to the top of Thompson Hill.' "
                "The sergeant said, 'If I send my squad to the top of Thompson Hill, "
                "we'll be taking the men out of the enemy's line of fire. They'll be rescued!' "
                "The lieutenant answered, 'Look, I know that we'll be taking them out of the "
                "line of fire, and I know that some of them would have been killed otherwise. "
                "But I don't care at all about what happens to our soldiers. All I care about "
                "is taking control of Thompson Hill.' "
                "The squad was sent to the top of Thompson Hill. As expected, the soldiers were "
                "taken out of the enemy's line of fire, and they thereby escaped getting killed."
            ),
            "verb": "took the soldiers out of the line of fire",
            "outcome": "the benefit to the soldiers",
        },
    },
    {
        "name": "factory",
        "agent": "the owner",
        "harm": {
            "vignette": (
                "The operations manager of a factory went to the owner and said, "
                "'We are thinking of switching to a new production method. It will cut our costs, "
                "but it will also harm the health of people living nearby.' "
                "The owner answered, 'I don't care at all about harming the health of people nearby. "
                "I just want to cut costs as much as I can. Let's switch to the new method.' "
                "They switched to the new method. Sure enough, the health of people living nearby "
                "was harmed."
            ),
            "verb": "harmed the health of nearby residents",
            "outcome": "the harm to nearby residents' health",
        },
        "help": {
            "vignette": (
                "The operations manager of a factory went to the owner and said, "
                "'We are thinking of switching to a new production method. It will cut our costs, "
                "and it will also help the health of people living nearby.' "
                "The owner answered, 'I don't care at all about helping the health of people nearby. "
                "I just want to cut costs as much as I can. Let's switch to the new method.' "
                "They switched to the new method. Sure enough, the health of people living nearby "
                "was helped."
            ),
            "verb": "helped the health of nearby residents",
            "outcome": "the benefit to nearby residents' health",
        },
    },
]

measures = [
    {"name": "intentionality", "applies_to": ["harm", "help"], "template": "{agent} intentionally {verb}."},
    {"name": "blame",          "applies_to": ["harm"],         "template": "{agent} deserves blame for {outcome}."},
    {"name": "praise",         "applies_to": ["help"],         "template": "{agent} deserves praise for {outcome}."},
    {"name": "responsibility", "applies_to": ["harm", "help"], "template": "{agent} is morally responsible for {outcome}."},
    {"name": "causation",      "applies_to": ["harm", "help"], "template": "{agent} caused {outcome}."},
]

# Timestamped filename: never collides with a CSV open in Excel, and every run is kept.
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
outfile = f"battery_multi_{stamp}.csv"

rows = []
with open(outfile, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["model", "scenario", "measure", "condition", "run", "rating"])
    writer.writeheader()

    for model in MODELS:
        for scenario in scenarios:
            sname = scenario["name"]
            agent = scenario["agent"]
            for measure in measures:
                for cond_name in measure["applies_to"]:
                    cond = scenario[cond_name]
                    statement = measure["template"].format(
                        agent=agent, verb=cond["verb"], outcome=cond["outcome"]
                    )
                    statement = statement[0].upper() + statement[1:]
                    full_prompt = (
                        cond["vignette"]
                        + "\n\nTo what extent do you agree with the following statement?"
                        + "\n\"" + statement + "\""
                        + "\n\nRespond with only a number from 1 to 7."
                    )
                    print("Running:", model, "-", sname, "-", measure["name"], "-", cond_name)
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
                        row = {"model": model, "scenario": sname, "measure": measure["name"],
                               "condition": cond_name, "run": run + 1, "rating": rating}
                        rows.append(row)
                        writer.writerow(row)   # write each result immediately...
                        f.flush()              # ...and force it to disk now

print("\nSaved", len(rows), "rows to", outfile)

def mean_of(model, sname, measure, cond):
    vals = [r["rating"] for r in rows if r["model"] == model and r["scenario"] == sname
            and r["measure"] == measure and r["condition"] == cond and r["rating"] is not None]
    return statistics.mean(vals) if vals else None

for model in MODELS:
    print("\n=================================")
    print("MODEL:", model)
    print("=================================")
    for scenario in scenarios:
        sname = scenario["name"]
        print(f"\n  [{sname}]")
        for m in ["intentionality", "responsibility", "causation"]:
            h = mean_of(model, sname, m, "harm")
            p = mean_of(model, sname, m, "help")
            if h is not None and p is not None:
                print(f"    {m:15} harm={round(h,2)} help={round(p,2)} asymmetry={round(h-p,2)}")
        b = mean_of(model, sname, "blame", "harm")
        pr = mean_of(model, sname, "praise", "help")
        if b is not None and pr is not None:
            print(f"    blame(harm)={round(b,2)}  praise(help)={round(pr,2)}  blame-praise={round(b-pr,2)}")