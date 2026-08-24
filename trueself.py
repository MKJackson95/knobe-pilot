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
        "name": "wallet",
        "statement": "Mark's behaviour reflects who he truly is, deep down.",
        "good": (
            "Mark is a successful businessman. One day, Mark came across a stranger "
            "who had dropped their wallet on a busy street. Mark picked up the wallet, "
            "found the owner's address inside, and personally returned it with all the "
            "money still in it."
        ),
        "bad": (
            "Mark is a successful businessman. One day, Mark came across a stranger "
            "who had dropped their wallet on a busy street. Mark picked up the wallet, "
            "took all the money out of it, and threw the empty wallet away."
        ),
    },
    {
        "name": "colleague",
        "statement": "Sarah's behaviour reflects who she truly is, deep down.",
        "good": (
            "Sarah works at a busy office. One day, a colleague was struggling to "
            "finish an important project before the deadline. Sarah stayed late, "
            "without being asked, and helped the colleague finish the work."
        ),
        "bad": (
            "Sarah works at a busy office. One day, a colleague was struggling to "
            "finish an important project before the deadline. Sarah secretly deleted "
            "part of the colleague's work, so that the colleague would miss the "
            "deadline and look bad."
        ),
    },
    {
        "name": "neighbour",
        "statement": "David's behaviour reflects who he truly is, deep down.",
        "good": (
            "David lives in a small neighbourhood. One evening, he noticed that an "
            "elderly neighbour who lived alone had not collected their mail for several "
            "days. David checked on the neighbour, found they had fallen and could not "
            "get up, and called for help, very likely saving their life."
        ),
        "bad": (
            "David lives in a small neighbourhood. One evening, he noticed that an "
            "elderly neighbour who lived alone had not collected their mail for several "
            "days. David ignored it completely, and later claimed he had never noticed "
            "anything, even though the neighbour had been seriously hurt."
        ),
    },
]

rows = []
for scenario in scenarios:
    name = scenario["name"]
    statement = scenario["statement"]
    for cond in ["good", "bad"]:
        vignette = scenario[cond]
        question = (
            "\n\nTo what extent do you agree with this statement?"
            "\n\"" + statement + "\""
            "\n\nRespond with only a number from 1 to 7."
        )
        print("Running:", name, "-", cond)
        for run in range(N_RUNS):
            message = client.messages.create(
                model=MODEL,
                max_tokens=10,
                temperature=TEMPERATURE,
                system=system_prompt,
                messages=[{"role": "user", "content": vignette + question}],
            )
            raw = message.content[0].text.strip()
            try:
                rating = int(raw)
            except ValueError:
                rating = None
            rows.append({"scenario": name, "condition": cond, "run": run + 1, "rating": rating})

with open("trueself_results.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["scenario", "condition", "run", "rating"])
    writer.writeheader()
    writer.writerows(rows)

print("\nSaved", len(rows), "rows to trueself_results.csv")

print("\n=== Results by scenario ===")
for scenario in scenarios:
    name = scenario["name"]
    good_vals = [r["rating"] for r in rows
                 if r["scenario"] == name and r["condition"] == "good" and r["rating"] is not None]
    bad_vals = [r["rating"] for r in rows
                if r["scenario"] == name and r["condition"] == "bad" and r["rating"] is not None]
    if good_vals and bad_vals:
        gm = statistics.mean(good_vals)
        bm = statistics.mean(bad_vals)
        gsd = statistics.stdev(good_vals) if len(good_vals) > 1 else 0
        bsd = statistics.stdev(bad_vals) if len(bad_vals) > 1 else 0
        print(f"\n{name}:")
        print(f"  good: n={len(good_vals)} mean={round(gm,2)} stdev={round(gsd,2)}")
        print(f"  bad:  n={len(bad_vals)} mean={round(bm,2)} stdev={round(bsd,2)}")
        print(f"  true-self asymmetry (good - bad): {round(gm - bm, 2)}")

all_good = [r["rating"] for r in rows if r["condition"] == "good" and r["rating"] is not None]
all_bad = [r["rating"] for r in rows if r["condition"] == "bad" and r["rating"] is not None]
print("\n=== Overall (pooled across scenarios) ===")
print(f"good: mean={round(statistics.mean(all_good),2)} stdev={round(statistics.stdev(all_good),2)}")
print(f"bad:  mean={round(statistics.mean(all_bad),2)} stdev={round(statistics.stdev(all_bad),2)}")
print(f"overall true-self asymmetry: {round(statistics.mean(all_good) - statistics.mean(all_bad), 2)}")