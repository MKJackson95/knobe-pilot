import csv
import statistics
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

MODELS = ["claude-haiku-4-5-20251001", "claude-sonnet-4-6", "claude-opus-4-8"]
N_RUNS = 20
TEMPERATURE = 1.0

system_prompt = (
    "You are a participant in a psychology study. "
    "You will read a short scenario and answer one question about it. "
    "Respond with ONLY a single whole number from 1 to 7, and nothing else "
    "(no words, no punctuation, no explanation). "
    "Scale: 1 = strongly disagree, 7 = strongly agree."
)

# Each scenario has a bad-bare version and a bad-out-of-character version.
scenarios = [
    {
        "name": "wallet",
        "statement": "Mark's behaviour reflects who he truly is, deep down.",
        "bad": (
            "Mark is a successful businessman. One day, Mark came across a stranger "
            "who had dropped their wallet on a busy street. Mark picked up the wallet, "
            "took all the money out of it, and threw the empty wallet away."
        ),
        "bad_ooc": (
            "Mark is normally an honest and generous person whom everyone trusts. "
            "One day, under extreme and unusual financial stress, in a single moment "
            "completely unlike him, Mark came across a stranger's dropped wallet, took "
            "the money out of it, and threw the wallet away. He immediately regretted "
            "it and it never happened again."
        ),
    },
    {
        "name": "colleague",
        "statement": "Sarah's behaviour reflects who she truly is, deep down.",
        "bad": (
            "Sarah works at a busy office. One day, a colleague was struggling to "
            "finish an important project before the deadline. Sarah secretly deleted "
            "part of the colleague's work, so that the colleague would miss the "
            "deadline and look bad."
        ),
        "bad_ooc": (
            "Sarah is normally a generous, kind, and supportive person whom everyone "
            "trusts. One day, under extreme and unusual stress, in a single moment "
            "completely unlike her, she secretly deleted part of a colleague's work, "
            "so that the colleague would miss an important deadline. She immediately "
            "regretted it and it never happened again."
        ),
    },
    {
        "name": "neighbour",
        "statement": "David's behaviour reflects who he truly is, deep down.",
        "bad": (
            "David lives in a small neighbourhood. One evening, he noticed that an "
            "elderly neighbour who lived alone had not collected their mail for several "
            "days. David ignored it completely, and later claimed he had never noticed "
            "anything, even though the neighbour had been seriously hurt."
        ),
        "bad_ooc": (
            "David is normally a caring and attentive person whom everyone trusts. "
            "One evening, under extreme and unusual stress, in a single moment "
            "completely unlike him, he noticed an elderly neighbour had not collected "
            "their mail for days but ignored it completely, and the neighbour turned "
            "out to have been seriously hurt. He immediately regretted it and it never "
            "happened again."
        ),
    },
]

rows = []
for model in MODELS:
    for scenario in scenarios:
        name = scenario["name"]
        statement = scenario["statement"]
        for framing in ["bad", "bad_ooc"]:
            vignette = scenario[framing]
            question = (
                "\n\nTo what extent do you agree with this statement?"
                "\n\"" + statement + "\""
                "\n\nRespond with only a number from 1 to 7."
            )
            print("Running:", model, "-", name, "-", framing)
            for run in range(N_RUNS):
                message = client.messages.create(
                    model=model,
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
                rows.append({"model": model, "scenario": name,
                             "framing": framing, "run": run + 1, "rating": rating})

with open("ooc_check_results.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["model", "scenario", "framing", "run", "rating"])
    writer.writeheader()
    writer.writerows(rows)

print("\nSaved", len(rows), "rows to ooc_check_results.csv")

for model in MODELS:
    print("\n=================================")
    print("MODEL:", model)
    print("=================================")
    for scenario in scenarios:
        name = scenario["name"]
        bare = [r["rating"] for r in rows if r["model"] == model
                and r["scenario"] == name and r["framing"] == "bad" and r["rating"] is not None]
        ooc = [r["rating"] for r in rows if r["model"] == model
               and r["scenario"] == name and r["framing"] == "bad_ooc" and r["rating"] is not None]
        if bare and ooc:
            bm = statistics.mean(bare)
            om = statistics.mean(ooc)
            print(f"  {name:10}  bad={round(bm,2)}  bad_ooc={round(om,2)}  drop={round(bm - om, 2)}")